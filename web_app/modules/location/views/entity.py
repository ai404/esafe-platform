from .. import bp_entity

from flask import g
from flask_login import current_user, login_required

from ..forms.entity import EntityAddForm, EntityEditForm
from database.models import Entity, Alert, Access, Role_dict

from web_app.modules._base_views import BaseUserItems, BasePanel, BaseLister, BaseAdder, BaseDeleter, BaseEditer
from web_app.helpers.decorators import has_role

from ._base import BaseLocPanel


class UserItems(BaseUserItems):
    def get_items(self):
        return current_user.entities


class Lister(BaseLister):
    def get_items(self):
        return current_user.entities


class Panel(BaseLocPanel):

    def get_item(self, id):
        return Entity.query.get(id)

    def get_items(self):
        return current_user.entities

    def get_alerts(self, id, offset=None, limit=100):
        return Alert.get_alerts(id=id, for_name="entity", offset=offset, limit=limit)


class Adder(BaseAdder):

    def set_special_attributes(self, form, record, **kwargs):
        record.company_id = current_user.company_id

    def post_transaction(self, form, record, **kwargs):
        # add current user to access list for entity
        access = Access()

        access.entity_id = record.id
        access.user_id = current_user.id

        g.session.add(access)
        g.session.commit()

    def get_template_name(self):
        return 'entity/adder.pug'


class Editer(BaseEditer):
    def get_template_name(self):
        return 'entity/adder.pug'


class Deleter(BaseDeleter):
    def get_items(self):
        return current_user.entities


class EntityVars(object):
    title = "Entitie"
    column_titles = ["ID", "Entity Name", "Location", "# Cameras"]
    column_ids = ["id", "name", "address", "cameras_count"]
    form = EntityAddForm
    form_edit = EntityEditForm
    model = Entity
    kind = bp_entity.name


role_decorator = has_role(Role_dict.ADMIN, Role_dict.MANAGER)

decorators = [login_required ,role_decorator]

for view in [Lister, Adder, Editer, Deleter]:
    view.add_url_rule(bp_entity, EntityVars, decorators)

for view in [UserItems, Panel]:
    view.add_url_rule(bp_entity, EntityVars, [login_required])