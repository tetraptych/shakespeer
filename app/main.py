"""Bare-bones Flask application."""
import json

import flask

from flask_bootstrap import Bootstrap

from flask_cors import CORS

from shakespeer.poetics import poem
from shakespeer.poetics import featurizer

TEXT_FILEPATH = 'data/sonnets.txt'
with open(TEXT_FILEPATH, 'r') as f:
    RAW_TEXT = f.read()
SOURCE = featurizer.convert_text_to_dataframe(text=RAW_TEXT)


def create_app():
    """Create a bootstrapped Flask application."""
    app = flask.Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()
CORS(app, resources={r'/api/*': {'origins': '*'}})


@app.route('/')
def homepage():
    """Render the landing page via index.html."""
    lines_to_display = json.loads(make_poem().get_data())['poem']
    return flask.render_template('index.html', poem=lines_to_display)


@app.route('/api/make_poem/', methods=['GET'])
def make_poem():
    """Generate a random poem."""
    random_poem = poem.Poem(scheme=poem.ELIZABETHAN_SONNET).fill(source=SOURCE)
    lines = random_poem.lines
    return flask.jsonify({'poem': lines})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
