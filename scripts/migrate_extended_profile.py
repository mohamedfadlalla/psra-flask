import sys
import os

# Add the project directory to sys.path so we can import app and models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User

def migrate_extended_data():
    with app.app_context():
        users = User.query.all()
        print(f"Migrating extended fields for {len(users)} users...")
        
        for user in users:
            if user.profile:
                user.profile.headline = user.headline
                user.profile.location = user.location
                user.profile.cover_photo_url = user.cover_photo_url
                user.profile.linkedin_url = user.linkedin_url
                user.profile.website_url = user.website_url
                user.profile.languages = user.languages
                user.profile.certifications = user.certifications
                user.profile.projects = user.projects
                user.profile.publications = user.publications
                user.profile.professional_summary = user.professional_summary
                user.profile.education = user.education
                user.profile.experience = user.experience

        try:
            db.session.commit()
            print("Extended data migration completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_extended_data()