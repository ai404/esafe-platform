from web_app.scripts.init_settings import Settings
from web_app import create_app
from config import Config
import eventlet
eventlet.monkey_patch()


def init_app(app):
    # initialize db config records
    settings = Settings()
    settings.populate_db()

    # Enable Web-Sockets support
    from flask_socketio import SocketIO
    socketio = SocketIO(app, message_queue=Config.REDIS_SERVER)
    socketio.init_app(app, cors_allowed_origins="*")

    from web_app.sockets import register_socket_events

    # Register web sockets
    register_socket_events(socketio)

    return app


application = init_app(create_app("config.Config"))


if __name__ == "__main__":
    application.run()
