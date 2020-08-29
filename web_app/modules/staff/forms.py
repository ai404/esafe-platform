from web_app.helpers.forms.rules import email_rules, password_rules_not_required

from database.models import Role, AccountStatus, Role_dict

from flask_login import current_user
from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, FloatField, PasswordField, SelectMultipleField, SelectField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class StaffFormStep1(FlaskForm):
    role = QuerySelectField('Role',
                            blank_text=u'-- please choose --',
                            query_factory=lambda: Role.query.filter(
                                Role.id < current_user.role.id),
                            get_label="role_name",
                            validators=[validators.DataRequired()])

    def to_dict(self):
        return {
            "role_id": self.role.data.id
        }


class StaffFormEdit(FlaskForm):
    first_name = StringField('First Name', validators=[
                             validators.DataRequired()])
    last_name = StringField('Last Name', validators=[
                            validators.DataRequired()])
    email = StringField('Email', validators=email_rules)
    password = PasswordField('Password', validators=password_rules_not_required)
    password_confirm = PasswordField('Repeat Password',
                                     description="Re-enter Password")

    account_status = QuerySelectField('Status',
                                      blank_text=u'-- please choose --',
                                      query_factory=lambda: AccountStatus.query,
                                      get_label="status_name",
                                      validators=[validators.DataRequired()])


def build_form(role_id):
    location_choices = map(lambda x: (
        x.id, x.location_name), current_user.locations)
    multi_selection = role_id == Role_dict.MANAGER

    class StaffFormStep2(StaffFormEdit):

        __params = dict(
            label='Location',
            coerce=int,
            choices=location_choices,
            validators=[validators.DataRequired()]
        )
        if multi_selection:
            assigned_locations = SelectMultipleField(**__params)
        else:
            assigned_locations = SelectField(**__params)

    return StaffFormStep2
