from py2neo import Graph
import os


class Neo4J:
    __instance = None

    @staticmethod
    def getInstance() -> 'Neo4J':
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
        self.__predicates_hash = None
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

    def __compute_predicates_hash(self):
        to_hash = tuple(sorted(list(self.__predicates.values())))
        return hash(to_hash)

    @staticmethod
    def clean_classes_list(classes):
        return [c for c in classes if c not in ['Thing', 'Literal', 'AuditableEntity', 'Resource']]

    def update_predicates(self):
        changed = False
        self.__predicates = {pred["key"]: pred["value"] for pred in
                             self.graph.run("MATCH (p:Predicate) RETURN p.predicate_id as key, p.label as value")}
        current_hash = self.__compute_predicates_hash()
        if current_hash != self.__predicates_hash:
            changed = True
            self.__predicates_hash = current_hash
        return changed

    def __get_subgraph(self, resource, bfs=True, with_ordering=True):
        method = "true" if bfs is True else "false"
        order_by = ' ORDER BY subject, object' if with_ordering is True else ''

        result = [x for x in self.graph.run(f"""
            MATCH (n:Resource {{resource_id: '{resource}'}})
            CALL apoc.path.subgraphAll(n, {{relationshipFilter:'>', bfs: {method} }})
            YIELD relationships
            UNWIND relationships AS rel
            RETURN
              startNode(rel).label AS subject,
              startNode(rel).resource_id AS subject_id,
              rel.predicate_id AS predicate,
              endNode(rel).label AS object,
              endNode(rel).resource_id AS object_id,
              endNode(rel).literal_id AS literal_id,
              labels(endNode(rel)) AS classes
              {order_by}  
            """)]
        self.graph_cache[resource] = result
        return result

    def __get_predicates_in_contributions(self, contributions):
        return {x for x in self.graph.run(f"""
            MATCH (n:Resource)
            WHERE n.resource_id in {contributions}
            CALL apoc.path.subgraphAll(n, {{relationshipFilter:'>' }})
            YIELD relationships
            UNWIND relationships AS rel
            MATCH (p:Predicate {{predicate_id: rel.predicate_id}})
            RETURN rel.predicate_id AS key, p.label AS value
        """)}

    def __get_spanning_tree(self, resource):
        """
        Get the spanning tree starting from a resource for a maximum of 5 levels deep
        :param resource: the resource ID to start with
        :return: neo4j query response
        """
        return [x for x in self.graph.run(f"""
            MATCH (n:Resource {{resource_id: "{resource}"}})
            CALL apoc.path.spanningTree(n, {{maxLevel: 5, relationshipFilter: ">", uniqueness: "NONE"}})
            YIELD path
            RETURN
              path,
              apoc.coll.flatten([rel in relationships(path) | [startNode(rel).resource_id, rel.predicate_id]]) AS path_components,
              [rel in relationships(path) WHERE endNode(rel):Literal | endNode(rel).literal_id][-1] AS literal_object,
              [rel in relationships(path) WHERE endNode(rel):Resource | endNode(rel).resource_id][-1] AS resource_object,
              [rel in relationships(path) | endNode(rel).label][-1] AS object_value, length(path) AS hops,
              labels([rel in relationships(path) | endNode(rel)][-1]) AS classes
        """)]

    def get_subgraph_predicates(self, resource):
        result = self.__get_subgraph(resource)
        return [x["predicate"] for x in result]

    def get_predicates_of_contributions(self, contributions):
        return dict(self.__get_predicates_in_contributions(contributions))

    def get_subgraph_full(self, resource):
        result = self.__get_subgraph(resource)
        return [(x['predicate'], x['object'], x['object_id'], x['literal_id'], x['subject_id'],
                 self.clean_classes_list(x['classes'])) for x in result]

    def get_spanning_tree(self, resource):
        result = self.__get_spanning_tree(resource)
        return [{
            'path': x['path'],
            'path_components': x['path_components'],
            'literal_object': x['literal_object'],
            'resource_object': x['resource_object'],
            'object_value': x['object_value'],
            'classes': self.clean_classes_list(x['classes']),
            'hops': x['hops']
        } for x in result if x['hops'] > 0]

    def __get_contribution(self, cont):
        return self.graph.run(f"""
            MATCH (paper:Paper)-[p:RELATED {{predicate_id:'P31'}}]->(cont:Contribution {{resource_id: '{cont}'}})
            WITH paper, cont 
            OPTIONAL MATCH (paper)-[p:RELATED {{predicate_id:'P29'}}]->(year:Literal)
            RETURN
              paper.label AS title,
              paper.resource_id AS paper_id,
              cont.label AS cont_label,
              cont.resource_id AS id,
              year.label AS paper_year
        """).data()

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

    def get_contributions_with_details(self, conts):
        result = self.graph.run(f"""
                    MATCH (paper:Paper)-[p:RELATED {{predicate_id:'P31'}}]->(cont:Contribution)
                    WHERE cont.resource_id IN {conts}
                    WITH paper, cont 
                    OPTIONAL MATCH (paper)-[p:RELATED {{predicate_id:'P29'}}]->(year:Literal)
                    RETURN
                      paper.label AS title,
                      paper.resource_id AS paper_id,
                      cont.label AS cont_label,
                      cont.resource_id AS id,
                      year.label AS paper_year
                """).data()

        return [{'id': cont['id'],
                 'paperId': cont['paper_id'],
                 'title': cont['title'],
                 'contributionLabel': cont['cont_label'],
                 'year': cont['paper_year']
                 } for cont in result]

    def __get_latest_contribution(self) -> str:
        return self.graph.run("""
            MATCH (n:Contribution)
            RETURN n.resource_id AS latest_id
            ORDER BY n.created_at DESC
            LIMIT 1
            """).evaluate()

    def __count_contributions(self) -> int:
        return self.graph.run("MATCH (n:Contribution) RETURN count(n.resource_id) AS total").data()[0]['total']

    def __get_contributions(self):
        return self.graph.run("MATCH (n:Contribution) RETURN n.resource_id AS id ORDER BY n.created_at DESC").data()

    def get_contributions_id(self):
        result = self.__get_contributions()
        return [p["id"] for p in result]

    def update_contributions(self):
        # Only update if the list of contributions changed. This works by assuming that the resource ID and creation
        # date never changes. When we get the contribution in the order of creation, the last element is the latest one.
        # To check if the actual state changed, we fetch the latest ID and count the total number of elements, in order
        # to compare them to the list we already know. (TODO: Could be one query, possibly.)
        last_contribution_known = self.__contributions[-1]
        last_contribution_actual = self.__get_latest_contribution()
        total_actual = self.__count_contributions()
        # Check if the list is still up-to-date, and refresh if not. If the last elements of our list are different
        # (assuming the order is preserved), we know that we need to update. If they are equal, earlier elements could
        # have been deleted, so we check if the size changed. If so, we need to update. If not, we should have the
        # same list as the database, meaning it did not change. (This assumes no elements are added with a creation
        # date in the past, which should be a safe assumption.)
        if last_contribution_actual != last_contribution_known or len(self.contributions) != total_actual:
            self.__contributions = self.get_contributions_id()

    def get_resource_label(self, resource_id):
        return self.graph.run(
            f"MATCH (r:Resource {{resource_id: '{resource_id}'}}) RETURN r.label as label LIMIT 1").evaluate()
