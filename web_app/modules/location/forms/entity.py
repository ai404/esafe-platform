from web_app.helpers.forms.base import BaseForm
from web_app.helpers.forms.fields import BoundingBoxField

from wtforms import StringField, TextAreaField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask_login import current_user


class EntityAddForm(BaseForm):
    location = QuerySelectField('Location', blank_text=u'-- please choose --',
                                query_factory=lambda: current_user.locations, get_label="location_name")
    name = StringField('Entity Name', validators=[validators.DataRequired()])
    description = TextAreaField('Description',
                                validators=[validators.length(max=200, message="Maximum length is 200 chars")])


class EntityEditForm(EntityAddForm):
    bounding_box = BoundingBoxField('Bounding Area')
