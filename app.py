"""
PSRA Flask Application

Main application module for the Pharmaceutical Studies and Research Association website.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_mail import Mail
from datetime import datetime
import os
import csv
import json

from config import Config
from models import db, User, Message, Post, Comment, Event, Research, Researcher
from services import EventService, MessageService, ResearchService
from utils.constants import FLASH_SUCCESS, FLASH_ERROR
from extensions import oauth
from werkzeug.middleware.proxy_fix import ProxyFix


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Add ProxyFix middleware to handle reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'forum.login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize OAuth
oauth.init_app(app)

# Load Google OAuth credentials from client_secret.json or environment variables
def get_google_oauth_credentials():
    """Load Google OAuth credentials from client_secret.json or environment variables."""
    # First try environment variables
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        return {
            'client_id': client_id,
            'client_secret': client_secret
        }

    # Fallback to client_secret.json
    client_secret_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
    if os.path.exists(client_secret_path):
        with open(client_secret_path, 'r') as f:
            credentials = json.load(f)
            web_creds = credentials.get('web', {})
            return {
                'client_id': web_creds.get('client_id'),
                'client_secret': web_creds.get('client_secret')
            }
    return {'client_id': None, 'client_secret': None}

google_creds = get_google_oauth_credentials()

# Register Google OAuth provider
google = oauth.register(
    name='google',
    client_id=google_creds['client_id'],
    client_secret=google_creds['client_secret'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Context processor for unread message count
@app.context_processor
def inject_unread_messages():
    """Make unread message count available to all templates."""
    if current_user.is_authenticated:
        unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}


# Register blueprints
from forum import forum_bp
app.register_blueprint(forum_bp, url_prefix='/forum')

from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from hub import hub_bp
app.register_blueprint(hub_bp, url_prefix='/hub')


# ==================== Static Page Routes ====================

@app.route('/')
def home():
    """Display home page with recent comments."""
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    return render_template('home.html', recent_comments=recent_comments)


@app.route('/research')
def research():
    """Display research publications page with filtering."""
    # Get filter parameters
    department = request.args.get('department', 'all')
    year = request.args.get('year', 'all')
    researcher_id = request.args.get('researcher', type=int)
    researcher_type = request.args.get('researcher_type', 'all')
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Apply filters using the service
    pagination = ResearchService.filter_researches(
        department=department,
        year=year,
        researcher_id=researcher_id,
        researcher_type=researcher_type,
        search_query=search_query if search_query else None,
        page=page,
        per_page=12
    )
    
    # Get filter choices and statistics
    year_choices = ResearchService.get_year_choices()
    researchers = ResearchService.get_all_researchers()
    statistics = ResearchService.get_research_statistics()
    
    return render_template(
        'researches.html',
        researches=pagination.items,
        pagination=pagination,
        department_choices=ResearchService.DEPARTMENT_CHOICES if hasattr(ResearchService, 'DEPARTMENT_CHOICES') else [],
        year_choices=year_choices,
        researcher_type_choices=ResearchService.RESEARCHER_TYPE_CHOICES if hasattr(ResearchService, 'RESEARCHER_TYPE_CHOICES') else [],
        researchers=researchers,
        statistics=statistics,
        current_department=department,
        current_year=year,
        current_researcher=researcher_id,
        current_researcher_type=researcher_type,
        search_query=search_query
    )


@app.route('/researchers')
def researchers():
    """Display all researchers page."""
    researchers_list = ResearchService.get_all_researchers()
    statistics = ResearchService.get_research_statistics()
    
    return render_template(
        'researchers.html',
        researchers=researchers_list,
        statistics=statistics
    )


@app.route('/researcher/<int:researcher_id>')
def researcher_profile(researcher_id):
    """Display researcher profile page."""
    profile_data = ResearchService.get_researcher_profile(researcher_id)
    
    if not profile_data:
        flash('Researcher not found.', FLASH_ERROR)
        return redirect(url_for('researchers'))
    
    return render_template(
        'researcher_profile.html',
        researcher=profile_data['researcher'],
        researches=profile_data['researches'],
        departments=profile_data['departments'],
        total_researches=profile_data['total_researches']
    )


@app.route('/submit-research', methods=['GET', 'POST'])
@login_required
def submit_research():
    """Submit a new research for approval."""
    from forum.forms import ResearchSubmissionForm
    
    form = ResearchSubmissionForm()
    
    if form.validate_on_submit():
        research = ResearchService.submit_research(
            title=form.title.data,
            researcher_name=form.researcher_name.data,
            department=form.department.data,
            year=form.year.data,
            doi_url=form.doi_url.data if form.doi_url.data else None,
            researcher_type=form.researcher_type.data,
            submitted_by=current_user.id
        )
        
        flash('Your research has been submitted for approval. You will be notified once it is reviewed.', FLASH_SUCCESS)
        return redirect(url_for('research'))
    
    return render_template(
        'submit_research.html',
        form=form
    )


@app.route('/api/search-researchers')
def api_search_researchers():
    """API endpoint to search researchers for autocomplete."""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    researchers = ResearchService.search_researchers(query, limit=10)
    return jsonify([{'id': r.id, 'name': r.name} for r in researchers])


@app.route('/events')
def events():
    """Display events page with categorized events."""
    events_data = EventService.get_categorized_events()
    return render_template('events.html', 
                          live_events=events_data['live'],
                          upcoming_events=events_data['upcoming'],
                          archived_events=events_data['archived'])


@app.route('/support')
def support():
    """Display support and donations page."""
    return render_template('placeholder.html', 
                          title='Support & Donations', 
                          content='Content for this page is coming soon. Please check back later.')


@app.route('/about')
def about():
    """Display about page."""
    return render_template('about.html')


@app.route('/collaborate')
def collaborate():
    """Display collaborate page."""
    return render_template('collaborate.html')


@app.route('/contact')
def contact():
    """Display contact page."""
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    """Display privacy policy page."""
    return render_template('placeholder.html', 
                          title='Privacy Policy', 
                          content='Content for this page is coming soon. Please check back later.')


@app.route('/faq')
def faq():
    """Display FAQ page."""
    return render_template('placeholder.html', 
                          title='FAQ', 
                          content='Content for this page is coming soon. Please check back later.')


# ==================== Forum Redirect ====================

@app.route('/forum')
def forum_redirect():
    """Redirect /forum to main forum page."""
    return redirect(url_for('forum.forum_main'))


# ==================== Google OAuth Routes ====================

@app.route('/login/google')
def login_google():
    """Initiate Google OAuth login."""
    # Use explicitly configured redirect URI if available (best for production)
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    
    if not redirect_uri:
        # Fallback to auto-generated URL
        if os.environ.get('FLASK_ENV') == 'production':
            redirect_uri = url_for('google_callback', _external=True, _scheme='https')
        else:
            redirect_uri = url_for('google_callback', _external=True)
            
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            # Fallback: fetch user info from Google
            user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        if not email:
            flash('Unable to get email from Google account.', FLASH_ERROR)
            return redirect(url_for('forum.login'))
        
        # Check if user exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email
            user = User.query.filter_by(email=email).first()
            if user:
                # Link Google account to existing user
                user.google_id = google_id
                db.session.commit()
            else:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    status='student'
                )
                db.session.add(user)
                db.session.commit()
        
        # Log in the user
        login_user(user)
        flash(f'Welcome, {user.name}!', FLASH_SUCCESS)
        
        # Redirect to the next page or home
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
        
    except Exception as e:
        flash(f'Google login failed: {str(e)}', FLASH_ERROR)
        return redirect(url_for('forum.login'))


# ==================== API Routes ====================

@app.route('/api/next-event')
def get_next_event():
    """Get the next upcoming event as JSON."""
    next_event = EventService.get_next_event()
    
    if next_event:
        return EventService.get_event_data(next_event)
    return {'no_event': True}


@app.route('/api/unread-count')
@login_required
def get_unread_count():
    """Get unread message count for current user."""
    unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return {'count': unread_count}


# ==================== SocketIO Event Handlers ====================

# Global dict to track typing status
typing_users = {}


@socketio.on('join')
def handle_join(data):
    """Handle user joining their personal room."""
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        emit('joined', {'room': room})


@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time message sending."""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not all([sender_id, receiver_id, content]):
        emit('error', {'message': 'Missing required fields'})
        return

    # Create message in database
    message = MessageService.send_message(sender_id, receiver_id, content)
    
    # Prepare message data for emission
    message_data = MessageService.get_message_data(message)

    # Send to receiver's room
    receiver_room = f"user_{receiver_id}"
    emit('new_message', message_data, room=receiver_room)

    # Send confirmation to sender
    emit('message_sent', message_data)


