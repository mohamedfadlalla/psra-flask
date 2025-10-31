from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import os
from datetime import datetime
from . import forum_bp
from .forms import LoginForm, RegisterForm, PostForm, CommentForm, ProfileForm, PasswordChangeForm, MessageForm
from models import db, User, Post, Comment, Like, Message

@forum_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('forum.forum_main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('forum.forum_main'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@forum_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('forum.forum_main'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.strip(),
            name=form.name.data,
            phone_number=form.phone_number.data,
            whatsapp_number=form.whatsapp_number.data
        )
        user.is_member = form.is_member.data
        user.batch_number = None
        if form.is_member.data:
            user.status = 'undergraduate'
        else:
            user.status = 'student'
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('forum.login'))
    return render_template('register.html', form=form)

@forum_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@forum_bp.route('/terms')
def terms():
    return render_template('forum_terms.html')

@forum_bp.route('/')
def forum_main():
    category = request.args.get('category')
    search = request.args.get('search')
    query = Post.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    posts = query.order_by(Post.created_at.desc()).all()

    if request.headers.get('Accept') == 'application/json':
        # Return JSON for AJAX requests
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                'author': post.author.name,
                'created_at': post.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'likes': len(post.likes),
                'comments': len(post.comments),
                'category': post.category
            })
        return {'posts': posts_data, 'selected_category': category or 'All Discussions'}

    return render_template('forum_main.html', posts=posts, selected_category=category, search=search)

@forum_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(user_id=current_user.id, category=form.category.data, title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('forum.post_detail', post_id=post.id))
    return render_template('create_post.html', form=form)

@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    form = CommentForm()
    return render_template('post_detail.html', post=post, comments=comments, form=form)

@forum_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(post_id=post_id, user_id=current_user.id, content=form.content.data)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('forum.post_detail', post_id=post_id))

@forum_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
    db.session.commit()
    return {'likes': len(Post.query.get(post_id).likes)}

@forum_bp.route('/profile')
@login_required
def profile():
    import json

    # Parse JSON data for template
    experience_entries = []
    education_entries = []

    if current_user.experience:
        try:
            experience_entries = json.loads(current_user.experience)
        except (json.JSONDecodeError, TypeError):
            experience_entries = []

    if current_user.education:
        try:
            education_entries = json.loads(current_user.education)
        except (json.JSONDecodeError, TypeError):
            education_entries = []

    # Combine experience and education into chronological timeline
    combined_experience = []
    for entry in experience_entries:
        entry['type'] = 'work'
        combined_experience.append(entry)
    for entry in education_entries:
        entry['type'] = 'education'
        combined_experience.append(entry)

    # Sort by start_date descending (most recent first)
    combined_experience.sort(key=lambda x: x.get('start_date', ''), reverse=True)

    return render_template('profile.html', experience_entries=combined_experience)

