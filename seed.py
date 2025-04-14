"""
Seed script to populate the database with initial data.
Run this script after setting up the database to create initial users, teams, and waste entries.
"""

from app import create_app, db
from app.models import User, Team, WasteEntry, WasteType, Permission, Role
from datetime import datetime, timedelta
import random


def create_core_data():
    """Create core permissions and roles."""
    print("Creating core permissions and roles...")

    # Dictionary to hold permissions
    permissions = {}
    
    # Define permission data
    permission_data = [
        # Waste Entry permissions
        ('manage_wasteentry', 'Can manage waste entries (create, read, update, delete)'),
        ('add_wasteentry', 'Can add waste entry'),
        ('edit_wasteentry', 'Can edit waste entry'),
        ('delete_wasteentry', 'Can delete waste entry'),
        ('view_wasteentry', 'Can view waste entry'),
        
        # Analytics permissions
        ('view_analytics', 'Can view analytics'),
        
        # User management permissions
        ('manage_user', 'Can manage users (create, read, update, delete)'),
        ('view_users', 'Can view users'),
        ('add_user', 'Can add users'),
        ('edit_user', 'Can edit users'),
        ('delete_user', 'Can delete users'),
        
        # Team management permissions
        ('manage_team', 'Can manage teams (create, read, update, delete)'),
        ('view_teams', 'Can view teams'),
        ('add_team', 'Can add teams'),
        ('edit_team', 'Can edit teams'),
        ('delete_team', 'Can delete teams'),
        ('view_team_members', 'Can view team members'),
        
        # Role management permissions
        ('manage_role', 'Can manage roles (create, read, update, delete)'),
        ('view_roles', 'Can view roles'),
        ('add_role', 'Can add roles'),
        ('edit_role', 'Can edit roles'),
        ('delete_role', 'Can delete roles'),
        
        # Permission management
        ('view_permissions', 'Can view permissions'),
        ('assign_permissions', 'Can assign permissions to roles'),
    ]
    
    # Create or get permissions
    for code, name in permission_data:
        # Check if permission already exists
        permission = Permission.query.filter_by(code=code).first()
        if not permission:
            permission = Permission(code=code, name=name)
            db.session.add(permission)
        permissions[code] = permission
    
    db.session.commit()
    print("Created permissions")

    # Create roles or get existing ones
    role_data = {
        'admin': 'Admin',
        'manager': 'Manager',
        'employee': 'Employee',
    }
    
    roles = {}
    for role_code, role_name in role_data.items():
        # Check if role already exists
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            db.session.flush()  # Get the ID without committing
        roles[role_code] = role
    
    # Assign permissions to roles
    roles['admin'].permissions = list(permissions.values())  # Admin gets all permissions
    
    roles['manager'].permissions = [
        # Waste Entry permissions
        permissions['manage_wasteentry'],  # Can manage their team's waste entries
        
        # Analytics permissions
        permissions['view_analytics'],  # Can access team-level analytics
        
        # Team permissions
        permissions['view_teams'],  # Can view teams (but only access their team's data)
        permissions['view_team_members'],  # Can view team members
        
        # User permissions (limited)
        permissions['view_users'],  # Can view users (but only their team members)
    ]
    
    roles['employee'].permissions = [
        # Waste Entry permissions
        permissions['add_wasteentry'],  # Can create waste entries
        permissions['view_wasteentry'],  # Can view their own waste entries
        
        # No team member viewing permission
        # No analytics permission
    ]
    
    db.session.commit()
    print("Created roles with permissions")
    
    return roles


def seed_database():
    """Seed the database with initial data."""
    print("Seeding database...")
    
    # Create core permissions and roles
    roles = create_core_data()
    
    # Create teams
    team_data = [
        ("Engineering", "Engineering team responsible for product development"),
        ("Marketing", "Marketing team responsible for product promotion"),
        ("Operations", "Operations team responsible for day-to-day operations")
    ]
    
    teams = {}
    for name, description in team_data:
        team = Team.query.filter_by(name=name).first()
        if not team:
            team = Team(name=name, description=description)
            db.session.add(team)
            db.session.flush()  # Get ID without committing
        teams[name.lower()] = team
    
    db.session.commit()
    
    print(f"Created teams: Engineering (ID: {teams['engineering'].id}), Marketing (ID: {teams['marketing'].id}), Operations (ID: {teams['operations'].id})")
    
    # Create users
    user_data = [
        {
            "username": "admin",
            "email": "admin@wasteer.com",
            "password": "adminpassword",
            "role_id": roles['admin'].id,
            "is_superuser": True
        },
        {
            "username": "eng_manager",
            "email": "eng_manager@wasteer.com",
            "password": "managerpassword",
            "role_id": roles['manager'].id,
            "team_id": teams['engineering'].id
        },
        {
            "username": "mkt_manager",
            "email": "mkt_manager@wasteer.com",
            "password": "managerpassword",
            "role_id": roles['manager'].id,
            "team_id": teams['marketing'].id
        },
        {
            "username": "ops_manager",
            "email": "ops_manager@wasteer.com",
            "password": "managerpassword",
            "role_id": roles['manager'].id,
            "team_id": teams['operations'].id
        },
        {
            "username": "eng_employee1",
            "email": "eng_employee1@wasteer.com",
            "password": "employeepassword",
            "role_id": roles['employee'].id,
            "team_id": teams['engineering'].id
        },
        {
            "username": "eng_employee2",
            "email": "eng_employee2@wasteer.com",
            "password": "employeepassword",
            "role_id": roles['employee'].id,
            "team_id": teams['engineering'].id
        },
        {
            "username": "mkt_employee",
            "email": "mkt_employee@wasteer.com",
            "password": "employeepassword",
            "role_id": roles['employee'].id,
            "team_id": teams['marketing'].id
        },
        {
            "username": "ops_employee",
            "email": "ops_employee@wasteer.com",
            "password": "employeepassword",
            "role_id": roles['employee'].id,
            "team_id": teams['operations'].id
        }
    ]
    
    users = []
    for user_info in user_data:
        # Check if user already exists
        user = User.query.filter_by(username=user_info["username"]).first()
        if not user:
            user = User(**user_info)
            db.session.add(user)
            users.append(user)
        else:
            users.append(user)
    
    db.session.commit()
    
    print(f"Created {len(users)} users")
    
    # Create waste entries
    waste_entries = []
    
    # Get all waste types
    waste_types = list(WasteType)
    
    # Check if we already have waste entries
    existing_entries = WasteEntry.query.count()
    if existing_entries > 0:
        print(f"Found {existing_entries} existing waste entries, skipping waste entry creation")
    else:
        # Create waste entries for the past 30 days
        for i in range(30):
            day = datetime.utcnow() - timedelta(days=i)
            
            # Each employee creates 1-3 waste entries per day
            for user in users[1:]:  # Skip admin
                num_entries = random.randint(1, 3)
                for _ in range(num_entries):
                    waste_type = random.choice(waste_types)
                    weight = round(random.uniform(0.1, 10.0), 2)  # Random weight between 0.1 and 10.0 kg
                    
                    waste_entry = WasteEntry(
                        waste_type=waste_type,
                        weight=weight,
                        user_id=user.id,
                        team_id=user.team_id,
                        description=f"Sample {waste_type.value} waste entry",
                        timestamp=day
                    )
                    waste_entries.append(waste_entry)
                    
        db.session.add_all(waste_entries)
        db.session.commit()
        print(f"Created {len(waste_entries)} waste entries")
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database() 