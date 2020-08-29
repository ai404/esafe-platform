from flask import Blueprint

bp_staff = Blueprint('staff', __name__, template_folder="templates", url_prefix='/staff')

from .views import *