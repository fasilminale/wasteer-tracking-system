from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    EMPLOYEE = 'employee'
    MANAGER = 'manager'
    ADMIN = 'admin'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = db.relationship('Team', back_populates='members')
    waste_entries = db.relationship('WasteEntry', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, email, password, role=UserRole.EMPLOYEE, team_id=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.team_id = team_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_manager(self):
        return self.role == UserRole.MANAGER or self.role == UserRole.ADMIN

    def is_employee(self):
        return True  # All roles can do what employees can do

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'team_id': self.team_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 