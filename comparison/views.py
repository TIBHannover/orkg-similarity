from flask import jsonify, request
from flask.views import MethodView
from comparison import compare
from ._params import ComparisonGetParams, ComparisonResponseGetParams
from models import ComparisonResponse
from util import NumpyEncoder, use_args_with
import hashlib
import json


class ComparisonAPI(MethodView):

    @use_args_with(ComparisonGetParams)
    def get(self, reqargs):
        print(reqargs.get("contributions"))
        if reqargs.get("response_hash"):
            comparison_response = ComparisonResponse.get_by_hash(reqargs.get("response_hash"))
            if comparison_response:
                return jsonify(json.loads(comparison_response.data))
        compare.pred_sim_matrix, compare.pred_label_index, compare.pred_index_id, compare.pred_id_index =\
            compare.compute_similarity_among_predicates()
        conts, preds, data = compare.compare_resources(reqargs.get("contributions"))
        response = {'contributions': conts, 'properties': preds, 'data': data}
        json_response = json.dumps(response, cls=NumpyEncoder ,sort_keys=True)
        response_hash = hashlib.md5(json_response.encode("utf-8")).hexdigest()
        if not ComparisonResponse.get_by_hash(response_hash):
            comparison_response = ComparisonResponse()
            comparison_response.response_hash = response_hash
            comparison_response.data = json_response
            comparison_response.save()
        response.update({'response_hash':response_hash})
        return jsonify(response)


class ComparisonResponseAPI(MethodView):

    @use_args_with(ComparisonResponseGetParams)
    def get(self, reqargs, response_hash):
        comparison_response = ComparisonResponse.get_by_hash(response_hash)
        if comparison_response:
            return comparison_response.data
        else:
            abort(404)
