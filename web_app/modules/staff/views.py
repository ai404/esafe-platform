from . import bp_staff

from flask import g, render_template
from flask_login import current_user, login_required
from wtforms.fields.core import SelectMultipleField

from .forms import StaffFormStep1, StaffFormEdit, build_form
from database.models import User, Role_dict, Location, Profile, Role

from web_app.helpers.decorators import has_role

from web_app.modules._base_views import BasePanel, BasePreAdder, BaseLister, BaseAdder, BaseDeleter, BaseEditer


class Lister(BaseLister):
    def get_items(self):
        return current_user.staff


class PreAdder(BasePreAdder):
    pass


class PreProcessMixin(object):
    def preprocess_form(self, form):
        # set assigned locations
        locations_ids = form.assigned_locations.data
        locations_ids = [locations_ids] if type(
            locations_ids) != list else locations_ids
        locations = list(map(Location.query.get, locations_ids))

        form.assigned_locations.data = locations

    def set_special_attributes(self, form, record, **kwargs):
        # set password
        if form.password:
            record.set_password(form.password.data)


class Adder(PreProcessMixin, BaseAdder):
    url_name = "adder_step2"

    def set_special_attributes(self, form, record, role_id):
        super().set_special_attributes(form, record, role_id)

        record.approved = True
        record.confirmed = True
        # set user role
        role = Role.query.get(role_id)
        record.role = role
        record.manager_id = current_user.id
        record.company_id = current_user.company_id

    def post_transaction(self, form, record, **kwargs):
        # create a profile for user
        profile = Profile(form.first_name.data, form.last_name.data, record.id)
        g.session.add(profile)
        g.session.commit()

        super().post_transaction(form, record, **kwargs)

    def build_form(self, role_id):
        return self.form(role_id)

    @classmethod
    def get_endpoint(self):
        return "/add-role-<int:role_id>"


class Deleter(BaseDeleter):
    def get_items(self):
        return current_user.entities


class Panel(BasePanel):

    def get_item(self, id):
        return User.query.get(id)

    def is_valid_item(self, item):
        return item in current_user.staff

    def get_template_name(self):
        return 'staff/panel.pug'


class Editer(PreProcessMixin, BaseEditer):
    def get_template_name(self):
        return 'base/adder.pug'

    def preprocess_form(self, form):
        super().preprocess_form(form)
        if form.password.data == form.password_confirm.data == "":
            del form.password

    def build_form(self, id):
        user = User.query.get(id)
        return self.form(user.role.id)

    def prepopulate_special_fields(self, form, record):
        if isinstance(form.assigned_locations, SelectMultipleField):
            form.assigned_locations.data = list(
                map(lambda x: x.id, record.locations))
        elif len(record.locations) == 1:
            form.assigned_locations.data = record.locations[0].id

    def before_validation_preprocess(self, form, record):
        if form.email.data == record.email:
            form.email.validators = []

        if form.password.data == form.password_confirm.data == "":
            form.password.validators = []


class Staffvars(object):
    title = "User"
    column_titles = ["ID", "Email", "Role", "Status", "Locations"]
    column_ids = ["id", "email",
                  lambda x:x.role.role_name,
                  lambda x:x.account_status.status_name,
                  lambda x: "-" if not x.locations else ", ".join(
                      map(lambda x:x.location_name, x.locations))
                  ]
    model = User
    form = build_form
    form_preadd = StaffFormStep1
    kind = "staff"


role_decorator = has_role(Role_dict.ADMIN, Role_dict.MANAGER)

decorators = [login_required, role_decorator]

views = [
    Lister, Adder, Editer, Deleter, PreAdder, Panel
]

for view in views:
    view.add_url_rule(bp_staff, Staffvars, decorators)
