import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import db, User
from utils.email_utils import send_email
from config import config

def create_app():
    # Detect environment
    env_name = os.getenv('FLASK_ENV', 'default')
    app = Flask(__name__)
    app.config.from_object(config[env_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Mail extension manually since it's usually done in create_app in app.py
    # checking app.py to see how it's done there would be better but for now let's try importing create_app
    return app

# Import the existing app instance from app.py
try:
    from app import app
except ImportError:
    print("Could not import app from app.py.")
    sys.exit(1)

def test_email_broadcast():
    with app.app_context():
        print("Checking email configuration...")
        print(f"Server: {app.config.get('MAIL_SERVER')}")
        print(f"Port: {app.config.get('MAIL_PORT')}")
        print(f"Username: {app.config.get('MAIL_USERNAME')}")
        print(f"Sender: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        # Verify database connection and fetch users
        try:
            users = User.query.filter(User.email.isnot(None)).all()
            print(f"\nFound {len(users)} users with email addresses.")
        except Exception as e:
            print(f"Error accessing database: {e}")
            return

        if not users:
            print("No users found to send emails to.")
            return

        # Check for --force argument to skip confirmation
        if "--force" in sys.argv:
            print("\nWARNING: Skipping confirmation due to --force flag.")
        else:
            print("\nWARNING: This will send a test email to ALL users found.")
            print("Press 'y' to continue, or any other key to abort.")
            choice = input("Proceed? ").lower()
            
            if choice != 'y':
                print("Aborted.")
                return

        print("\nSending emails...")
        success_count = 0
        failure_count = 0
        
        subject = "Test Email Notification"
        html_body = """
        <h1>Test Notification</h1>
        <p>This is a test email sent from the PSRA website notification system.</p>
        <p>If you received this, the email broadcasting functionality is working correctly.</p>
        """
        text_body = "This is a test email sent from the PSRA website notification system. If you received this, the email broadcasting functionality is working correctly."

        for user in users:
            print(f"Sending to {user.email}...", end=" ")
            try:
                if send_email(subject, [user.email], html_body, text_body):
                    print("SUCCESS")
                    success_count += 1
                else:
                    print("FAILED")
                    failure_count += 1
            except Exception as e:
                print(f"ERROR: {e}")
                failure_count += 1

        print(f"\nFinished.")
        print(f"Success: {success_count}")
        print(f"Failed: {failure_count}")

if __name__ == "__main__":
    test_email_broadcast()
