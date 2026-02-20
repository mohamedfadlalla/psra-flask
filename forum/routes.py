"""
Forum Routes Module

Routes for forum functionality including posts, comments, profiles, and messaging.
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import json

from . import forum_bp
from .forms import LoginForm, RegisterForm, PostForm, CommentForm, ProfileForm, PasswordChangeForm, MessageForm
from models import db, User, UserRole, Profile, StudentProfile, AlumniProfile, ResearcherProfile, Post, Comment, Like, Message
from utils import get_user_timeline, safe_json_parse, FLASH_SUCCESS, FLASH_ERROR
from utils.image_utils import process_profile_picture
from services import MessageService, UserService


def resolve_role_and_track(account_type, batch_number):
    """Resolve canonical role/track with graduation rule.

    Business rule:
    - Any graduate is alumni
    - Any student with batch <= 54 is alumni
    """
    batch = int(batch_number) if batch_number else None

    if account_type == 'researcher':
        return UserRole.RESEARCHER, None

    if account_type in ('graduate', 'alumni'):
        return UserRole.ALUMNI, 'graduate'

    if batch is not None and batch <= 54:
        return UserRole.ALUMNI, 'graduate'

    return UserRole.STUDENT, 'undergraduate'


# ==================== Authentication Routes ====================

@forum_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('forum.forum_main'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('forum.forum_main'))
        flash('Invalid email or password.', FLASH_ERROR)
    
    return render_template('login.html', form=form)


@forum_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('forum.forum_main'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        role, academic_level = resolve_role_and_track(form.account_type.data, form.batch_number.data)
        user = User(
            email=form.email.data.strip(),
            phone_number=form.phone_number.data,
            whatsapp_number=form.whatsapp_number.data
        )
        user.is_member = form.is_member.data
        user.batch_number = int(form.batch_number.data) if form.batch_number.data else None
        user.role = role
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.flush()

        profile = Profile(
            user_id=user.id,
            full_name=form.name.data
        )

        db.session.add(profile)

        if role == UserRole.STUDENT:
            db.session.add(StudentProfile(user_id=user.id, academic_level=academic_level))
        elif role == UserRole.ALUMNI:
            db.session.add(AlumniProfile(user_id=user.id, open_to_mentor=True, graduation_year=None))
        elif role == UserRole.RESEARCHER:
            db.session.add(ResearcherProfile(user_id=user.id, academic_rank=None, lab_name=None, office_location=None))

        db.session.commit()

        # Handle profile picture upload if provided
        if form.profile_picture.data:
            profile_url = process_profile_picture(
                form.profile_picture.data,
                user.id,
                current_app.config['UPLOAD_FOLDER'],
                current_app.root_path
            )
            if profile_url:
                user.profile_picture_url = profile_url
                db.session.commit()

        flash('Account created successfully! You can now log in.', FLASH_SUCCESS)
        return redirect(url_for('forum.login'))
    
    return render_template('register.html', form=form)


@forum_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('home'))


# ==================== Forum Routes ====================

@forum_bp.route('/terms')
def terms():
    """Display forum terms and conditions."""
    return render_template('forum_terms.html')


@forum_bp.route('/')
def forum_main():
    """Display main forum page with posts."""
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Post.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    
    posts = query.order_by(Post.created_at.desc()).all()

    # Return JSON for AJAX requests
    if request.headers.get('Accept') == 'application/json':
        posts_data = [{
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': post.author.name,
            'created_at': post.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'likes': len(post.likes),
            'comments': len(post.comments),
            'category': post.category
        } for post in posts]
        return {'posts': posts_data, 'selected_category': category or 'All Discussions'}

    return render_template('forum_main.html', posts=posts, selected_category=category, search=search)


@forum_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            user_id=current_user.id,
            category=form.category.data,
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('forum.post_detail', post_id=post.id))
    
    return render_template('create_post.html', form=form)


@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """Display a single post with comments."""
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    form = CommentForm()
    return render_template('post_detail.html', post=post, comments=comments, form=form)


@forum_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post."""
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            content=form.content.data
        )
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('forum.post_detail', post_id=post_id))


