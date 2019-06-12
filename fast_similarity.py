from py2neo import Graph
from fuzzywuzzy import fuzz
from time import time

__VERBOSE__ = False
graph = Graph()
graph_cache = {}
predicates = {pred["key"]: pred["value"] for pred in graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, "
                                                               "p.label as value")}


def get_subgraph(start, bfs=True):
    if start in graph_cache:
        if __VERBOSE__:
            print(f"CACHE HIT {start}")
        return graph_cache[start]
    if __VERBOSE__:
        print(f"CACHE MISS! {start}")
    do_bfs = "true" if bfs is True else "false"
    paths = graph.run("MATCH (n:Resource {resource_id: \"" + start + "\"}) CALL apoc.path.subgraphAll(n, "
                                                                     "{relationshipFilter:'>', bfs:" + do_bfs + "}) YIELD "
                                                                                                                "relationships UNWIND relationships as rel RETURN startNode(rel).label as subject, startNode(rel).resource_id as subject_id, rel.predicate_id as predicate, endNode(rel).label as object, endNode(rel).resource_id as object_id")
    result = ""
    for path in paths:
        result = f'{result} {path["subject"]} {predicates[path["predicate"]]} {path["object"]}'
    graph_cache[start] = result
    return result


def compute_similarity_between_two_entities(first, second):
    path1 = get_subgraph(first)
    path2 = get_subgraph(second)
    return fuzz.token_set_ratio(path1, path2)


if __name__ == '__main__':
    st = time()
    x = compute_similarity_between_two_entities("R1", "R0")
    ed = time()
    print(f'TIME: ========== {ed-st} SECONDS ==========')
