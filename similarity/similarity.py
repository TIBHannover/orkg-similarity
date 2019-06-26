from py2neo import Graph
from fuzzywuzzy import fuzz
import itertools
import statistics
from time import time

graph = Graph()
cut_threshold = 0.4

__VERBOSE__ = False


def walk_the_graph(walks, start, walk=None):
    if start is None:
        return
    paths = graph.run("MATCH (s{resource_id: '" + start + "'})-[p]->(o) MATCH (pr:Predicate{predicate_id : "
                                                          "p.predicate_id}) RETURN s.label as subject,pr.label as "
                                                          "predicate,o.label as object, o.resource_id as object_id,"
                                                          "size((o)-->()) as out, size((o)<--()) as in").data()
    for path in paths:
        if walk is None:
            new_walk = f'{path["subject"]}/{path["predicate"]}/{path["object"]}'
        else:
            new_walk = f'{walk}/{path["predicate"]}/{path["object"]}'
        if __VERBOSE__:
            print(new_walk)
        walks.append(new_walk)
        if path["out"] / path["in"] > cut_threshold:
            walk_the_graph(walks, path["object_id"], new_walk)


def filter_walks_by_steps(walks, steps_min=2, steps_max=None):
    new_list = list(filter(lambda x: (x.count('/') / 2.0 >= steps_min), walks))
    if steps_max is not None:
        new_list = list(filter(lambda x: (x.count('/') / 2.0 <= steps_max), new_list))
    return new_list


def compute_similarity_between_two_entities(first, second):
    walks1 = []
    walk_the_graph(walks1, first)
    # walks1 = filter_walks_by_steps(walks1, steps_min=1)

    walks2 = []
    walk_the_graph(walks2, second)
    # walks2 = filter_walks_by_steps(walks2, steps_min=1)

    ratios = []
    for perm in itertools.product(walks1, walks2):
        ratios.append(fuzz.partial_ratio(perm[0], perm[1]))  # (token_set_ratio) another method to use
    if __VERBOSE__:
        print(ratios)
    if len(ratios) > 0:
        return statistics.mean(ratios)  # perhaps we can use a median also to compute it!!
    else:
        return 0.0


if __name__ == '__main__':
    st = time()
    print(compute_similarity_between_two_entities("R0", "R1029"))
    ed = time()
    print(ed-st)
