from flask import Flask, request, render_template, make_response
from flask_bootstrap import Bootstrap
from logging import StreamHandler, FileHandler
import os
import subprocess
import requests

app = Flask(__name__)
bootstrap = Bootstrap(app)
TOKEN = "80d3c4fd-ccfa-43fc-8e1d-a23c9dd0ded9"
API_URL = "http://192.168.1.12:8000/api/beacon/active"

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
