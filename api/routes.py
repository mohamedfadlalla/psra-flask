from flask import request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import os
import jwt
import datetime
from functools import wraps
from . import api_bp
from models import db, User, Post, Comment, Like, Event, Message
from forum.forms import LoginForm, RegisterForm, PostForm, CommentForm, ProfileForm

# Enable CORS for all API routes
CORS(api_bp)

# JWT Secret Key
JWT_SECRET_KEY = 'your-jwt-secret-key-change-in-production'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication Routes
@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email'].strip()).first()
    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, JWT_SECRET_KEY, algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'profile_picture_url': user.profile_picture_url
            }
        })

    return jsonify({'message': 'Invalid email or password'}), 401

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['email', 'name', 'password', 'phone_number', 'whatsapp_number']

    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email'].strip()).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(
        email=data['email'].strip(),
        name=data['name'],
        phone_number=data['phone_number'],
        whatsapp_number=data['whatsapp_number']
    )
    user.is_member = data.get('is_member', False)
    user.status = 'undergraduate' if user.is_member else 'student'
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET_KEY, algorithm='HS256')

    return jsonify({
        'message': 'Account created successfully',
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 201

@api_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    # In JWT, logout is handled client-side by removing the token
    return jsonify({'message': 'Logged out successfully'})

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone_number': current_user.phone_number,
            'whatsapp_number': current_user.whatsapp_number,
            'is_member': current_user.is_member,
            'status': current_user.status,
            'headline': current_user.headline,
            'location': current_user.location,
            'about': current_user.about,
            'skills': current_user.skills,
            'linkedin_url': current_user.linkedin_url,
            'website_url': current_user.website_url,
            'languages': current_user.languages,
            'certifications': current_user.certifications,
            'projects': current_user.projects,
            'publications': current_user.publications,
            'professional_summary': current_user.professional_summary,
            'profile_picture_url': current_user.profile_picture_url,
            'cover_photo_url': current_user.cover_photo_url,
            'is_admin': current_user.is_admin,
            'created_at': current_user.created_at.isoformat()
        }
    })

# Forum Routes
@api_bp.route('/forum/posts', methods=['GET'])
def get_posts():
    category = request.args.get('category')
    search = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = Post.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))

    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page)

    posts_data = []
    for post in posts.items:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_picture_url': post.author.profile_picture_url
            },
            'created_at': post.created_at.isoformat(),
            'likes_count': len(post.likes),
            'comments_count': len(post.comments),
            'image_url': post.image_url
        })

    return jsonify({
        'posts': posts_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': posts.total,
            'pages': posts.pages,
            'has_next': posts.has_next,
            'has_prev': posts.has_prev
        }
    })

@api_bp.route('/forum/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()

    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'name': comment.author.name,
                'profile_picture_url': comment.author.profile_picture_url
            },
            'created_at': comment.created_at.isoformat()
        })

    return jsonify({
        'post': {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'profile_picture_url': post.author.profile_picture_url
            },
            'created_at': post.created_at.isoformat(),
            'likes_count': len(post.likes),
            'comments_count': len(post.comments),
            'image_url': post.image_url
        },
        'comments': comments_data
    })

@api_bp.route('/forum/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content') or not data.get('category'):
        return jsonify({'message': 'Title, content, and category are required'}), 400

    post = Post(
        user_id=current_user.id,
        category=data['category'],
        title=data['title'],
        content=data['content'],
        image_url=data.get('image_url')
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({
        'message': 'Post created successfully',
        'post': {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'author': {
                'id': current_user.id,
                'name': current_user.name
            },
            'created_at': post.created_at.isoformat()
        }
    }), 201

@api_bp.route('/forum/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, post_id):
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'message': 'Content is required'}), 400

    post = Post.query.get_or_404(post_id)
    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=data['content']
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'message': 'Comment added successfully',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': current_user.id,
                'name': current_user.name,
                'profile_picture_url': current_user.profile_picture_url
            },
            'created_at': comment.created_at.isoformat()
        }
    }), 201

