from py2neo import Graph
import os


class Neo4J:
    __instance = None

    @staticmethod
    def getInstance():
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
        self.update_predicates()
        self.__contributions = self.get_contributions_id()

    @property
    def predicates(self):
        return self.__predicates

    @property
    def contributions(self):
        return self.__contributions

    def update_predicates(self):
        self.__predicates = {pred["key"]: pred["value"] for pred in
                             self.graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, p.label as value")}

    def __get_subgraph(self, resource, bfs=True):
        if resource in self.graph_cache:
            return self.graph_cache[resource]
        else:
            method = "true" if bfs is True else "false"
            result = [x for x in self.graph.run(
                "MATCH (n:Resource {resource_id: \"" + resource + "\"}) CALL apoc.path.subgraphAll(n, "
                                                                  "{relationshipFilter:'>', bfs:"+method+"}) YIELD relationships "
                                                                  "UNWIND relationships as rel RETURN startNode(rel).label as "
                                                                  "subject, startNode(rel).resource_id as subject_id, "
                                                                  "rel.predicate_id as predicate, endNode(rel).label as "
                                                                  "object, endNode(rel).resource_id as object_id, "
                                                                  "endNode(rel).literal_id as literal_id ORDER BY subject, object")]
            self.graph_cache[resource] = result
            return result

    def get_subgraph_predicates(self, resource):
        result = self.__get_subgraph(resource)
        return [x["predicate"] for x in result]

    def get_subgraph_full(self, resource):
        result = self.__get_subgraph(resource)
        return [(x['predicate'], x['object'], x['object_id'], x['literal_id'], x['subject_id']) for x in result]

    def __get_contribution(self, cont):
        for neo4j_content in self.graph.run(
            "MATCH (paper:Resource)-[p {predicate_id:'P31'}]"
            "->(cont:Resource {resource_id: '" + cont + "'}) RETURN paper.label as title, paper.resource_id as "
                                                        "paper_id, cont.label as cont_label, cont.resource_id as id"):
            return neo4j_content

    def get_contribution_details(self, cont):
        result = self.__get_contribution(cont)
        return {'id': result['id'],
                'paperId': result['paper_id'],
                'title': result['title'],
                'contributionLabel': result['cont_label']}

    def __get_contributions(self):
        return self.graph.run("MATCH ()-[{predicate_id:'P31'}]->(n:Resource) RETURN n.resource_id as id").data()

    def get_contributions_id(self):
        result = self.__get_contributions()
        return [p["id"] for p in result]

    def update_contributions(self):
        self.__contributions = self.get_contributions_id()

    def get_resource_label(self, resource_id):
        return self.graph.run(f"MATCH (r:Resource {{resource_id: '{resource_id}'}}) RETURN r.label as label LIMIT 1").evaluate()

