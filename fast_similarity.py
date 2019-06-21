from fuzzywuzzy import fuzz
from time import time
from connection.neo4j import Neo4J

__VERBOSE__ = False

neo4j = Neo4J.getInstance()


def get_subgraph(start):
    paths = neo4j._Neo4J__get_subgraph(start)
    result = ""
    for path in paths:
        result = f'{result} {path["subject"]} {neo4j.predicates[path["predicate"]]} {path["object"]}'
    return result


def compute_similarity_between_two_entities(first, second):
    path1 = get_subgraph(first)
    path2 = get_subgraph(second)
    return fuzz.token_set_ratio(path1, path2)


if __name__ == '__main__':
    st = time()
    x = compute_similarity_between_two_entities("R1", "R494")
    ed = time()
    print(f'TIME: ========== {ed-st} SECONDS ==========')
