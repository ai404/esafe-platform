import datetime

from .. import bp_account
from database.models import Token, User

from web_app.helpers import confirm_token
from flask import flash, url_for, redirect, g

@bp_account.route('/confirm/<token>')
def confirm_email(token):
    """Confirm a user's new account"""
    email = confirm_token(token)

    if not email:
        flash('Invalid or Expired Token!', 'error')
        return redirect(url_for('account.login'))
    
    user = User.query.filter_by(email=email).first()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        tk = Token.query.filter_by(token_value=token).first()
        tk.used = True

        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()

        g.session.add(tk)
        g.session.add(user)
        g.session.commit()
        flash('You have confirmed your account. Thanks!', 'info')
    
    return redirect(url_for('main.dashboard'))
