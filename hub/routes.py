from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json

from . import hub_bp
from .forms import MentorshipRequestForm, ResearchProjectForm, ApplicationForm
from models import db, User, UserRole, Profile, AlumniProfile, MentorshipStatus, MentorRequest, ActiveMentorship
from models import Skill, ResearchProject, ProjectStatus, ProjectRequiredSkill, ProjectApplication, ApplicationStatus
from utils.constants import FLASH_SUCCESS, FLASH_ERROR
from utils.email_utils import send_mentorship_request_email, send_mentorship_response_email

def get_or_create_skills(skill_string):
    if not skill_string:
        return []
    skill_names = [s.strip() for s in skill_string.split(',') if s.strip()]
    skills = []
    for name in skill_names:
        skill = Skill.query.filter_by(name=name).first()
        if not skill:
            skill = Skill(name=name)
            db.session.add(skill)
            db.session.flush()
        skills.append(skill)
    return skills

# ==================== Mentorship Module ====================

@hub_bp.route('/mentors')
@login_required
def browse_mentors():
    """Browse alumni mentors."""
    query = User.query.join(AlumniProfile).filter(
        User.role == UserRole.ALUMNI,
        AlumniProfile.open_to_mentor == True,
        User.id != current_user.id
    )
    mentors = query.all()
    return render_template('hub/mentors.html', mentors=mentors)

@hub_bp.route('/mentors/request/<int:alumni_id>', methods=['GET', 'POST'])
@login_required
def request_mentorship(alumni_id):
    """Send a mentorship request to an alumni."""
    alumni = User.query.get_or_404(alumni_id)
    if alumni.role != UserRole.ALUMNI or not alumni.alumni_profile.open_to_mentor:
        flash('This user is not open to mentorship.', FLASH_ERROR)
        return redirect(url_for('hub.browse_mentors'))

    # Check if a request already exists
    existing_request = MentorRequest.query.filter_by(
        student_id=current_user.id,
        alumni_id=alumni.id,
        status=MentorshipStatus.PENDING
    ).first()
    if existing_request:
        flash('You already have a pending request with this mentor.', FLASH_ERROR)
        return redirect(url_for('hub.browse_mentors'))

    form = MentorshipRequestForm()
    if form.validate_on_submit():
        mentor_req = MentorRequest(
            student_id=current_user.id,
            alumni_id=alumni.id,
            message=form.message.data
        )
        db.session.add(mentor_req)
        db.session.commit()
        
        send_mentorship_request_email(alumni, current_user, form.message.data)
        
        flash('Mentorship request sent successfully.', FLASH_SUCCESS)
        return redirect(url_for('hub.browse_mentors'))

    return render_template('hub/request_mentorship.html', form=form, alumni=alumni)

@hub_bp.route('/mentorships/manage')
@login_required
def manage_mentorships():
    """Manage incoming mentorship requests (for alumni) and active mentorships."""
    incoming_requests = []
    if current_user.role == UserRole.ALUMNI:
        incoming_requests = MentorRequest.query.filter_by(
            alumni_id=current_user.id,
            status=MentorshipStatus.PENDING
        ).all()
        
    sent_requests = MentorRequest.query.filter_by(
        student_id=current_user.id,
        status=MentorshipStatus.PENDING
    ).all()
    
    active_as_mentor = ActiveMentorship.query.join(MentorRequest).filter(
        MentorRequest.alumni_id == current_user.id,
        ActiveMentorship.ended_at == None
    ).all()
    
    active_as_mentee = ActiveMentorship.query.join(MentorRequest).filter(
        MentorRequest.student_id == current_user.id,
        ActiveMentorship.ended_at == None
    ).all()

    return render_template('hub/manage_mentorships.html', 
                           incoming_requests=incoming_requests,
                           sent_requests=sent_requests,
                           active_as_mentor=active_as_mentor,
                           active_as_mentee=active_as_mentee)

@hub_bp.route('/mentorships/request/<int:request_id>/<action>', methods=['POST'])
@login_required
def respond_mentorship(request_id, action):
    """Accept or reject a mentorship request."""
    mentor_req = MentorRequest.query.get_or_404(request_id)
    if mentor_req.alumni_id != current_user.id:
        flash('Unauthorized action.', FLASH_ERROR)
        return redirect(url_for('hub.manage_mentorships'))

    if action == 'accept':
        mentor_req.status = MentorshipStatus.ACCEPTED
        active = ActiveMentorship(mentor_request_id=mentor_req.id)
        db.session.add(active)
        
        # Optionally create a conversation automatically here
        from services.message_service import MessageService
        MessageService.get_or_create_conversation(mentor_req.student_id, mentor_req.alumni_id)
        
        send_mentorship_response_email(mentor_req.student, current_user, 'accepted')
        
        flash('Mentorship request accepted.', FLASH_SUCCESS)
    elif action == 'reject':
        mentor_req.status = MentorshipStatus.REJECTED
        
        send_mentorship_response_email(mentor_req.student, current_user, 'rejected')
        
        flash('Mentorship request rejected.', FLASH_SUCCESS)
        
    db.session.commit()
    return redirect(url_for('hub.manage_mentorships'))

