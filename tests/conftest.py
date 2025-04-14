"""
Test configuration for the Wasteer application.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Team, WasteEntry, WasteType, Role, Permission


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'JWT_ACCESS_TOKEN_EXPIRES': False  # Tokens never expire in testing
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        _init_test_data()

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


def _init_test_data():
    """Initialize test data for the database."""
    # Create permissions
    permissions = {
        'add_wasteentry': Permission(code='add_wasteentry', name='Can add waste entry'),
        'edit_wasteentry': Permission(code='edit_wasteentry', name='Can edit waste entry'),
        'delete_wasteentry': Permission(code='delete_wasteentry', name='Can delete waste entry'),
        'view_wasteentry': Permission(code='view_wasteentry', name='Can view waste entry'),
        'view_analytics': Permission(code='view_analytics', name='Can view analytics'),
        'view_users': Permission(code='view_users', name='Can view users'),
        'manage_users': Permission(code='manage_users', name='Can manage users'),
        'view_teams': Permission(code='view_teams', name='Can view teams'),
        'view_team_members': Permission(code='view_team_members', name='Can view team members')
    }
    
    db.session.add_all(permissions.values())
    db.session.commit()
    
    # Create roles
    admin_role = Role(name='Admin')
    manager_role = Role(name='Manager')
    employee_role = Role(name='Employee')
    
    # Assign permissions to roles
    admin_role.permissions = list(permissions.values())
    
    manager_role.permissions = [
        permissions['add_wasteentry'],
        permissions['edit_wasteentry'],
        permissions['delete_wasteentry'],
        permissions['view_wasteentry'],
        permissions['view_analytics'],
        permissions['view_teams'],
        permissions['view_team_members'],
        permissions['view_users']
    ]
    
    employee_role.permissions = [
        permissions['add_wasteentry'],
        permissions['view_wasteentry']
    ]
    
    db.session.add_all([admin_role, manager_role, employee_role])
    db.session.commit()
    
    # Create test teams
    engineering = Team(name="Engineering", description="Engineering team")
    marketing = Team(name="Marketing", description="Marketing team")
    
    db.session.add_all([engineering, marketing])
    db.session.commit()
    
    # Create test users
    admin = User(
        username="admin",
        email="admin@test.com",
        password="adminpass",
        role_id=admin_role.id,
        is_superuser=True
    )
    
    manager = User(
        username="manager",
        email="manager@test.com",
        password="managerpass",
        role_id=manager_role.id,
        team_id=engineering.id
    )
    
    employee = User(
        username="employee",
        email="employee@test.com",
        password="employeepass",
        role_id=employee_role.id,
        team_id=engineering.id
    )
    
    db.session.add_all([admin, manager, employee])
    db.session.commit()
    
    # Create test waste entries
    waste_entry = WasteEntry(
        waste_type=WasteType.PAPER,
        weight=2.5,
        user_id=employee.id,
        team_id=engineering.id,
        description="Test waste entry",
        timestamp=db.func.now()  # Add timestamp
    )
    
    db.session.add(waste_entry)
    db.session.commit()


@pytest.fixture
def auth_tokens(client):
    """Get authentication tokens for different user roles."""
    tokens = {}
    
    # Get admin token
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    tokens['admin'] = response.json['access_token']
    
    # Get manager token
    response = client.post('/api/auth/login', json={
        'username': 'manager',
        'password': 'managerpass'
    })
    tokens['manager'] = response.json['access_token']
    
    # Get employee token
    response = client.post('/api/auth/login', json={
        'username': 'employee',
        'password': 'employeepass'
    })
    tokens['employee'] = response.json['access_token']
    
    return tokens 