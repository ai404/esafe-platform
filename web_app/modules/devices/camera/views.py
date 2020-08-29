
from . import bp_camera

from flask_login import current_user, login_required

from flask import g
from .forms import CameraEditForm, CameraAddForm
from database.models import Camera, Access, Role_dict

from web_app.helpers.decorators import has_role
from web_app.modules._base_views import BasePanel, BaseLister, BaseAdder, BaseDeleter, BaseEditer


class Lister(BaseLister):
    def get_items(self):
        return current_user.cameras


class Adder(BaseAdder):

    def set_special_attributes(self, form, record, **kwargs):
        record.company_id = current_user.company_id

    def post_transaction(self, form, record, **kwargs):
        # add current user to access list for entity
        access = Access()

        access.camera_id = record.id
        access.user_id = current_user.id

        g.session.add(access)
        g.session.commit()

    def get_template_name(self):
        return 'camera/adder.pug'


class Editer(BaseEditer):
    def get_template_name(self):
        return 'camera/adder.pug'


class Deleter(BaseDeleter):
    def get_items(self):
        return current_user.cameras


class Panel(BasePanel):

    def get_item(self, id):
        return Camera.query.get(id)

    def is_valid_item(self, item):
        return item in current_user.cameras


class StreamingPanel(BasePanel):
    url_name = "streaming"
    
    def get_item(self, id):
        return Camera.query.get(id)

    def is_valid_item(self, item):
        return item in current_user.cameras

    def get_template_name(self):
        return "camera/panel.pug"

    @classmethod
    def get_endpoint(cls):
        return '/streaming/<id>'


class CameraVars(object):
    title = "Camera"
    column_titles = ["Camera ID", "Active",
                     "Output Streaming", "Entity Name", "Location"]
    column_ids = ["id", "active", "streaming_output",
                  "entity_name", "location_name"]
    form = CameraAddForm
    form_edit = CameraEditForm
    model = Camera
    kind = "camera"

role_decorator = has_role(Role_dict.ADMIN, Role_dict.MANAGER)

decorators = [login_required ,role_decorator]

views = [
    Lister, Adder, Editer, Deleter, Panel, StreamingPanel
]

for view in views:
    view.add_url_rule(bp_camera, CameraVars, decorators)