from flask import jsonify, request, abort
from flask.views import MethodView
from models import Link


class ShortenerAPI(MethodView):

    def get(self, link_id, **kwargs):
        link = Link.get(link_id)
        if link:
            return jsonify({'long_url': str(link.long_url)})
        else:
            abort(404)


    def post(self, **kwargs):
        link = Link()
        link.long_url = request.form["link"]
        link.save()
        return jsonify({'id': str(link.id)})
