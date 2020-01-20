from flask import jsonify
from flask.views import MethodView
from similarity import elastic_similarity as es
from connection.neo4j import Neo4J

neo4j = Neo4J.getInstance()


class ComputeSimilarityAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        num_items = 5
        similar = es.query_index(contribution_id, num_items)
        results = sorted([{'paperId': item[0]['paperId'],
                           'contributionId': item[0]['id'],
                           'contributionLabel': item[0]['contributionLabel'],
                           'similarityPercentage': item[1]}
                          for item in [(neo4j.get_contribution_details(cont), sim) for cont, sim in similar.items()
                                       if cont in neo4j.contributions]][:num_items],
                         key=lambda i: i['similarityPercentage'], reverse=True)
        return jsonify(results)


class IndexContributionAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        es.index_document(contribution_id)
        return jsonify({"message": "document indexed baby!!"})


class SetupSimilarityAPI(MethodView):

    def get(self, **kwargs):
        es.recreate_index()
        return jsonify({"message": "done initing baby!!"})
