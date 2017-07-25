from elasticsearch import Elasticsearch, helpers

from config import logger
from index_config import INDEX, DOC_TYPE


def decorate():
    """
    The attribute 'Vintage' can be used as a timestamp. To store it in a form recognizable by Kibana/Elastic,
    we use this decorator.

    :return:
    """
    es = Elasticsearch()
    query = {"query": {"bool": {
        "must": [
            # Process only items where the information stored in the field 'Vintage' resembles a value indicating a year
            {"regexp": {"Vintage.keyword": "[0-9]{4}"}}
        ],
        "must_not": [
            # skip items that already have a date field
            {"exists": {"field": "date"}}
        ]
    }}}
    bulk_size = 1000
    bulk = []
    counter = 0
    # Being not very time consuming, we can use the default parameters for 'scroll' for this operation:
    # If you're operation is more time consuming, make sure to increase this parameter to keep the context alive.
    scan_response = helpers.scan(client=es, query=query, index="wine_geo")
    for hit in scan_response:
        source = hit['_source']
        vintage = source['Vintage']
        source['date'] = "%s-01-01T00:00:00Z" % vintage
        bulk.append({'_index': INDEX, '_type': DOC_TYPE, '_id': source['Id'], '_source': source})
        counter += 1
        if counter % bulk_size == 0:
            helpers.bulk(es, bulk, chunk_size=bulk_size)
            bulk = []
            logger.info("Decorated % items with date field" % counter)
    # flush any remaining requests
    helpers.bulk(es, bulk)


if __name__ == '__main__':
    decorate()
