# PSRA Flask Codebase Refactoring Plan

## ✅ REFACTORING COMPLETED

**Completion Date:** 2026-02-14

### Summary of Changes

All planned refactoring has been successfully implemented. The codebase has been reorganized with:
- **6 new utility modules** created in `utils/`
- **3 service layer modules** created in `services/`
- **Configuration module** created
- **~200+ lines of duplicate code eliminated**
- **2 empty directories removed**

---

## Executive Summary

This document outlines a comprehensive plan to reorganize the PSRA Flask codebase, reduce duplicate code, and improve maintainability. The codebase is a functional Flask application for a pharmaceutical research association with user authentication, forum, events, and messaging features.

---

## Current Architecture Analysis

### Project Structure Overview

```
psra-flask/
|-- app.py                 # Main app + routes + SocketIO handlers (292 lines)
|-- models.py              # Database models (95 lines)
|-- admin/
|   |-- __init__.py        # Blueprint registration
|   |-- routes.py          # Admin routes (300+ lines)
|-- forum/
|   |-- __init__.py        # Blueprint registration
|   |-- forms.py           # WTForms definitions (76 lines)
|   |-- routes.py          # Forum routes (549 lines)
|-- utils/
|   |-- email_utils.py     # Email utilities (181 lines)
|-- static/                # CSS, JS, images
|-- templates/             # Jinja2 templates
|-- instance/              # SQLite database
|-- migrations/            # Database migrations
```

### Identified Issues

#### 1. Duplicate Code Patterns

| Pattern | Location | Lines |
|---------|----------|-------|
| JSON parsing for education/experience | [`forum/routes.py:141-151`](forum/routes.py:141), [`forum/routes.py:187-204`](forum/routes.py:187), [`forum/routes.py:525-535`](forum/routes.py:525) | ~40 lines duplicated |
| Image upload/processing | [`forum/routes.py:235-292`](forum/routes.py:235) | ~60 lines, similar logic for cover/profile |
| Message query patterns | [`forum/routes.py:314-346`](forum/routes.py:314), [`forum/routes.py:402-405`](forum/routes.py:402), [`forum/routes.py:475-478`](forum/routes.py:475) | ~30 lines duplicated |
| Pagination pattern | [`admin/routes.py:45-62`](admin/routes.py:45), [`admin/routes.py:116-130`](admin/routes.py:116), [`forum/routes.py:490-510`](forum/routes.py:490) | ~30 lines duplicated |
| Event date/time parsing | [`admin/routes.py:209-210`](admin/routes.py:209), [`admin/routes.py:247-249`](admin/routes.py:247) | ~10 lines duplicated |
| Flash + redirect pattern | Throughout all route files | ~50+ instances |

#### 2. Organization Issues

- **[`app.py`](app.py)**: Contains mixed concerns - app initialization, routes, SocketIO handlers, and context processors
- **Empty directories**: `staticcss/` and `staticjs/` serve no purpose
- **Configuration**: Hardcoded values mixed with environment variables
- **No service layer**: Business logic embedded directly in route handlers

#### 3. Missing Abstractions

- No query helpers for common database operations
- No response helpers for API endpoints
- No decorator utilities module
- No constants/enums module

---

## Proposed Refactoring

### Phase 1: Create Utility Modules

#### 1.1 JSON Utilities Module

Create [`utils/json_utils.py`](utils/json_utils.py):

```python
def safe_json_parse(json_string, default=None):
    """Safely parse JSON string with fallback default."""
    if default is None:
        default = []
    if not json_string:
        return default
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def combine_timeline(experience_data, education_data):
    """Combine experience and education into sorted timeline."""
    combined = []
    for entry in experience_data:
        entry['type'] = 'work'
        combined.append(entry)
    for entry in education_data:
        entry['type'] = 'education'
        combined.append(entry)
    combined.sort(key=lambda x: x.get('start_date', ''), reverse=True)
    return combined
```

**Impact**: Reduces ~40 lines of duplicate code to 2 function calls.

