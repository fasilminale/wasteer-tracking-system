from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import WasteEntry, WasteType, User
from app.utils import employee_required, manager_required

waste_bp = Blueprint('waste', __name__)


@waste_bp.route('', methods=['POST'])
@employee_required()
def create_waste_entry():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.json
    waste_type_name = data.get('waste_type')
    weight = data.get('weight')
    description = data.get('description')

    # Validate required fields
    if not waste_type_name or not weight:
        return jsonify({"message": "Missing required fields"}), 400

    # Validate waste type
    try:
        waste_type = WasteType(waste_type_name)
    except ValueError:
        return jsonify({"message": "Invalid waste type"}), 400

    # Get user and team
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user.team_id:
        return jsonify({"message": "User must be assigned to a team"}), 400

    # Create waste entry
    waste_entry = WasteEntry(
        waste_type=waste_type,
        weight=weight,
        description=description,
        user_id=user.id,
        team_id=user.team_id
    )

    db.session.add(waste_entry)
    db.session.commit()

    return jsonify({
        "message": "Waste entry created successfully",
        "waste_entry": waste_entry.to_dict()
    }), 201


@waste_bp.route('', methods=['GET'])
@employee_required()
def get_waste_entries():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    # Parse query parameters
    team_id = request.args.get('team_id', type=int)
    waste_type = request.args.get('waste_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = WasteEntry.query

    # Apply filters
    if team_id and user.is_admin():
        query = query.filter(WasteEntry.team_id == team_id)
    elif not user.is_admin() and user.is_manager():
        query = query.filter(WasteEntry.team_id == user.team_id)
    elif not user.is_admin() and not user.is_manager():
        query = query.filter(WasteEntry.user_id == user.id)
    # No filter for admin without team_id - they see all entries

    if waste_type:
        try:
            waste_type_enum = WasteType(waste_type)
            query = query.filter(WasteEntry.waste_type == waste_type_enum)
        except ValueError:
            pass  # Ignore invalid waste type

    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(WasteEntry.timestamp >= start)
        except ValueError:
            pass  # Ignore invalid date format

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(WasteEntry.timestamp <= end)
        except ValueError:
            pass  # Ignore invalid date format

    waste_entries = query.order_by(WasteEntry.timestamp.desc()).all()

    return jsonify({
        "waste_entries": [entry.to_dict() for entry in waste_entries]
    }), 200


@waste_bp.route('/analytics', methods=['GET'])
@manager_required()
def get_waste_analytics():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    # Parse query parameters
    team_id = request.args.get('team_id', type=int)
    period = request.args.get('period', 'week')  # week, month, year
    waste_type = request.args.get('waste_type')

    # Determine date range based on period
    now = datetime.utcnow()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        return jsonify({"message": "Invalid period"}), 400

    # Base query
    query = db.session.query(
        WasteEntry.waste_type,
        func.sum(WasteEntry.weight).label('total_weight'),
        func.count(WasteEntry.id).label('entry_count')
    ).filter(WasteEntry.timestamp >= start_date)

    # Apply team filter
    if team_id and user.is_admin():
        query = query.filter(WasteEntry.team_id == team_id)
    else:
        query = query.filter(WasteEntry.team_id == user.team_id)

    # Apply waste type filter
    if waste_type:
        try:
            waste_type_enum = WasteType(waste_type)
            query = query.filter(WasteEntry.waste_type == waste_type_enum)
        except ValueError:
            pass  # Ignore invalid waste type

    # Group by waste type
    results = query.group_by(WasteEntry.waste_type).all()

    # Calculate totals
    total_weight = sum(float(result[1]) for result in results)
    total_entries = sum(result[2] for result in results)

    # Format results by waste type
    waste_by_type = {
        result[0].value: float(result[1])
        for result in results
    }

    return jsonify({
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': now.isoformat(),
        'total_entries': total_entries,
        'total_weight': total_weight,
        'waste_by_type': waste_by_type
    }), 200 