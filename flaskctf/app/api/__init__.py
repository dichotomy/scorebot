from flask import Blueprint

ctf_api = Blueprint('ctf_api', __name__)

from . import views
