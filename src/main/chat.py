from flask_socketio import SocketIO, join_room, emit
from flask import request
from flask_login import current_user

# This will be initialized in app.py
socketio = SocketIO()

# In-memory message store: { (club_slug, date): [ {user, message, time}, ... ] }
chat_messages = {}

def get_room_key(club_slug, date):
    return f"{club_slug}:{date}"

def register_chat_handlers(app):
    socketio.init_app(app, async_mode='eventlet', manage_session=False)

    @socketio.on('join')
    def handle_join(data):
        date_id = data.get('date_id')
        club_slug = data.get('club_slug')
        room = get_room_key(club_slug, date_id)
        join_room(room)
        # Send existing messages
        messages = chat_messages.get(room, [])
        emit('load_messages', messages)

    @socketio.on('send_message')
    def handle_send_message(data):
        date_id = data.get('date_id')
        club_slug = data.get('club_slug')
        message = data.get('message')
        room = get_room_key(club_slug, date_id)
        user = current_user.username if current_user.is_authenticated else 'Anonymous'
        from datetime import datetime
        msg_obj = {
            'user': user,
            'message': message,
            'time': datetime.now().strftime('%H:%M')
        }
        chat_messages.setdefault(room, []).append(msg_obj)
        emit('new_message', msg_obj, room=room)

    return socketio
