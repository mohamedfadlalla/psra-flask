"""
Admin Routes Module

Routes for admin panel functionality including content moderation and event management.
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os

from . import admin_bp
from models import db, User, Post, Comment, Event, Research, Researcher, Announcement, UserRole
from utils.decorators import admin_required
from utils.constants import FLASH_SUCCESS, FLASH_ERROR, FLASH_WARNING, DEFAULT_PER_PAGE
from utils.image_utils import save_event_image, delete_file, get_event_image_path
from utils.query_helpers import paginate_query
from services import EventService, ResearchService
from utils.email_utils import send_event_notification, send_research_status_email, send_announcement_email, is_mail_configured
from utils.notification_utils import send_research_approved_notification, send_research_rejected_notification
import json


# ==================== Dashboard ====================

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Display admin dashboard with statistics."""
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_events = Event.query.count()

    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_posts=total_posts,
                         total_comments=total_comments,
                         total_events=total_events,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments)


# ==================== User Management ====================

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Display users for management with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')

    query = User.query

    if search:
        from models import Profile
        query = query.outerjoin(Profile).filter(
            User.email.contains(search) | Profile.full_name.contains(search)
        )
    if role:
        for r in UserRole:
            if r.value == role:
                query = query.filter(User.role == r)
                break

    users = paginate_query(query.order_by(User.created_at.desc()), page)

    roles = [r.value for r in UserRole]

    return render_template('admin/users.html',
                         users=users,
                         search=search,
                         role=role,
                         roles=roles)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit a user."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        
        role_val = request.form.get('role')
        if role_val:
            user.status = role_val

        try:
            db.session.commit()
            flash('User updated successfully.', FLASH_SUCCESS)
            return redirect(url_for('admin.manage_users'))
        except Exception:
            db.session.rollback()
            flash('Error updating user.', FLASH_ERROR)

    return render_template('admin/edit_user.html', user=user, roles=[r.value for r in UserRole])


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    if user_id == current_user.id:
        flash('You cannot delete your own account.', FLASH_ERROR)
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', FLASH_SUCCESS)
    except Exception:
        db.session.rollback()
        flash('Error deleting user.', FLASH_ERROR)

    return redirect(url_for('admin.manage_users'))


# ==================== Post Management ====================

@admin_bp.route('/posts')
@login_required
@admin_required
def manage_posts():
    """Display posts for management with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    author = request.args.get('author', '')

    query = Post.query

    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    if category:
        query = query.filter_by(category=category)
    if author:
        from models import Profile
        query = query.join(User).join(Profile).filter(Profile.full_name.contains(author))

    posts = paginate_query(query.order_by(Post.created_at.desc()), page)

    # Get unique categories for filter dropdown
    categories = [cat[0] for cat in db.session.query(Post.category).distinct().all()]

    return render_template('admin/posts.html',
                         posts=posts,
                         search=search,
                         category=category,
                         author=author,
                         categories=categories)


@admin_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    """Edit a post."""
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.category = request.form.get('category')

        try:
            db.session.commit()
            flash('Post updated successfully.', FLASH_SUCCESS)
            return redirect(url_for('admin.manage_posts'))
        except Exception:
            db.session.rollback()
            flash('Error updating post.', FLASH_ERROR)

    return render_template('admin/edit_post.html', post=post)


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', FLASH_SUCCESS)
    except Exception:
        db.session.rollback()
        flash('Error deleting post.', FLASH_ERROR)

    return redirect(url_for('admin.manage_posts'))


# ==================== Comment Management ====================

@admin_bp.route('/comments')
@login_required
@admin_required
def manage_comments():
    """Display comments for management with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    author = request.args.get('author', '')

    query = Comment.query.join(Post).join(User, Comment.user_id == User.id)

    if search:
        query = query.filter(Comment.content.contains(search))
    if author:
        from models import Profile
        query = query.join(Profile, User.id == Profile.user_id).filter(Profile.full_name.contains(author))

    comments = paginate_query(query.order_by(Comment.created_at.desc()), page)

    return render_template('admin/comments.html',
                         comments=comments,
                         search=search,
                         author=author)