@forum_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Toggle like on a post."""
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
    db.session.commit()
    return {'likes': len(Post.query.get(post_id).likes)}


# ==================== Profile Routes ====================

@forum_bp.route('/profile')
@login_required
def profile():
    """Display current user's profile."""
    combined_experience = get_user_timeline(current_user)
    return render_template('profile.html', experience_entries=combined_experience)


@forum_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit current user's profile."""
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()

    # Pre-populate profile form with current user data
    if request.method == 'GET':
        form_data = UserService.get_profile_form_data(current_user)
        profile_form.name.data = form_data['name']
        profile_form.account_type.data = form_data['account_type']
        profile_form.headline.data = form_data['headline']
        profile_form.location.data = form_data['location']
        profile_form.about.data = form_data['about']
        profile_form.batch_number.data = form_data['batch_number']
        profile_form.email.data = form_data['email']
        profile_form.phone_number.data = form_data['phone_number']
        profile_form.whatsapp_number.data = form_data['whatsapp_number']
        profile_form.skills.data = form_data['skills']
        profile_form.education_data.data = json.dumps(form_data['education_data'])
        profile_form.experience_data.data = json.dumps(form_data['experience_data'])
        profile_form.linkedin_url.data = form_data['linkedin_url']
        profile_form.website_url.data = form_data['website_url']
        profile_form.languages.data = form_data['languages']
        profile_form.certifications.data = form_data['certifications']
        profile_form.projects.data = form_data['projects']
        profile_form.publications.data = form_data['publications']
        profile_form.professional_summary.data = form_data['professional_summary']
        profile_form.open_to_mentor.data = form_data['open_to_mentor']

    # Handle profile form submission
    if profile_form.submit.data and profile_form.validate_on_submit():
        role, academic_level = resolve_role_and_track(profile_form.account_type.data, profile_form.batch_number.data)

        # Update basic fields
        current_user.name = profile_form.name.data
        current_user.role = role
        current_user.headline = profile_form.headline.data
        current_user.location = profile_form.location.data
        current_user.about = profile_form.about.data
        current_user.batch_number = int(profile_form.batch_number.data) if profile_form.batch_number.data else None
        current_user.phone_number = profile_form.phone_number.data
        current_user.whatsapp_number = profile_form.whatsapp_number.data
        current_user.skills = profile_form.skills.data
        current_user.education = profile_form.education_data.data or '[]'
        current_user.experience = profile_form.experience_data.data or '[]'
        current_user.linkedin_url = profile_form.linkedin_url.data
        current_user.website_url = profile_form.website_url.data
        current_user.languages = profile_form.languages.data
        current_user.certifications = profile_form.certifications.data
        current_user.projects = profile_form.projects.data
        current_user.publications = profile_form.publications.data
        current_user.professional_summary = profile_form.professional_summary.data

        # Ensure role-specific profile records and mentorship preference are consistent
        if role == UserRole.STUDENT:
            student_profile = current_user.student_profile
            if not student_profile:
                student_profile = StudentProfile(user_id=current_user.id)
                db.session.add(student_profile)
            student_profile.academic_level = academic_level
        elif role == UserRole.ALUMNI:
            alumni_profile = current_user.alumni_profile
            if not alumni_profile:
                alumni_profile = AlumniProfile(user_id=current_user.id, open_to_mentor=True)
                db.session.add(alumni_profile)
            alumni_profile.open_to_mentor = bool(profile_form.open_to_mentor.data)
        elif role == UserRole.RESEARCHER:
            researcher_profile = current_user.researcher_profile
            if not researcher_profile:
                researcher_profile = ResearcherProfile(user_id=current_user.id)
                db.session.add(researcher_profile)
            researcher_profile.open_to_mentor = bool(profile_form.open_to_mentor.data)

        # Handle profile picture upload
        if profile_form.profile_picture.data:
            profile_url = process_profile_picture(
                profile_form.profile_picture.data,
                current_user.id,
                current_app.config['UPLOAD_FOLDER'],
                current_app.root_path
            )
            if profile_url:
                current_user.profile_picture_url = profile_url

        db.session.commit()
        flash('Profile updated successfully!', FLASH_SUCCESS)
        return redirect(url_for('forum.profile'))

    # Handle password form submission
    if password_form.submit.data and password_form.validate_on_submit():
        success, error = UserService.change_password(
            current_user,
            password_form.current_password.data,
            password_form.new_password.data
        )
        if success:
            flash('Password changed successfully!', FLASH_SUCCESS)
            return redirect(url_for('forum.profile'))
        else:
            flash(error, FLASH_ERROR)

    return render_template('edit_profile.html', profile_form=profile_form, password_form=password_form)


