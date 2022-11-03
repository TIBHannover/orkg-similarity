from flask import Blueprint
from .views import ReviewAPI

review_blueprint = Blueprint("review", __name__)

review_blueprint.add_url_rule('/review/', view_func=ReviewAPI.as_view('review_view'), methods=['GET'])
