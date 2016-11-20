import os

from flask import json
from flask import render_template
from flask import request

os.environ["KERAS_BACKEND"] = "theano"

from flask import Flask
from var_len import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html');


@app.route('/gen')
def gen():
    print("generate deck from ", request.args.getlist("seed"))
    return json.dumps(generateDeck(request.args.getlist("seed")))

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    print("port is", port);
    app.run(host='0.0.0.0', port=port)