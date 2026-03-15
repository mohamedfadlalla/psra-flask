"""
Research Service Module

Business logic for research and researcher management functionality.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import or_, and_, func

from models import db, Research, Researcher, User


class ResearchService:
    """Service class for research-related operations."""
    
    # Valid department choices for filtering
    DEPARTMENT_CHOICES = [
        ('all', 'All Departments'),
        ('Pharmaceutics & Drug Delivery', 'Pharmaceutics & Drug Delivery'),
        ('Pharmacology & Toxicology', 'Pharmacology & Toxicology'),
        ('Clinical Pharmacy & Pharmacy Practice', 'Clinical Pharmacy & Pharmacy Practice'),
        ('Pharmaceutical Chemistry', 'Pharmaceutical Chemistry'),
    ]
    
    @staticmethod
    def get_year_choices() -> List[Tuple[str, str]]:
        """
        Get list of years from database for filtering.
        
        Returns:
            List of (value, label) tuples for year choices
        """
        years = db.session.query(Research.year).distinct().order_by(Research.year.desc()).all()
        choices = [('all', 'All Years')]
        for year in years:
            if year[0]:
                choices.append((str(year[0]), str(year[0])))
        return choices
    
    @staticmethod
    def get_all_researchers() -> List[Researcher]:
        """
        Get all researchers ordered by name.
        
        Returns:
            List of Researcher objects
        """
        return Researcher.query.order_by(Researcher.name).all()
    
    @staticmethod
    def get_researcher_by_id(researcher_id: int) -> Optional[Researcher]:
        """
        Get a researcher by ID.
        
        Args:
            researcher_id: The ID of the researcher
            
        Returns:
            Researcher object or None if not found
        """
        return Researcher.query.get(researcher_id)
    
    @staticmethod
    def get_researcher_by_name(name: str) -> Optional[Researcher]:
        """
        Get a researcher by name.
        
        Args:
            name: The name of the researcher
            
        Returns:
            Researcher object or None if not found
        """
        return Researcher.query.filter_by(name=name).first()
    
    @staticmethod
    def get_researcher_profile(researcher_id: int) -> Optional[Dict[str, Any]]:
        """
        Get researcher profile with their researches.
        
        Args:
            researcher_id: The ID of the researcher
            
        Returns:
            Dictionary containing researcher info and researches
        """
        researcher = Researcher.query.get(researcher_id)
        if not researcher:
            return None
        
        researches = Research.query.filter_by(
            researcher_id=researcher_id
        ).order_by(Research.year.desc()).all()
        
        # Group researches by department
        departments = {}
        for research in researches:
            if research.department not in departments:
                departments[research.department] = []
            departments[research.department].append(research)
        
        return {
            'researcher': researcher,
            'researches': researches,
            'departments': departments,
            'total_researches': len(researches)
        }
    
    # Valid researcher type choices for filtering
    RESEARCHER_TYPE_CHOICES = [
        ('all', 'All Types'),
        ('doctor', 'Doctor'),
        ('student', 'Student'),
    ]
    
    @staticmethod
    def filter_researches(
        department: str = 'all',
        year: str = 'all',
        researcher_id: Optional[int] = None,
        researcher_type: str = 'all',
        search_query: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Any:
        """
        Filter researches based on criteria with pagination.
        
        Args:
            department: Department filter ('all' for no filter)
            year: Year filter ('all' for no filter)
            researcher_id: Researcher ID filter (None for no filter)
            researcher_type: Researcher type filter ('all', 'doctor', or 'student')
            search_query: Search query for title/researcher name
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            SQLAlchemy Pagination object
        """
        query = Research.query.filter(Research.is_approved == True)
        
        # Apply department filter
        if department and department != 'all':
            query = query.filter(Research.department == department)
        
        # Apply year filter
        if year and year != 'all':
            try:
                year_int = int(year)
                query = query.filter(Research.year == year_int)
            except ValueError:
                pass
        
        # Apply researcher filter
        if researcher_id:
            query = query.filter(Research.researcher_id == researcher_id)
        
        # Apply researcher type filter
        if researcher_type and researcher_type != 'all':
            query = query.filter(Research.researcher_type == researcher_type)
        
        # Apply search filter
        if search_query:
            search_term = f'%{search_query}%'
            # Join with researcher to search by name
            query = query.join(Researcher).filter(
                or_(
                    Research.title.ilike(search_term),
                    Researcher.name.ilike(search_term)
                )
            )
        
        # Order by year descending, then by title
        query = query.order_by(Research.year.desc(), Research.title)
        
        # Apply pagination
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_research_statistics() -> Dict[str, Any]:
        """
        Get statistics about researches.
        
        Returns:
            Dictionary containing various statistics
        """
        # Total approved researches
        total_researches = Research.query.filter_by(is_approved=True).count()
        
        # Total researchers
        total_researchers = Researcher.query.count()
        
        # Researches by department
        dept_stats = db.session.query(
            Research.department,
            func.count(Research.id)
        ).filter(Research.is_approved == True).group_by(Research.department).all()
        
        departments = {dept: count for dept, count in dept_stats}
        
        # Researches by year
        year_stats = db.session.query(
            Research.year,
            func.count(Research.id)
        ).filter(Research.is_approved == True).group_by(Research.year).order_by(Research.year.desc()).all()
        
        years = {year: count for year, count in year_stats}
        
        # Top researchers (by number of researches)
        top_researchers = db.session.query(
            Researcher,
            func.count(Research.id).label('research_count')
        ).join(Research).filter(
            Research.is_approved == True
        ).group_by(Researcher.id).order_by(func.count(Research.id).desc()).limit(5).all()
        
        return {
            'total_researches': total_researches,
            'total_researchers': total_researchers,
            'departments': departments,
            'years': years,
            'top_researchers': [(r.name, count) for r, count in top_researchers]
        }
    
    @staticmethod
    def create_researcher(
        name: str,
        bio: Optional[str] = None,
        profile_picture_url: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Researcher:
        """
        Create a new researcher.
        
        Args:
            name: Researcher name
            bio: Optional biography
            profile_picture_url: Optional profile picture URL
            user_id: Optional linked user ID
            
        Returns:
            The created Researcher object
        """
        researcher = Researcher(
            name=name,
            bio=bio,
            profile_picture_url=profile_picture_url,
            user_id=user_id,
            is_registered_user=user_id is not None
        )
        db.session.add(researcher)
        db.session.commit()
        return researcher
    
    @staticmethod
    def update_researcher(
        researcher_id: int,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        profile_picture_url: Optional[str] = None
    ) -> Optional[Researcher]:
        """
        Update a researcher's information.
        
        Args:
            researcher_id: The ID of the researcher
            name: New name (optional)
            bio: New bio (optional)
            profile_picture_url: New profile picture URL (optional)
            
        Returns:
            The updated Researcher or None if not found
        """
        researcher = Researcher.query.get(researcher_id)
        if not researcher:
            return None
        
        if name:
            researcher.name = name
        if bio is not None:
            researcher.bio = bio
        if profile_picture_url is not None:
            researcher.profile_picture_url = profile_picture_url
        
        db.session.commit()
        return researcher
    
    @staticmethod
    def delete_researcher(researcher_id: int) -> bool:
        """
        Delete a researcher and all their researches.
        
        Args:
            researcher_id: The ID of the researcher
            
        Returns:
            True if deleted, False if not found
        """
        researcher = Researcher.query.get(researcher_id)
        if not researcher:
            return False
        
        db.session.delete(researcher)
        db.session.commit()
        return True
    
    @staticmethod
    def submit_research(
        title: str,
        researcher_name: str,
        department: str,
        year: int,
        doi_url: Optional[str] = None,
        researcher_type: str = 'doctor',
        submitted_by: Optional[int] = None
    ) -> Research:
        """
        Submit a new research for approval.
        
        Args:
            title: Research title
            researcher_name: Name of the researcher
            department: Department name
            year: Year of publication
            doi_url: Optional DOI URL
            researcher_type: 'doctor' or 'student'
            submitted_by: User ID of submitter (optional)
            
        Returns:
            The created Research object (pending approval)
        """
        # Get or create researcher
        researcher = ResearchService.get_researcher_by_name(researcher_name)
        if not researcher:
            researcher = Researcher(name=researcher_name)
            db.session.add(researcher)
            db.session.flush()  # Get ID without committing
        
        # Create research (not approved by default)
        research = Research(
            title=title,
            doi_url=doi_url,
            department=department,
            year=year,
            researcher_id=researcher.id,
            researcher_type=researcher_type,
            is_approved=False,  # Pending approval
            submitted_by=submitted_by
        )
        db.session.add(research)
        db.session.commit()
        
        return research
    
    @staticmethod
    def approve_research(research_id: int) -> Optional[Research]:
        """
        Approve a submitted research.
        
        Args:
            research_id: The ID of the research
            
        Returns:
            The approved Research or None if not found
        """
        research = Research.query.get(research_id)
        if not research:
            return None
        
        research.is_approved = True
        db.session.commit()
        return research
    
    @staticmethod
    def reject_research(research_id: int) -> bool:
        """
        Reject (delete) a submitted research.
        
        Args:
            research_id: The ID of the research
            
        Returns:
            True if rejected/deleted, False if not found
        """
        research = Research.query.get(research_id)
        if not research:
            return False
        
        db.session.delete(research)
        db.session.commit()
        return True
    
    @staticmethod
    def get_pending_submissions(page: int = 1, per_page: int = 20) -> Any:
        """
        Get pending research submissions for admin review.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            SQLAlchemy Pagination object
        """
        return Research.query.filter_by(
            is_approved=False
        ).order_by(Research.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_research_by_id(research_id: int) -> Optional[Research]:
        """
        Get a research by ID.
        
        Args:
            research_id: The ID of the research
            
        Returns:
            Research object or None if not found
        """
        return Research.query.get(research_id)
    
    @staticmethod
    def update_research(
        research_id: int,
        title: Optional[str] = None,
        department: Optional[str] = None,
        year: Optional[int] = None,
        doi_url: Optional[str] = None,
        researcher_type: Optional[str] = None
    ) -> Optional[Research]:
        """
        Update a research's information.
        
        Args:
            research_id: The ID of the research
            title: New title (optional)
            department: New department (optional)
            year: New year (optional)
            doi_url: New DOI URL (optional)
            researcher_type: New researcher type (optional)
            
        Returns:
            The updated Research or None if not found
        """
        research = Research.query.get(research_id)
        if not research:
            return None
        
        if title:
            research.title = title
        if department:
            research.department = department
        if year:
            research.year = year
        if doi_url is not None:
            research.doi_url = doi_url
        if researcher_type:
            research.researcher_type = researcher_type
        
        db.session.commit()
        return research
    
    @staticmethod
    def delete_research(research_id: int) -> bool:
        """
        Delete a research.
        
        Args:
            research_id: The ID of the research
            
        Returns:
            True if deleted, False if not found
        """
        research = Research.query.get(research_id)
        if not research:
            return False
        
        db.session.delete(research)
        db.session.commit()
        return True
    
    @staticmethod
    def search_researchers(query: str, limit: int = 10) -> List[Researcher]:
        """
        Search researchers by name.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of Researcher objects
        """
        search_term = f'%{query}%'
        return Researcher.query.filter(
            Researcher.name.ilike(search_term)
        ).limit(limit).all()


# Create convenience functions that use the service class
def get_year_choices():
    return ResearchService.get_year_choices()

def get_all_researchers():
    return ResearchService.get_all_researchers()

def get_researcher_by_id(researcher_id):
    return ResearchService.get_researcher_by_id(researcher_id)

def get_researcher_by_name(name):
    return ResearchService.get_researcher_by_name(name)

def get_researcher_profile(researcher_id):
    return ResearchService.get_researcher_profile(researcher_id)

def filter_researches(department='all', year='all', researcher_id=None, search_query=None, page=1, per_page=10):
    return ResearchService.filter_researches(department, year, researcher_id, search_query, page, per_page)

def get_research_statistics():
    return ResearchService.get_research_statistics()

def create_researcher(name, bio=None, profile_picture_url=None, user_id=None):
    return ResearchService.create_researcher(name, bio, profile_picture_url, user_id)

def update_researcher(researcher_id, name=None, bio=None, profile_picture_url=None):
    return ResearchService.update_researcher(researcher_id, name, bio, profile_picture_url)

def delete_researcher(researcher_id):
    return ResearchService.delete_researcher(researcher_id)

def submit_research(title, researcher_name, department, year, doi_url=None, researcher_type='doctor', submitted_by=None):
    return ResearchService.submit_research(title, researcher_name, department, year, doi_url, researcher_type, submitted_by)

def approve_research(research_id):
    return ResearchService.approve_research(research_id)

def reject_research(research_id):
    return ResearchService.reject_research(research_id)

def get_pending_submissions(page=1, per_page=20):
    return ResearchService.get_pending_submissions(page, per_page)

def get_research_by_id(research_id):
    return ResearchService.get_research_by_id(research_id)

def update_research(research_id, title=None, department=None, year=None, doi_url=None, researcher_type=None):
    return ResearchService.update_research(research_id, title, department, year, doi_url, researcher_type)

def delete_research(research_id):
    return ResearchService.delete_research(research_id)

def search_researchers(query, limit=10):
    return ResearchService.search_researchers(query, limit)