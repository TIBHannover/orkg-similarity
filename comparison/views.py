from flask import jsonify
from flask.views import MethodView
from comparison import compare


class ComparisonAPI(MethodView):

    def get(self, contributions: list, **kwargs):
        compare.pred_sim_matrix, compare.pred_label_index, compare.pred_index_id, compare.pred_id_index =\
            compare.compute_similarity_among_predicates()
        conts, preds, data = compare.compare_resources(contributions)
        return jsonify({'contributions': conts, 'properties': preds, 'data': data})
