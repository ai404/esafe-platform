from .. import bp_account
from ..forms import RegisterForm

from web_app.helpers.decorators import user_redirect_to

from database import db_session
from database.models import Profile, User

from flask import render_template, url_for, request, g, current_app
from flask_login import current_user, logout_user
from werkzeug.utils import redirect

from web_app.helpers.senders import send_confirmation

@bp_account.route('/register', methods=['GET', 'POST'])
@user_redirect_to("main.dashboard")
def register():
    """New user account registration"""
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        new_user = User(form.email.data, form.password.data)
        g.session.add(new_user)
        g.session.commit()

        new_profile = Profile(form.first_name.data, form.last_name.data, new_user.id)
        g.session.add(new_profile)
        g.session.commit()
        # TODO: make it async
        if current_app.config["REQUIRE_EMAIL_CONFIRMATION"]:
            send_confirmation(new_user)
        new_user.init_folders()
        logout_user()
        return redirect(url_for(".login"))
    return render_template("account/register_user.pug", form=form)
