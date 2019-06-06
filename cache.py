import numpy as np
import pandas as pd
from py2neo import Graph
import similarity as sim

graph = Graph()

# class Cache:
#     def __init__(self):
#         self._


def get_papers():
    papers = graph.run("MATCH (n)-[p]->() WHERE p.predicate_id = 'P1001' RETURN n.resource_id as id").data()
    return [p["id"] for p in papers]


if __name__ == '__main__':
    resources = get_papers()
    dic = {}
    for first in resources:
        temp = {}
        for second in resources:
            temp[second] = sim.compute_similarity_between_two_entities(first, second)
        dic[first] = temp

