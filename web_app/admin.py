from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView

class AccessMixin(object):
    def is_accessible(self):
        return current_user.is_su

    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('account.login', next="/admin"))
        
        if not self.is_accessible():
            return "<p>Access denied</p>"

class UserView(AccessMixin, ModelView):
    can_create = False  # disable model deletion
    column_exclude_list = ['password', ]

class CompanyView(AccessMixin, ModelView):
    pass

class AdminView(AccessMixin, AdminIndexView):
    pass