# ==================== Messaging Routes ====================

@forum_bp.route('/messages')
@login_required
def messages():
    """Display all conversations for current user."""
    conversations = MessageService.get_conversations(current_user.id)
    return render_template('messages.html', conversations=conversations)


@forum_bp.route('/messages/send/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    """Send a message to a specific user."""
    recipient = User.query.get_or_404(user_id)
    
    if recipient.id == current_user.id:
        flash('You cannot send messages to yourself.', FLASH_ERROR)
        return redirect(url_for('forum.messages'))

    form = MessageForm()
    if form.validate_on_submit():
        MessageService.send_message(current_user.id, user_id, form.content.data)
        flash('Message sent successfully!', FLASH_SUCCESS)
        return redirect(url_for('forum.conversation', user_id=user_id))

    return render_template('send_message.html', form=form, recipient=recipient)


@forum_bp.route('/messages/send', methods=['GET', 'POST'])
@login_required
def send_message_by_username():
    """Send a message by searching for a user."""
    username = request.args.get('username')
    recipient = None
    if username:
        from models import Profile
        recipient = User.query.join(Profile).filter(Profile.full_name == username).first() or User.query.filter_by(email=username).first()

    form = MessageForm()
    if form.validate_on_submit():
        if not recipient:
            flash('User not found.', FLASH_ERROR)
            return redirect(url_for('forum.send_message_by_username'))

        if recipient.id == current_user.id:
            flash('You cannot send messages to yourself.', FLASH_ERROR)
            return redirect(url_for('forum.messages'))

        MessageService.send_message(current_user.id, recipient.id, form.content.data)
        flash('Message sent successfully!', FLASH_SUCCESS)
        return redirect(url_for('forum.conversation', user_id=recipient.id))

    return render_template('send_message.html', form=form, recipient=recipient, search_mode=True)


@forum_bp.route('/messages/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    """Display conversation with a specific user."""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('You cannot view messages with yourself.', FLASH_ERROR)
        return redirect(url_for('forum.messages'))

    # Get grouped messages
    grouped_messages = MessageService.get_grouped_messages(current_user.id, user_id)
    
    # Mark received messages as read
    MessageService.mark_messages_as_read(current_user.id, user_id)

    form = MessageForm()
    today = datetime.now().date()
    return render_template('conversation.html', grouped_messages=grouped_messages, other_user=other_user, form=form, today=today)


@forum_bp.route('/messages/reply/<int:user_id>', methods=['POST'])
@login_required
def reply_message(user_id):
    """Reply to a conversation."""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('You cannot send messages to yourself.', FLASH_ERROR)
        return redirect(url_for('forum.messages'))

    form = MessageForm()
    if form.validate_on_submit():
        MessageService.send_message(current_user.id, user_id, form.content.data)
        flash('Message sent successfully!', FLASH_SUCCESS)

    return redirect(url_for('forum.conversation', user_id=user_id))


@forum_bp.route('/messages/delete/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete a message."""
    success, error = MessageService.delete_message(message_id, current_user.id)
    if success:
        return {'success': True, 'message_id': message_id}
    return {'error': error}, 403


@forum_bp.route('/messages/delete_conversation/<int:user_id>', methods=['DELETE'])
@login_required
def delete_conversation(user_id):
    """Delete all messages in a conversation."""
    count = MessageService.delete_conversation(current_user.id, user_id)
    return {'success': True, 'deleted_conversation_with': user_id, 'count': count}


# ==================== User Routes ====================

@forum_bp.route('/users')
@login_required
def users():
    """Display list of users with search."""
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    from models import Profile
    query = User.query.join(User.profile).filter(User.id != current_user.id)
    if search:
        query = query.filter(Profile.full_name.ilike(f'%{search}%'))

    users_pagination = query.order_by(Profile.full_name).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('users.html', users=users_pagination.items, search=search, pagination=users_pagination)


@forum_bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    """Display another user's profile."""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return redirect(url_for('forum.profile'))

    combined_experience = get_user_timeline(user)
    return render_template('user_profile.html', user=user, experience_entries=combined_experience)
