from app import db
from datetime import datetime
from enum import Enum


class WasteType(Enum):
    PAPER = 'paper'
    PLASTIC = 'plastic'
    GLASS = 'glass'
    METAL = 'metal'
    ORGANIC = 'organic'
    ELECTRONIC = 'electronic'
    HAZARDOUS = 'hazardous'
    OTHER = 'other'


class WasteEntry(db.Model):
    __tablename__ = 'waste_entries'

    id = db.Column(db.Integer, primary_key=True)
    waste_type = db.Column(db.Enum(WasteType), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # in kilograms
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='waste_entries')
    team = db.relationship('Team', back_populates='waste_entries')

    def __init__(
        self,
        waste_type,
        weight,
        user_id,
        team_id,
        description=None,
        timestamp=None
    ):
        self.waste_type = waste_type
        self.weight = weight
        self.user_id = user_id
        self.team_id = team_id
        self.description = description
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'waste_type': self.waste_type.value,
            'weight': self.weight,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'team_id': self.team_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 