@forum_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()

    # Pre-populate profile form with current user data
    if request.method == 'GET':
        profile_form.name.data = current_user.name
        profile_form.headline.data = current_user.headline
        profile_form.location.data = current_user.location
        profile_form.about.data = current_user.about
        profile_form.batch_number.data = str(current_user.batch_number) if current_user.batch_number else None
        profile_form.email.data = current_user.email
        profile_form.phone_number.data = current_user.phone_number
        profile_form.whatsapp_number.data = current_user.whatsapp_number
        profile_form.skills.data = current_user.skills
        # Convert JSON data to form data for editing
        import json
        if current_user.education:
            try:
                education_entries = json.loads(current_user.education)
                profile_form.education_data.data = json.dumps(education_entries)
            except (json.JSONDecodeError, TypeError):
                # Handle legacy text data or empty data
                profile_form.education_data.data = '[]'
        else:
            profile_form.education_data.data = '[]'

        if current_user.experience:
            try:
                experience_entries = json.loads(current_user.experience)
                profile_form.experience_data.data = json.dumps(experience_entries)
            except (json.JSONDecodeError, TypeError):
                # Handle legacy text data or empty data
                profile_form.experience_data.data = '[]'
        else:
            profile_form.experience_data.data = '[]'
        profile_form.linkedin_url.data = current_user.linkedin_url
        profile_form.website_url.data = current_user.website_url
        profile_form.languages.data = current_user.languages
        profile_form.certifications.data = current_user.certifications
        profile_form.projects.data = current_user.projects
        profile_form.publications.data = current_user.publications
        profile_form.professional_summary.data = current_user.professional_summary

    # Handle profile form submission
    if profile_form.submit.data and profile_form.validate_on_submit():
        current_user.name = profile_form.name.data
        current_user.headline = profile_form.headline.data
        current_user.location = profile_form.location.data
        current_user.about = profile_form.about.data
        current_user.batch_number = int(profile_form.batch_number.data)
        current_user.phone_number = profile_form.phone_number.data
        current_user.whatsapp_number = profile_form.whatsapp_number.data
        current_user.skills = profile_form.skills.data
        # Store JSON data from form
        current_user.education = profile_form.education_data.data or '[]'
        current_user.experience = profile_form.experience_data.data or '[]'
        current_user.linkedin_url = profile_form.linkedin_url.data
        current_user.website_url = profile_form.website_url.data
        current_user.languages = profile_form.languages.data
        current_user.certifications = profile_form.certifications.data
        current_user.projects = profile_form.projects.data
        current_user.publications = profile_form.publications.data
        current_user.professional_summary = profile_form.professional_summary.data

        # Handle cover photo upload
        if profile_form.cover_photo.data:
            cover_file = profile_form.cover_photo.data
            cover_filename = secure_filename(f"{current_user.id}_cover_{cover_file.filename}")
            cover_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], cover_filename)

            # Ensure the upload directory exists
            os.makedirs(os.path.dirname(cover_path), exist_ok=True)

            # Resize and save cover photo
            try:
                cover_image = Image.open(cover_file)
                # Convert to RGB if necessary
                if cover_image.mode in ("RGBA", "P"):
                    cover_image = cover_image.convert("RGB")
                # Resize cover photo to LinkedIn-like dimensions (1200x300 or similar)
                cover_image.thumbnail((1200, 400), Image.Resampling.LANCZOS)
                cover_image.save(cover_path, quality=85)

                # Update user cover photo URL
                current_user.cover_photo_url = url_for('static', filename=f'profile_images/{cover_filename}')
            except Exception as e:
                # If image processing fails, continue without cover photo
                print(f"Error processing cover photo: {e}")
                pass

        # Handle profile picture upload
        if profile_form.profile_picture.data:
            profile_file = profile_form.profile_picture.data
            profile_filename = secure_filename(f"{current_user.id}_profile_{profile_file.filename}")
            profile_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], profile_filename)

            # Ensure the upload directory exists
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)

            # Resize and save profile picture
            try:
                profile_image = Image.open(profile_file)
                # Convert to RGB if necessary
                if profile_image.mode in ("RGBA", "P"):
                    profile_image = profile_image.convert("RGB")
                # Create a square image for profile picture
                size = min(profile_image.size)
                # Crop to square from center
                left = (profile_image.width - size) // 2
                top = (profile_image.height - size) // 2
                right = left + size
                bottom = top + size
                profile_image = profile_image.crop((left, top, right, bottom))
                # Resize to 150x150
                profile_image = profile_image.resize((150, 150), Image.Resampling.LANCZOS)
                profile_image.save(profile_path, quality=85)

                # Update user profile picture URL
                current_user.profile_picture_url = url_for('static', filename=f'profile_images/{profile_filename}')
            except Exception as e:
                # If image processing fails, continue without profile picture
                print(f"Error processing profile picture: {e}")
                pass

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('forum.profile'))

    # Handle password form submission
    if password_form.submit.data and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Current password is incorrect.', 'error')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('forum.profile'))

    return render_template('edit_profile.html', profile_form=profile_form, password_form=password_form)

