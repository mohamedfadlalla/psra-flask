# PSRA (Pharmaceutical Studies and Research Association) Website

A comprehensive web platform for the Pharmaceutical Studies and Research Association, built with Flask and featuring a minimalist, professional design with a strict black, white, and grayscale color palette.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features & Roles](#features--roles)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Database Schema](#database-schema)
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

* **User (`user`)**: Core entity representing system users (students, alumni, undergraduates). Handles authentication, profile data, and preferences.
* **Post (`post`)**: User-generated content/posts in the forum. Linked to the User table.
* **Comment (`comment`)**: Threaded comments on posts. Linked to Post and User tables.
* **Like (`like`)**: Tracks user likes on posts.
* **Event (`event`)**: System events managed by admins.
* **Message (`message`)**: Private, real-time messages between users.
* **Researcher (`researcher`)**: Profiles for researchers. Can be linked to a User account or standalone.
* **Research (`research`)**: Research papers and publications linked to a researcher. Requires admin approval.
* **NotificationLog (`notification_log`)**: Logs of system notifications (emails) sent out.

## ⚙️ System / CLI Commands
These are automated or command-line interface (CLI) tools used by the server to keep the platform running.

* **`flask send-event-reminders`**: Runs in the background to send scheduled email reminders to users about upcoming events. Best run via a daily cron job.
* **`flask send-new-research-alerts`**: Emails subscribed users when new research is approved and published.
* **`flask notification-stats`**: Generates reports on how many automated emails/alerts were sent over the last 24 hours, 7 days, or 30 days.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.