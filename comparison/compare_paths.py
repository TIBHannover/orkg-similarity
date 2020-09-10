from typing import List
from connection.neo4j import Neo4J
import numpy as np

neo4j = Neo4J.getInstance()


def stringify(self: List[str]) -> str:
    """
    Convert the list of strings to a string separated by /
    :param self: the list of strings
    :return: a string combined from the input list
    """
    return '/'.join(self)


def get_path_labels(components: List[str]) -> List[str]:
    """
    extracts the labels for the given IDs of the resources and predicates
    :param components: list of IDs in the from resource_id, predicate_id, .....
    :return: a list of labels skipping the first one which is the contribution
    """
    return [neo4j.get_resource_label(components[i]).strip().lower() if i % 2 == 0
            else neo4j.predicates[components[i]].strip().lower() for i in range(len(components))][1:]


def compare_resources(resources: List[str]):
    """
    compares resources based on the paths of the spanning tree of each resource
    :param resources: list of contribution ids
    :return:
    """
    resources = [res for res in resources if res in neo4j.contributions]
    if len(resources) == 0:
        return [], [], {}
    out_contributions = [neo4j.get_contribution_details(res) for res in resources]
    paths_dict = {res: neo4j.get_spanning_tree(res) for res in resources}
    # Fetch labels for path ids
    for _, paths in paths_dict.items():
        for i in range(len(paths)):
            paths[i]['path_labels'] = get_path_labels(paths[i]['path_components'])
    # Create comparison matrix
    paths_set = set()
    for _, paths in paths_dict.items():
        for i in range(len(paths)):
            paths_set.add(stringify(paths[i]['path_labels']))
    paths_contribution_matrix = np.zeros((len(paths_set), len(resources)), dtype=bool)
    paths_indices = {path: index for index, path in enumerate(paths_set)}
    for idx, cont_id in enumerate(resources):
        for path in paths_dict[cont_id]:
            paths_contribution_matrix[paths_indices[stringify(path['path_labels'])], idx] = True
    # Transform the predicates to simcomp response format
    out_predicates = [
        {'id': path,  # TODO: Check if this valid for the frontend
         'label': path,
         'contributionAmount': np.sum(paths_contribution_matrix[path_idx]),
         'active': True if np.sum(paths_contribution_matrix[path_idx]) >= 2 else False}
        for path, path_idx in paths_indices.items()]
    # Transform the data to simcomp response format
    out_data = {}
    for path, path_idx in paths_indices.items():
        values = []
        for idx, cont_id in enumerate(resources):
            candidates_values = list(filter(lambda p: stringify(p['path_labels']) == path, paths_dict[cont_id]))
            if len(candidates_values) == 0:
                values.append([{}])
            else:
                cont_pred_values = []
                for value in candidates_values:
                    cont_pred_values.append({
                        "label": value['object_value'],
                        "path": value['path_components'],
                        "pathLabels": value['path_labels'],
                        'resourceId': value['literal_object'] if value['literal_object'] is not None else value['resource_object'],
                        'type': 'literal' if value['literal_object'] is not None else 'resource'
                    })
                values.append(cont_pred_values)
        out_data[path] = values
        # for cont_idx in np.argwhere(paths_contribution_matrix[path_idx]).flatten():
    return out_contributions, out_predicates, out_data


def update_neo4j_entities():
    neo4j.update_predicates()
    neo4j.update_contributions()


if __name__ == '__main__':
    neo4j.update_predicates()
    neo4j.update_contributions()
    compare_resources(['R6110', 'R6117', 'R1018'])
