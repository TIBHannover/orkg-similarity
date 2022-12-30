import os

from orkg import ORKG
from connection.neo4j import Neo4J
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError

from .document import DocumentCreator

es = Elasticsearch(
    hosts=[os.getenv('SIMCOMP_ELASTIC_HOST', 'http://localhost:9200')])
client = ORKG(host=os.getenv('ORKG_API_HOST', 'localhost'))
__INDEX_NAME__ = os.getenv('SIMCOMP_ELASTIC_INDEX', 'test')


def create_index():
    es.indices.create(index=__INDEX_NAME__, ignore=400)
    indexed_contributions = 0
    not_indexed = []

    contributions = Neo4J.getInstance().contributions
    for contribution_id in contributions:

        document = DocumentCreator.create(client, contribution_id)

        if not document:
            not_indexed.append(contribution_id)
            continue

        es.index(index=__INDEX_NAME__, id=contribution_id, body={'text': document})
        indexed_contributions += 1

    return {
        'indexedContributions': indexed_contributions,
        'contributions': len(contributions),
        'notIndexedContributions': not_indexed
    }


def recreate_index():
    es.indices.delete(index=__INDEX_NAME__, ignore=[400, 404])
    return create_index()


def index_document(contribution_id):
    document = DocumentCreator.create(client, contribution_id)

    if not document:
        return False

    es.index(index=__INDEX_NAME__, id=contribution_id, body={'text': document})

    return True


def query_index(contribution_id, top_k=5):
    query = DocumentCreator.create(client, contribution_id, is_query=True)

    if not query:
        return {}

    body = '{"query": { "match" : { "text" : { "query" : "' + query + '" } } }, "size":' + str(top_k * 2) + '}'

    try:
        interm_results = es.search(index=__INDEX_NAME__, body=body, track_scores=True)
        similar = {hit["_id"]: hit["_score"] for hit in interm_results["hits"]["hits"]}

        for key in similar.keys():
            similar[key] = similar[key] / interm_results['hits']['max_score']

        if contribution_id in similar:
            del similar[contribution_id]

        return {k: v for k, v in similar.items()}

    except (RequestError, KeyError):
        # TODO: add logging here
        # TODO: fix RequestError for longer queries by upgrading ES and configuring the query length.
        #  R247961 is an example of a long query.
        return {}
