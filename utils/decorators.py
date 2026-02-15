"""
Decorators Module

Provides custom decorators for the application.
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator that requires the user to be an admin.
    
    Checks if the current user is authenticated and has admin privileges.
    If not, redirects to home page with an error message.
    
    Usage:
        @app.route('/admin/panel')
        @login_required
        @admin_required
        def admin_panel():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Decorator that requires the user to NOT be authenticated.
    
    Useful for login and registration pages where authenticated users
    should be redirected away.
    
    Usage:
        @app.route('/login')
        @anonymous_required
        def login():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('forum.forum_main'))
        return f(*args, **kwargs)
    return decorated_function


def owner_required(model, param_name='user_id'):
    """
    Decorator factory that requires the current user to own the resource.
    
    Args:
        model: The model class to query
        param_name: The URL parameter name for the resource ID
    
    Usage:
        @app.route('/profile/<int:user_id>/edit')
        @login_required
        @owner_required(User, 'user_id')
        def edit_profile(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get(param_name)
            if resource_id is None:
                flash('Resource not found.', 'error')
                return redirect(url_for('home'))
            
            resource = model.query.get(resource_id)
            if resource is None:
                flash('Resource not found.', 'error')
                return redirect(url_for('home'))
            
            # Check ownership - handle both direct user_id and user relationship
            owner_id = getattr(resource, 'user_id', None) or getattr(resource, 'id', None)
            if owner_id != current_user.id:
                flash('You do not have permission to access this resource.', 'error')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
