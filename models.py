from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    batch_number = db.Column(db.Integer, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    is_member = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='student')  # 'student', 'alumni', 'undergraduate'
    headline = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    about = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    education = db.Column(db.Text, nullable=True)  # JSON array of education entries
    experience = db.Column(db.Text, nullable=True)  # JSON array of work experience entries
    linkedin_url = db.Column(db.String(200), nullable=True)
    website_url = db.Column(db.String(200), nullable=True)
    cover_photo_url = db.Column(db.String(200), default=None)
    profile_picture_url = db.Column(db.String(200), default=None)
    languages = db.Column(db.Text, nullable=True)  # Comma-separated languages
    certifications = db.Column(db.Text, nullable=True)  # JSON or text for certifications
    projects = db.Column(db.Text, nullable=True)  # JSON or text for projects
    publications = db.Column(db.Text, nullable=True)  # Research publications
    professional_summary = db.Column(db.Text, nullable=True)  # Separate from about
    is_admin = db.Column(db.Boolean, default=False)
    # Notification preferences
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    event_reminders_enabled = db.Column(db.Boolean, default=True)
    new_research_alerts_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    events = db.relationship('Event', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Pharmacology'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    image_url = db.Column(db.String(200), default=None)
    presenter = db.Column(db.String(200), nullable=True)
    event_url = db.Column(db.String(500), nullable=True)
    is_archived = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')


class Researcher(db.Model):
    """Model for researchers (doctors and students) who author research papers."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    profile_picture_url = db.Column(db.String(200), default=None)
    bio = db.Column(db.Text, nullable=True)
    is_registered_user = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to research papers
    researches = db.relationship('Research', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Researcher {self.name}>'


class Research(db.Model):
    """Model for research papers/publications."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    doi_url = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.id'), nullable=False)
    researcher_type = db.Column(db.String(20), default='doctor')  # 'doctor' or 'student'
    is_approved = db.Column(db.Boolean, default=True)  # For submitted research pending approval
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # User who submitted
    submitted_by_user = db.relationship('User', foreign_keys=[submitted_by], backref='submitted_researches')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Research {self.title}>'
    
    @property
    def department_choices(self):
        """Return list of valid departments."""
        return [
            'Pharmaceutics & Drug Delivery',
            'Pharmacology & Toxicology',
            'Clinical Pharmacy & Pharmacy Practice',
            'Pharmaceutical Chemistry'
        ]


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    target_filter = db.Column(db.Text, nullable=True)
    recipient_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='announcements')

    def __repr__(self):
        return f'<Announcement {self.subject}>'


class NotificationLog(db.Model):
    """Model to track sent notifications."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notification_type = db.Column(db.String(50), nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')
    error_message = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', backref='notification_logs')
    
    def __repr__(self):
        return f'<NotificationLog {self.notification_type} to {self.recipient_email}>'
