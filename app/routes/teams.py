from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import Team, User
from app.utils import permission_required

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('', methods=['POST'])
@permission_required('add_team')
def create_team():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.json
    name = data.get('name')
    description = data.get('description')

    # Validate required fields
    if not name:
        return jsonify({"message": "Team name is required"}), 400

    # Check if team already exists
    if Team.query.filter_by(name=name).first():
        return jsonify({"message": "Team name already exists"}), 409

    # Create new team
    team = Team(
        name=name,
        description=description
    )

    db.session.add(team)
    db.session.commit()

    return jsonify({
        "message": "Team created successfully",
        "team": team.to_dict()
    }), 201


@teams_bp.route('', methods=['GET'])
@permission_required('view_teams')
def get_teams():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Admins can see all teams, others can only see their team
    if user.is_superuser:
        teams = Team.query.all()
    else:
        team = user.team
        teams = [team] if team else []

    return jsonify({
        "teams": [team.to_dict() for team in teams]
    }), 200


@teams_bp.route('/<int:team_id>', methods=['GET'])
@permission_required('view_teams')
def get_team(team_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    # Check team access permission
    if not user.is_superuser and user.team_id != team_id:
        return jsonify({"message": "Access denied for this team"}), 403
    
    team = db.session.get(Team, team_id)

    if not team:
        return jsonify({"message": "Team not found"}), 404

    return jsonify(team.to_dict()), 200


@teams_bp.route('/<int:team_id>', methods=['PUT'])
@permission_required('edit_team')
def update_team(team_id):
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    # Check team access permission (for non-superusers)
    if not user.is_superuser and user.team_id != team_id:
        return jsonify({"message": "Access denied for this team"}), 403

    team = db.session.get(Team, team_id)

    if not team:
        return jsonify({"message": "Team not found"}), 404

    data = request.json
    name = data.get('name')
    description = data.get('description')

    # Update fields if provided
    if name:
        # Check if name already exists for another team
        existing_team = Team.query.filter_by(name=name).first()
        if existing_team and existing_team.id != team_id:
            return jsonify({"message": "Team name already exists"}), 409
        team.name = name

    if description:
        team.description = description

    db.session.commit()

    return jsonify({
        "message": "Team updated successfully",
        "team": team.to_dict()
    }), 200


@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@permission_required('delete_team')
def delete_team(team_id):
    team = Team.query.get(team_id)

    if not team:
        return jsonify({"message": "Team not found"}), 404

    # Check if team has members
    if team.members:
        return jsonify({
            "message": "Cannot delete team with members. Reassign members first."
        }), 400

    db.session.delete(team)
    db.session.commit()

    return jsonify({
        "message": "Team deleted successfully"
    }), 200


@teams_bp.route('/<int:team_id>/members', methods=['GET'])
@permission_required('view_team_members')
def get_team_members(team_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    # Check team access permission (for non-superusers)
    if not user.is_superuser and user.team_id != team_id:
        return jsonify({"message": "Access denied for this team"}), 403
    
    team = db.session.get(Team, team_id)

    if not team:
        return jsonify({"message": "Team not found"}), 404

    members = [member.to_dict() for member in team.members]
    return jsonify({"members": members}), 200 