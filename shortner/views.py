from flask import jsonify, request, abort
from flask.views import MethodView
from models import Link
from ._params import ShortCodeCreateParams, LinkGetParams
from util import use_args_with


class ShortenerAPI(MethodView):

    @use_args_with(LinkGetParams)
    def get(self, reqargs, short_code):
        link = Link.get_by_code(reqargs.get("short_code"))
        if link:
            return jsonify({'long_url': str(link.long_url)})
        else:
            abort(404)

    @use_args_with(ShortCodeCreateParams, locations=("form", "json"))
    def post(self, reqargs):
        short_code = Link.generate_next_short_code()
        link = Link()
        link.long_url = reqargs.get("link")
        link.short_code = short_code
        link.save()
        return jsonify({'id': str(link.id), 'short_code': short_code})
