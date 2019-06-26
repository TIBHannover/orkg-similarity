from elasticsearch import Elasticsearch
from connection.neo4j import Neo4J
import os

es = Elasticsearch(hosts=[os.environ["SIMCOMP_ELASTIC_HOST"]] if "SIMCOMP_ELASTIC_HOST" in os.environ  else ['http://localhost:9200'])
neo4j = Neo4J.getInstance()
__INDEX_NAME__ = "test"  # TODO: Add index name from env variables (read from docker-compose)


def get_document(cont):
    content = neo4j._Neo4J__get_subgraph(cont, False)
    document = ""
    for part in content:
        document = '%s %s %s %s' % (document, part["subject"], neo4j.predicates[part["predicate"]], part["object"])
        #document = f'{document} {part["subject"]} {neo4j.predicates[part["predicate"]]} {part["object"]}'
    return document


def create_index():
    # create an index in elasticsearch, ignore status code 400 (index already exists)
    es.indices.create(index=__INDEX_NAME__, ignore=400)
    for cont in neo4j.contributions:
        document = get_document(cont)
        es.index(index=__INDEX_NAME__, id=cont, body={"content": document})


def index_document(cont):
    document = get_document(cont)
    es.index(index=__INDEX_NAME__, id=cont, body={"content": document})


def query_index(cont, top_k=5):
    neo4j.update_predicates()
    query = get_document(cont)
    body = '{"query": { "match" : { "content" : { "query" : "' + query + '" } } }, "size":' + str(top_k+1) + '}'
    interm_results = es.search(index="test", body=body)
    try:
        similar = {hit["_id"]: hit["_score"] for hit in interm_results["hits"]["hits"]}
        max_score = max(list(similar.values()))
        for key in similar.keys():
            similar[key] = similar[key]/max_score
        if cont in similar:
            del similar[cont]
        return similar
    except:
        return {}


if __name__ == '__main__':
    create_index()
    similar = query_index("R925")
    print(similar)
