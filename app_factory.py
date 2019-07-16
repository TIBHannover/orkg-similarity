# -*- coding: utf-8 -*-
from flask import Flask, g, request, make_response, jsonify
from util import ListConverter, NumpyEncoder
from flask_cors import CORS
from comparison import comparison_blueprint
from similarity import similarity_blueprint
from connection.neo4j import Neo4J
import os

DEFAULT_BLUEPRINTS = [comparison_blueprint, similarity_blueprint]


def create_app(blueprints=None):
    """
    Builds up a Flask app and return it to the caller
    :param blueprints: a custom list of Flask blueprints
    :return: Flask app object
    """
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(__name__)

    configure_app(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_error_handlers(app)

    return app


def configure_app(app):
    app.url_map.converters['list'] = ListConverter
    app.json_encoder = NumpyEncoder
    app.config["HOST"] = os.environ["SIMCOMP_FLASK_HOST"] if "SIMCOMP_FLASK_HOST" in os.environ else '0.0.0.0'
    app.config["PORT"] = int(os.environ["SIMCOMP_FLASK_PORT"]) if "SIMCOMP_FLASK_PORT" in os.environ else 5000
    app.config["DEBUG"] = True if "SIMCOMP_FLASK_DEBUG" in os.environ else False


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_extensions(app):

    CORS(app)
    

def configure_error_handlers(app):

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)
