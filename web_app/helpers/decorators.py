from functools import wraps
from flask_login import current_user
from flask import render_template, url_for, redirect


def has_role(*roles):
    """A decorator to check if the current user has one of the given roles"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role_id in roles:
                return function(*args, **kwargs)
            return render_template("404.pug")
        return wrapper
    return decorator


def user_redirect_to(path):
    """Redirect user if autheticated to a given path"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url_for(path))
            return function(*args, **kwargs)
        return wrapper
    return decorator
