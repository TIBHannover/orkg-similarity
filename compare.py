from gensim.models import FastText
from py2neo import Graph
import numpy as np
import pandas as pd
import itertools


graph = Graph(host="neo4j")
pred_sim_matrix = None
model = FastText.load_fasttext_format("./data/cc.en.300.bin")
predicates = None
__SIMILARITY_THRESHOLD__ = 0.95


def update_predicates():
    return {pred["key"]: pred["value"] for pred in graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, "
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


def get_sub_graph(resource):
    return [(x['predicate'], x['object'], x['object_id'], x['literal_id']) for x in graph.run("MATCH (n:Resource {resource_id: \""+resource+"\"}) CALL apoc.path.subgraphAll(n, {relationshipFilter:'>', bfs:true}) YIELD relationships UNWIND relationships as rel RETURN startNode(rel).label as subject, startNode(rel).resource_id as subject_id, rel.predicate_id as predicate, endNode(rel).label as object, endNode(rel).resource_id as object_id, endNode(rel).literal_id as literal_id")]


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
        sims = [(pair[0], pair[1], pred_sim_matrix.at[predicates[pair[0]], predicates[pair[1]]])
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
    to_compare = [list(set(get_sub_graph_predicates(res))) for res in resources]
    tuples = list(itertools.product(*to_compare))
    dic = _get_common_among_k(tuples, {item: {'freq': 1, 'similar': {item}} for item in set([x for y in to_compare for x in y])}, 2)
    return dic


def get_contribution_details(cont):
    for neo4j_content in graph.run("MATCH (paper:Resource)-[p {predicate_id:'P31'}]->(cont:Resource {resource_id: '"+cont+"'}) RETURN paper.label as title, paper.resource_id as paper_id, cont.label as cont_label, cont.resource_id as id"):
        return {'id': neo4j_content['id'],
                'paperId': neo4j_content['paper_id'],
                'title': neo4j_content['title'],
                'contributionLabel': neo4j_content['cont_label']}


def compare_resources(resources):
    # TODO: check if resources exists
    out_contributions = [get_contribution_details(res) for res in resources]
    common = remove_redundant_entries(get_common_predicates(resources))
    # TODO: (OUTPUT) add path??
    out_predicates = [{'id': key, 'label': predicates[key], 'contributionAmount': value['freq'], 'active':True if value['freq'] >= 2 else False} for key, value in common.items()]
    graphs = {res: get_sub_graph(res) for res in resources}
    data = {}
    for res, content in graphs.items():
        for tup in content:
            if tup[0] in common or tup[0] in [i for i in [value['similar'] for value in common.values()]]:
                if tup[0] not in data:
                    data[tup[0]] = {}
                if res not in data[tup[0]]:
                    data[tup[0]][res] = []
                data[tup[0]][res].append({'label': tup[1],
                                          'resourceId': tup[2] if tup[2] is not None else tup[3],
                                          'type': 'resource' if tup[2] is not None else 'literal'})
    out_data = {pred: [content[res] if res in content else [{}] for res in resources] for pred, content in data.items()}
    return out_contributions, out_predicates, out_data


if __name__ == '__main__':
    pred_sim_matrix = compute_similarity_among_predicates()
    conts, preds, data = compare_resources(["R490", "R499", "R518"])
