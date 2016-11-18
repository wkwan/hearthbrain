import os

from flask import Flask
from var_len import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/gen')
def gen():
    print("generate deck")
    return str(generateDeck())

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    os.environ["KERAS_BACKEND"] = "theano"
    print("port is", port);
    app.run(host='0.0.0.0', port=port)