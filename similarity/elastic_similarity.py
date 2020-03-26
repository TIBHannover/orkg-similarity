from elasticsearch import Elasticsearch
from connection.neo4j import Neo4J
import os

es = Elasticsearch(
    hosts=[os.environ["SIMCOMP_ELASTIC_HOST"]] if "SIMCOMP_ELASTIC_HOST" in os.environ else ['http://localhost:9200'])
neo4j = Neo4J.getInstance()
__INDEX_NAME__ = os.environ["SIMCOMP_ELASTIC_INDEX"] if "SIMCOMP_ELASTIC_INDEX" in os.environ else "test"


def get_document(cont):
    content = neo4j._Neo4J__get_subgraph(cont, False)
    document = ""
    for part in content:
        document = '%s %s %s %s' % (document, part["subject"], neo4j.predicates[part["predicate"]], part["object"])
        # document = f'{document} {part["subject"]} {neo4j.predicates[part["predicate"]]} {part["object"]}'
    title = neo4j.get_contribution_paper(cont)
    document = '%s %s' % (title, document)
    return document


def create_index():
    # create an index in elasticsearch, ignore status code 400 (index already exists)
    es.indices.create(index=__INDEX_NAME__, ignore=400)
    # es.indices.put_settings(index=__INDEX_NAME__, body={"index": {"blocks": {"read_only_allow_delete": "false"}}})
    for cont in neo4j.contributions:
        document = get_document(cont)
        es.index(index=__INDEX_NAME__, id=cont, body={"content": document})


def recreate_index():
    try:
        es.indices.delete(index=__INDEX_NAME__)
    except:
        pass
    create_index()


def index_document(cont):
    document = get_document(cont)
    es.index(index=__INDEX_NAME__, id=cont, body={"content": document})


escape_rules = {'+': r'\+',
                '-': r'\-',
                '&': r'\&',
                '|': r'\|',
                '!': r'\!',
                '(': r'\(',
                ')': r'\)',
                '{': r'\{',
                '}': r'\}',
                '[': r'\[',
                ']': r'\]',
                '^': r'\^',
                '~': r'\~',
                '*': r'\*',
                '?': r'\?',
                ':': r'\:',
                '"': r'\"',
                '\\': r'\\;',
                '/': r'\/',
                '>': r' ',
                '<': r' '}


def escaped_seq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escape_rules.keys():
            yield escape_rules[char]
        else:
            yield char


def escape_es_query(query):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = query.replace('\\', r'\\')  # escape \ first
    return "".join([nextStr for nextStr in escaped_seq(term)])


def query_index(cont, top_k=5):
    neo4j.update_predicates()
    query = get_document(cont)
    query = escape_es_query(query)
    body = '{"query": { "match" : { "content" : { "query" : "' + query + '" } } }, "size":' + str(top_k * 2) + '}'
    interm_results = es.search(index="test", body=body)
    try:
        similar = {hit["_id"]: hit["_score"] for hit in interm_results["hits"]["hits"]}
        max_score = max(list(similar.values()))
        for key in similar.keys():
            similar[key] = similar[key] / max_score
        if cont in similar:
            del similar[cont]
        return {k: v for k, v in similar.items() if v <= 0.8}
    except:
        return {}


if __name__ == '__main__':
    # create_index()
    # index_document("R61003")
    similar = query_index("R91001")
    # results = sorted([{'paperId': item[0]['paperId'],
    #                   'contributionId': item[0]['id'],
    #                   'contributionLabel': item[0]['contributionLabel'],
    #                   'similarityPercentage': item[1]}
    #                  for item in [(neo4j.get_contribution_details(cont), sim) for cont, sim in similar.items()
    #                               if cont in neo4j.contributions]],
    #                 key=lambda i: i['similarityPercentage'], reverse=True)
    print(similar)
