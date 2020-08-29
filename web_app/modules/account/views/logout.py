from .. import bp_account

from flask import flash,redirect, url_for
from flask_login import login_required, logout_user


@bp_account.route('/logout', methods=['GET'])
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for(".login"))



