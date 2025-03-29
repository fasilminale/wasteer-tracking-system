from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import User


def admin_required():
    """
    Decorator to require admin role for a route
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user or not user.is_admin():
                return jsonify(message="Admin access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def manager_required():
    """
    Decorator to require manager or admin role for a route
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user or not user.is_manager():
                return jsonify(message="Manager access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def employee_required():
    """
    Decorator to require any authenticated user (employee or higher)
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify(message="Authentication required"), 401
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def team_access_required(team_id_param='team_id'):
    """
    Decorator to require team access (manager of the team or admin)
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            # Get team_id from URL parameters or request JSON
            team_id = kwargs.get(team_id_param)
            if not team_id and request.is_json:
                team_id = request.json.get(team_id_param)
            
            # Admins have access to all teams
            if user and user.is_admin():
                return fn(*args, **kwargs)
            
            # Managers have access to their own team
            if user and user.is_manager() and user.team_id == team_id:
                return fn(*args, **kwargs)
            
            return jsonify(message="Access denied for this team"), 403
            
        return decorator
    return wrapper 