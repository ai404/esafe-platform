import datetime
from .. import bp_account
from ..forms import ResetPasswordSubmit

from database.models import User, Token

from web_app.helpers import confirm_token
from flask import request, flash, url_for, render_template, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from flask import g


@bp_account.route('/change/<token>', methods=['GET', 'POST'])
def change(token):
    """Change user password"""
    verified_result = confirm_token(token)
    if token and verified_result:
        user = User.query.get(verified_result)
        pwd_submit_form = ResetPasswordSubmit(request.form)
        if request.method == "POST" and pwd_submit_form.validate():
            token = Token.query.filter_by(token_value=token).first()
            token.used = True

            user.password = generate_password_hash(
                pwd_submit_form.password.data)
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()

            g.session.add(user)
            g.session.add(token)
            g.session.commit()

            flash("Password updated successfully!", "info")
            return redirect(url_for('account.login'))
        return render_template("account/change_password.pug", form=pwd_submit_form)
    else:
        flash("Invalid or Expired token", "error")
    return redirect(url_for("account.login"))


@bp_account.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit current user password"""
    pwd_submit_form = ResetPasswordSubmit(request.form)
    if request.method == "POST":
        if pwd_submit_form.validate_on_submit():
            current_user.password = generate_password_hash(
                pwd_submit_form.password.data)
            g.session.add(current_user)
            g.session.commit()
            flash("Password updated successfully!", "info")
            return redirect(url_for('.edit'))
    return render_template("account/account.pug", form=pwd_submit_form)
