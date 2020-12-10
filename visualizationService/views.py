from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView

from util import use_args_with
from ._params import VisualizationGetParams
from models import VisualizationResponse

import json


class VisualizationAPI(MethodView):
    @use_args_with(VisualizationGetParams)
    def get(self, reqargs):
        resource_id = reqargs.get("resourceId")
        visualization_response = VisualizationResponse.get_by_resource_id(resource_id)
        if visualization_response:
            return visualization_response.__repr__()
        else:
            abort(404)

    def post(self):
        call = json.dumps(request.json)
        data_item = json.loads(call)
        resource_id = data_item['resourceId']
        data_value = data_item['jsonData']
        VisualizationResponse.add_visualization(resource_id, data_value)
        return jsonify({'success': True})
