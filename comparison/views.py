from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView
from comparison import compare, compare_paths
from ._params import ComparisonGetParams, ComparisonResponseGetParams
from models import ComparisonResponse, VisualizationResponse

from util import NumpyEncoder, use_args_with
import hashlib
import json


class ComparisonAPI(MethodView):

    @use_args_with(ComparisonGetParams)
    def get(self, reqargs):
        if reqargs.get("response_hash"):
            comparison_response = ComparisonResponse.get_by_hash(reqargs.get("response_hash"))
            if comparison_response:
                return jsonify(json.loads(comparison_response.data))
        if reqargs.get("type") == 'path':
            compare_paths.update_neo4j_entities()
            conts, preds, data = compare_paths.compare_resources(reqargs.get("contributions"))
            response = {'contributions': conts, 'properties': preds, 'data': data}
        else:
            conts, preds, data = compare.compare_resources(reqargs.get("contributions"))
            response = {'contributions': conts, 'properties': preds, 'data': data}
        json_response = json.dumps(response, cls=NumpyEncoder, sort_keys=True)
        if reqargs.get("save_response"):
            response_hash = hashlib.md5(json_response.encode("utf-8")).hexdigest()
            if not ComparisonResponse.get_by_hash(response_hash):
                comparison_response = ComparisonResponse()
                comparison_response.response_hash = response_hash
                comparison_response.data = json_response
                comparison_response.save()
            response.update({'response_hash': response_hash})
        return jsonify(response)


class OldComparisonAPI(MethodView):

    def get(self, contributions: list, **kwargs):
        return redirect(url_for('comparison.compare_resources', contributions=','.join(contributions)), 301)


class ComparisonResponseAPI(MethodView):

    @use_args_with(ComparisonResponseGetParams)
    def get(self, reqargs, response_hash):
        comparison_response = ComparisonResponse.get_by_hash(response_hash)
        if comparison_response:
            return comparison_response.data
        else:
            abort(404)
