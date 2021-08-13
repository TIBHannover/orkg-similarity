from py2neo import Graph
import os


class Neo4J:
    __instance = None

    @staticmethod
    def getInstance():
        """
        Fetches the instance of the singleton class
        :return: a simcomp Neo4J object
        """
        if Neo4J.__instance is None:
            Neo4J()
        return Neo4J.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Neo4J.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Neo4J.__instance = self
        host = os.environ["SIMCOMP_NEO4J_HOST"] if "SIMCOMP_NEO4J_HOST" in os.environ else "localhost"
        user = os.environ["SIMCOMP_NEO4J_USER"] if "SIMCOMP_NEO4J_USER" in os.environ else "neo4j"
        password = os.environ["SIMCOMP_NEO4J_PASSWORD"] if "SIMCOMP_NEO4J_PASSWORD" in os.environ else "password"
        self.graph = Graph(host=host, user=user, password=password)
        self.graph_cache = {}
        self.__predicates = None
        self.__previous_predicates = None
        self.__contributions = self.get_contributions_id()

    @property
    def predicates(self):
        """
        The ORKG predicates
        :return: list of dictionaries of predicates information
        """
        return self.__predicates

    @property
    def contributions(self):
        """
        The ORKG contribution resources
        :return: list of contributions IDs
        """
        return self.__contributions

    def update_predicates(self):
        changed = False
        self.__predicates = {pred["key"]: pred["value"] for pred in
                             self.graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, p.label as value")}
        if self.__predicates != self.__previous_predicates:
            changed = True
            self.__previous_predicates = self.__predicates
        return changed

    def __get_subgraph(self, resource, bfs=True, with_ordering=True):
        method = "true" if bfs is True else "false"
        order_by = ' ORDER BY subject, object' if with_ordering is True else ''

        result = [x for x in self.graph.run(
            "MATCH (n:Resource {resource_id: \"" + resource + "\"}) CALL apoc.path.subgraphAll(n, "
                                                              "{relationshipFilter:'>', bfs:"+method+"}) YIELD relationships "
                                                              "UNWIND relationships as rel RETURN startNode(rel).label as "
                                                              "subject, startNode(rel).resource_id as subject_id, "
                                                              "rel.predicate_id as predicate, endNode(rel).label as "
                                                              "object, endNode(rel).resource_id as object_id, "
                                                              "endNode(rel).literal_id as literal_id" + order_by)]
        self.graph_cache[resource] = result
        return result

    def __get_spanning_tree(self, resource):
        """
        Get the spanning tree starting from a resource for a maximum of 5 levels deep
        :param resource: the resource ID to start with
        :return: neo4j query response
        """
        return [x for x in self.graph.run(
            "MATCH (n:Resource {resource_id: \"" + resource + """\"})
            CALL apoc.path.spanningTree(n, {maxLevel: 5, relationshipFilter: ">"})
            YIELD path
            RETURN path, apoc.coll.flatten([rel in relationships(path) | [startNode(rel).resource_id, rel.predicate_id]]) AS path_components,[rel in relationships(path) WHERE endNode(rel):Literal | endNode(rel).literal_id][-1] AS literal_object,[rel in relationships(path) WHERE endNode(rel):Resource | endNode(rel).resource_id][-1] AS resource_object,[rel in relationships(path) | endNode(rel).label][-1] AS object_value, length(path) AS hops
            """)]

    def get_subgraph_predicates(self, resource):
        result = self.__get_subgraph(resource)
        return [x["predicate"] for x in result]

    def get_subgraph_full(self, resource):
        result = self.__get_subgraph(resource)
        return [(x['predicate'], x['object'], x['object_id'], x['literal_id'], x['subject_id']) for x in result]

    def get_spanning_tree(self, resource):
        result = self.__get_spanning_tree(resource)
        return [{
            'path': x['path'],
            'path_components': x['path_components'],
            'literal_object': x['literal_object'],
            'resource_object': x['resource_object'],
            'object_value': x['object_value'],
            'hops': x['hops']
        } for x in result if x['hops'] > 0]

    def __get_contribution(self, cont):
        return self.graph.run(
            "MATCH (paper:Paper)-[p {predicate_id:'P31'}]"
            "->(cont:Contribution {resource_id: '" + cont + "'}) "
            "WITH paper, cont OPTIONAL MATCH (paper)-[p {predicate_id:'P29'}]->(year)"
            " RETURN paper.label as title, paper.resource_id as "
            "paper_id, cont.label as cont_label, cont.resource_id as id, year.label as paper_year").data()

    def get_contribution_details(self, cont):
        result = self.__get_contribution(cont)

        if not result:
            return {}

        return {'id': result[0]['id'],
                'paperId': result[0]['paper_id'],
                'title': result[0]['title'],
                'contributionLabel': result[0]['cont_label'],
                'year': result[0]['paper_year']
                }

    def __get_contributions(self):
        return self.graph.run("MATCH (n:Contribution) RETURN n.resource_id as id").data()

    def get_contributions_id(self):
        result = self.__get_contributions()
        return [p["id"] for p in result]

    def update_contributions(self):
        self.__contributions = self.get_contributions_id()

    def get_resource_label(self, resource_id):
        return self.graph.run(f"MATCH (r:Resource {{resource_id: '{resource_id}'}}) RETURN r.label as label LIMIT 1").evaluate()
