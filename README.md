# PSRA (Pharmaceutical Studies and Research Association) Website

A comprehensive web platform for the Pharmaceutical Studies and Research Association, built with Flask and featuring a minimalist, professional design with a strict black, white, and grayscale color palette.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
  - [Implemented Features](#implemented-features)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Page Summaries](#page-summaries)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [File Logic & Architecture](#file-logic--architecture)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

The PSRA website serves as the official online platform for students, researchers, and potential partners in pharmaceutical sciences. The platform provides a professional space for academic collaboration, research discussion, event management, and community engagement with a focus on pharmaceutical education and innovation.

### Design Philosophy
- **Minimalist & Professional**: Clean, uncluttered design with generous whitespace
- **Academic Aesthetic**: Strict black, white, and grayscale color palette
- **Responsive**: Fully functional on desktop, tablet, and mobile devices
- **Accessibility**: Semantic HTML and proper contrast ratios

## ✨ Features

### Implemented Features

#### 🎨 Design & UI
- **Grayscale Image Processing**: All images automatically desaturated using CSS `filter: grayscale(100%)`
- **Responsive Grid Layout**: Consistent alignment and spacing across all pages
- **Professional Typography**: Clean sans-serif fonts (Arial/Open Sans)
- **Mobile-First Design**: Collapsible navigation and stacked layouts for mobile

#### 🏠 Static Pages
- **Home Page**: Hero section with background image, vision/mission, goals grid, upcoming event countdown, recent forum comments, associated organizations
- **About Us**: Organization information, mission statement, and team member profiles with circular avatars
- **Events Page**: Live, upcoming, and archived events with detailed information, presenters, images, and registration links
- **Collaborate**: Partnership opportunities and Google Forms integration
- **Contact**: Contact form and location information with embedded Google Maps

#### 👥 User Authentication & Profiles
- **Registration**: Email/password with terms acceptance, phone/WhatsApp numbers, member status
- **Login/Logout**: Secure session management with Flask-Login
- **Password Security**: Werkzeug password hashing
- **Form Validation**: WTForms with CSRF protection
- **User Profiles**: Comprehensive profiles with cover photos, professional summaries, skills, education, experience, publications, social links
- **Profile Editing**: Extensive profile customization with image upload

#### 💬 Forum System
- **Discussion Categories**: Pharmacology, Clinical Pharmacy, Research Skills
- **Post Creation**: Rich text posts with category selection
- **Comment System**: Threaded discussions with user attribution
- **Like Functionality**: AJAX-powered post liking with real-time count updates
- **Search & Filter**: Dynamic filtering by category and keyword search with debounced input
- **User Profiles**: Avatar display and post/comment history

#### 📅 Event Management
- **Event Creation**: Admin panel for creating events with dates, times, presenters, descriptions, images
- **Event Status**: Automatic categorization into live, upcoming, and archived events
- **Event Details**: Comprehensive event information with registration links
- **Event Archiving**: Automatic archiving of past events

#### 🔧 Admin Panel
- **Dashboard**: Statistics overview (users, posts, comments, events)
- **Content Moderation**: Edit and delete posts and comments
- **Event Management**: Full CRUD operations for events
- **User Management**: Admin role assignment and oversight

#### ✉️ Messaging System
- **Private Messaging**: Direct messaging between users
- **Conversation Threads**: Organized message history
- **Unread Indicators**: Notification of new messages
- **Message Search**: Send messages by username or email

#### 🔗 Technical Features
- **AJAX Interactions**: Dynamic likes, filtering, and real-time updates without page reloads
- **Debounced Search**: Optimized search input with 300ms debounce
- **RESTful API**: JSON endpoints for dynamic content updates
- **Blueprint Architecture**: Modular routing for forum, admin, and main app
- **Database Relationships**: Proper ORM relationships with SQLAlchemy
- **File Upload**: Secure image upload for profiles and events with PIL processing
- **Image Processing**: Automatic resizing and optimization of uploaded images

## 🛠 Technology Stack

### Backend
- **Flask 3.0**: Lightweight WSGI web framework
- **SQLAlchemy 2.0**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Migrate**: Database migration management
- **Werkzeug**: Password hashing and utilities
- **Pillow (PIL)**: Image processing for uploads

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom properties, grid/flexbox layouts
- **Vanilla JavaScript**: DOM manipulation and AJAX with Fetch API
- **Jinja2**: Template engine

### Database
- **SQLite**: File-based database for development
- **SQLAlchemy ORM**: Database abstraction layer

### Development Tools
- **Python 3.8+**: Programming language
- **pip**: Package management
- **Git**: Version control

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 200MB free space
- **Operating System**: Windows, macOS, or Linux

### Python Dependencies
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
Flask-Login==0.6.3
Flask-Migrate==4.0.5
Werkzeug==3.1.3
WTForms==3.1.2
Pillow==10.1.0
```

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd psra-website
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python -c "from app import app; app.app_context().push(); from models import db; db.create_all()"
```

### 5. Seed Sample Data (Optional)
```python
from app import app
app.app_context().push()
from models import db, User, Post

# Create admin user
admin = User(name='Admin User', email='admin@example.com', is_admin=True)
admin.set_password('adminpass')
db.session.add(admin)

# Create sample user
user = User(name='Test User', email='test@example.com')
user.set_password('password')
db.session.add(user)
db.session.commit()

# Create sample post
post = Post(user_id=user.id, category='Pharmacology', title='Welcome', content='Sample content')
db.session.add(post)
db.session.commit()
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`

## 📖 Usage

### For Users
1. **Browse Public Content**: Visit the home page to explore PSRA information and upcoming events
2. **Register Account**: Create an account to access the forum and messaging features
3. **Join Discussions**: Login to participate in forum discussions and create posts
4. **Customize Profile**: Build a comprehensive professional profile with photos and details
5. **Network**: Send private messages to other users and build connections
6. **Stay Updated**: View live and upcoming events with registration links

### For Administrators
1. **Access Admin Panel**: Login with admin credentials to access `/admin/`
2. **Manage Content**: Moderate posts and comments through the admin interface
3. **Create Events**: Add new events with full details and images
4. **Monitor Activity**: View statistics and recent activity on the dashboard

### For Developers
1. **Local Development**: Follow installation steps above
2. **Database Management**: Use Flask shell for database operations
3. **Testing**: Run the app and test all features manually
4. **Customization**: Modify templates, styles, and routes as needed

## 📄 Page Summaries

### Home Page (`/`)
- **Hero Section**: Background image with call-to-action buttons for joining and learning more
- **Vision/Mission**: Text describing PSRA's goals and objectives
- **Goals Grid**: Three-card layout highlighting research advancement, collaboration, and education
- **Upcoming Event Countdown**: Live countdown timer for next event with details
- **Recent Forum Comments**: Latest discussion activity with user avatars and links
- **Associated Organizations**: Logos and links to partner institutions (UofK Faculty of Pharmacy, FPSA, PharmaRx)

### About Us Page (`/about`)
- **Organization Overview**: Description of PSRA as a student-led organization at University of Khartoum
- **Mission Statement**: Focus on bridging academic learning with real-world pharmaceutical applications
- **Team Members**: Grid of team member cards with photos, names, and roles
- **Affiliations**: Connection to Faculty of Pharmacy Students' Association (FPSA)

### Events Page (`/events`)
- **Live Events Section**: Currently happening events with green status badges and join links
- **Upcoming Events Section**: Future events with orange status badges and registration links
- **Archived Events Section**: Past events with gray status badges and view details links
- **Event Details**: Each event shows date/time, presenter, description, image, and action buttons
- **Automatic Status Updates**: Events automatically move between sections based on current time

### Forum Main Page (`/forum/`)
- **Sidebar Filters**: Search input and category dropdown (Pharmacology, Clinical Pharmacy, Research Skills)
- **Posts List**: Cards showing author avatar, title, content preview, like/comment counts
- **Create Post Button**: Link to post creation form (authenticated users only)
- **AJAX Filtering**: Real-time post filtering without page reload

### Post Detail Page (`/forum/post/<id>`)
- **Post Header**: Author info, title, full content, creation date
- **Comments Section**: Threaded comments with user avatars and timestamps
- **Like Button**: AJAX-powered like toggle with count updates
- **Add Comment Form**: Form for authenticated users to add comments

### Create Post Page (`/forum/create`)
- **Post Form**: Title, category selection, content textarea
- **Validation**: Required fields with WTForms validation
- **Redirect**: After creation, redirects to post detail page

### User Profile Page (`/forum/profile`)
- **Cover Photo**: Large header image (uploaded or default gradient)
- **Profile Info**: Name, headline, location
- **About Section**: Personal description
- **Professional Summary**: Career overview
- **Basic Information**: Contact details, status, batch number, membership
- **Professional Details**: Skills, education, experience
- **Additional Info**: Languages, certifications, projects, publications
- **Social Links**: LinkedIn, GitHub, personal website links

### Edit Profile Page (`/forum/profile/edit`)
- **Dual Forms**: Profile information and password change
- **Image Upload**: Cover photo upload with PIL processing and resizing
- **Extensive Fields**: All profile fields with pre-populated values
- **Validation**: Email uniqueness, password confirmation

### Messages Inbox (`/forum/messages`)
- **Conversations List**: Recent conversations with latest message preview
- **Unread Indicators**: Red badges showing unread message counts
- **User Search**: Send messages by username or email

### Conversation View (`/forum/messages/conversation/<user_id>`)
- **Message Thread**: Chronological message history between two users
- **Reply Form**: Quick reply input at bottom of conversation
- **Read Status**: Automatic marking of received messages as read

### Admin Dashboard (`/admin/`)
- **Statistics Cards**: Total users, posts, comments, events
- **Recent Activity**: Latest posts and comments with moderation links
- **Quick Actions**: Links to management sections

### Admin Posts Management (`/admin/posts`)
- **Posts Table**: Paginated list with search and category filters
- **Actions**: Edit and delete buttons for each post
- **Bulk Operations**: Filter by author and category

### Admin Comments Management (`/admin/comments`)
- **Comments Table**: Paginated list with search and author filters
- **Moderation**: Edit and delete comment content

### Admin Events Management (`/admin/events`)
- **Events List**: All events with status indicators
- **CRUD Operations**: Create, edit, delete events with image upload

### Authentication Pages
- **Login/Register**: Clean forms with validation feedback
- **Terms Page**: Forum terms and conditions
- **Password Security**: Secure password requirements

## 📁 Project Structure

```
psra-website/
├── app.py                      # Main Flask application with routes
├── models.py                   # Database models (User, Post, Comment, Like, Event, Message)
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── create_admin.py             # Script to create admin user
├── details.md                  # Additional project details
├── instance/
│   └── psra.db                # SQLite database file
├── migrations/                 # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── forum/                      # Forum blueprint
│   ├── __init__.py           # Blueprint initialization
│   ├── forms.py              # WTForms definitions
│   └── routes.py             # Forum routes and logic
├── admin/                      # Admin blueprint
│   ├── __init__.py           # Blueprint initialization
│   └── routes.py             # Admin routes and logic
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css         # Main stylesheet with design system
│   ├── js/
│   │   └── script.js         # Client-side JavaScript
│   └── images/               # Image assets
│       ├── logo.png
│       ├── image1.jpg
│       ├── image2.jpg
│       ├── [team-photos]/
│       ├── [event-images]/
│       └── [profile-images]/
├── templates/                  # Jinja2 templates
│   ├── base.html             # Base template with header/footer
│   ├── home.html             # Home page
│   ├── about.html            # About us page
│   ├── collaborate.html      # Collaboration page
│   ├── contact.html          # Contact page
│   ├── events.html           # Events listing page
│   ├── placeholder.html      # Generic placeholder template
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   ├── forum_terms.html      # Terms and conditions
│   ├── forum_main.html       # Forum main page
│   ├── create_post.html      # Create post form
│   ├── post_detail.html      # Individual post view
│   ├── profile.html          # User profile display
│   ├── edit_profile.html     # Profile editing form
│   ├── messages.html         # Messages inbox
│   ├── send_message.html     # Send message form
│   ├── conversation.html     # Message conversation view
│   └── admin/                # Admin templates
│       ├── base.html         # Admin base template
│       ├── dashboard.html    # Admin dashboard
│       ├── posts.html        # Posts management
│       ├── edit_post.html    # Edit post form
│       ├── comments.html     # Comments management
│       ├── edit_comment.html # Edit comment form
│       ├── events.html       # Events management
│       ├── create_event.html # Create event form
│       └── edit_event.html   # Edit event form
```

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    batch_number INTEGER,
    phone_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    is_member BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'student',
    headline VARCHAR(200),
    location VARCHAR(100),
    about TEXT,
    skills TEXT,
    education TEXT,
    experience TEXT,
    linkedin_url VARCHAR(200),
    github_url VARCHAR(200),
    website_url VARCHAR(200),
    cover_photo_url VARCHAR(200),
    languages TEXT,
    certifications TEXT,
    projects TEXT,
    publications TEXT,
    professional_summary TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Table
```sql
CREATE TABLE post (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Comments Table
```sql
CREATE TABLE comment (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Likes Table
```sql
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);
```

### Events Table
```sql
CREATE TABLE event (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time TIME,
    image_url VARCHAR(200),
    presenter VARCHAR(200),
    event_url VARCHAR(500),
    is_archived BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user (id)
);
```

### Messages Table
```sql
CREATE TABLE message (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user (id),
    FOREIGN KEY (receiver_id) REFERENCES user (id)
);
```

## 🔗 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /about` - About us page
- `GET /collaborate` - Collaboration page
- `GET /contact` - Contact page
- `GET /events` - Events listing page
- `GET /research` - Research placeholder
- `GET /support` - Support placeholder
- `GET /privacy` - Privacy policy placeholder
- `GET /faq` - FAQ placeholder
- `GET /api/next-event` - Next upcoming event data (JSON)

### Authentication Endpoints
- `GET/POST /forum/login` - User login
- `GET/POST /forum/register` - User registration
- `POST /forum/logout` - User logout
- `GET /forum/terms` - Terms and conditions

### Forum Endpoints
- `GET /forum/` - Forum main page (authenticated)
- `GET /forum/?category=X&search=Y` - Filtered forum posts
- `GET/POST /forum/create` - Create new post
- `GET /forum/post/<id>` - View individual post
- `POST /forum/post/<id>/comment` - Add comment to post
- `POST /forum/post/<id>/like` - Toggle like on post (AJAX)
- `GET /forum/profile` - User profile page
- `GET/POST /forum/profile/edit` - Edit profile
- `GET /forum/messages` - Messages inbox
- `GET/POST /forum/messages/send/<user_id>` - Send message to user
- `GET/POST /forum/messages/send` - Send message by username
- `GET /forum/messages/conversation/<user_id>` - View conversation
- `POST /forum/messages/reply/<user_id>` - Reply to conversation

### Admin Endpoints (Admin Only)
- `GET /admin/` - Admin dashboard
- `GET /admin/posts` - Posts management
- `GET/POST /admin/posts/<id>/edit` - Edit post
- `POST /admin/posts/<id>/delete` - Delete post
- `GET /admin/comments` - Comments management
- `GET/POST /admin/comments/<id>/edit` - Edit comment
- `POST /admin/comments/<id>/delete` - Delete comment
- `GET /admin/events` - Events management
- `GET/POST /admin/events/create` - Create event
- `GET/POST /admin/events/<id>/edit` - Edit event
- `POST /admin/events/<id>/delete` - Delete event
- `GET /admin/api/events` - Events data (JSON)

## 🧠 File Logic & Architecture

### app.py - Main Application
**Purpose**: Entry point and configuration of the Flask application
**Key Components**:
- Flask app initialization with secret key and database URI
- SQLAlchemy, LoginManager, and Migrate setup
- Blueprint registration for forum and admin functionality
- Route definitions for static pages (home, about, events, etc.)
- Database initialization and event archiving logic
- API endpoint for next event data

**Architecture**: Follows Flask application factory pattern with blueprint modularity

### models.py - Database Models
**Purpose**: Define database schema and relationships using SQLAlchemy ORM
**Key Classes**:
- `User`: Comprehensive user model with authentication, profile fields, and admin status
- `Post`: Forum posts with user relationships and categories
- `Comment`: Post comments with threading support
- `Like`: Many-to-many like relationships with unique constraints
- `Event`: Event management with date/time, presenter, and archiving
- `Message`: Private messaging between users with read status

**Logic**: Implements password hashing, relationship backrefs, and data validation

### forum/__init__.py & routes.py - Forum Blueprint
**Purpose**: Handle all forum-related HTTP requests and business logic
**Key Functions**:
- Authentication routes with session management and form validation
- CRUD operations for posts, comments, and likes
- User profile management with image upload and processing
- Private messaging system with conversation threading
- AJAX endpoints for dynamic interactions (likes, filtering)

**Architecture**: Blueprint-based routing with proper error handling and redirects

### admin/__init__.py & routes.py - Admin Blueprint
**Purpose**: Administrative interface for content management
**Key Functions**:
- Dashboard with statistics and recent activity
- Content moderation (posts and comments)
- Event management with image upload
- Access control with admin-only decorators

**Architecture**: Protected routes with role-based access control

### forum/forms.py - Form Definitions
**Purpose**: WTForms classes for data validation and CSRF protection
**Key Forms**:
- `LoginForm`: Email/password authentication
- `RegisterForm`: User registration with member status and contact info
- `PostForm`: Post creation with category selection
- `CommentForm`: Comment submission
- `ProfileForm`: Extensive profile editing with file uploads
- `PasswordChangeForm`: Secure password updates
- `MessageForm`: Private message composition

**Logic**: Custom validators for email uniqueness and password confirmation

### templates/base.html - Layout Template
**Purpose**: Common HTML structure with header, navigation, and footer
**Features**:
- Responsive navigation with active page highlighting
- User authentication status and profile links
- Social media links (placeholders)
- Footer with organized link sections
- Template inheritance support

### static/css/style.css - Styling
**Purpose**: Comprehensive CSS with design system and responsive layouts
**Key Features**:
- CSS custom properties for consistent theming
- Grid and flexbox layouts for responsiveness
- Image grayscale filtering
- Mobile-first media queries
- Utility classes for common patterns
- Card-based design system
- Professional color palette

### static/js/script.js - Client-Side Logic
**Purpose**: Dynamic interactions without page reloads
**Key Functions**:
- `toggleLike()`: AJAX like toggling with count updates
- `filterPosts()`: Dynamic post filtering and search
- `debounce()`: Input optimization for search performance
- Event countdown timers
- Form validation helpers

**Architecture**: Event-driven JavaScript with fetch API for AJAX

### Template Files
**Purpose**: Jinja2 templates for server-side rendering
**Structure**: Each page extends base.html with specific content blocks
**Features**: Form rendering, flash message display, dynamic content loops, conditional rendering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Use meaningful commit messages
- Test all new features thoroughly
- Update documentation for API changes
- Maintain responsive design principles
- Ensure database migrations for schema changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Pharmaceutical Studies and Research Association (PSRA)**  
*Advancing pharmaceutical education and research through digital collaboration*
