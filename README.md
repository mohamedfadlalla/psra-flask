# PSRA (Pharmaceutical Studies and Research Association) Website

A comprehensive web platform for the Pharmaceutical Studies and Research Association, built with Flask and featuring a minimalist, professional design with a strict black, white, and grayscale color palette.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
  - [Implemented Features](#implemented-features)
  - [Coming Soon Features](#coming-soon-features)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [File Logic & Architecture](#file-logic--architecture)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

The PSRA website serves as the official online platform for students, researchers, and potential partners in pharmaceutical sciences. The platform provides a professional space for academic collaboration, research discussion, and community engagement with a focus on pharmaceutical education and innovation.

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
- **Home Page**: Hero section with background image, vision/mission, goals grid, associated logos
- **About Us**: Organization information and team member profiles with circular avatars
- **Collaborate**: Partnership opportunities and Google Forms integration
- **Contact**: Contact form and location information with embedded Google Maps
- **Placeholder Pages**: Research, Events, Support & Donations, Privacy Policy, FAQ

#### 👥 User Authentication
- **Registration**: Email/password with terms acceptance and validation
- **Login/Logout**: Secure session management with Flask-Login
- **Password Security**: Werkzeug password hashing
- **Form Validation**: WTForms with CSRF protection

#### 💬 Forum System
- **Discussion Categories**: Pharmacology, Clinical Pharmacy, Research Skills
- **Post Creation**: Rich text posts with category selection
- **Comment System**: Threaded discussions with user attribution
- **Like Functionality**: AJAX-powered post liking with real-time count updates
- **Search & Filter**: Dynamic filtering by category and keyword search
- **User Profiles**: Avatar display and post/comment history

#### 🔧 Technical Features
- **AJAX Interactions**: Dynamic likes and filtering without page reloads
- **Debounced Search**: Optimized search input with 300ms debounce
- **RESTful API**: JSON endpoints for dynamic content updates
- **Blueprint Architecture**: Modular forum routing
- **Database Relationships**: Proper ORM relationships with SQLAlchemy

### Coming Soon Features

#### 📊 Advanced Analytics
- **User Activity Tracking**: Post views, engagement metrics
- **Forum Statistics**: Most active users, popular topics
- **Content Analytics**: Reading time, interaction rates

#### 🔔 Notifications
- **Email Notifications**: New replies, mentions, forum updates
- **In-App Notifications**: Real-time activity feeds
- **Push Notifications**: Browser-based notifications

#### 👤 User Profiles
- **Profile Customization**: Avatar upload, bio, social links
- **Activity History**: Personal post/comment timeline
- **Reputation System**: Points for contributions and engagement

#### 🔍 Advanced Search
- **Full-Text Search**: Elasticsearch integration
- **Advanced Filters**: Date ranges, user filters, content types
- **Saved Searches**: Personalized search preferences

#### 📱 Mobile App
- **Progressive Web App**: Installable mobile experience
- **Offline Support**: Cached content for offline reading
- **Push Notifications**: Mobile-optimized notifications

#### 🤝 Collaboration Tools
- **Document Sharing**: File upload and version control
- **Project Management**: Task boards and milestone tracking
- **Video Conferencing**: Integrated meeting tools

#### 🌐 Internationalization
- **Multi-language Support**: Arabic/English localization
- **RTL Support**: Right-to-left layout for Arabic content
- **Cultural Adaptation**: Region-specific content and features

## 🛠 Technology Stack

### Backend
- **Flask 3.0**: Lightweight WSGI web framework
- **SQLAlchemy 2.0**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Werkzeug**: Password hashing and utilities

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom properties, grid/flexbox layouts
- **Vanilla JavaScript**: DOM manipulation and AJAX
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
- **Storage**: 100MB free space
- **Operating System**: Windows, macOS, or Linux

### Python Dependencies
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
Flask-Login==0.6.3
Werkzeug==3.1.3
WTForms==3.1.2
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
1. **Browse Public Content**: Visit the home page to explore PSRA information
2. **Register Account**: Create an account to access the forum
3. **Join Discussions**: Login to participate in forum discussions
4. **Create Posts**: Start new discussions in appropriate categories
5. **Interact**: Like posts and leave comments

### For Developers
1. **Local Development**: Follow installation steps above
2. **Database Management**: Use Flask shell for database operations
3. **Testing**: Run the app and test all features manually
4. **Customization**: Modify templates, styles, and routes as needed

## 📁 Project Structure

```
psra-website/
├── app.py                      # Main Flask application
├── models.py                   # Database models and schemas
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── instance/
│   └── psra.db                # SQLite database file
├── forum/                      # Forum blueprint
│   ├── __init__.py           # Blueprint initialization
│   ├── forms.py              # WTForms definitions
│   └── routes.py             # Forum routes and logic
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── js/
│   │   └── script.js         # Client-side JavaScript
│   └── images/               # Image assets
│       ├── logo.png
│       ├── image1.jpg
│       ├── image2.jpg
│       └── [team-photos]/
└── templates/                  # Jinja2 templates
    ├── base.html             # Base template with header/footer
    ├── home.html             # Home page
    ├── about.html            # About us page
    ├── collaborate.html      # Collaboration page
    ├── contact.html          # Contact page
    ├── placeholder.html      # Generic placeholder template
    ├── login.html            # Login form
    ├── register.html         # Registration form
    ├── forum_terms.html      # Terms and conditions
    ├── forum_main.html       # Forum main page
    ├── create_post.html      # Create post form
    └── post_detail.html      # Individual post view
```

## 🗄 Database Schema

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    profile_picture_url VARCHAR(200),
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

## 🔗 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /about` - About us page
- `GET /collaborate` - Collaboration page
- `GET /contact` - Contact page
- `GET /research` - Research placeholder
- `GET /events` - Events placeholder
- `GET /support` - Support placeholder
- `GET /privacy` - Privacy policy placeholder
- `GET /faq` - FAQ placeholder

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
- `POST /forum/post/<id>/like` - Toggle like on post

## 🧠 File Logic & Architecture

### app.py - Main Application
**Purpose**: Entry point and configuration of the Flask application
**Key Components**:
- Flask app initialization with secret key and database URI
- SQLAlchemy and LoginManager setup
- Blueprint registration for forum functionality
- Route definitions for static pages
- Database initialization on first run

**Architecture**: Follows Flask application factory pattern with blueprint modularity

### models.py - Database Models
**Purpose**: Define database schema and relationships using SQLAlchemy ORM
**Key Classes**:
- `User`: Authentication model with Flask-Login integration
- `Post`: Forum posts with user relationships
- `Comment`: Post comments with threading support
- `Like`: Many-to-many like relationships

**Logic**: Implements password hashing, relationship backrefs, and unique constraints

### forum/__init__.py - Blueprint Setup
**Purpose**: Initialize the forum blueprint with proper template/static paths
**Architecture**: Modular routing separation for maintainability

### forum/forms.py - Form Definitions
**Purpose**: WTForms classes for data validation and CSRF protection
**Key Forms**:
- `LoginForm`: Email/password authentication
- `RegisterForm`: User registration with validation
- `PostForm`: Post creation with category selection
- `CommentForm`: Comment submission

**Logic**: Custom validators for email uniqueness and password confirmation

### forum/routes.py - Forum Logic
**Purpose**: Handle all forum-related HTTP requests and business logic
**Key Functions**:
- Authentication routes with session management
- CRUD operations for posts and comments
- AJAX endpoints for dynamic interactions
- Search and filtering logic

**Architecture**: Blueprint-based routing with proper error handling

### templates/base.html - Layout Template
**Purpose**: Common HTML structure with header, navigation, and footer
**Features**:
- Responsive navigation with active page highlighting
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

### static/js/script.js - Client-Side Logic
**Purpose**: Dynamic interactions without page reloads
**Key Functions**:
- `toggleLike()`: AJAX like toggling with count updates
- `filterPosts()`: Dynamic post filtering and search
- `debounce()`: Input optimization for search performance

**Architecture**: Event-driven JavaScript with fetch API for AJAX

### Template Files
**Purpose**: Jinja2 templates for server-side rendering
**Structure**: Each page extends base.html with specific content blocks
**Features**: Form rendering, flash message display, dynamic content loops

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Pharmaceutical Studies and Research Association (PSRA)**  
*Advancing pharmaceutical education and research through digital collaboration*
