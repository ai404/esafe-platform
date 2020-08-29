from flask import Blueprint

bp_account = Blueprint('account', __name__, template_folder="templates", url_prefix='/account')

from .views import *
