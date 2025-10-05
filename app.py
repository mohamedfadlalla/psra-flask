from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///psra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'forum.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import models to register them with db
from models import Post, Comment, Like, Event

# Register forum blueprint
from forum import forum_bp
app.register_blueprint(forum_bp, url_prefix='/forum')

# Register admin blueprint
from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Static Page Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/research')
def research():
    return render_template('placeholder.html', title='Research', content='Content for this page is coming soon. Please check back later.')

@app.route('/events')
def events():
    from models import Event
    from datetime import datetime, date

    today = date.today()
    now = datetime.now().time()

    # Get upcoming events (future dates or today with future times)
    upcoming_events = Event.query.filter(
        (Event.event_date > today) |
        ((Event.event_date == today) & (Event.event_time > now) & (Event.event_time.isnot(None)))
    ).order_by(Event.event_date.asc(), Event.event_time.asc()).all()

    return render_template('events.html', events=upcoming_events)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
