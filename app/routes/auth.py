from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from app import db
from app.models import User, Role

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role_id = data.get('role_id')
    team_id = data.get('team_id')

    # Validate required fields
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    # Validate role
    if not role_id:
        # Default to Employee role
        role = Role.query.filter_by(name='Employee').first()
        if not role:
            return jsonify({"message": "Default role not found"}), 500
        role_id = role.id
    else:
        # Verify role exists
        role = db.session.get(Role, role_id)
        if not role:
            return jsonify({"message": "Invalid role"}), 400

    # Create new user
    user = User(
        username=username,
        email=email,
        password=password,
        role_id=role_id,
        team_id=team_id
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Create access token with string user ID
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user.to_dict()), 200 