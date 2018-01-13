"""Bare-bones Flask application."""
import flask
import json
import random
import string

from flask_bootstrap import Bootstrap
from flask_cors import CORS


def create_app():
    app = flask.Flask(__name__)
    Bootstrap(app)
    return app

app = create_app()
CORS(app, resources={r'/api/*': {'origins': '*'}})


@app.route('/')
def homepage():
    poem = json.loads(make_poem().get_data())['poem']
    return flask.render_template('index.html', poem=poem)


@app.route('/api/make_poem/', methods=['GET'])
def make_poem():
    """Generate a random poem."""
    return_string = ''.join(random.choices(string.ascii_lowercase, k=10))
    return flask.jsonify({'poem': return_string})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