@api_bp.route('/forum/posts/<int:post_id>/like', methods=['POST'])
@token_required
def toggle_like(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        liked = True

    db.session.commit()

    return jsonify({
        'liked': liked,
        'likes_count': len(post.likes)
    })

# Events Routes
@api_bp.route('/events', methods=['GET'])
def get_events():
    from datetime import datetime, date

    today = date.today()
    now = datetime.now().time()

    # Get live events
    live_events = Event.query.filter(
        (Event.event_date == today) & (Event.event_time > now) & (Event.event_time.isnot(None))
    ).filter(Event.is_archived == False).order_by(Event.event_time.asc()).all()

    # Get upcoming events
    upcoming_events = Event.query.filter(Event.event_date > today).filter(Event.is_archived == False).order_by(Event.event_date.asc(), Event.event_time.asc()).all()

    # Get archived events
    archived_events = Event.query.filter(Event.is_archived == True).order_by(Event.event_date.desc(), Event.event_time.desc()).all()

    def format_event(event):
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_date': event.event_date.isoformat(),
            'event_time': event.event_time.isoformat() if event.event_time else None,
            'image_url': event.image_url,
            'presenter': event.presenter,
            'event_url': event.event_url,
            'is_archived': event.is_archived,
            'creator': {
                'id': event.creator.id,
                'name': event.creator.name
            },
            'created_at': event.created_at.isoformat()
        }

    return jsonify({
        'live_events': [format_event(event) for event in live_events],
        'upcoming_events': [format_event(event) for event in upcoming_events],
        'archived_events': [format_event(event) for event in archived_events]
    })

@api_bp.route('/events/next', methods=['GET'])
def get_next_event():
    from datetime import datetime, date

    today = date.today()
    next_event = Event.query.filter(
        (Event.event_date > today) |
        ((Event.event_date == today) & (Event.event_time > datetime.now().time()) & (Event.event_time.isnot(None)))
    ).order_by(Event.event_date.asc(), Event.event_time.asc()).first()

    if next_event:
        event_datetime = datetime.combine(next_event.event_date, next_event.event_time) if next_event.event_time else datetime.combine(next_event.event_date, datetime.min.time())
        return jsonify({
            'title': next_event.title,
            'description': next_event.description,
            'event_datetime': event_datetime.isoformat(),
            'has_time': next_event.event_time is not None,
            'image_url': next_event.image_url
        })

    return jsonify({'no_event': True})

# Messages Routes
@api_bp.route('/messages/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
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
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'profile_picture_url': user.profile_picture_url
                },
                'latest_message': {
                    'content': latest_message.content if latest_message else None,
                    'created_at': latest_message.created_at.isoformat() if latest_message else None,
                    'is_from_me': latest_message.sender_id == current_user.id if latest_message else False
                } if latest_message else None,
                'unread_count': unread_count
            })

    # Sort by latest message timestamp
    conversations.sort(key=lambda x: x['latest_message']['created_at'] if x['latest_message'] else '', reverse=True)

    return jsonify({'conversations': conversations})

@api_bp.route('/messages/conversation/<int:user_id>', methods=['GET'])
@token_required
def get_conversation(current_user, user_id):
    other_user = User.query.get_or_404(user_id)

    # Get all messages between current user and other user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    # Mark received messages as read
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
            message.read_at = datetime.datetime.utcnow()
    db.session.commit()

    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat(),
            'is_from_me': message.sender_id == current_user.id
        })

    return jsonify({
        'other_user': {
            'id': other_user.id,
            'name': other_user.name,
            'profile_picture_url': other_user.profile_picture_url
        },
        'messages': messages_data
    })

