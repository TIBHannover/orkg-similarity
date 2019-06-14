from flask import Flask, jsonify, make_response
from util import ListConverter

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/compare/<list:contributions>', methods=['GET'])
def compare_resources(contributions: list):
    return jsonify({'value': contributions})


@app.route('/')
def index():
    return "Welcome to the Magic of ORKG"


if __name__ == '__main__':
    app.run(debug=True)
