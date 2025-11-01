from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///psra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/profile_images'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'forum.login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize SocketIO with CORS enabled for real-time messaging
socketio = SocketIO(app, cors_allowed_origins="*")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to make unread message count available to all templates
@app.context_processor
def inject_unread_messages():
    if current_user.is_authenticated:
        unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}

# Import models to register them with db
from models import Post, Comment, Like, Event, Message

# Register forum blueprint
from forum import forum_bp
app.register_blueprint(forum_bp, url_prefix='/forum')

# Register admin blueprint
from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Register API blueprint
from api import api_bp
app.register_blueprint(api_bp)

# Static Page Routes
@app.route('/')
def home():
    # Fetch recent comments for display on home page
    from models import Comment
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    return render_template('home.html', recent_comments=recent_comments)

@app.route('/research')
def research():
    return render_template('placeholder.html', title='Research', content='Content for this page is coming soon. Please check back later.')

@app.route('/events')
def events():
    from models import Event
    from datetime import datetime, date

    today = date.today()
    now = datetime.now().time()

    # Archive past events automatically
    past_events = Event.query.filter(
        (Event.event_date < today) |
        ((Event.event_date == today) & (Event.event_time <= now) & (Event.event_time.isnot(None)))
    ).filter(Event.is_archived == False).all()

    for event in past_events:
        event.is_archived = True

    if past_events:
        db.session.commit()

    # Get live events (today with future times)
    live_events = Event.query.filter(
        (Event.event_date == today) & (Event.event_time > now) & (Event.event_time.isnot(None))
    ).filter(Event.is_archived == False).order_by(Event.event_time.asc()).all()

    # Get upcoming events (future dates)
    upcoming_events = Event.query.filter(Event.event_date > today).filter(Event.is_archived == False).order_by(Event.event_date.asc(), Event.event_time.asc()).all()

    # Get archived events
    archived_events = Event.query.filter(Event.is_archived == True).order_by(Event.event_date.desc(), Event.event_time.desc()).all()

    return render_template('events.html', live_events=live_events, upcoming_events=upcoming_events, archived_events=archived_events)

@app.route('/support')
def support():
    return render_template('placeholder.html', title='Support & Donations', content='Content for this page is coming soon. Please check back later.')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/collaborate')
def collaborate():
    return render_template('collaborate.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('placeholder.html', title='Privacy Policy', content='Content for this page is coming soon. Please check back later.')

@app.route('/faq')
def faq():
    return render_template('placeholder.html', title='FAQ', content='Content for this page is coming soon. Please check back later.')

# Forum main redirect
@app.route('/forum')
def forum_redirect():
    return redirect(url_for('forum.forum_main'))

# API route for next event
@app.route('/api/next-event')
def get_next_event():
    from models import Event
    from datetime import datetime, date

    today = date.today()
    next_event = Event.query.filter(
        (Event.event_date > today) |
        ((Event.event_date == today) & (Event.event_time > datetime.now().time()) & (Event.event_time.isnot(None)))
    ).order_by(Event.event_date.asc(), Event.event_time.asc()).first()

    if next_event:
        event_datetime = datetime.combine(next_event.event_date, next_event.event_time) if next_event.event_time else datetime.combine(next_event.event_date, datetime.min.time())
        return {
            'title': next_event.title,
            'description': next_event.description,
            'event_datetime': event_datetime.isoformat(),
            'has_time': next_event.event_time is not None,
            'image_url': next_event.image_url
        }
    return {'no_event': True}

# API endpoint for unread message count
@app.route('/api/unread-count')
@login_required
def get_unread_count():
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return {'count': unread_count}

# SocketIO event handlers for real-time messaging
typing_users = {}  # Global dict to track typing status: {conversation_id: {user_id: True/False}}

@socketio.on('join')
def handle_join(data):
    """User joins their personal room for receiving messages"""
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        emit('joined', {'room': room})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time message sending"""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not all([sender_id, receiver_id, content]):
        emit('error', {'message': 'Missing required fields'})
        return

    # Create message in database
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()

    # Prepare message data for emission
    message_data = {
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'is_read': message.is_read,
        'read_at': message.read_at.isoformat() if message.read_at else None,
        'created_at': message.created_at.isoformat(),
        'sender_name': message.sender.name
    }

    # Send to receiver's room
    receiver_room = f"user_{receiver_id}"
    emit('new_message', message_data, room=receiver_room)

    # Send confirmation to sender
    emit('message_sent', message_data)

@socketio.on('typing_start')
def handle_typing_start(data):
    """Handle typing start event"""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    if sender_id and receiver_id:
        conversation_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        if conversation_id not in typing_users:
            typing_users[conversation_id] = {}
        typing_users[conversation_id][sender_id] = True

        # Notify the receiver
        receiver_room = f"user_{receiver_id}"
        emit('typing_started', {'user_id': sender_id, 'user_name': User.query.get(sender_id).name}, room=receiver_room)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Handle typing stop event"""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    if sender_id and receiver_id:
        conversation_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        if conversation_id in typing_users and sender_id in typing_users[conversation_id]:
            typing_users[conversation_id][sender_id] = False

        # Notify the receiver
        receiver_room = f"user_{receiver_id}"
        emit('typing_stopped', {'user_id': sender_id}, room=receiver_room)

@socketio.on('mark_read')
def handle_mark_read(data):
    """Mark messages as read and notify sender"""
    user_id = data.get('user_id')  # Current user (receiver)
    other_user_id = data.get('other_user_id')  # Conversation partner

    if user_id and other_user_id:
        # Mark unread messages from other_user as read
        unread_messages = Message.query.filter_by(
            sender_id=other_user_id,
            receiver_id=user_id,
            is_read=False
        ).all()

        for message in unread_messages:
            message.is_read = True
            message.read_at = datetime.utcnow()

        if unread_messages:
            db.session.commit()

            # Notify sender that messages were read
            sender_room = f"user_{other_user_id}"
            read_message_ids = [msg.id for msg in unread_messages]
            emit('messages_read', {
                'reader_id': user_id,
                'message_ids': read_message_ids,
                'read_at': datetime.utcnow().isoformat()
            }, room=sender_room)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
