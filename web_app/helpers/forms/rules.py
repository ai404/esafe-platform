from database.models import User
from wtforms import ValidationError, validators


class ExistingUser(object):
    """Verify if a user exist with the given email"""
    def __init__(self, message=""):
        self.message = message

    def __call__(self, form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(self.message)


email_rules = [validators.DataRequired(),
               validators.Email("Enter a valid Email"),
               ExistingUser(message='Email address is not available')
               ]

password_rules_not_required = [
    validators.length(min=5, message="Minimum length is 5 chars"),
    validators.EqualTo('password_confirm', message='Passwords must match')
]
password_rules = [
    validators.DataRequired(), *password_rules_not_required
]
