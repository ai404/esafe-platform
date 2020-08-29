from web_app.helpers.forms.rules import password_rules, email_rules

from flask import request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class RegisterForm(FlaskForm):
    """User registeration form"""
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=email_rules)
    password = PasswordField('Password', validators=password_rules)
    password_confirm = PasswordField('Repeat Password', validators=[validators.DataRequired()], description="Re-enter Password")

    def validate(self):
        """Extend parent's method to verify if user agrees to terms of use"""
        _value = super().validate()
        if not _value:
            return False
        
        if request.form.get("terms", "")=="agree":
            return True

        flash("You need to agree on terms of use!", "error")
        return False

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[validators.DataRequired(),
                                             validators.Email("Enter a valid Email")])
    password = PasswordField('Password', validators=[validators.DataRequired()])