@socketio.on('typing_start')
def handle_typing_start(data):
    """Handle typing start event."""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')

    if sender_id and receiver_id:
        conversation_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        if conversation_id not in typing_users:
            typing_users[conversation_id] = {}
        typing_users[conversation_id][sender_id] = True

        # Notify the receiver
        receiver_room = f"user_{receiver_id}"
        user = User.query.get(sender_id)
        emit('typing_started', {'user_id': sender_id, 'user_name': user.name}, room=receiver_room)


@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Handle typing stop event."""
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
    """Mark messages as read and notify sender."""
    user_id = data.get('user_id')
    other_user_id = data.get('other_user_id')

    if user_id and other_user_id:
        count = MessageService.mark_messages_as_read(user_id, other_user_id)
        
        if count > 0:
            # Notify sender that messages were read
            sender_room = f"user_{other_user_id}"
            emit('messages_read', {
                'reader_id': user_id,
                'read_at': datetime.utcnow().isoformat()
            }, room=sender_room)


# ==================== CLI Commands for Notifications ====================

import click
from utils.notification_utils import send_scheduled_event_reminders, send_new_research_alert
from utils.email_utils import send_event_reminder_email, send_new_research_email


@app.cli.command('send-event-reminders')
def send_event_reminders_command():
    """Send event reminder notifications to users who have them enabled.
    
    This command should be scheduled to run daily via a cron job or task scheduler.
    Example cron entry: 0 9 * * * cd /path/to/app && flask send-event-reminders
    """
    click.echo('Sending event reminders...')
    
    try:
        count = send_scheduled_event_reminders(
            send_email_func=send_event_reminder_email
        )
        click.echo(f'Successfully sent {count} event reminders.')
    except Exception as e:
        click.echo(f'Error sending event reminders: {str(e)}', err=True)
        raise


@app.cli.command('send-new-research-alerts')
@click.option('--research-id', type=int, help='Send alert for a specific research ID')
def send_new_research_alerts_command(research_id):
    """Send new research publication alerts to subscribed users.
    
    If research-id is provided, sends alert for that specific research.
    Otherwise, sends alerts for all newly approved research from the last 24 hours.
    """
    click.echo('Sending new research alerts...')
    
    try:
        if research_id:
            # Send alert for specific research
            research = Research.query.get(research_id)
            if not research:
                click.echo(f'Research with ID {research_id} not found.', err=True)
                return
            
            count = send_new_research_alert(
                research=research,
                send_email_func=send_new_research_email
            )
            click.echo(f'Sent {count} alerts for research: {research.title[:50]}...')
        else:
            # Send alerts for research approved in last 24 hours
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=24)
            new_researches = Research.query.filter(
                Research.is_approved == True,
                Research.created_at >= cutoff
            ).all()
            
            total_sent = 0
            for research in new_researches:
                count = send_new_research_alert(
                    research=research,
                    send_email_func=send_new_research_email
                )
                total_sent += count
            
            click.echo(f'Sent {total_sent} alerts for {len(new_researches)} new research publications.')
    except Exception as e:
        click.echo(f'Error sending new research alerts: {str(e)}', err=True)
        raise


@app.cli.command('notification-stats')
def notification_stats_command():
    """Display notification statistics."""
    from models import NotificationLog
    from datetime import timedelta
    
    # Get stats for different time periods
    now = datetime.utcnow()
    
    # Last 24 hours
    day_ago = now - timedelta(hours=24)
    day_count = NotificationLog.query.filter(NotificationLog.sent_at >= day_ago).count()
    
    # Last 7 days
    week_ago = now - timedelta(days=7)
    week_count = NotificationLog.query.filter(NotificationLog.sent_at >= week_ago).count()
    
    # Last 30 days
    month_ago = now - timedelta(days=30)
    month_count = NotificationLog.query.filter(NotificationLog.sent_at >= month_ago).count()
    
    # By type
    event_reminders = NotificationLog.query.filter_by(notification_type='event_reminder').count()
    research_alerts = NotificationLog.query.filter_by(notification_type='new_research').count()
    status_updates = NotificationLog.query.filter_by(notification_type='research_status').count()
    
    click.echo('\n=== Notification Statistics ===')
    click.echo(f'Last 24 hours: {day_count}')
    click.echo(f'Last 7 days: {week_count}')
    click.echo(f'Last 30 days: {month_count}')
    click.echo('\nBy Type:')
    click.echo(f'  Event Reminders: {event_reminders}')
    click.echo(f'  New Research Alerts: {research_alerts}')
    click.echo(f'  Research Status Updates: {status_updates}')
    click.echo(f'  Total: {event_reminders + research_alerts + status_updates}')


# ==================== Application Entry Point ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