#### 1.2 Image Processing Module

Create [`utils/image_utils.py`](utils/image_utils.py):

```python
from PIL import Image
from werkzeug.utils import secure_filename
import os

def process_profile_picture(file, user_id, upload_folder, app_root):
    """Process and save profile picture with resizing."""
    # ... consolidated logic

def process_cover_photo(file, user_id, upload_folder, app_root):
    """Process and save cover photo with resizing."""
    # ... consolidated logic

def process_event_image(file, app_root):
    """Process and save event image."""
    # ... consolidated logic
```

**Impact**: Reduces ~60 lines of duplicate image processing code.

#### 1.3 Query Helpers Module

Create [`utils/query_helpers.py`](utils/query_helpers.py):

```python
def get_conversation_messages(user_id, other_user_id):
    """Get all messages between two users."""
    return Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    )

def get_unread_count(user_id, from_user_id=None):
    """Get unread message count for user."""
    query = Message.query.filter_by(receiver_id=user_id, is_read=False)
    if from_user_id:
        query = query.filter_by(sender_id=from_user_id)
    return query.count()

def paginate_query(query, page, per_page=20):
    """Apply pagination to a query."""
    return query.paginate(page=page, per_page=per_page, error_out=False)
```

**Impact**: Reduces ~30 lines of duplicate query patterns.

---

### Phase 2: Reorganize Application Structure

#### 2.1 Extract Configuration

Create [`config.py`](config.py):

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///psra.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/profile_images'
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

#### 2.2 Create Application Factory

Refactor [`app.py`](app.py) into [`app/__init__.py`](app/__init__.py):

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    mail.init_app(app)
    
    # Register blueprints
    from app.main import main_bp
    from app.forum import forum_bp
    from app.admin import admin_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
```

#### 2.3 Create Main Blueprint

Create [`app/main/__init__.py`](app/main/__init__.py) and [`app/main/routes.py`](app/main/routes.py):

Move static page routes from [`app.py`](app.py):
- home()
- research()
- events()
- support()
- about()
- collaborate()
- contact()
- privacy()
- faq()

#### 2.4 Create API Blueprint

Create [`app/api/__init__.py`](app/api/__init__.py) and [`app/api/routes.py`](app/api/routes.py):

Move API routes:
- get_next_event()
- get_unread_count()

#### 2.5 Create SocketIO Module

Create [`app/socketio_handlers.py`](app/socketio_handlers.py):

Move all SocketIO event handlers from [`app.py`](app.py):
- handle_join()
- handle_send_message()
- handle_typing_start()
- handle_typing_stop()
- handle_mark_read()

---

### Phase 3: Create Service Layer

#### 3.1 Message Service

Create [`services/message_service.py`](services/message_service.py):

```python
class MessageService:
    @staticmethod
    def get_conversations(user_id):
        """Get all conversations for a user."""
        # ... extracted logic
    
    @staticmethod
    def send_message(sender_id, receiver_id, content):
        """Send a message and notify via SocketIO."""
        # ... extracted logic
    
    @staticmethod
    def mark_as_read(user_id, other_user_id):
        """Mark messages as read."""
        # ... extracted logic
```

#### 3.2 Event Service

Create [`services/event_service.py`](services/event_service.py):

```python
class EventService:
    @staticmethod
    def get_categorized_events():
        """Get events categorized by status (live, upcoming, archived)."""
        # ... extracted logic
    
    @staticmethod
    def archive_past_events():
        """Automatically archive past events."""
        # ... extracted logic
```

#### 3.3 User Service

Create [`services/user_service.py`](services/user_service.py):

```python
class UserService:
    @staticmethod
    def get_user_timeline(user):
        """Get combined experience/education timeline for user."""
        # ... extracted logic
    
    @staticmethod
    def update_profile(user, form_data, files=None):
        """Update user profile with form data and files."""
        # ... extracted logic
