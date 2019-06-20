from flask import Flask, jsonify, make_response
from util import ListConverter

import compare
import cache

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter


@app.after_request
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
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
    compare.predicates = compare.update_predicates()
    compare.pred_sim_matrix = compare.compute_similarity_among_predicates()
    conts, preds, data = compare.compare_resources(contributions)
    return jsonify({'contributions': conts, 'properties': preds, 'data': data})


@app.route('/internal/init')
def setup_similarity():
    store = cache.Cache()
    store.create_new_cache()
    store.save_cache()
    return "done initing baby!!"


@app.route('/similar/<contribution_id>/')
def compute_similarity(contribution_id):
    store = cache.Cache()
    store.load_cache()
    similar = store.get_top_similar(contribution_id, 5)
    return jsonify([{'paperId': item[0]['paperId'],
                     'contributionId': item[0]['id'],
                     'contributionLabel': item[0]['contributionLabel'],
                     'similarityPercentage': item[1]
                     } for item in [(compare.get_contribution_details(cont), sim) for cont, sim in similar.items()]])


@app.route('/')
def index():
    return "Welcome to the Magic of ORKG"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
