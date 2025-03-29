from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserRole, Team
from app.utils import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@admin_required()
def get_users():
    # Parse query parameters
    team_id = request.args.get('team_id', type=int)
    role = request.args.get('role')
    
    # Base query
    query = User.query
    
    # Apply filters
    if team_id:
        query = query.filter(User.team_id == team_id)
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass  # Ignore invalid role
    
    users = query.all()
    
    return jsonify({
        "users": [user.to_dict() for user in users]
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required()
def get_user(user_id):
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    role_name = data.get('role')
    team_id = data.get('team_id')
    password = data.get('password')
    
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
    
    if role_name:
        try:
            role = UserRole(role_name)
            user.role = role
        except ValueError:
            return jsonify({"message": "Invalid role"}), 400
    
    if team_id is not None:  # Allow setting team_id to null
        if team_id:
            team = db.session.get(Team, team_id)
            if not team:
                return jsonify({"message": "Team not found"}), 404
        user.team_id = team_id
    
    if password:
        user.set_password(password)
    
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    }), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Prevent deleting the last admin
    if user.is_admin():
        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
        if admin_count <= 1:
            return jsonify({
                "message": "Cannot delete the last admin user"
            }), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        "message": "User deleted successfully"
    }), 200 