from flask import Blueprint
from .views import ShortenerAPI

shortener_blueprint = Blueprint("shortener", __name__, url_prefix='/shortener')

shortener_blueprint.add_url_rule('/', view_func=ShortenerAPI.as_view('links'), methods=['POST'])
shortener_blueprint.add_url_rule('/<short_code>/', view_func=ShortenerAPI.as_view('link_single'), methods=['GET'])
