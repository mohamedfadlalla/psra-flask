# PSRA (Pharmaceutical Studies and Research Association) Website

A comprehensive web platform for the Pharmaceutical Studies and Research Association, built with Flask and featuring a minimalist, professional design with a strict black, white, and grayscale color palette.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features & Roles](#features--roles)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Database Schema](#database-schema)
- [Website Templates](#website-templates)
- [CLI Commands](#cli-commands)
- [License](#license)

## 🎯 Project Overview

The PSRA website serves as the official online platform for students, researchers, and potential partners in pharmaceutical sciences. The platform provides a professional space for academic collaboration, research discussion, event management, and community engagement with a focus on pharmaceutical education and innovation.

### Design Philosophy
- **Minimalist & Professional**: Clean, uncluttered design with generous whitespace.
- **Academic Aesthetic**: Strict black, white, and grayscale color palette.
- **Responsive**: Fully functional on desktop, tablet, and mobile devices.

## ✨ Features & Roles

### 🌐 Public Features (Unauthenticated Users)
Anyone visiting the website can access these features without logging in.

* **Informational Pages & Directory**
  * **Home Page:** View the landing page and recent forum comments.
  * **Static Pages:** Access About, Support & Donations, Collaborate, Contact, Privacy Policy, and FAQ pages.
  * **Event Directory:** View categorized events (Live, Upcoming, and Archived).
  * **Researcher Directory:** View a list of all researchers, research statistics, and individual researcher profiles.
* **Research Library**
  * **Browse & Search:** View approved research publications.
  * **Filtering:** Filter research by department, year, researcher, and researcher type.
  * **Autocomplete Search:** API endpoint for searching researchers dynamically.
* **Authentication**
  * **Registration:** Create an account using an email address. Specify if an undergraduate (member) or general student.
  * **Standard Login:** Log in using email and password.
  * **Google OAuth:** Log in or sign up using a Google Account.

### 👤 Authenticated User Features (Student / Member / Undergraduate)
Logged-in users have access to all public features plus the following interactive functionalities.

* **Profile Management**
  * **View/Edit Profile:** Update personal information, headline, location, contact details, batch number, and professional summary.
  * **Resume/Portfolio Building:** Add skills, education history, work experience, languages, certifications, projects, and publications.
  * **Media:** Upload a profile picture and a cover photo.
  * **Security:** Change account password.
* **Forum & Community**
  * **Browse Forum:** View discussion posts, filter by category, and search for specific topics.
  * **Post Creation:** Create new discussion threads/posts in specific categories.
  * **Engagement:** View post details, add comments to posts, and "Like" / "Unlike" posts.
  * **User Directory:** Browse and search for other registered users and view their public profiles/timelines.
* **Real-Time Messaging (Chat)**
  * **Conversations:** View a list of all active conversations and unread message counts.
  * **Direct Messaging:** Send direct messages to other users by clicking on their profile or searching their username/email.
  * **Real-Time Features:** Uses WebSockets (SocketIO) for real-time message delivery, "typing..." indicators, and read receipts.
  * **Message Management:** Delete specific messages or clear an entire conversation history.
* **Research Contributions**
  * **Submit Research:** Submit new research publications for admin approval (providing title, researcher name, department, year, DOI URL, etc.).
* **Mentorship Hub**
  * **Browse Mentors:** View alumni who have opted in to provide mentorship.
  * **Request Mentorship:** Send mentorship requests to alumni with a personalized message.
  * **Manage Requests:** View sent requests, incoming requests, and active mentorships.
  * **Accept/Reject:** Alumni can accept or reject mentorship requests from students.
* **Research Projects**
  * **Browse Projects:** View open research projects posted by researchers and alumni.
  * **Create Projects:** Researchers and alumni can post research projects with required positions and skills.
  * **Apply to Projects:** Students can apply to projects with a motivation letter.
  * **Manage Applications:** Project owners can view, accept, or reject applications. Applicants can track their application status.
* **Researcher Profile Claims**
  * **Claim Profile:** Users can submit claims to link their account to existing researcher profiles.
  * **Track Status:** View pending claims and their approval status.

### 🛡️ Admin Features (Requires Admin Role)
Administrators have access to a dedicated backend panel (`/admin/`) to manage the platform and moderate content.

* **Dashboard & Analytics**
  * **Admin Dashboard:** View overall platform statistics (total users, posts, comments, events) and quick glances at recent activity.
* **Content Moderation**
  * **Post Management:** Search, filter, edit, or delete any forum post.
  * **Comment Management:** Search, filter, edit, or delete any user comment.
* **Event Management**
  * **Create Events:** Add new events with titles, descriptions, presenter info, external links, dates, times, and cover images. Triggers email notifications to users.
  * **Edit/Delete Events:** Modify existing event details or remove them.
* **Research & Database Moderation**
  * **Review Submissions:** View a queue of pending research submitted by users.
  * **Approve/Reject:** Approve research (makes it public and emails the submitter) or reject/delete it (emails the submitter with an optional reason).
  * **Manage Approved Research:** Edit details of existing public research or delete them from the database.
  * **Manage Researchers:** Edit researcher bios/details or delete researchers entirely.
  * **Profile Claims:** Review and approve/reject user claims to link their account with researcher profiles.
* **Mass Communication**
  * **Announcements:** Compose and send mass emails/announcements to registered users.
  * **Targeted Mailing:** Filter email recipients by user status or restrict to "members only".
  * **Email Logs:** View a history of past announcements and track success/failure delivery rates.

## 🛠 Technology Stack

### Backend
- **Flask 3.0**: Lightweight WSGI web framework
- **SQLAlchemy 2.0**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Migrate**: Database migration management
- **Flask-SocketIO**: Real-time WebSocket communication
- **Werkzeug**: Password hashing and utilities
- **Pillow (PIL)**: Image processing for uploads
- **Authlib**: Google OAuth integration

### Frontend
- **HTML5 & CSS3**: Semantic markup and grid/flexbox layouts
- **Vanilla JavaScript**: DOM manipulation, Fetch API, and Socket.IO client
- **Jinja2**: Template engine

### Database
- **SQLite / PostgreSQL**: Database backend supported via SQLAlchemy ORM.

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

### 4. Setup Environment Variables
Create a `.env` file in the root directory and configure the following parameters:
```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///psra.db
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
```

### 5. Initialize Database
```bash
flask db upgrade
```

### 6. Run the Application
```bash
python app.py
```
The application will be available at `http://127.0.0.1:5000/`

## 🗄 Database Schema

### Core User & Profile Tables
* **User (`user`)**: Core entity representing system users with roles (student, alumni, researcher, admin). Handles authentication, profile data, notification preferences, and links to role-specific profiles.
* **Profile (`profiles`)**: Extended user profile with personal information including full name, bio, headline, location, LinkedIn URL, website URL, languages, certifications, projects, publications, professional summary, education history, and work experience.
* **StudentProfile (`student_profiles`)**: Student-specific data including academic level (undergraduate/graduate), GPA, graduation year, and CV URL.
* **AlumniProfile (`alumni_profiles`)**: Alumni-specific data including graduation year, job title, company, industry, and mentorship opt-in status.
* **ResearcherProfile (`researcher_profiles`)**: Researcher-specific data including academic rank, lab name, office location, and mentorship availability.

### Skills & Organization
* **Skill (`skills`)**: Master list of skills in the system (e.g., Python, Data Analysis).
* **UserSkill (`user_skills`)**: Many-to-many relationship between users and skills, with optional proficiency level.
* **Department (`departments`)**: Academic departments for organizing research and profiles.

### Forum & Community
* **Post (`post`)**: User-generated discussion posts in the forum, linked to a specific category.
* **Comment (`comment`)**: Threaded comments on posts. Linked to Post and User tables.
* **Like (`like`)**: Tracks user likes on posts (unique constraint prevents duplicate likes).

### Events & Messaging
* **Event (`event`)**: System events managed by admins with title, description, date, time, presenter, external URL, and cover image.
* **Message (`message`)**: Private messages between users with read status and read timestamp.
* **Conversation (`conversations`)**: Message conversation threads for organizing messages between users.
* **ConversationParticipant (`conversation_participants`)**: Junction table linking users to conversations.

### Research & Publications
* **Researcher (`researcher`)**: Profiles for research authors (doctors and students). Can be standalone or linked to a registered User account.
* **Research (`research`)**: Research papers and publications linked to a researcher. Requires admin approval (is_approved flag).
* **Announcement (`announcement`)**: Mass email announcements sent to users, with target filtering and delivery statistics.

### Mentorship System
* **MentorRequest (`mentor_requests`)**: Mentorship requests from students to alumni, with status (pending/accepted/rejected/ended).
* **ActiveMentorship (`active_mentorships`)**: Accepted/active mentorship relationships.

### Research Projects
* **ResearchProject (`research_projects`)**: Research project postings created by researchers/alumni with title, description, required positions, and status (open/closed).
* **ProjectRequiredSkill (`project_required_skills`)**: Skills required for research projects.
* **ProjectApplication (`project_applications`)**: Student applications to research projects with motivation letter and status (pending/accepted/rejected).

### Profile Management
* **ProfileClaim (`profile_claims`)**: User claims to link their account with existing researcher profiles, pending admin approval.

### System
* **NotificationLog (`notification_log`)**: Logs of all system notifications (emails) sent out, including type, recipient, status, and error messages.

## ⚙️ System / CLI Commands
These are automated or command-line interface (CLI) tools used by the server to keep the platform running.

* **`flask send-event-reminders`**: Runs in the background to send scheduled email reminders to users about upcoming events. Best run via a daily cron job.
* **`flask send-new-research-alerts`**: Emails subscribed users when new research is approved and published.
* **`flask notification-stats`**: Generates reports on how many automated emails/alerts were sent over the last 24 hours, 7 days, or 30 days.

## 📄 Website Templates

The PSRA website uses Jinja2 templates organized into three main categories: main templates, hub templates, and admin templates.

### Main Templates (24 templates)
Located in the `templates/` directory:

| Template | Description |
|----------|-------------|
| `base.html` | Base layout template with navigation, footer, and common elements |
| `home.html` | Landing page with recent forum comments |
| `about.html` | About the PSRA organization |
| `collaborate.html` | Collaboration opportunities page |
| `contact.html` | Contact information and form |
| `login.html` | User login page with email/password and Google OAuth |
| `register.html` | User registration with account type selection |
| `profile.html` | Current user's profile page |
| `edit_profile.html` | Edit profile form with all profile fields |
| `user_profile.html` | Public profile view of other users |
| `dashboard.html` | User dashboard with activity feed and quick stats |
| `forum_main.html` | Main forum listing with posts and categories |
| `post_detail.html` | Single post view with comments |
| `create_post.html` | Create new forum post |
| `messages.html` | Conversations inbox |
| `conversation.html` | Individual conversation thread |
| `send_message.html` | Send new message form |
| `users.html` | User directory with search |
| `researches.html` | Research library with filtering |
| `researchers.html` | Researchers directory |
| `researcher_profile.html` | Individual researcher profile |
| `submit_research.html` | Submit research for approval |
| `claim_profile.html` | Claim researcher profile |
| `events.html` | Events listing (live, upcoming, archived) |
| `placeholder.html` | Generic placeholder for static pages |

### Hub Templates (8 templates)
Located in the `templates/hub/` directory:

| Template | Description |
|----------|-------------|
| `projects.html` | Browse open research projects |
| `project_detail.html` | Project details with required skills |
| `create_project.html` | Create new research project |
| `apply_project.html` | Apply to a research project |
| `manage_projects.html` | Manage your projects and applications |
| `mentors.html` | Browse available mentors (alumni) |
| `request_mentorship.html` | Send mentorship request |
| `manage_mentorships.html` | Manage mentorship requests and active mentorships |

### Admin Templates (18 templates)
Located in the `templates/admin/` directory:

| Template | Description |
|----------|-------------|
| `dashboard.html` | Admin dashboard with statistics |
| `users.html` | User management with search/filter |
| `edit_user.html` | Edit user details and role |
| `posts.html` | Post management with moderation tools |
| `edit_post.html` | Edit any forum post |
| `comments.html` | Comment management |
| `edit_comment.html` | Edit any comment |
| `events.html` | Event management |
| `create_event.html` | Create new event |
| `edit_event.html` | Edit existing event |
| `submissions.html` | Research submissions queue |
| `researchers.html` | Researcher management |
| `edit_researcher.html` | Edit researcher details |
| `researches.html` | Manage approved research |
| `edit_research.html` | Edit research details |
| `claims.html` | Profile claims queue |
| `announcements.html` | Announcement history |
| `send_announcement.html` | Compose mass email |

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.