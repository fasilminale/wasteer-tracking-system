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

    # Create permissions
    permissions = {
        # Waste Entry permissions
        'manage_wasteentry': Permission(
            code='manage_wasteentry',
            name='Can manage waste entries (create, read, update, delete)'
        ),
        'add_wasteentry': Permission(
            code='add_wasteentry',
            name='Can add waste entry'
        ),
        'edit_wasteentry': Permission(
            code='edit_wasteentry',
            name='Can edit waste entry'
        ),
        'delete_wasteentry': Permission(
            code='delete_wasteentry',
            name='Can delete waste entry'
        ),
        'view_wasteentry': Permission(
            code='view_wasteentry',
            name='Can view waste entry'
        ),
        
        # Analytics permissions
        'view_analytics': Permission(
            code='view_analytics',
            name='Can view analytics'
        ),
        
        # User management permissions
        'manage_user': Permission(
            code='manage_user',
            name='Can manage users (create, read, update, delete)'
        ),
        'view_users': Permission(
            code='view_users',
            name='Can view users'
        ),
        'add_user': Permission(
            code='add_user',
            name='Can add users'
        ),
        'edit_user': Permission(
            code='edit_user',
            name='Can edit users'
        ),
        'delete_user': Permission(
            code='delete_user',
            name='Can delete users'
        ),
        
        # Team management permissions
        'manage_team': Permission(
            code='manage_team',
            name='Can manage teams (create, read, update, delete)'
        ),
        'view_teams': Permission(
            code='view_teams',
            name='Can view teams'
        ),
        'add_team': Permission(
            code='add_team',
            name='Can add teams'
        ),
        'edit_team': Permission(
            code='edit_team',
            name='Can edit teams'
        ),
        'delete_team': Permission(
            code='delete_team',
            name='Can delete teams'
        ),
        'view_team_members': Permission(
            code='view_team_members',
            name='Can view team members'
        ),
        
        # Role management permissions
        'manage_role': Permission(
            code='manage_role',
            name='Can manage roles (create, read, update, delete)'
        ),
        'view_roles': Permission(
            code='view_roles',
            name='Can view roles'
        ),
        'add_role': Permission(
            code='add_role',
            name='Can add roles'
        ),
        'edit_role': Permission(
            code='edit_role',
            name='Can edit roles'
        ),
        'delete_role': Permission(
            code='delete_role',
            name='Can delete roles'
        ),
        
        # Permission management
        'view_permissions': Permission(
            code='view_permissions',
            name='Can view permissions'
        ),
        'assign_permissions': Permission(
            code='assign_permissions',
            name='Can assign permissions to roles'
        ),
    }
    
    db.session.add_all(permissions.values())
    db.session.commit()
    print("Created permissions")

    # Create roles with permissions
    roles = {
        'admin': Role(name='Admin'),
        'manager': Role(name='Manager'),
        'employee': Role(name='Employee'),
    }
    
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
    
    db.session.add_all(roles.values())
    db.session.commit()
    print("Created roles with permissions")
    
    return roles


def seed_database():
    """Seed the database with initial data."""
    print("Seeding database...")
    
    # Create core permissions and roles
    roles = create_core_data()
    
    # Create teams
    engineering = Team(name="Engineering", description="Engineering team responsible for product development")
    marketing = Team(name="Marketing", description="Marketing team responsible for product promotion")
    operations = Team(name="Operations", description="Operations team responsible for day-to-day operations")
    
    db.session.add_all([engineering, marketing, operations])
    db.session.commit()
    
    print(f"Created teams: Engineering (ID: {engineering.id}), Marketing (ID: {marketing.id}), Operations (ID: {operations.id})")
    
    # Create users
    admin = User(
        username="admin",
        email="admin@wasteer.com",
        password="adminpassword",
        role_id=roles['admin'].id,
        is_superuser=True
    )
    
    eng_manager = User(
        username="eng_manager",
        email="eng_manager@wasteer.com",
        password="managerpassword",
        role_id=roles['manager'].id,
        team_id=engineering.id
    )
    
    mkt_manager = User(
        username="mkt_manager",
        email="mkt_manager@wasteer.com",
        password="managerpassword",
        role_id=roles['manager'].id,
        team_id=marketing.id
    )
    
    ops_manager = User(
        username="ops_manager",
        email="ops_manager@wasteer.com",
        password="managerpassword",
        role_id=roles['manager'].id,
        team_id=operations.id
    )
    
    eng_employee1 = User(
        username="eng_employee1",
        email="eng_employee1@wasteer.com",
        password="employeepassword",
        role_id=roles['employee'].id,
        team_id=engineering.id
    )
    
    eng_employee2 = User(
        username="eng_employee2",
        email="eng_employee2@wasteer.com",
        password="employeepassword",
        role_id=roles['employee'].id,
        team_id=engineering.id
    )
    
    mkt_employee = User(
        username="mkt_employee",
        email="mkt_employee@wasteer.com",
        password="employeepassword",
        role_id=roles['employee'].id,
        team_id=marketing.id
    )
    
    ops_employee = User(
        username="ops_employee",
        email="ops_employee@wasteer.com",
        password="employeepassword",
        role_id=roles['employee'].id,
        team_id=operations.id
    )
    
    users = [admin, eng_manager, mkt_manager, ops_manager, eng_employee1, eng_employee2, mkt_employee, ops_employee]
    db.session.add_all(users)
    db.session.commit()
    
    print(f"Created {len(users)} users")
    
    # Create waste entries
    waste_entries = []
    
    # Get all waste types
    waste_types = list(WasteType)
    
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