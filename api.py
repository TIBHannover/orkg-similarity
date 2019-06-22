from flask import Flask, jsonify, make_response
from util import ListConverter, NumpyEncoder
from connection.neo4j import Neo4J
import os

import compare
import cache

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter
app.json_encoder = NumpyEncoder
neo4j = Neo4J.getInstance()


@app.after_request
def add_headers(response):
    #response.headers.add('Content-Type', 'application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    return response


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/compare/<list:contributions>', methods=['GET'])
def compare_resources(contributions: list):
    compare.pred_sim_matrix, compare.pred_label_index, compare.pred_index_id, compare.pred_id_index = compare.compute_similarity_among_predicates()
    conts, preds, data = compare.compare_resources(contributions)
    return jsonify({'contributions': conts, 'properties': preds, 'data': data})


@app.route('/internal/init')
def setup_similarity():
    store = cache.Cache()
    store.create_new_cache()
    store.save_cache()
    return jsonify({"message": "done initing baby!!"})


@app.route('/similar/<contribution_id>/')
def compute_similarity(contribution_id):
    store = cache.Cache()
    store.load_cache()
    similar = store.get_top_similar(contribution_id, 5)
    return jsonify([{'paperId': item[0]['paperId'],
                     'contributionId': item[0]['id'],
                     'contributionLabel': item[0]['contributionLabel'],
                     'similarityPercentage': item[1]
                     } for item in [(neo4j.get_contribution_details(cont), sim) for cont, sim in similar.items()]])


@app.route('/')
def index():
    return "Welcome to the Magic of ORKG"


if __name__ == '__main__':
    host = os.environ["SIMCOMP_FLASK_HOST"] if "SIMCOMP_FLASK_HOST" in os.environ else '0.0.0.0'
    port = int(os.environ["SIMCOMP_FLASK_PORT"]) if "SIMCOMP_FLASK_PORT" in os.environ else 5000
    debug = True if "SIMCOMP_FLASK_DEBUG" in os.environ else False
    app.run(host=host, port=port, debug=debug, use_reloader=False)
