from typing import Dict
import numpy as np
import itertools
from connection.neo4j import Neo4J
from fuzzywuzzy import fuzz as model
from sklearn.metrics import pairwise_distances


__SIMILARITY_THRESHOLD__ = 0.90
neo4j = Neo4J.getInstance()
stopwords = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out',
             'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into',
             'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the',
             'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were',
             'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to',
             'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have',
             'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can',
             'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself',
             'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by',
             'doing', 'it', 'how', 'further', 'was', 'here', 'than'}


def compute_similarity_among_predicates(contributions):
    similarity_cache = {}
    predicates = neo4j.get_predicates_of_contributions(contributions)
    pred_label_index = {value: index for (_, value), index in zip(predicates.items(), range(len(predicates)))}
    pred_index_id = {index: key for (key, _), index in zip(predicates.items(), range(len(predicates)))}
    pred_id_index = {key: index for (key, _), index in zip(predicates.items(), range(len(predicates)))}
    predicates_values = [' '.join([w for w in val.lower().split(' ') if w not in stopwords])for val in predicates.values()]

    def custom_fuzz_metric(s1, s2):
        i1 = int(s1[0])
        i2 = int(s2[0])
        if i1 == i2:
            return 1.0
        if (i1, i2) in similarity_cache:
            return similarity_cache[(i1, i2)]
        similarity = model.ratio(predicates_values[i1], predicates_values[i2]) / 100.0
        similarity_cache[(i1, i2)] = similarity
        similarity_cache[(i2, i1)] = similarity
        return similarity

    pred_sim_matrix = pairwise_distances(X=np.array(range(len(predicates_values))).reshape(-1, 1), metric=custom_fuzz_metric)
    return pred_sim_matrix, pred_label_index, pred_index_id, pred_id_index, predicates


def remove_redundant_entries(entries):
    to_remove = []
    for pred, info in entries.items():
        for pred_2, info_2 in entries.items():
            if pred == pred_2:
                continue
            if info_2['freq'] > info['freq']:
                if pred in info_2['similar']:
                    to_remove.append(pred)
    return {key: value for key, value in entries.items() if key not in set(to_remove)}


def get_common_predicates_efficient(resources, pred_id_index, pred_index_id, pred_sim_matrix):
    to_compare = [list(set(neo4j.get_subgraph_predicates(res))) for res in resources]
    used = list(set(itertools.chain(*to_compare)))
    mask = np.full((len(resources), len(pred_id_index)), False)
    for i in range(len(to_compare)):
        for pred in to_compare[i]:
            mask[i][pred_id_index[pred]] = True
    found = {}
    for pred in used:
        if pred in found:
            continue
        key = pred_id_index[pred]
        similar = np.where(pred_sim_matrix[key] > __SIMILARITY_THRESHOLD__)
        freq = np.sum(np.any(np.sum(mask[:, similar], axis=1), axis=1))
        similar_ids = set([pred_index_id[index] for index in similar[0]])
        found[pred] = {'freq': freq, 'similar': similar_ids}
    return found


def trace_back_path(tuples, path, subject, cont, visited, predicates):
    if subject == cont or subject in visited:
        path_array = path.split("//")
        return path_array, [neo4j.get_resource_label(path_array[i]) if i % 2 == 0
                            else predicates[path_array[i]] for i in range(len(path_array))]
    visited.append(subject)
    for tuple in tuples:
        if tuple[2] == subject:
            return trace_back_path(tuples, "%s//%s//%s" % (tuple[4], tuple[0], path), tuple[4], cont, visited, predicates)


def compare_resources(resources):
    pred_sim_matrix, pred_label_index, pred_index_id, pred_id_index, predicates = compute_similarity_among_predicates(resources)
    resources = [res for res in resources if res in neo4j.contributions]
    if len(resources) == 0:
        return [], [], {}
    out_contributions = neo4j.get_contributions_with_details(resources)
    common = remove_redundant_entries(get_common_predicates_efficient(resources, pred_id_index, pred_index_id, pred_sim_matrix))
    graphs = {res: neo4j.get_subgraph_full(res) for res in resources}
    data = {}
    similar_keys = {}
    for key, value in common.items():
        for sim in value['similar']:
            similar_keys[sim] = key
    for res, content in graphs.items():
        for tup in content:
            in_common = tup[0] in common
            in_similar = tup[0] in list(itertools.chain(*[list(i) for i in [value['similar'] for value in common.values()]]))
            if in_common or in_similar:
                key = similar_keys[tup[0]]
                if key not in data:
                    data[key] = {}
                if res not in data[key]:
                    data[key][res] = []
                resource_id = tup[2] if tup[2] is not None else tup[3]
                if resource_id in set([value['resourceId'] for value in data[key][res]]):  # remove duplicate values
                    continue
                path, path_labels = trace_back_path(content, "%s//%s" % (tup[4], tup[0]), tup[4], res, [], predicates)
                data[key][res].append({'label': tup[1], 'resourceId': resource_id,
                                       'type': 'resource' if tup[2] is not None else 'literal',
                                       'path': path, 'pathLabels': path_labels, 'classes': tup[-1]})
    out_predicates = [{'id': key, 'label': predicates[key], 'contributionAmount': value['freq'],
                       'active': True if value['freq'] >= 2 else False} for key, value in common.items() if
                      key in set(similar_keys.values())]
    out_data = {pred: [content[res] if res in content else [{}] for res in resources] for pred, content in data.items()}
    out_predicates = [pred for pred in out_predicates if pred['id'] in out_data.keys()]
    return out_contributions, out_predicates, out_data