@forum_bp.route('/messages')
@login_required
def messages():
    # Get all users who have messaged with current user
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()

    # Get unique user IDs for conversations
    user_ids = set()
    for msg in sent_messages:
        user_ids.add(msg.receiver_id)
    for msg in received_messages:
        user_ids.add(msg.sender_id)

    # Get conversation data
    conversations = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            # Get latest message between current user and this user
            latest_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
                ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()

            # Count unread messages from this user
            unread_count = Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).count()

            conversations.append({
                'user': user,
                'latest_message': latest_message,
                'unread_count': unread_count
            })

    # Sort by latest message timestamp
    conversations.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else datetime.min, reverse=True)

    return render_template('messages.html', conversations=conversations)

@forum_bp.route('/messages/send/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    recipient = User.query.get_or_404(user_id)
    if recipient.id == current_user.id:
        flash('You cannot send messages to yourself.', 'error')
        return redirect(url_for('forum.messages'))

    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=user_id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('forum.conversation', user_id=user_id))

    return render_template('send_message.html', form=form, recipient=recipient)

@forum_bp.route('/messages/send', methods=['GET', 'POST'])
@login_required
def send_message_by_username():
    username = request.args.get('username')
    recipient = None
    if username:
        recipient = User.query.filter_by(name=username).first() or User.query.filter_by(email=username).first()

    form = MessageForm()
    if form.validate_on_submit():
        if not recipient:
            flash('User not found.', 'error')
            return redirect(url_for('forum.send_message_by_username'))

        if recipient.id == current_user.id:
            flash('You cannot send messages to yourself.', 'error')
            return redirect(url_for('forum.messages'))

        message = Message(sender_id=current_user.id, receiver_id=recipient.id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('forum.conversation', user_id=recipient.id))

    return render_template('send_message.html', form=form, recipient=recipient, search_mode=True)

@forum_bp.route('/messages/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    if other_user.id == current_user.id:
        flash('You cannot view messages with yourself.', 'error')
        return redirect(url_for('forum.messages'))

    # Get all messages between current user and other user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    # Mark received messages as read
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
    db.session.commit()

    # Group messages by date for date markers
    from collections import defaultdict
    messages_by_date = defaultdict(list)

    for message in messages:
        date_key = message.created_at.date()
        messages_by_date[date_key].append(message)

    # Convert to list of tuples for template
    grouped_messages = []
    for date_key in sorted(messages_by_date.keys()):
        grouped_messages.append((date_key, messages_by_date[date_key]))

    form = MessageForm()
    today = datetime.now().date()
    return render_template('conversation.html', grouped_messages=grouped_messages, other_user=other_user, form=form, today=today)

@forum_bp.route('/messages/reply/<int:user_id>', methods=['POST'])
@login_required
def reply_message(user_id):
    other_user = User.query.get_or_404(user_id)
    if other_user.id == current_user.id:
        flash('You cannot send messages to yourself.', 'error')
        return redirect(url_for('forum.messages'))

    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=user_id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')

    return redirect(url_for('forum.conversation', user_id=user_id))

@forum_bp.route('/messages/delete/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)

    # Check if user owns this message
    if message.sender_id != current_user.id:
        return {'error': 'You can only delete your own messages'}, 403

    # Store conversation partner for notification
    other_user_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id

    # Delete the message
    db.session.delete(message)
    db.session.commit()

    # Notify the other user about the deletion
    # This would be sent via SocketIO in a real implementation

    return {'success': True, 'message_id': message_id}

@forum_bp.route('/messages/delete_conversation/<int:user_id>', methods=['DELETE'])
@login_required
def delete_conversation(user_id):
    other_user = User.query.get_or_404(user_id)

    # Delete all messages between current user and other user
    Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).delete()

    db.session.commit()

    # Notify the other user about conversation deletion
    # This would be sent via SocketIO in a real implementation

    return {'success': True, 'deleted_conversation_with': user_id}
