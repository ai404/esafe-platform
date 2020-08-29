from .. import bp_account
from ..forms import LoginForm

from web_app.helpers.decorators import user_redirect_to

from database.models import User

from flask import render_template, request, flash, url_for, redirect, current_app
from flask_login import login_user

@bp_account.route('/login', methods=['GET', 'POST'])
@user_redirect_to("main.dashboard")
def login():
    """Login page controller"""
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        
        user = User.authenticate(email, password)
        if user:
            if user.confirmed or not current_app.config["REQUIRE_EMAIL_CONFIRMATION"]:
                if user.approved:
                    remember_me = 'remember_me' in request.form
                    login_user(user, remember=remember_me)

                    if request.args.get("next"):
                        return redirect(request.args.get("next"))
                    else:
                        return redirect(url_for("main.dashboard"))
                else:
                    flash("Your account is not approved yet, please contact an administrator or try again later!", "error")
            else:
                flash("This email is not verified. Please check your Inbox", "error")
            
        else:
            flash("Username/Password doesn't match", "error")
    return render_template("account/login_user.pug", form=form)

