from flask import Blueprint
from .views import ComparisonAPI, ComparisonResponseAPI, OldComparisonAPI

comparison_blueprint = Blueprint("comparison", __name__)

comparison_blueprint.add_url_rule('/compare/', view_func=ComparisonAPI.as_view('compare_resources'), methods=['GET'])
comparison_blueprint.add_url_rule('/compare/<list:contributions>', view_func=OldComparisonAPI.as_view('old_compare_resources'), methods=['GET'])
comparison_blueprint.add_url_rule('/responses/<response_hash>/', view_func=ComparisonResponseAPI.as_view('compare_response'), methods=['GET'])