from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import User, Role, Team
from app.utils import permission_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@permission_required('view_users')
def get_users():
    # Parse query parameters
    team_id = request.args.get('team_id', type=int)
    role_id = request.args.get('role_id', type=int)
    
    # Get the current user
    user_id = int(get_jwt_identity())
    current_user = db.session.get(User, user_id)
    
    # Base query
    query = User.query
    
    # Apply filters
    if team_id:
        query = query.filter(User.team_id == team_id)
    elif not current_user.is_superuser:
        # Non-superusers can only see users from their team
        query = query.filter(User.team_id == current_user.team_id)
    
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    users = query.all()
    
    return jsonify({
        "users": [user.to_dict() for user in users]
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@permission_required('view_users')
def get_user(user_id):
    # Get the current user
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if the user has access to view this user
    if not current_user.is_superuser and current_user.team_id != user.team_id:
        return jsonify({"message": "Access denied"}), 403
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@permission_required('edit_user')
def update_user(user_id):
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    
    # Get the current user
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if the user has access to edit this user
    if not current_user.is_superuser and current_user.team_id != user.team_id:
        return jsonify({"message": "Access denied"}), 403
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    role_id = data.get('role_id')
    team_id = data.get('team_id')
    password = data.get('password')
    is_superuser = data.get('is_superuser')
    
    # Update fields if provided
    if username:
        # Check if username already exists for another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"message": "Username already exists"}), 409
        user.username = username
    
    if email:
        # Check if email already exists for another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"message": "Email already exists"}), 409
        user.email = email
    
    # Only superusers can change these fields
    if current_user.is_superuser:
        if role_id is not None:
            role = db.session.get(Role, role_id)
            if not role:
                return jsonify({"message": "Role not found"}), 404
            user.role_id = role_id
        
        if team_id is not None:  # Allow setting team_id to null
            if team_id:
                team = db.session.get(Team, team_id)
                if not team:
                    return jsonify({"message": "Team not found"}), 404
            user.team_id = team_id
        
        if is_superuser is not None:
            user.is_superuser = is_superuser
    
    if password:
        user.set_password(password)
    
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    }), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@permission_required('delete_user')
def delete_user(user_id):
    # Get the current user
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)
    
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Prevent deleting the last superuser
    if user.is_superuser:
        superuser_count = User.query.filter_by(is_superuser=True).count()
        if superuser_count <= 1:
            return jsonify({
                "message": "Cannot delete the last admin user"
            }), 400
    
    # Only superusers can delete users from other teams
    if not current_user.is_superuser and current_user.team_id != user.team_id:
        return jsonify({"message": "Access denied"}), 403
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        "message": "User deleted successfully"
    }), 200 