from typing import List
from connection.neo4j import Neo4J

neo4j = Neo4J.getInstance()


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
            # paths[i].insert(2, get_path_labels(paths[i][1]))
            paths[i] = get_path_labels(paths[i][1])
    # Transform the data to simcomp response format
    data = {}
    # Find which have  similar paths
    return [], [], {}


if __name__ == '__main__':
    neo4j.update_predicates()
    neo4j.update_contributions()
    compare_resources(['R6110', 'R6117'])
