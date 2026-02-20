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