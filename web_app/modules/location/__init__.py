from flask import Blueprint

bp_location = Blueprint('location', __name__, template_folder="templates", url_prefix='/location')
from .views.location import *

bp_entity = Blueprint('entity', __name__, template_folder="templates", url_prefix='/entity')
from .views.entity import *