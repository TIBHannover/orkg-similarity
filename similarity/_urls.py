from flask import Blueprint
from .views import ComputeSimilarityAPI, IndexContributionAPI, SetupSimilarityAPI

similarity_blueprint = Blueprint("similarity", __name__)

similarity_blueprint.add_url_rule('/similar/<contribution_id>/',
                                  view_func=ComputeSimilarityAPI.as_view('compute_similarity'), methods=['GET'])
similarity_blueprint.add_url_rule('/internal/init',
                                  view_func=SetupSimilarityAPI.as_view('setup_similarity'), methods=['GET'])
similarity_blueprint.add_url_rule('/internal/index/<contribution_id>/',
                                  view_func=IndexContributionAPI.as_view('index_contribution'), methods=['GET'])
