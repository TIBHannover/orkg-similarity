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
            return ShortCodeCreateParams().dumps(link).data
        else:
            abort(404)

    @use_args_with(ShortCodeCreateParams, locations=("json",))
    def post(self, reqargs):
        link = Link.get_by_long_url(reqargs.get("long_url"))
        if(link):
            return jsonify({'id': str(link.id), 'short_code': link.short_code})
        short_code = Link.generate_next_short_code()
        link = Link()
        link.long_url = reqargs.get("long_url")
        link.response_hash = reqargs.get("response_hash")
        link.contributions = reqargs.get("contributions")
        link.properties = reqargs.get("properties")
        link.transpose = reqargs.get("transpose")
        link.json_code = reqargs.get("json_code")
        link.short_code = short_code
        link.save()
        return jsonify({'id': str(link.id), 'short_code': short_code})
