from flask import Blueprint

bp_camera = Blueprint('camera', __name__, template_folder="templates", url_prefix='/camera')

from .views import *