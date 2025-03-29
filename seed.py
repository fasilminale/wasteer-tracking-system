"""
Seed script to populate the database with initial data.
Run this script after setting up the database to create initial users, teams, and waste entries.
"""

from app import create_app, db
from app.models import User, UserRole, Team, WasteEntry, WasteType
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with initial data."""
    print("Seeding database...")
    
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
        role=UserRole.ADMIN
    )
    
    eng_manager = User(
        username="eng_manager",
        email="eng_manager@wasteer.com",
        password="managerpassword",
        role=UserRole.MANAGER,
        team_id=engineering.id
    )
    
    mkt_manager = User(
        username="mkt_manager",
        email="mkt_manager@wasteer.com",
        password="managerpassword",
        role=UserRole.MANAGER,
        team_id=marketing.id
    )
    
    ops_manager = User(
        username="ops_manager",
        email="ops_manager@wasteer.com",
        password="managerpassword",
        role=UserRole.MANAGER,
        team_id=operations.id
    )
    
    eng_employee1 = User(
        username="eng_employee1",
        email="eng_employee1@wasteer.com",
        password="employeepassword",
        role=UserRole.EMPLOYEE,
        team_id=engineering.id
    )
    
    eng_employee2 = User(
        username="eng_employee2",
        email="eng_employee2@wasteer.com",
        password="employeepassword",
        role=UserRole.EMPLOYEE,
        team_id=engineering.id
    )
    
    mkt_employee = User(
        username="mkt_employee",
        email="mkt_employee@wasteer.com",
        password="employeepassword",
        role=UserRole.EMPLOYEE,
        team_id=marketing.id
    )
    
    ops_employee = User(
        username="ops_employee",
        email="ops_employee@wasteer.com",
        password="employeepassword",
        role=UserRole.EMPLOYEE,
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