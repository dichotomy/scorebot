from flask import Flask, request, render_template, make_response
from flask_bootstrap import Bootstrap
from logging import StreamHandler, FileHandler
import os
import subprocess
import requests

app = Flask(__name__)
bootstrap = Bootstrap(app)
TOKEN = "d2f2d571-a7fc-4a08-8715-1eb4493ddafa"
API_URL = "http://10.151.100.220/api/beacon/active"

basedir = os.path.abspath(os.path.dirname(__file__))
log_file = os.path.join(basedir, 'log')


@app.before_first_request
def setup_logging():
    if not app.debug:
        file_handler = FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)


@app.route('/')
def main():
    headers = {"SBE-AUTH": TOKEN}
    r = requests.get(API_URL, headers=headers)
    beacons = r.json()
    return render_template('home.html', beacons=beacons)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
