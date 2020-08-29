from database import db_session
from database.models import Camera

from .._base_module.handler import BaseHandler


class Handler(BaseHandler):
    def get_devices_config(self):
        db_session().commit()
        return Camera.get_all()
