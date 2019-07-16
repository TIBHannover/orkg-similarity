from flask import jsonify
from flask.views import MethodView
from similarity import elastic_similarity as es
from connection.neo4j import Neo4J

neo4j = Neo4J.getInstance()


class ComputeSimilarityAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        similar = es.query_index(contribution_id, 5)
        return jsonify([{'paperId': item[0]['paperId'],
                        'contributionId': item[0]['id'],
                        'contributionLabel': item[0]['contributionLabel'],
                        'similarityPercentage': item[1]
                        } for item in [(neo4j.get_contribution_details(cont), sim) for cont, sim in similar.items()]])


class IndexContributionAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        es.index_document(contribution_id)
        return jsonify({"message": "done indexing baby!!"})


class SetupSimilarityAPI(MethodView):

    def get(self, **kwargs):
        es.create_index()
        return jsonify({"message": "done initing baby!!"})