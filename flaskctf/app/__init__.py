from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from api import ctf_api as ctf_api_blueprint
    app.register_blueprint(ctf_api_blueprint, url_prefix='/scorebot/api/v1.0')

    return app
