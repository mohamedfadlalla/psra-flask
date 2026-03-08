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
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True)
    
    profiles = db.relationship('Profile', back_populates='department', lazy=True)
    university = db.relationship('University', back_populates='departments')

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    
    # Relationship to user_skills
    users = db.relationship('UserSkill', back_populates='skill', cascade='all, delete-orphan')

class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    abbreviation = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profiles = db.relationship('Profile', back_populates='university', lazy=True)
    departments = db.relationship('Department', back_populates='university', lazy=True)
    
    def __repr__(self):
        return f'<University {self.name}>'

class UserSkill(db.Model):
    __tablename__ = 'user_skills'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True, index=True)
    level = db.Column(db.String(50), nullable=True)
    
    user = db.relationship('User', back_populates='user_skills')
    skill = db.relationship('Skill', back_populates='users')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    batch_number = db.Column(db.Integer, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    is_member = db.Column(db.Boolean, default=False)
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

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='creator', lazy=True, cascade='all, delete-orphan')

    # Properties to maintain backward compatibility with templates
    @property
    def name(self):
        return self.profile.full_name if self.profile else "Unknown User"

    @name.setter
    def name(self, value):
        if self.profile:
            self.profile.full_name = value
        else:
            self.profile = Profile(full_name=value)

    @property
    def status(self):
        return self.role.value if self.role else 'student'

    @status.setter
    def status(self, value):
        mapping = {
            'student': UserRole.STUDENT,
            'undergraduate': UserRole.STUDENT,
            'graduate': UserRole.ALUMNI,
            'alumni': UserRole.ALUMNI,
            'researcher': UserRole.RESEARCHER,
            'admin': UserRole.ADMIN,
        }
        self.role = mapping.get(value, UserRole.STUDENT)

    @property
    def is_undergraduate(self):
        return self.role == UserRole.STUDENT and self.student_profile and self.student_profile.academic_level == 'undergraduate'

    @property
    def can_create_projects(self):
        return self.role in (UserRole.ALUMNI, UserRole.RESEARCHER, UserRole.ADMIN)

    @property
    def can_offer_mentorship(self):
        if self.role == UserRole.ALUMNI and self.alumni_profile:
            return bool(self.alumni_profile.open_to_mentor)
        if self.role == UserRole.RESEARCHER and self.researcher_profile:
            return bool(getattr(self.researcher_profile, 'open_to_mentor', False))
        return False

    @property
    def headline(self):
        return self.profile.headline if self.profile else None

    @headline.setter
    def headline(self, value):
        if self.profile:
            self.profile.headline = value

    @property
    def location(self):
        return self.profile.location if self.profile else None

    @location.setter
    def location(self, value):
        if self.profile:
            self.profile.location = value

    @property
    def about(self):
        return self.profile.bio if self.profile else None

    @about.setter
    def about(self, value):
        if self.profile:
            self.profile.bio = value

    @property
    def profile_picture_url(self):
        return self.profile.profile_picture_url if self.profile else None

    @profile_picture_url.setter
    def profile_picture_url(self, value):
        if self.profile:
            self.profile.profile_picture_url = value

    @property
    def linkedin_url(self):
        return self.profile.linkedin_url if self.profile else None

    @linkedin_url.setter
    def linkedin_url(self, value):
        if self.profile:
            self.profile.linkedin_url = value

    @property
    def website_url(self):
        return self.profile.website_url if self.profile else None

    @website_url.setter
    def website_url(self, value):
        if self.profile:
            self.profile.website_url = value

    @property
    def languages(self):
        return self.profile.languages if self.profile else None

    @languages.setter
    def languages(self, value):
        if self.profile:
            self.profile.languages = value

    @property
    def certifications(self):
        return self.profile.certifications if self.profile else None

    @certifications.setter
    def certifications(self, value):
        if self.profile:
            self.profile.certifications = value

    @property
    def projects(self):
        return self.profile.projects if self.profile else None

    @projects.setter
    def projects(self, value):
        if self.profile:
            self.profile.projects = value

    @property
    def publications(self):
        return self.profile.publications if self.profile else None

    @publications.setter
    def publications(self, value):
        if self.profile:
            self.profile.publications = value

    @property
    def professional_summary(self):
        return self.profile.professional_summary if self.profile else None

    @professional_summary.setter
    def professional_summary(self, value):
        if self.profile:
            self.profile.professional_summary = value

    @property
    def education(self):
        return self.profile.education if self.profile else '[]'

    @education.setter
    def education(self, value):
        if self.profile:
            self.profile.education = value

    @property
    def experience(self):
        return self.profile.experience if self.profile else '[]'

    @experience.setter
    def experience(self, value):
        if self.profile:
            self.profile.experience = value

    @property
    def skills(self):
        if not self.user_skills:
            return ""
        return ",".join([us.skill.name for us in self.user_skills if us.skill])

    @skills.setter
    def skills(self, value):
        if not value:
            self.user_skills = []
            return
            
        skill_names = [s.strip() for s in value.split(',') if s.strip()]
        new_user_skills = []
        for s_name in skill_names:
            skill = Skill.query.filter_by(name=s_name).first()
            if not skill:
                skill = Skill(name=s_name)
                db.session.add(skill)
                db.session.flush() # get id
            
            # Check if this user_skill already exists
            existing = next((us for us in self.user_skills if us.skill and us.skill.name == s_name), None)
            if existing:
                new_user_skills.append(existing)
            else:
                us = UserSkill(skill=skill)
                new_user_skills.append(us)
        
        self.user_skills = new_user_skills

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
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True)
    
    # Extended profile fields moved from User
    headline = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    website_url = db.Column(db.String(200), nullable=True)
    languages = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    projects = db.Column(db.Text, nullable=True)
    publications = db.Column(db.Text, nullable=True)
    professional_summary = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='profile')
    department = db.relationship('Department', back_populates='profiles')
    university = db.relationship('University', back_populates='profiles')

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
    open_to_mentor = db.Column(db.Boolean, default=False)
    
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

class ProfileClaim(db.Model):
    __tablename__ = 'profile_claims'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    researcher_id = db.Column(db.Integer, db.ForeignKey('researcher.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='profile_claims')
    researcher = db.relationship('Researcher', backref='claims')

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
