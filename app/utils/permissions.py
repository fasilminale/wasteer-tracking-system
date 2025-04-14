from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import User


def permission_required(permission_code):
    """
    Decorator to require a specific permission for a route
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify(message="Authentication required"), 401
            
            if not user.has_permission(permission_code):
                return jsonify(message=f"Permission denied: {permission_code}"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def admin_required():
    """
    Decorator to require admin (superuser) access for a route
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user or not user.is_superuser:
                return jsonify(message="Admin access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def team_access_required(team_id_param='team_id'):
    """
    Decorator to require team access
    - Admins have access to all teams
    - Managers have access to their own team
    - Users with the 'manage_team' permission have access to their own team
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify(message="Authentication required"), 401
            
            # Get team_id from URL parameters or request JSON
            team_id = kwargs.get(team_id_param)
            if not team_id and request.is_json:
                team_id = request.json.get(team_id_param)
            
            # Admins have access to all teams
            if user.is_superuser:
                return fn(*args, **kwargs)
            
            # Others have access to their own team only
            if user.team_id == team_id and user.has_permission('view_teams'):
                return fn(*args, **kwargs)
            
            return jsonify(message="Access denied for this team"), 403
            
        return decorator
    return wrapper 