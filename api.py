from flask import Flask, jsonify, make_response
from util import ListConverter

import compare

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/compare/<list:contributions>', methods=['GET'])
def compare_resources(contributions: list):
    compare.predicates = compare.update_predicates()
    compare.pred_sim_matrix = compare.compute_similarity_among_predicates()
    conts, preds, data = compare.compare_resources(contributions)
    return jsonify({'contributions': conts, 'properties': preds, 'data': data})


@app.route('/')
def index():
    return "Welcome to the Magic of ORKG"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
