from flask import jsonify, request, abort
from flask.views import MethodView
from models import Link
from ._params import ShortCodeCreateParams, LinkGetParams
from util import use_args_with


class ShortenerAPI(MethodView):

    @use_args_with(LinkGetParams)
    def get(self, reqargs, link_id):
        link = Link.get(reqargs.get("link_id"))
        if link:
            return jsonify({'long_url': str(link.long_url)})
        else:
            abort(404)

    @use_args_with(ShortCodeCreateParams, locations=("form", "json"))
    def post(self, reqargs):
        link = Link()
        link.long_url = reqargs.get("link")
        link.save()
        return jsonify({'id': str(link.id)})
