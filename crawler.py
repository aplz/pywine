import time

import requests
from elasticsearch import Elasticsearch

import config
from config import apikey
from config import logger

base_catalog_url = "http://services.wine.com/api/beta2/service.svc/json/catalog"


def crawl(api_key, limit=0):
    es = Elasticsearch()

    # create the index if it doesn't exist already.
    # es.indices.create(index=config.INDEX, body=mapping)

    # fetch the total number of available wines first
    initial_query = {'filter': 'categories(490)', 'apikey': api_key, 'size': 0, 'offset': 0}
    initial_response = requests.get(base_catalog_url, params=initial_query).json()
    total_wines = initial_response['Products']['Total']
    logger.info("Total number of wines available: %s" % total_wines)

    # set the total number of products to be requested
    if limit == 0:
        # If you don't want all wines, use something smaller like 5000
        limit = total_wines

    # set the maximum number of products by request
    page_size = 500
    offset = 0
    wines_json = []

    catalog_query_params = {
        'filter': 'categories(490)',
        'apikey': apikey,
        'size': page_size,
        'offset': offset
    }
    while offset < limit:
        response = requests.get(base_catalog_url, params=catalog_query_params).json()
        wines_json.extend(response['Products']['List'])
        for wine in wines_json:
            # flattening the nested objects is merely necessary so that we can visualize them with kibana that does
            # not support nested objects currently
            flattened = join_nested(wine, parent_key='ProductAttributes', child_key='Name')
            wine['ProductAttributesNames'] = flattened
            es.index(index=config.INDEX, doc_type=config.DOC_TYPE, id=wine['Id'], body=wine)

        logger.info("Read %s wines from Wine.com so far" % len(wines_json))
        offset = offset + page_size
        catalog_query_params['offset'] = offset
        time.sleep(1)


def join_nested(wine, parent_key, child_key):
    joined_attributes = list()
    for attributes in wine[parent_key]:
        joined_attributes.append(attributes[child_key])
    return joined_attributes


if __name__ == '__main__':
    crawl(apikey, limit=0)
