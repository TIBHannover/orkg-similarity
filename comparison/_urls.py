from flask import Blueprint
from .views import ComparisonAPI

comparison_blueprint = Blueprint("comparison", __name__)

comparison_blueprint.add_url_rule('/compare/<list:contributions>', view_func=ComparisonAPI.as_view('compare_resources'), methods=['GET'])
