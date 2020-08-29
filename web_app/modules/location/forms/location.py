from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, TextAreaField, FloatField, validators


class LocationForm(FlaskForm):
    location_name = StringField('Location Name',
                                validators=[validators.DataRequired()])
    location_description = TextAreaField('Description',
                                         validators=[validators.length(max=200, 
                                         message="Maximum length is 200 chars")])
    location_address = StringField('Address',
                                   validators=[validators.DataRequired()])
    plan = FileField('Location Image Plan',
                     validators=[FileAllowed(["png", "jpg", "jpeg"], 
                     'Only supported image formats (png, jpg and jpeg) are allowed.')])
    lat = FloatField('Latitude', validators=[validators.Optional()])
    lng = FloatField('Longitude', validators=[validators.Optional()])
