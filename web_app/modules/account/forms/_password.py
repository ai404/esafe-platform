from web_app.helpers.forms.rules import password_rules

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class ResetPassword(FlaskForm):
    """Request Password reset form"""
    email = StringField('Email', validators=[validators.DataRequired(),
                                             validators.Email("Enter a valid Email")],
                        description="Enter your email address")


class ResetPasswordSubmit(FlaskForm):
    """Resetting new password form"""
    password = PasswordField('New Password', validators=password_rules)
    password_confirm = PasswordField('Confirm Password', validators=[validators.DataRequired()], description="Re-enter Password")