@admin_bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_comment(comment_id):
    """Edit a comment."""
    comment = Comment.query.get_or_404(comment_id)

    if request.method == 'POST':
        comment.content = request.form.get('content')

        try:
            db.session.commit()
            flash('Comment updated successfully.', FLASH_SUCCESS)
            return redirect(url_for('admin.manage_comments'))
        except Exception:
            db.session.rollback()
            flash('Error updating comment.', FLASH_ERROR)

    return render_template('admin/edit_comment.html', comment=comment)


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)

    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully.', FLASH_SUCCESS)
    except Exception:
        db.session.rollback()
        flash('Error deleting comment.', FLASH_ERROR)

    return redirect(url_for('admin.manage_comments'))


# ==================== Event Management ====================

@admin_bp.route('/events')
@login_required
@admin_required
def manage_events():
    """Display all events for management."""
    events = Event.query.order_by(Event.event_date.asc(), Event.event_time.asc()).all()
    return render_template('admin/events.html', events=events)


@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    """Create a new event."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        presenter = request.form.get('presenter')
        event_url = request.form.get('event_url')
        event_date = EventService.parse_event_date(request.form.get('event_date'))
        event_time = EventService.parse_event_time(request.form.get('event_time'))

        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_url = save_event_image(file, current_app.root_path)

        try:
            event = EventService.create_event(
                title=title,
                description=description,
                presenter=presenter,
                event_url=event_url,
                event_date=event_date,
                event_time=event_time,
                image_url=image_url,
                created_by=current_user.id
            )

            # Send email notification to all users
            try:
                success_count, failure_count = send_event_notification(event)
                if success_count > 0:
                    flash(f'Event created successfully. Notifications sent to {success_count} users.', FLASH_SUCCESS)
                else:
                    flash('Event created successfully, but no email notifications were sent.', FLASH_WARNING)
            except Exception as e:
                current_app.logger.error(f"Failed to send event notification: {str(e)}")
                flash('Event created successfully, but email notifications failed.', FLASH_WARNING)

            return redirect(url_for('admin.manage_events'))
        except Exception:
            db.session.rollback()
            flash('Error creating event.', FLASH_ERROR)

    return render_template('admin/create_event.html')


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Edit an event."""
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.presenter = request.form.get('presenter')
        event.event_url = request.form.get('event_url')
        event.event_date = EventService.parse_event_date(request.form.get('event_date'))
        event.event_time = EventService.parse_event_time(request.form.get('event_time'))

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Delete old image if exists
                if event.image_url:
                    old_file_path = get_event_image_path(event.image_url, current_app.root_path)
                    delete_file(old_file_path)

                event.image_url = save_event_image(file, current_app.root_path)

        try:
            db.session.commit()
            flash('Event updated successfully.', FLASH_SUCCESS)
            return redirect(url_for('admin.manage_events'))
        except Exception:
            db.session.rollback()
            flash('Error updating event.', FLASH_ERROR)

    return render_template('admin/edit_event.html', event=event)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Delete an event."""
    event = Event.query.get_or_404(event_id)

    try:
        # Delete associated image file if exists
        if event.image_url:
            file_path = get_event_image_path(event.image_url, current_app.root_path)
            delete_file(file_path)

        EventService.delete_event(event)
        flash('Event deleted successfully.', FLASH_SUCCESS)
    except Exception:
        db.session.rollback()
        flash('Error deleting event.', FLASH_ERROR)

    return redirect(url_for('admin.manage_events'))


# ==================== Research Submission Management ====================

@admin_bp.route('/submissions')
@login_required
@admin_required
def manage_submissions():
    """Manage research submissions pending approval."""
    page = request.args.get('page', 1, type=int)
    pagination = ResearchService.get_pending_submissions(page=page, per_page=15)
    
    return render_template('admin/submissions.html', pagination=pagination)


@admin_bp.route('/submissions/<int:research_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_submission(research_id):
    """Approve a research submission."""
    research = ResearchService.get_research_by_id(research_id)
    if not research:
        flash('Research not found.', FLASH_ERROR)
        return redirect(url_for('admin.manage_submissions'))
    
    if research.is_approved:
        flash('This research is already approved.', FLASH_WARNING)
        return redirect(url_for('admin.manage_submissions'))
    
    # Store submitter info before approval
    submitter = research.submitted_by_user
    
    # Approve the research
    approved_research = ResearchService.approve_research(research_id)
    
    # Send notification to the submitter if they exist
    if submitter:
        try:
            send_research_approved_notification(
                user=submitter,
                research=approved_research,
                send_email_func=send_research_status_email
            )
        except Exception as e:
            # Log the error but don't fail the approval
            current_app.logger.error(f"Failed to send approval notification: {str(e)}")
    
    flash(f'Research "{approved_research.title}" has been approved.', FLASH_SUCCESS)
    return redirect(url_for('admin.manage_submissions'))


@admin_bp.route('/submissions/<int:research_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_submission(research_id):
    """Reject (delete) a research submission."""
    research = ResearchService.get_research_by_id(research_id)
    if not research:
        flash('Research not found.', FLASH_ERROR)
        return redirect(url_for('admin.manage_submissions'))
    
    # Store info before rejection
    title = research.title
    submitter = research.submitted_by_user
    reason = request.form.get('reason', '').strip()  # Optional rejection reason
    
    # Reject (delete) the research
    success = ResearchService.reject_research(research_id)
    
    if success:
        # Send notification to the submitter if they exist
        if submitter:
            try:
                send_research_rejected_notification(
                    user=submitter,
                    research_title=title,
                    reason=reason if reason else None,
                    send_email_func=send_research_status_email
                )
            except Exception as e:
                # Log the error but don't fail the rejection
                current_app.logger.error(f"Failed to send rejection notification: {str(e)}")
        
        flash(f'Research "{title}" has been rejected and removed.', FLASH_SUCCESS)
    else:
        flash('Failed to reject research.', FLASH_ERROR)
    
    return redirect(url_for('admin.manage_submissions'))


# ==================== Researcher Management ====================

@admin_bp.route('/researchers')
@login_required
@admin_required
def manage_researchers():
    """Manage researchers."""
    researchers = ResearchService.get_all_researchers()
    return render_template('admin/researchers.html', researchers=researchers)


@admin_bp.route('/researchers/<int:researcher_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_researcher(researcher_id):
    """Edit a researcher's information."""
    researcher = ResearchService.get_researcher_by_id(researcher_id)
    if not researcher:
        flash('Researcher not found.', FLASH_ERROR)
        return redirect(url_for('admin.manage_researchers'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        
        if name:
            updated = ResearchService.update_researcher(researcher_id, name=name, bio=bio)
            if updated:
                flash('Researcher updated successfully.', FLASH_SUCCESS)
                return redirect(url_for('admin.manage_researchers'))
            else:
                flash('Failed to update researcher.', FLASH_ERROR)
        else:
            flash('Name is required.', FLASH_ERROR)
    
    return render_template('admin/edit_researcher.html', researcher=researcher)


@admin_bp.route('/researchers/<int:researcher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_researcher(researcher_id):
    """Delete a researcher and all their researches."""
    success = ResearchService.delete_researcher(researcher_id)
    
    if success:
        flash('Researcher and all their researches have been deleted.', FLASH_SUCCESS)
    else:
        flash('Failed to delete researcher.', FLASH_ERROR)
    
    return redirect(url_for('admin.manage_researchers'))


# ==================== Research Management ====================

@admin_bp.route('/researches')
@login_required
@admin_required
def manage_researches():
    """Manage all approved researches."""
    page = request.args.get('page', 1, type=int)
    pagination = ResearchService.filter_researches(page=page, per_page=20)
    
    return render_template('admin/researches.html', pagination=pagination)


@admin_bp.route('/researches/<int:research_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_research(research_id):
    """Edit a research's information."""
    research = ResearchService.get_research_by_id(research_id)
    if not research:
        flash('Research not found.', FLASH_ERROR)
        return redirect(url_for('admin.manage_researches'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        department = request.form.get('department')
        year = request.form.get('year', type=int)
        doi_url = request.form.get('doi_url')
        researcher_type = request.form.get('researcher_type')
        
        if title and department and year:
            updated = ResearchService.update_research(
                research_id,
                title=title,
                department=department,
                year=year,
                doi_url=doi_url,
                researcher_type=researcher_type
            )
            if updated:
                flash('Research updated successfully.', FLASH_SUCCESS)
                return redirect(url_for('admin.manage_researches'))
            else:
                flash('Failed to update research.', FLASH_ERROR)
        else:
            flash('Title, department, and year are required.', FLASH_ERROR)
    
    return render_template('admin/edit_research.html', research=research)


@admin_bp.route('/researches/<int:research_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_research(research_id):
    """Delete a research."""
    success = ResearchService.delete_research(research_id)
    
    if success:
        flash('Research has been deleted.', FLASH_SUCCESS)
    else:
        flash('Failed to delete research.', FLASH_ERROR)
    
    return redirect(url_for('admin.manage_researches'))


# ==================== Announcement Management ====================

@admin_bp.route('/announcements')
@login_required
@admin_required
def manage_announcements():
    """Display all sent announcements with pagination."""
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.order_by(Announcement.created_at.desc()).paginate(
        page=page, per_page=DEFAULT_PER_PAGE, error_out=False
    )
    return render_template('admin/announcements.html', pagination=pagination)


@admin_bp.route('/announcements/send', methods=['GET', 'POST'])
@login_required
@admin_required
def send_announcement():
    """Compose and send a new announcement to users."""
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        target_status = request.form.getlist('target_status')
        members_only = request.form.get('members_only') == 'on'
        
        if not subject or not body:
            flash('Subject and body are required.', FLASH_ERROR)
            return redirect(url_for('admin.send_announcement'))
        
        query = User.query.filter(User.email.isnot(None))
        
        if target_status:
            from models import UserRole
            target_roles = []
            if 'student' in target_status or 'undergraduate' in target_status:
                target_roles.append(UserRole.STUDENT)
            if 'alumni' in target_status:
                target_roles.append(UserRole.ALUMNI)
            if 'researcher' in target_status:
                target_roles.append(UserRole.RESEARCHER)
            if target_roles:
                query = query.filter(User.role.in_(target_roles))
        
        if members_only:
            query = query.filter(User.is_member == True)
        
        recipients = query.all()
        
        if not recipients:
            flash('No users match the selected criteria.', FLASH_WARNING)
            return redirect(url_for('admin.send_announcement'))
        
        target_filter = json.dumps({
            'status': target_status,
            'members_only': members_only
        })
        
        announcement = Announcement(
            subject=subject,
            body=body,
            target_filter=target_filter,
            recipient_count=len(recipients),
            created_by=current_user.id
        )
        
        try:
            db.session.add(announcement)
            db.session.commit()
            
            success_count, failure_count, error_msg = send_announcement_email(announcement, recipients)
            
            announcement.success_count = success_count
            announcement.failure_count = failure_count
            db.session.commit()
            
            if success_count > 0:
                flash(f'Announcement sent successfully to {success_count} users.', FLASH_SUCCESS)
            if failure_count > 0:
                if error_msg:
                    flash(f'Failed to send to {failure_count} users. Error: {error_msg}', FLASH_ERROR)
                else:
                    flash(f'Failed to send to {failure_count} users.', FLASH_WARNING)
            if success_count == 0 and failure_count == 0 and error_msg:
                flash(f'Announcement saved but email not sent: {error_msg}', FLASH_ERROR)
            
            return redirect(url_for('admin.manage_announcements'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to send announcement: {str(e)}")
            flash(f'Failed to send announcement: {str(e)}', FLASH_ERROR)
    
    mail_configured, mail_error = is_mail_configured()
    return render_template('admin/send_announcement.html', mail_configured=mail_configured, mail_error=mail_error)
