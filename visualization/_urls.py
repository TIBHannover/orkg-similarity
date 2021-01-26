from flask import Blueprint
from .views import VisualizationAPI

visualization_blueprint = Blueprint("visualization", __name__)

visualization_blueprint.add_url_rule('/visualization/', view_func=VisualizationAPI.as_view('visualization_view'),
                                     methods=['GET', 'POST'])
