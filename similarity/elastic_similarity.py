import os
from connection.neo4j import Neo4J
from elasticsearch import Elasticsearch
from .document import DocumentCreator

es = Elasticsearch(
    hosts=[os.environ["SIMCOMP_ELASTIC_HOST"]] if "SIMCOMP_ELASTIC_HOST" in os.environ else ['http://localhost:9200'])
neo4j = Neo4J.getInstance()
__INDEX_NAME__ = os.environ["SIMCOMP_ELASTIC_INDEX"] if "SIMCOMP_ELASTIC_INDEX" in os.environ else "test"


def create_index():
    es.indices.create(index=__INDEX_NAME__, ignore=400)
    indexed_contributions = 0
    not_indexed = []

    for contribution_id in neo4j.contributions:

        document = DocumentCreator.create(contribution_id, neo4j)

        if not document:
            not_indexed.append(contribution_id)
            continue

        es.index(index=__INDEX_NAME__, id=contribution_id, body={'text': document})
        indexed_contributions += 1

    return {
        'indexedContributions': indexed_contributions,
        'contributions': len(neo4j.contributions),
        'notIndexedContributions': not_indexed
    }


def recreate_index():
    es.indices.delete(index=__INDEX_NAME__, ignore=[400, 404])
    neo4j.update_predicates()

    return create_index()


def index_document(contribution_id):
    neo4j.update_predicates()
    document = DocumentCreator.create(contribution_id, neo4j)

    if not document:
        return False

    es.index(index=__INDEX_NAME__, id=contribution_id, body={'text': document})

    return True


def query_index(contribution_id, top_k=5):
    neo4j.update_predicates()
    query = DocumentCreator.create(contribution_id, neo4j, is_query=True)

    if not query:
        return {}

    body = '{"query": { "match" : { "text" : { "query" : "' + query + '" } } }, "size":' + str(top_k * 2) + '}'
    interm_results = es.search(index=__INDEX_NAME__, body=body, track_scores=True)

    try:
        similar = {hit["_id"]: hit["_score"] for hit in interm_results["hits"]["hits"]}

        for key in similar.keys():
            similar[key] = similar[key] / interm_results['hits']['max_score']

        if contribution_id in similar:
            del similar[contribution_id]

        return {k: v for k, v in similar.items()}

    except:
        return {}