@api_bp.route('/messages/send/<int:user_id>', methods=['POST'])
@token_required
def send_message(current_user, user_id):
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'message': 'Content is required'}), 400

    recipient = User.query.get_or_404(user_id)
    if recipient.id == current_user.id:
        return jsonify({'message': 'You cannot send messages to yourself'}), 400

    message = Message(
        sender_id=current_user.id,
        receiver_id=user_id,
        content=data['content']
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({
        'message': 'Message sent successfully',
        'message_data': {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'created_at': message.created_at.isoformat(),
            'is_from_me': True
        }
    }), 201

# Profile Routes
@api_bp.route('/profile/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()

    # Update basic profile fields
    current_user.name = data.get('name', current_user.name)
    current_user.headline = data.get('headline', current_user.headline)
    current_user.location = data.get('location', current_user.location)
    current_user.about = data.get('about', current_user.about)
    current_user.phone_number = data.get('phone_number', current_user.phone_number)
    current_user.whatsapp_number = data.get('whatsapp_number', current_user.whatsapp_number)
    current_user.skills = data.get('skills', current_user.skills)
    current_user.education = data.get('education', current_user.education)
    current_user.experience = data.get('experience', current_user.experience)
    current_user.linkedin_url = data.get('linkedin_url', current_user.linkedin_url)
    current_user.website_url = data.get('website_url', current_user.website_url)
    current_user.languages = data.get('languages', current_user.languages)
    current_user.certifications = data.get('certifications', current_user.certifications)
    current_user.projects = data.get('projects', current_user.projects)
    current_user.publications = data.get('publications', current_user.publications)
    current_user.professional_summary = data.get('professional_summary', current_user.professional_summary)

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'headline': current_user.headline,
            'location': current_user.location,
            'about': current_user.about,
            'skills': current_user.skills,
            'linkedin_url': current_user.linkedin_url,
            'website_url': current_user.website_url,
            'languages': current_user.languages,
            'certifications': current_user.certifications,
            'projects': current_user.projects,
            'publications': current_user.publications,
            'professional_summary': current_user.professional_summary,
            'profile_picture_url': current_user.profile_picture_url,
            'cover_photo_url': current_user.cover_photo_url
        }
    })

# Static Pages Data
@api_bp.route('/pages/home', methods=['GET'])
def get_home_data():
    # Fetch recent comments for display on home page
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()

    comments_data = []
    for comment in recent_comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content[:200] + '...' if len(comment.content) > 200 else comment.content,
            'author': {
                'id': comment.author.id,
                'name': comment.author.name,
                'profile_picture_url': comment.author.profile_picture_url
            },
            'post': {
                'id': comment.post.id,
                'title': comment.post.title
            },
            'created_at': comment.created_at.isoformat()
        })

    return jsonify({
        'recent_comments': comments_data
    })

# Admin Routes
@api_bp.route('/admin/posts', methods=['GET'])
@token_required
def get_admin_posts(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403

    posts = Post.query.order_by(Post.created_at.desc()).all()
    posts_data = []

    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
            'category': post.category,
            'author': post.author.name,
            'created_at': post.created_at.isoformat(),
            'likes_count': len(post.likes),
            'comments_count': len(post.comments)
        })

    return jsonify({'posts': posts_data})

@api_bp.route('/admin/comments', methods=['GET'])
@token_required
def get_admin_comments(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403

    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    comments_data = []

    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
            'author': comment.author.name,
            'post_title': comment.post.title,
            'created_at': comment.created_at.isoformat()
        })

    return jsonify({'comments': comments_data})

@api_bp.route('/admin/events', methods=['GET'])
@token_required
def get_admin_events(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403

    events = Event.query.order_by(Event.created_at.desc()).all()
    events_data = []

    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.description[:100] + '...' if event.description and len(event.description) > 100 else event.description,
            'event_date': event.event_date.isoformat(),
            'event_time': event.event_time.isoformat() if event.event_time else None,
            'is_archived': event.is_archived,
            'creator': event.creator.name,
            'created_at': event.created_at.isoformat()
        })

    return jsonify({'events': events_data})
