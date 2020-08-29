from flask import Blueprint

bp_main = Blueprint('main', __name__, template_folder="templates", url_prefix='/')

from .views import *
