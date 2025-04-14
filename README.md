# Waste Management System

A Flask-based system for tracking and managing organizational waste disposal.

## Features

- JWT authentication
- Permission-based access control
- Role management
- Team organization
- Waste entry tracking
- Analytics and reporting

## System Architecture

For details on the system architecture, database schema, and permission model, see the [ARCHITECTURE.md](ARCHITECTURE.md) document.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and database schema
- [PERMISSIONS.md](PERMISSIONS.md) - Permission system details

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip

## Setup

### Automated Setup

```bash
# Clone the repository
git clone git@github.com:fasilminale/wasteer-tracking-system.git
cd wasteer-tracking-system

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Manual Setup

1. Clone the repository:
```bash
git clone git@github.com:fasilminale/wasteer-tracking-system.git
cd wasteer-tracking-system
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
```

5. Set up the database:
```bash
# Create the database
createdb wasteer

# Initialize migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Seed the database:
```bash
python seed.py
```

## Running the Application

```bash
# Start the server
flask run

# Alternatively
python run.py
```

Access the application:
- API: http://localhost:5000/api
- Swagger: http://localhost:5000/api/docs

## Default Users

| Username     | Email                  | Password        | Role     | Team        |
|--------------|------------------------|-----------------|----------|-------------|
| admin        | admin@wasteer.com      | adminpassword   | Admin    | None        |
| eng_manager  | eng_manager@wasteer.com| managerpassword | Manager  | Engineering |
| mkt_manager  | mkt_manager@wasteer.com| managerpassword | Manager  | Marketing   |
| ops_manager  | ops_manager@wasteer.com| managerpassword | Manager  | Operations  |
| eng_employee1| eng_employee1@wasteer.com| employeepassword | Employee | Engineering |
| eng_employee2| eng_employee2@wasteer.com| employeepassword | Employee | Engineering |
| mkt_employee | mkt_employee@wasteer.com| employeepassword | Employee | Marketing   |
| ops_employee | ops_employee@wasteer.com| employeepassword | Employee | Operations  |

## Default Roles

| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| Admin    | All permissions                                  |
| Manager  | Team management, analytics, user viewing         |
| Employee | Personal waste entry management                  |

## Testing

```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py

# Run specific test
python -m pytest tests/test_auth.py::test_login
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get profile

### Teams
- `POST /api/teams` - Create team (requires 'add_team')
- `GET /api/teams` - Get teams (requires 'view_teams')
- `GET /api/teams/<id>` - Get team (requires 'view_teams')
- `PUT /api/teams/<id>` - Update team (requires 'edit_team')
- `DELETE /api/teams/<id>` - Delete team (requires 'delete_team')
- `GET /api/teams/<id>/members` - Get members (requires 'view_team_members')

### Users
- `GET /api/users` - Get users (requires 'view_users')
- `GET /api/users/<id>` - Get user (requires 'view_users')
- `PUT /api/users/<id>` - Update user (requires 'edit_user')
- `DELETE /api/users/<id>` - Delete user (requires 'delete_user')

### Roles
- `GET /api/roles` - Get roles (requires 'view_roles')
- `POST /api/roles` - Create role (requires 'add_role')
- `GET /api/roles/<id>` - Get role (requires 'view_roles')
- `PUT /api/roles/<id>` - Update role (requires 'edit_role')
- `DELETE /api/roles/<id>` - Delete role (requires 'delete_role')
- `GET /api/permissions` - Get permissions (requires 'view_permissions')
- `POST /api/roles/<id>/permissions` - Assign permissions (requires 'assign_permissions')

### Waste
- `POST /api/waste` - Create entry (requires 'add_wasteentry')
- `GET /api/waste` - Get entries (requires 'view_wasteentry')
- `GET /api/waste/analytics` - Get analytics (requires 'view_analytics')

## Project Structure

```
wasteer-tracking-system/
├── app/
│   ├── models/      # Database models
│   ├── routes/      # API routes
│   ├── utils/       # Utility functions
│   └── __init__.py  # Application factory
├── tests/           # Test files
├── migrations/      # Database migrations
├── seed.py          # Database seeding
├── setup.sh         # Setup script
├── run.py           # Run script
├── requirements.txt # Dependencies
├── ARCHITECTURE.md  # Architecture docs
└── README.md        # This file
```
