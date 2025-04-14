from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import Role, Permission, User
from app.utils import permission_required

roles_bp = Blueprint('roles', __name__)


@roles_bp.route('', methods=['GET'])
@permission_required('view_roles')
def get_roles():
    roles = Role.query.all()
    return jsonify({
        "roles": [role.to_dict() for role in roles]
    }), 200


@roles_bp.route('/<int:role_id>', methods=['GET'])
@permission_required('view_roles')
def get_role(role_id):
    role = db.session.get(Role, role_id)
    
    if not role:
        return jsonify({"message": "Role not found"}), 404
    
    return jsonify(role.to_dict()), 200


@roles_bp.route('', methods=['POST'])
@permission_required('add_role')
def create_role():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.json
    name = data.get('name')
    permission_ids = data.get('permission_ids', [])

    # Validate required fields
    if not name:
        return jsonify({"message": "Role name is required"}), 400

    # Check if role already exists
    if Role.query.filter_by(name=name).first():
        return jsonify({"message": "Role name already exists"}), 409

    # Create new role
    role = Role(name=name)
    
    # Add permissions if provided
    if permission_ids:
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions

    db.session.add(role)
    db.session.commit()

    return jsonify({
        "message": "Role created successfully",
        "role": role.to_dict()
    }), 201


@roles_bp.route('/<int:role_id>', methods=['PUT'])
@permission_required('edit_role')
def update_role(role_id):
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({"message": "Role not found"}), 404

    data = request.json
    name = data.get('name')
    permission_ids = data.get('permission_ids')

    # Update name if provided
    if name:
        # Check if name already exists for another role
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role and existing_role.id != role_id:
            return jsonify({"message": "Role name already exists"}), 409
        role.name = name

    # Update permissions if provided
    if permission_ids is not None:
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions

    db.session.commit()

    return jsonify({
        "message": "Role updated successfully",
        "role": role.to_dict()
    }), 200


@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@permission_required('delete_role')
def delete_role(role_id):
    role = db.session.get(Role, role_id)
    
    if not role:
        return jsonify({"message": "Role not found"}), 404
    
    # Check if role is in use
    if User.query.filter_by(role_id=role_id).first():
        return jsonify({
            "message": "Cannot delete role that is assigned to users"
        }), 400
    
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({
        "message": "Role deleted successfully"
    }), 200 