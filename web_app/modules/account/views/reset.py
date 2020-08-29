from .. import bp_account
from ..forms import ResetPassword
from web_app.helpers.senders import send_reset_link

from database.models import User

from flask import request, render_template

@bp_account.route('/reset', methods=('GET', 'POST',))
def reset():
    """Reset password"""
    form = ResetPassword(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_link(user)
    return render_template('account/forgot_password.pug', form=form)
