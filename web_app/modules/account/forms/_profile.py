from flask_wtf import FlaskForm
from wtforms import StringField, validators, FileField

class UploadPhotoForm(FlaskForm):
    """Change Profile picture form"""
    picture = FileField('Select a valid photo')


class ProfileForm(FlaskForm):
    """Edit Profile informations form"""
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
