from flask_socketio import join_room


def register_socket_events(socketio):
    @socketio.on('join')
    def on_join(data):
        room = data['room']
        join_room(room)
    