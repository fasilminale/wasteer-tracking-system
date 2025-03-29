"""
Test configuration for the Wasteer application.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, UserRole, Team, WasteEntry, WasteType


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
        role=UserRole.ADMIN
    )
    
    manager = User(
        username="manager",
        email="manager@test.com",
        password="managerpass",
        role=UserRole.MANAGER,
        team_id=engineering.id
    )
    
    employee = User(
        username="employee",
        email="employee@test.com",
        password="employeepass",
        role=UserRole.EMPLOYEE,
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