from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, BooleanField, TextAreaField, FloatField, validators
from flask_login import current_user

from web_app.helpers.forms.base import BaseForm

# TODO: create custom Fields objects with HTML
from web_app.helpers.forms.fields import CameraConfigField, CameraPicker


class CameraAddForm(BaseForm):
    entity = QuerySelectField('Entity', blank_text=u'-- please choose --',
                              query_factory=lambda: current_user.entities, get_label="name")
    streaming_uri = StringField('Streaming URI', validators=[validators.URL(
        message='A valid URL is required.'), validators.DataRequired()])
    active = BooleanField('Active')
    streaming_output = BooleanField('Output Streaming')
    description = TextAreaField('Description',
                                validators=[validators.length(max=200, message="Maximum length is 200 chars"), validators.DataRequired()])


class CameraEditForm(CameraAddForm):
    h_units = FloatField('Horizontal Units', validators=[
                         validators.DataRequired()])
    v_units = FloatField('Vertical Units', validators=[
                         validators.DataRequired()])
    notif_min_units = FloatField('Min Notification Units', validators=[
                                 validators.DataRequired()])
    coordinates = CameraPicker('Camera Localization')
    device_metadata = CameraConfigField('Camera Config', validators=[
                                        validators.DataRequired()])
