# -*- coding: utf-8 -*-
from flask import Flask, g, request, make_response, jsonify
from util import ListConverter, NumpyEncoder
from flask_cors import CORS
from comparison import comparison_blueprint
from similarity import similarity_blueprint
from shortner import shortener_blueprint
from connection.neo4j import Neo4J
from extensions import db
from models import *
import yaml
import os

DEFAULT_BLUEPRINTS = [comparison_blueprint,
                      similarity_blueprint,
                      shortener_blueprint]


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

    with open('_config/config.yml') as _file:
        data = (yaml.load(_file, Loader=yaml.FullLoader)).copy()
        app.config.update(data)

    app.config["HOST"] = os.environ["SIMCOMP_FLASK_HOST"] if "SIMCOMP_FLASK_HOST" in os.environ else '0.0.0.0'
    app.config["PORT"] = int(os.environ["SIMCOMP_FLASK_PORT"]) if "SIMCOMP_FLASK_PORT" in os.environ else 5000


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_extensions(app):

    db.init_app(app)
    with app.app_context():
        db.create_all()  # TODO: create the initial database from an interactive Python shell or cli command
    CORS(app)


def configure_error_handlers(app):

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    # Return validation errors as JSON
    @app.errorhandler(422)
    @app.errorhandler(400)
    def handle_error(err):
        headers = err.data.get("headers", None)
        messages = err.data.get("messages", ["Invalid request."])
        if headers:
                return jsonify({"errors": messages}), err.code, headers
        else:
                return jsonify({"errors": messages}), err.code
