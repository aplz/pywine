from elasticsearch import Elasticsearch, helpers

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
    scan_response = helpers.scan(client=es, query=query, scroll="10m", index="wine_geo", timeout="10m")
    for hit in scan_response:
        source = hit['_source']
        vintage = source['Vintage']
        source['date'] = "%s-01-01T00:00:00Z" % vintage
        es.index(index=INDEX, doc_type=DOC_TYPE, id=source['Id'], body=source)


if __name__ == '__main__':
    decorate()
