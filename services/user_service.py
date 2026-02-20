"""
User Service Module

Business logic for user management functionality.
"""

from typing import Dict, List, Optional

from models import db, User, Profile
from utils.json_utils import safe_json_parse, combine_timeline, get_user_timeline
from utils.image_utils import process_profile_picture, process_cover_photo


class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    def get_user_timeline(user: User) -> List[Dict]:
        """
        Get combined experience/education timeline for a user.
        
        Args:
            user: User model instance
        
        Returns:
            Combined and sorted timeline list
        """
        return get_user_timeline(user)
    
    @staticmethod
    def update_profile(user: User, form_data: Dict, files: Optional[Dict] = None, 
                       app_root: str = '', upload_folder: str = 'static/profile_images') -> User:
        """
        Update a user's profile with form data and optional file uploads.
        
        Args:
            user: User model instance to update
            form_data: Dictionary of form data
            files: Optional dictionary of uploaded files
            app_root: Application root path for file operations
            upload_folder: Folder for profile image uploads
        
        Returns:
            The updated User instance
        """
        # Update basic profile fields
        basic_fields = [
            'name', 'headline', 'location', 'about', 'batch_number',
            'phone_number', 'whatsapp_number', 'skills',
            'linkedin_url', 'website_url', 'languages',
            'certifications', 'projects', 'publications', 'professional_summary'
        ]
        
        for field in basic_fields:
            if field in form_data:
                setattr(user, field, form_data[field])
        
        # Handle JSON data fields
        if 'education_data' in form_data:
            user.education = form_data['education_data'] or '[]'
        if 'experience_data' in form_data:
            user.experience = form_data['experience_data'] or '[]'
        
        # Handle file uploads
        if files:
            # Handle cover photo upload
            if files.get('cover_photo'):
                cover_url = process_cover_picture(
                    files['cover_photo'],
                    user.id,
                    upload_folder,
                    app_root
                )
                if cover_url:
                    user.cover_photo_url = cover_url
            
            # Handle profile picture upload
            if files.get('profile_picture'):
                profile_url = process_profile_picture(
                    files['profile_picture'],
                    user.id,
                    upload_folder,
                    app_root
                )
                if profile_url:
                    user.profile_picture_url = profile_url
        
        db.session.commit()
        return user
    
    @staticmethod
    def create_user(email: str, name: str, password: str, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email
            name: User's name
            password: Plain text password (will be hashed)
            **kwargs: Additional user fields
        
        Returns:
            The created User instance
        """
        user = User(
            email=email.strip(),
            name=name,
            **kwargs
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: Email address to search for
        
        Returns:
            User instance or None
        """
        return User.query.filter_by(email=email.strip()).first()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User's ID
        
        Returns:
            User instance or None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_name_or_email(identifier: str) -> Optional[User]:
        """
        Get a user by name or email.
        
        Args:
            identifier: Name or email to search for
        
        Returns:
            User instance or None
        """
        user = User.query.join(User.profile).filter(Profile.full_name == identifier).first()
        if not user:
            user = User.query.filter_by(email=identifier.strip()).first()
        return user
    
    @staticmethod
    def search_users(query: str, exclude_user_id: Optional[int] = None) -> List[User]:
        """
        Search users by name (case-insensitive partial match).
        
        Args:
            query: Search query
            exclude_user_id: Optional user ID to exclude from results
        
        Returns:
            List of matching users
        """
        search = User.query.join(User.profile)
        if exclude_user_id:
            search = search.filter(User.id != exclude_user_id)
        if query:
            search = search.filter(Profile.full_name.ilike(f'%{query}%'))
        return search.order_by(Profile.full_name).all()
    
    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> tuple:
        """
        Change a user's password.
        
        Args:
            user: User instance
            current_password: Current password for verification
            new_password: New password to set
        
        Returns:
            Tuple of (success, error_message)
        """
        if not user.check_password(current_password):
            return False, 'Current password is incorrect'
        
        user.set_password(new_password)
        db.session.commit()
        return True, ''
    
    @staticmethod
    def get_profile_form_data(user: User) -> Dict:
        """
        Get user data pre-populated for profile edit form.
        
        Args:
            user: User model instance
        
        Returns:
            Dictionary of form data
        """
        return {
            'name': user.name,
            'headline': user.headline,
            'location': user.location,
            'about': user.about,
            'batch_number': str(user.batch_number) if user.batch_number else None,
            'email': user.email,
            'phone_number': user.phone_number,
            'whatsapp_number': user.whatsapp_number,
            'skills': user.skills,
            'education_data': safe_json_parse(user.education),
            'experience_data': safe_json_parse(user.experience),
            'linkedin_url': user.linkedin_url,
            'website_url': user.website_url,
            'languages': user.languages,
            'certifications': user.certifications,
            'projects': user.projects,
            'publications': user.publications,
            'professional_summary': user.professional_summary
        }
