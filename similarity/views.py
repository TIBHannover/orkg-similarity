from flask import jsonify
from flask.views import MethodView
from similarity import elastic_similarity as es
from connection.neo4j import Neo4J

neo4j = Neo4J.getInstance()
NUMBER_OF_RESULTS = 5

class ComputeSimilarityAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        results = []
        similar = es.query_index(contribution_id, top_k=NUMBER_OF_RESULTS)

        if not similar:
            return jsonify(results)

        for similar_id, score in similar.items():
            details = neo4j.get_contribution_details(similar_id)
            results.append({
                'paperId': '' if not details else details['paperId'],
                'contributionId': similar_id,
                'contributionLabel': '' if not details else details['contributionLabel'],
                'similarityPercentage': score
            })

        results = sorted(results, key=lambda i: i['similarityPercentage'], reverse=True)[:NUMBER_OF_RESULTS]

        return jsonify(results)

class IndexContributionAPI(MethodView):

    def get(self, contribution_id, **kwargs):
        response = es.index_document(contribution_id)

        if not response:
            return jsonify({'message': 'Couldn\'t index contribution {}'.format(contribution_id)})
        
        return jsonify({'message': 'Contirbution {} indexed'.format(contribution_id)})

class SetupSimilarityAPI(MethodView):

    def get(self, **kwargs):
        return jsonify(es.recreate_index())