# ==================== Research Recruitment ====================

@hub_bp.route('/projects')
def browse_projects():
    """Browse research projects."""
    projects = ResearchProject.query.filter_by(status=ProjectStatus.OPEN).order_by(ResearchProject.created_at.desc()).all()
    return render_template('hub/projects.html', projects=projects)

@hub_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a research project (Researcher only)."""
    if current_user.role not in [UserRole.RESEARCHER, UserRole.ADMIN]:
        flash('Only researchers can create projects.', FLASH_ERROR)
        return redirect(url_for('hub.browse_projects'))

    form = ResearchProjectForm()
    if form.validate_on_submit():
        project = ResearchProject(
            researcher_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            required_positions=form.required_positions.data
        )
        db.session.add(project)
        db.session.flush()

        skills = get_or_create_skills(form.skills.data)
        for skill in skills:
            proj_skill = ProjectRequiredSkill(project_id=project.id, skill_id=skill.id)
            db.session.add(proj_skill)

        db.session.commit()
        flash('Research project created successfully.', FLASH_SUCCESS)
        return redirect(url_for('hub.browse_projects'))

    return render_template('hub/create_project.html', form=form)

@hub_bp.route('/projects/<int:project_id>')
def project_detail(project_id):
    """View project details."""
    project = ResearchProject.query.get_or_404(project_id)
    return render_template('hub/project_detail.html', project=project)

@hub_bp.route('/projects/<int:project_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_project(project_id):
    """Apply to a research project."""
    project = ResearchProject.query.get_or_404(project_id)
    if project.status == ProjectStatus.CLOSED:
        flash('This project is closed to new applications.', FLASH_ERROR)
        return redirect(url_for('hub.project_detail', project_id=project.id))

    existing_app = ProjectApplication.query.filter_by(
        project_id=project.id,
        student_id=current_user.id
    ).first()
    if existing_app:
        flash('You have already applied for this project.', FLASH_ERROR)
        return redirect(url_for('hub.project_detail', project_id=project.id))

    form = ApplicationForm()
    if form.validate_on_submit():
        application = ProjectApplication(
            project_id=project.id,
            student_id=current_user.id,
            motivation_letter=form.motivation_letter.data
        )
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully.', FLASH_SUCCESS)
        return redirect(url_for('hub.project_detail', project_id=project.id))

    return render_template('hub/apply_project.html', form=form, project=project)

@hub_bp.route('/projects/manage')
@login_required
def manage_projects():
    """Manage projects (researcher) and applications."""
    if current_user.role in [UserRole.RESEARCHER, UserRole.ADMIN]:
        my_projects = ResearchProject.query.filter_by(researcher_id=current_user.id).all()
    else:
        my_projects = []
        
    my_applications = ProjectApplication.query.filter_by(student_id=current_user.id).all()
    return render_template('hub/manage_projects.html', my_projects=my_projects, my_applications=my_applications)

@hub_bp.route('/applications/<int:app_id>/<action>', methods=['POST'])
@login_required
def respond_application(app_id, action):
    """Accept or reject a project application."""
    application = ProjectApplication.query.get_or_404(app_id)
    project = application.project
    
    if project.researcher_id != current_user.id:
        flash('Unauthorized action.', FLASH_ERROR)
        return redirect(url_for('hub.manage_projects'))

    if action == 'accept':
        application.status = ApplicationStatus.ACCEPTED
        flash('Application accepted.', FLASH_SUCCESS)
        
        # Check if project should be closed
        accepted_count = ProjectApplication.query.filter_by(
            project_id=project.id,
            status=ApplicationStatus.ACCEPTED
        ).count()
        
        # Include the newly accepted one
        if (accepted_count + 1) >= project.required_positions:
            project.status = ProjectStatus.CLOSED
            flash('Required positions filled. Project is now closed.', FLASH_SUCCESS)
            
    elif action == 'reject':
        application.status = ApplicationStatus.REJECTED
        flash('Application rejected.', FLASH_SUCCESS)
        
    db.session.commit()
    return redirect(url_for('hub.manage_projects'))