```

---

### Phase 4: Clean Up and Optimize

#### 4.1 Remove Empty Directories

- Delete `staticcss/`
- Delete `staticjs/`

#### 4.2 Create Constants Module

Create [`utils/constants.py`](utils/constants.py):

```python
# User status options
USER_STATUS_STUDENT = 'student'
USER_STATUS_ALUMNI = 'alumni'
USER_STATUS_UNDERGRADUATE = 'undergraduate'
USER_STATUSES = [USER_STATUS_STUDENT, USER_STATUS_ALUMNI, USER_STATUS_UNDERGRADUATE]

# Post categories
POST_CATEGORIES = [
    ('Pharmacology', 'Pharmacology'),
    ('Clinical Pharmacy', 'Clinical Pharmacy'),
    ('Research Skills', 'Research Skills')
]

# Pagination defaults
DEFAULT_PER_PAGE = 20
```

#### 4.3 Create Decorators Module

Create [`utils/decorators.py`](utils/decorators.py):

```python
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
```

---

## Proposed New Directory Structure

```
psra-flask/
|-- config.py                    # Configuration classes
|-- run.py                       # Application entry point
|-- app/
|   |-- __init__.py              # Application factory
|   |-- models.py                # Database models (moved from root)
|   |-- main/
|   |   |-- __init__.py          # Main blueprint
|   |   |-- routes.py            # Static page routes
|   |-- forum/
|   |   |-- __init__.py          # Forum blueprint
|   |   |-- routes.py            # Forum routes (simplified)
|   |   |-- forms.py             # Forum forms
|   |-- admin/
|   |   |-- __init__.py          # Admin blueprint
|   |   |-- routes.py            # Admin routes (simplified)
|   |-- api/
|   |   |-- __init__.py          # API blueprint
|   |   |-- routes.py            # API endpoints
|   |-- socketio_handlers.py     # SocketIO event handlers
|-- services/
|   |-- __init__.py
|   |-- message_service.py       # Message business logic
|   |-- event_service.py         # Event business logic
|   |-- user_service.py          # User business logic
|-- utils/
|   |-- __init__.py
|   |-- constants.py             # Application constants
|   |-- decorators.py            # Custom decorators
|   |-- email_utils.py           # Email utilities (existing)
|   |-- image_utils.py           # Image processing utilities
|   |-- json_utils.py            # JSON parsing utilities
|   |-- query_helpers.py         # Database query helpers
|-- static/                      # Static files
|-- templates/                   # Jinja2 templates
|-- instance/                    # SQLite database
|-- migrations/                  # Database migrations
```

---

## Implementation Order

1. **Phase 1**: Create utility modules (low risk, high impact)
   - json_utils.py
   - image_utils.py
   - query_helpers.py
   - constants.py
   - decorators.py

2. **Phase 2**: Create service layer (medium risk, high impact)
   - message_service.py
   - event_service.py
   - user_service.py

3. **Phase 3**: Reorganize application structure (higher risk, high impact)
   - config.py
   - Application factory
   - Main blueprint
   - API blueprint
   - SocketIO handlers module

4. **Phase 4**: Clean up (low risk)
   - Remove empty directories
   - Update imports across all files

---

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|--------------|
| Duplicate code lines | ~200+ | ~20 | 90% reduction |
| Files in root | 8 | 2 | 75% reduction |
| Lines in app.py | 292 | 0 (moved) | Complete reorganization |
| Service layer | None | 3 services | Better separation of concerns |
| Configuration | Hardcoded | Class-based | More maintainable |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Implement in phases, test after each phase |
| Import errors during migration | Update all imports systematically |
| Database migration issues | No model changes, only code reorganization |
| SocketIO connection issues | Test real-time features after migration |

---

## Testing Recommendations

1. Create automated tests before refactoring
2. Test each phase independently
3. Verify all routes still work after migration
4. Test SocketIO real-time messaging
5. Verify database operations

---

## Conclusion

This refactoring plan will significantly improve code organization, reduce duplicate code by approximately 90%, and make the codebase more maintainable and scalable. The phased approach minimizes risk while maximizing impact.