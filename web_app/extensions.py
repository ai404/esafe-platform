from flask_images import Images
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask_admin import Admin

from .admin import AdminView

ext_login_manager = LoginManager()
ext_csrf = CSRFProtect()
ext_images = Images()
ext_admin = Admin(index_view=AdminView(),template_mode='bootstrap3')

# init mail extension
ext_mail = Mail()
