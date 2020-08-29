from flask import Flask, g


def create_app(config):
    # Define the WSGI application object
    app = Flask(__name__)

    # Init Database session
    from database import db_session

    @app.before_request
    def create_session():
        g.session = db_session()

    @app.teardown_request
    def teardown_request(response_or_exc):
        db_session.remove()

    @app.teardown_appcontext
    def session_shutdown(response_or_exc):
        db_session.remove()

    from database.models import Role_dict

    @app.context_processor
    def inject_roles():
        return Role_dict.__dict__

    # Configurations
    app.config.from_object(config)

    # change template engine
    app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

    # set logging levels
    import sys
    import logging
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    from .extensions import ext_csrf, ext_images, ext_login_manager, ext_mail, ext_admin

    # login manager
    ext_login_manager.init_app(app)
    ext_login_manager.login_view = "account.login"

    from database.models import User

    @ext_login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    # Setup csrf extension
    ext_csrf.init_app(app)

    # Setup images extension
    ext_images.init_app(app)

    # Setup mail extension
    ext_mail.init_app(app)

    # simple HTTP error handling
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.pug'), 404

    # Serve uploaded files
    import os
    from flask import send_from_directory

    @app.route(f'{app.config["UPLOAD_URL"]}<path:filename>')
    def uploaded_file(filename):
        abs_path = os.path.abspath(app.config['UPLOAD_FOLDER'])
        return send_from_directory(abs_path,
                                   filename)

    # Register Blueprints
    from .modules.account import bp_account
    from .modules.main import bp_main
    from .modules.location import bp_location, bp_entity
    from .modules.staff import bp_staff

    from .modules.devices.camera import bp_camera

    app.register_blueprint(bp_account)
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_entity)
    app.register_blueprint(bp_location)
    app.register_blueprint(bp_staff)
    app.register_blueprint(bp_camera)

    # Setup Flask Admin extension
    app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
    ext_admin.init_app(app)
    
    from database import models
    from .admin import UserView, CompanyView

    ext_admin.add_view(UserView(models.User, db_session()))
    ext_admin.add_view(CompanyView(models.Company, db_session()))

    return app
