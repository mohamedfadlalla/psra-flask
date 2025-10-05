from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from . import forum_bp
from .forms import LoginForm, RegisterForm, PostForm, CommentForm, ProfileForm, PasswordChangeForm
from models import db, User, Post, Comment, Like

@forum_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('forum.forum_main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
            email=form.email.data,
            name=form.name.data,
            batch_number=int(form.batch_number.data),
            phone_number=form.phone_number.data,
            whatsapp_number=form.whatsapp_number.data
        )
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
    return render_template('profile.html')

@forum_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()

    # Pre-populate profile form with current user data
    if request.method == 'GET':
        profile_form.name.data = current_user.name
        profile_form.batch_number.data = str(current_user.batch_number) if current_user.batch_number else None
        profile_form.email.data = current_user.email
        profile_form.phone_number.data = current_user.phone_number
        profile_form.whatsapp_number.data = current_user.whatsapp_number

    # Handle profile form submission
    if profile_form.submit.data and profile_form.validate_on_submit():
        current_user.name = profile_form.name.data
        current_user.batch_number = int(profile_form.batch_number.data)
        current_user.phone_number = profile_form.phone_number.data
        current_user.whatsapp_number = profile_form.whatsapp_number.data
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
