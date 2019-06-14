from gensim.models import FastText
from py2neo import Graph
import numpy as np
import pandas as pd
import itertools
import statistics

# import requests, zipfile, io
# ft_url = 'https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki-news-300d-1M-subword.bin.zip'
# r = requests.get(ft_url)
# z = zipfile.ZipFile(io.BytesIO(r.content))
# z.extractall()
# TODO: install model via docker or python code and put it into the data folder

graph = Graph()
pred_sim_matrix = None
model = FastText.load_fasttext_format("./data/cc.en.300.bin")
predicates = {pred["key"]: pred["value"] for pred in graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, "
                                                               "p.label as value")}


def compute_similarity_among_predicates():
    preds = list(predicates.values())
    res = {}
    for first in range(len(preds)):
        temp = {}
        for second in range(len(preds)):
            temp[preds[second]] = model.similarity(preds[first], preds[second])
        res[preds[first]] = temp
    df = pd.DataFrame.from_dict(res)
    df = df.fillna(0) + df.fillna(0).T
    np.fill_diagonal(df.values, 1.0)
    return df


def get_sub_graph_predicates(resource):
    return [x["predicate"] for x in graph.run("MATCH (n:Resource {resource_id: \""+resource+"\"}) CALL "
                                                                                            "apoc.path.subgraphAll(n, "
                                                                                            "{relationshipFilter:'>', "
                                                                                            "bfs:true}) YIELD "
                                                                                            "relationships UNWIND "
                                                                                            "relationships as rel "
                                                                                            "RETURN startNode("
                                                                                            "rel).label as subject, "
                                                                                            "startNode("
                                                                                            "rel).resource_id as "
                                                                                            "subject_id, "
                                                                                            "rel.predicate_id as "
                                                                                            "predicate, "
                                                                                            "endNode(rel).label as "
                                                                                            "object, "
                                                                                            "endNode(rel).resource_id "
                                                                                            "as object_id")]


def _remove_used_preds(to_compare, found):
    temp = []
    for list in to_compare:
        temp.append([pred for pred in list if pred not in found])
    return temp


def _get_common_among_k(tuples, found, k):
    print(f'dic: {found}, k: {k}')
    new_found = found
    if k > len(tuples[0]):
        return new_found
    for tup in tuples:
        combinations = list(itertools.combinations(tup, k))
        sims = [(pair[0], pair[1], pred_sim_matrix.at[predicates[pair[0]], predicates[pair[1]]])
                for comb in combinations for pair in list(itertools.combinations(comb, 2))]
        if sum(1 for sim in sims if sim[2] >= 0.85) >= k-1:
            for sim in sims:
                if sim[2] >= 0.85:
                    holder = new_found[sim[0]]
                    holder['freq'] = k
                    holder['similar'].add(sim[0])
                    holder['similar'].add(sim[1])
                    new_found[sim[0]] = holder
    new_found = _get_common_among_k(tuples, new_found, k + 1)
    return new_found


def get_common_predicates(resources):
    to_compare = [list(set(get_sub_graph_predicates(res))) for res in resources]
    # to_compare = [['P9', 'P1001', 'P6'], ['P10', 'P1001', 'P7'], ['P1003', 'P1001', 'P6']]
    # dic = {common: len(resources) for common in set.intersection(*[set(list) for list in to_compare])}
    # to_compare = _remove_used_preds(to_compare, dic)
    tuples = list(itertools.product(*to_compare))
    dic = _get_common_among_k(tuples, {item: {'freq': 1, 'similar': {item}} for item in set([x for y in to_compare for x in y])}, 2)
    print(f'final dic: {dic}')
    return dic


if __name__ == '__main__':
    pred_sim_matrix = compute_similarity_among_predicates()
    x = get_common_predicates(["R1301", "R1311", "R0"])
