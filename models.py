from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    STUDENT = 'student'
    ALUMNI = 'alumni'
    RESEARCHER = 'researcher'
    ADMIN = 'admin'

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    faculty_name = db.Column(db.String(150), nullable=True)
    
    profiles = db.relationship('Profile', back_populates='department', lazy=True)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    
    # Relationship to user_skills
    users = db.relationship('UserSkill', back_populates='skill', cascade='all, delete-orphan')

class UserSkill(db.Model):
    __tablename__ = 'user_skills'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
    level = db.Column(db.String(50), nullable=True)
    
    user = db.relationship('User', back_populates='user_skills')
    skill = db.relationship('Skill', back_populates='users')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
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

    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # New relationships
    user_skills = db.relationship('UserSkill', back_populates='user', cascade='all, delete-orphan')
    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    alumni_profile = db.relationship('AlumniProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    researcher_profile = db.relationship('ResearcherProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')

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

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture_url = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='profile')
    department = db.relationship('Department', back_populates='profiles')

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    academic_level = db.Column(db.String(100), nullable=True)
    gpa = db.Column(db.Numeric(3, 2), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    cv_url = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', back_populates='student_profile')

class AlumniProfile(db.Model):
    __tablename__ = 'alumni_profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    job_title = db.Column(db.String(200), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    industry = db.Column(db.String(200), nullable=True)
    open_to_mentor = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', back_populates='alumni_profile')

class ResearcherProfile(db.Model):
    __tablename__ = 'researcher_profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    academic_rank = db.Column(db.String(150), nullable=True)
    lab_name = db.Column(db.String(150), nullable=True)
    office_location = db.Column(db.String(150), nullable=True)
    
    user = db.relationship('User', back_populates='researcher_profile')

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
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
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


class MentorshipStatus(enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    ENDED = 'ended'

class MentorRequest(db.Model):
    __tablename__ = 'mentor_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    alumni_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(MentorshipStatus), default=MentorshipStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', foreign_keys=[student_id], backref='mentor_requests_sent')
    alumni = db.relationship('User', foreign_keys=[alumni_id], backref='mentor_requests_received')

class ActiveMentorship(db.Model):
    __tablename__ = 'active_mentorships'
    id = db.Column(db.Integer, primary_key=True)
    mentor_request_id = db.Column(db.Integer, db.ForeignKey('mentor_requests.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    request = db.relationship('MentorRequest', backref=db.backref('active_mentorship', uselist=False))

class ProjectStatus(enum.Enum):
    OPEN = 'open'
    CLOSED = 'closed'

class ResearchProject(db.Model):
    __tablename__ = 'research_projects'
    id = db.Column(db.Integer, primary_key=True)
    researcher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    required_positions = db.Column(db.Integer, default=1)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.OPEN)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    researcher = db.relationship('User', backref='research_projects')
    required_skills = db.relationship('ProjectRequiredSkill', back_populates='project', cascade='all, delete-orphan')
    applications = db.relationship('ProjectApplication', back_populates='project', cascade='all, delete-orphan')

class ProjectRequiredSkill(db.Model):
    __tablename__ = 'project_required_skills'
    project_id = db.Column(db.Integer, db.ForeignKey('research_projects.id', ondelete='CASCADE'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
    
    project = db.relationship('ResearchProject', back_populates='required_skills')
    skill = db.relationship('Skill')

class ApplicationStatus(enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class ProjectApplication(db.Model):
    __tablename__ = 'project_applications'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('research_projects.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    motivation_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('ResearchProject', back_populates='applications')
    student = db.relationship('User', backref='project_applications')

class JobType(enum.Enum):
    INTERNSHIP = 'internship'
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    job_type = db.Column(db.Enum(JobType), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    poster = db.relationship('User', backref='posted_jobs')
    required_skills = db.relationship('JobRequiredSkill', back_populates='job', cascade='all, delete-orphan')

class JobRequiredSkill(db.Model):
    __tablename__ = 'job_required_skills'
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
    
    job = db.relationship('Job', back_populates='required_skills')
    skill = db.relationship('Skill')

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    participants = db.relationship('ConversationParticipant', back_populates='conversation', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='conversation_rel', lazy='dynamic') # Note: named conversation_rel to avoid conflict if any

class ConversationParticipant(db.Model):
    __tablename__ = 'conversation_participants'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    
    conversation = db.relationship('Conversation', back_populates='participants')
    user = db.relationship('User', backref='conversations_participated')

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
