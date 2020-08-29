from .. import bp_location

from flask import g
from flask_login import current_user, login_required

from ..forms.location import LocationForm
from database.models import Location, Alert, Access, Role_dict

from web_app.modules._base_views import BaseUserItems, BasePanel, BaseLister, BaseAdder, BaseDeleter, BaseEditer
from web_app.helpers.decorators import has_role
from web_app.helpers import save_plan

from ._base import BaseLocPanel


class UserItems(BaseUserItems):
    def get_items(self):
        return current_user.locations

class Lister(BaseLister):
    def get_items(self):
        return current_user.locations

class Panel(BaseLocPanel):

    def get_item(self, id):
        return Location.query.get(id)

    def get_items(self):
        return current_user.locations

    def get_alerts(self, id, offset=None, limit=10):
        return Alert.get_alerts(id=id, for_name="location", offset=offset, limit=limit)

class LocationSpecialAttrsMixin(object):
    def set_special_attributes(self, form, record, **kwargs):
        record.company_id = current_user.company_id

    def preprocess_form(self, form):
        filename = save_plan(form.plan.data)
        if filename:
            form.plan.data = filename
        else:
            del form.plan

class Adder(LocationSpecialAttrsMixin, BaseAdder):

    def post_transaction(self, form, record, **kwargs):
        # add current user to access list for location
        access = Access()

        access.location_id = record.id
        access.user_id = current_user.id

        g.session.add(access)
        g.session.commit()

    def get_template_name(self):
        return 'entity/adder.pug'

class Editer(LocationSpecialAttrsMixin, BaseEditer):
    pass

class Deleter(BaseDeleter):
    def get_items(self):
        return current_user.locations


class LocationVars(object):
    title = "Location"
    column_titles= ["ID", "Entity Name", "Location", "# Cameras"]
    column_ids= ["id","name","address", "cameras_count"]
    form= LocationForm
    model= Location
    kind = bp_location.name

role_decorator = has_role(Role_dict.ADMIN)

decorators = [login_required ,role_decorator]

for view in [Lister, Adder, Editer, Deleter]:
    view.add_url_rule(bp_location, LocationVars, decorators)

for view in [UserItems, Panel]:
    view.add_url_rule(bp_location, LocationVars, [login_required])
