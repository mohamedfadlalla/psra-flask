# PSRA Platform Schema & Feature Architecture Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Safely implement the new normalized PostgreSQL schema, migrate data from the existing monolithic `User` model, and establish the new structural foundation (Profiles, Departments, Skills) without breaking existing functionality.

**Architecture:** We will implement this in distinct phases. Phase 1 focuses *strictly* on schema definition in SQLAlchemy (`models.py`) and Alembic data migration. Later phases will wire up the Flask application logic to use the new models. The approach is additive first (create new tables, sync data) before removing old fields (to prevent downtime).

**Tech Stack:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), PostgreSQL (via psycopg2).

---

### Task 1: Add Base Models (Departments, Skills, User Roles)

**Files:**
- Modify: `models.py`

**Step 1: Define new SQLAlchemy models in `models.py`**
We need to add the new Enums and core lookup tables. We will add these near the top of the file, after imports.

```python
# In models.py (add these below imports, before User model)
import enum
from datetime import datetime

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
```

**Step 2: Add relationship to `User` model**
Update the `User` model in `models.py` to include the relationship. Also add the `role` enum.
```python
    # In User model
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # New relationships
    user_skills = db.relationship('UserSkill', back_populates='user', cascade='all, delete-orphan')
    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    alumni_profile = db.relationship('AlumniProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    researcher_profile = db.relationship('ResearcherProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
```

---

### Task 2: Add Profile Models

**Files:**
- Modify: `models.py`

**Step 1: Define Profile, StudentProfile, AlumniProfile, ResearcherProfile in `models.py`**
Add these after the `User` model definition.

```python
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
```

---

### Task 3: Generate Initial Schema Migration

**Files:**
- Run commands in terminal

**Step 1: Generate Alembic migration script**
Run: `flask db migrate -m "Add core schema and profiles"`

**Step 2: Inspect migration script**
Review the generated file in `migrations/versions/` to ensure it correctly creates `UserRole` enum (might require manual adjustment in alembic if using sqlite vs postgres, but assume standard for now), creates `departments`, `skills`, `user_skills`, `profiles`, `student_profiles`, `alumni_profiles`, `researcher_profiles`.

**Step 3: Apply Migration**
Run: `flask db upgrade`

---

### Task 4: Write Data Migration Script (Populate New Tables)

**Files:**
- Create: `scripts/migrate_user_data.py`

**Step 1: Create script to move data from `User` to `Profile` and `UserSkill`**
```python
# scripts/migrate_user_data.py
import sys
import os
import json

# Add the project directory to sys.path so we can import app and models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Profile, Skill, UserSkill, UserRole, StudentProfile, AlumniProfile

def migrate_data():
    with app.app_context():
        users = User.query.all()
        print(f"Migrating {len(users)} users...")
        
        for user in users:
            # 1. Map Role
            if user.is_admin:
                user.role = UserRole.ADMIN
            elif user.status == 'alumni':
                user.role = UserRole.ALUMNI
            else:
                user.role = UserRole.STUDENT # Default for 'student' or 'undergraduate'
                
            # 2. Create Profile
            if not user.profile:
                profile = Profile(
                    user_id=user.id,
                    full_name=user.name,
                    bio=user.about,
                    profile_picture_url=user.profile_picture_url
                )
                db.session.add(profile)
            
            # 3. Create Specific Profiles based on Role/Status
            if user.role == UserRole.ALUMNI and not user.alumni_profile:
                alumni_prof = AlumniProfile(
                    user_id=user.id,
                    job_title=user.headline
                )
                db.session.add(alumni_prof)
            elif user.role == UserRole.STUDENT and not user.student_profile:
                student_prof = StudentProfile(
                    user_id=user.id
                )
                db.session.add(student_prof)

            # 4. Migrate Skills (from comma-separated string)
            if user.skills:
                skill_names = [s.strip() for s in user.skills.split(',') if s.strip()]
                for s_name in skill_names:
                    # Find or create skill
                    skill = Skill.query.filter_by(name=s_name).first()
                    if not skill:
                        skill = Skill(name=s_name)
                        db.session.add(skill)
                        db.session.flush() # get id
                    
                    # Create UserSkill link if not exists
                    if not UserSkill.query.filter_by(user_id=user.id, skill_id=skill.id).first():
                        user_skill = UserSkill(user_id=user.id, skill_id=skill.id)
                        db.session.add(user_skill)
            
        try:
            db.session.commit()
            print("Migration completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_data()
```

**Step 2: Execute data migration script**
Run: `python scripts/migrate_user_data.py`

---

### Task 5: Add Research & Mentorship Models

**Files:**
- Modify: `models.py`

**Step 1: Define Mentorship Models**
Add below existing models:
```python
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
```

**Step 2: Define Research Recruitment Models**
```python
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
```

---

### Task 6: Add Job Board Models

**Files:**
- Modify: `models.py`

**Step 1: Define Job Models**
```python
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
```

**Step 2: Generate Migration for Modules**
Run: `flask db migrate -m "Add Mentorship, Research Recruitment, and Job Board models"`
Run: `flask db upgrade`

---

### Task 7: Scalable Messaging Schema

**Files:**
- Modify: `models.py`

**Step 1: Add Conversation Models**
*Note: We maintain the old `Message` model temporarily to ensure we don't break existing chat, but we wire it up to the new structure.*
```python
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
```

**Step 2: Modify existing `Message` model**
We need to add `conversation_id` to the existing `Message` table.
```python
    # Add to existing Message class in models.py
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
```

**Step 3: Generate Migration for Messaging**
Run: `flask db migrate -m "Add Conversation models for scalable messaging"`
Run: `flask db upgrade`

**Step 4: Message Data Migration Script (Optional for now, but good practice)**
We can write a script to map existing 1-to-1 messages to a Conversation, but to keep this phase focused and safe, we'll stop at schema creation. The app logic refactoring (Phase 2 & 3) will handle switching over.

---
**End of Phase 1 Plan**
