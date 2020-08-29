from database import models

from flask import flash, current_app
from itsdangerous import URLSafeTimedSerializer

import datetime
import uuid
import os

def flash_errors(form):
    """Flash all errors"""
    for _, errors in form.errors.items():
        for error in errors:
            flash(error, "error")


def generate_token(data):
    """Generate a token for given data object"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(data, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    """Check if a given token is valid"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except Exception as e:
        print(e)
        return False
    tk = models.Token.query.filter_by(token_value=token).first()
    if not tk or tk.used or tk.expires_on < datetime.datetime.now():
        return False
    return data


def save_plan(field):
    """Save a location plan to the upload folder"""
    if field:
        file_extension = field.filename.rsplit('.', 1)[1].lower()
        file_id = uuid.uuid4().hex
        filename = f"{file_id}.{file_extension}"

        if not os.path.isdir("media/plans"):
            os.makedirs("media/plans")
        field.save(f"media/plans/{filename}")
        return filename
    return
