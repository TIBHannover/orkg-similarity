from gensim.models import FastText
import numpy as np
import pandas as pd
import itertools
from connection.neo4j import Neo4J


pred_sim_matrix = None
model = FastText.load_fasttext_format("./data/cc.en.300.bin")
__SIMILARITY_THRESHOLD__ = 0.90
neo4j = Neo4J.getInstance()


def compute_similarity_among_predicates():
    neo4j.update_predicates()
    preds = list(neo4j.predicates.values())
    res = {}
    for first in range(len(preds)):
        temp = {}
        for second in range(len(preds)):
            temp[preds[second]] = model.similarity(preds[first], preds[second])
        res[preds[first]] = temp
    return pd.DataFrame.from_dict(res)


def get_similarity_from_matrix(first, second):
    if not pd.isna(pred_sim_matrix.at[first, second]):
        return pred_sim_matrix.at[first, second]
    else:
        return pred_sim_matrix.at[second, first]


def _remove_used_preds(to_compare, found):
    temp = []
    for list in to_compare:
        temp.append([pred for pred in list if pred not in found])
    return temp


def _get_common_among_k(tuples, found, k):
    new_found = found
    if k > len(tuples[0]):
        return new_found
    for tup in tuples:
        combinations = list(itertools.combinations(tup, k))
        sims = [(pair[0], pair[1], get_similarity_from_matrix(neo4j.predicates[pair[0]], neo4j.predicates[pair[1]]))
                for comb in combinations for pair in list(itertools.combinations(comb, 2))]
        if sum(1 for sim in sims if sim[2] >= __SIMILARITY_THRESHOLD__) >= k-1:
            for sim in sims:
                if sim[2] >= __SIMILARITY_THRESHOLD__:
                    holder = new_found[sim[0]]
                    holder['freq'] = k
                    holder['similar'].add(sim[0])
                    holder['similar'].add(sim[1])
                    new_found[sim[0]] = holder
    new_found = _get_common_among_k(tuples, new_found, k + 1)
    return new_found


def remove_redundant_entries(entries):
    to_remove = []
    for pred, info in entries.items():
        for pred_2, info_2 in entries.items():
            if pred == pred_2:
                continue
            if info_2['freq'] > info['freq']:
                if pred in info_2['similar']:
                    to_remove.append(pred)
    return {key: value for key, value in entries.items() if key not in list(set(to_remove))}


def get_common_predicates(resources):
    to_compare = [list(set(neo4j.get_subgraph_predicates(res))) for res in resources]
    tuples = list(itertools.product(*to_compare))
    dic = _get_common_among_k(tuples, {item: {'freq': 1, 'similar': {item}} for item in set([x for y in to_compare for x in y])}, 2)
    return dic


def compare_resources(resources):
    # TODO: check if resources exists
    out_contributions = [neo4j.get_contribution_details(res) for res in resources]
    common = remove_redundant_entries(get_common_predicates(resources))
    # TODO: (OUTPUT) add path??
    graphs = {res: neo4j.get_subgraph_full(res) for res in resources}
    data = {}
    similar_keys = {}
    for key, value in common.items():
        for sim in value['similar']:
            similar_keys[sim] = key
    for res, content in graphs.items():
        for tup in content:
            in_common = tup[0] in common
            in_simialr = tup[0] in list(itertools.chain(*[list(i) for i in [value['similar'] for value in common.values()]]))
            if in_common or in_simialr:
                key = similar_keys[tup[0]]
                if key not in data:
                    data[key] = {}
                if res not in data[key]:
                    data[key][res] = []
                data[key][res].append({'label': tup[1],
                                          'resourceId': tup[2] if tup[2] is not None else tup[3],
                                          'type': 'resource' if tup[2] is not None else 'literal'})
    out_predicates = [{'id': key, 'label': neo4j.predicates[key], 'contributionAmount': value['freq'],
                       'active': True if value['freq'] >= 2 else False} for key, value in common.items() if
                      key in list(set(similar_keys.values()))]
    out_data = {pred: [content[res] if res in content else [{}] for res in resources] for pred, content in data.items()}
    return out_contributions, out_predicates, out_data


if __name__ == '__main__':
    pred_sim_matrix = compute_similarity_among_predicates()
    x = get_similarity_from_matrix("dataset", "has research problem")
    conts, preds, data = compare_resources(["R790", "R810"])
