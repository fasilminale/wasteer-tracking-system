from flask import Blueprint, request, jsonify
from app import db
from app.models import Permission
from app.utils import permission_required

permissions_bp = Blueprint('permissions', __name__)


@permissions_bp.route('', methods=['GET'])
@permission_required('view_permissions')
def get_permissions():
    permissions = Permission.query.all()
    return jsonify({
        "permissions": [permission.to_dict() for permission in permissions]
    }), 200


@permissions_bp.route('/<int:permission_id>', methods=['GET'])
@permission_required('view_permissions')
def get_permission(permission_id):
    permission = db.session.get(Permission, permission_id)
    
    if not permission:
        return jsonify({"message": "Permission not found"}), 404
    
    return jsonify(permission.to_dict()), 200 