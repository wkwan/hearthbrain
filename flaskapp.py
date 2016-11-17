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
    app.run()