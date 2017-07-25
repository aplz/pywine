import time

import requests
from elasticsearch import Elasticsearch, helpers

from config import logger
from index_config import INDEX, DOC_TYPE

GOOGLE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'


def fetch_address(address):
    """
    Query the google api for the given address and try to receive latitude and longitude information. The result is a
    dictionary with keys latitude and longitude where each value is set according to the response of the request. If
    the request was not successful because no or more than one address were returned or any other error occurs during
    the API request, the respective values are set to 'None'.

    :param address: the address of interest.
    :return: a dictionary with keys latitude and longitude.
    """
    geo_location = {"latitude": None, "longitude": None}
    logger.info("Querying for address '%s'", address)

    response = requests.get(GOOGLE_URL, params={'address': address})
    time.sleep(1)

    try:
        body = response.json()
    except:
        logger.error(response.status_code)
        logger.error(response.text)
        return geo_location

    if body['status'] == 'OK':
        if len(body['results']) == 1:
            if 'geometry' in body['results'][0]:
                location = body['results'][0]['geometry']['location']
                geo_location['latitude'] = location['lat']
                geo_location['longitude'] = location['lng']
        else:
            logger.warning("Address is ambiguous!")
    elif body['status'] == 'ZERO_RESULTS':
        logger.debug("Unknown address.")
    elif body['status'] == 'OVER_QUERY_LIMIT':
        logger.warning(body)
    else:
        logger.error("ERROR: status is unknown!")
        logger.error(body)

    return geo_location


def decorate(num_calls=10):
    es = Elasticsearch()
    # This loop is necessary so that we can fetch one item without location, update the index accordingly and refresh
    # it. This is necessary to avoid duplicate calls to the google api with the same address.
    # We could also use a while loop but this gives a little more explict control on the number of requests.
    for i in range(0, num_calls):
        # fetch indexed item without location field
        hits = es.search(index=INDEX, body=has_no_location_query(), size=1)
        items_without_address = len(hits["hits"]['hits'])
        logger.info("Found %s items without address." % items_without_address)
        if items_without_address == 0:
            logger.info("No more items available without address. Aborting.")
            break
        for hit in hits["hits"]['hits']:
            source = hit['_source']
            region_name = source['Appellation']['Region']['Name']
            name = source['Appellation']['Name']
            geo_location = fetch_address(address=("%s %s" % (name, region_name)))
            logger.info("Fetched address %s:", geo_location)
            # update all vineyards located in the region specified by 'address' with the according latitude and
            # longitude information
            located_at = es.search(index=INDEX,
                                   body=is_located_at_query(appellation_name=name, appellation_region=region_name),
                                   size=10000)
            # update the location field for all vineyards that are in that region
            bulk = []
            for entity in located_at["hits"]['hits']:
                entity_source = entity['_source']
                if geo_location['latitude'] is not None:
                    entity_source['location'] = {"lat": geo_location['latitude'], "lon": geo_location['longitude']}
                else:
                    entity_source['location'] = {"lat": -1, "lon": -1}
                bulk.append({'_index': INDEX, '_type': DOC_TYPE, '_id': entity_source['Id'], '_source': entity_source})
            helpers.bulk(es, bulk, chunk_size=len(bulk))
        es.indices.refresh(index=INDEX)


def has_no_location_query():
    return {"query": {"bool": {"must_not": [{"exists": {"field": "location"}}]}}}


def is_located_at_query(appellation_name, appellation_region):
    return {"query": {"bool": {"must": [
        {"term": {"Appellation.Name.keyword": appellation_name}},
        {"term": {"Appellation.Region.Name.keyword": appellation_region}}
    ]}}}


if __name__ == '__main__':
    decorate()
