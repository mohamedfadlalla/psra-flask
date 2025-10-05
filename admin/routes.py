from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Post, Comment, Event
from . import admin_bp
from datetime import datetime
import os
from werkzeug.utils import secure_filename

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics for dashboard
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

@admin_bp.route('/posts')
@login_required
@admin_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Get filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    author = request.args.get('author', '')

    query = Post.query

    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    if category:
        query = query.filter_by(category=category)
    if author:
        query = query.join(User).filter(User.name.contains(author))

    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # Get unique categories for filter dropdown
    categories = db.session.query(Post.category).distinct().all()
    categories = [cat[0] for cat in categories]

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
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.category = request.form.get('category')

        try:
            db.session.commit()
            flash('Post updated successfully.', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating post.', 'error')

    return render_template('admin/edit_post.html', post=post)

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting post.', 'error')

    return redirect(url_for('admin.manage_posts'))

@admin_bp.route('/comments')
@login_required
@admin_required
def manage_comments():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Get filter parameters
    search = request.args.get('search', '')
    author = request.args.get('author', '')

    query = Comment.query.join(Post).join(User, Comment.user_id == User.id)

    if search:
        query = query.filter(Comment.content.contains(search))
    if author:
        query = query.filter(User.name.contains(author))

    comments = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/comments.html',
                         comments=comments,
                         search=search,
                         author=author)

@admin_bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if request.method == 'POST':
        comment.content = request.form.get('content')

        try:
            db.session.commit()
            flash('Comment updated successfully.', 'success')
            return redirect(url_for('admin.manage_comments'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating comment.', 'error')

    return render_template('admin/edit_comment.html', comment=comment)

@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting comment.', 'error')

    return redirect(url_for('admin.manage_comments'))

@admin_bp.route('/events')
@login_required
@admin_required
def manage_events():
    events = Event.query.order_by(Event.event_date.asc(), Event.event_time.asc()).all()
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')

        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = filename

        try:
            event = Event(
                title=title,
                description=description,
                event_date=datetime.strptime(event_date, '%Y-%m-%d').date(),
                event_time=datetime.strptime(event_time, '%H:%M').time() if event_time else None,
                image_url=image_url,
                created_by=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully.', 'success')
            return redirect(url_for('admin.manage_events'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating event.', 'error')

    return render_template('admin/create_event.html')

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date()
        event_time = request.form.get('event_time')
        event.event_time = datetime.strptime(event_time, '%H:%M').time() if event_time else None

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Delete old image if exists
                if event.image_url:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.image_url)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                event.image_url = filename

        try:
            db.session.commit()
            flash('Event updated successfully.', 'success')
            return redirect(url_for('admin.manage_events'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating event.', 'error')

    return render_template('admin/edit_event.html', event=event)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    try:
        # Delete associated image file if exists
        if event.image_url:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.image_url)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting event.', 'error')

    return redirect(url_for('admin.manage_events'))

@admin_bp.route('/api/events')
@login_required
@admin_required
def get_events_json():
    events = Event.query.all()
    events_data = []

    for event in events:
        event_datetime = datetime.combine(event.event_date, event.event_time) if event.event_time else datetime.combine(event.event_date, datetime.min.time())
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event_datetime.isoformat(),
            'description': event.description,
            'allDay': event.event_time is None
        })

    return jsonify(events_data)
