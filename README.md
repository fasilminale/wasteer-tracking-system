# Waste Management System

A Flask-based waste management system that helps organizations track and manage their waste disposal.

## Features

- User authentication with JWT
- Granular permission-based access control
- Role management with customizable permissions
- Team management
- Waste entry tracking
- Waste analytics and reporting

## System Architecture

For details on the system architecture, database schema, and permission model, see the [ARCHITECTURE.md](ARCHITECTURE.md) document.

For detailed documentation on the permission system, see the [PERMISSIONS.md](PERMISSIONS.md) document.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

## Setup Instructions

### Automated Setup (Recommended)

The easiest way to set up the project is using the provided setup script:

```bash
# Clone the repository
git clone git@github.com:fasilminale/wasteer-tracking-system.git
cd wasteer-tracking-system

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The setup script will:
1. Create a virtual environment
2. Install dependencies
3. Create a `.env` file with default configuration
4. Set up the database and run migrations
5. Seed the database with initial test data

### Manual Setup

If you prefer to set up the project manually:

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
# Required variables:
# - DATABASE_URL: PostgreSQL connection string
# - SECRET_KEY: Application secret key
# - JWT_SECRET_KEY: JWT token secret key
```

5. Set up the database:
```bash
# Create the database
createdb wasteer

# Initialize database migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

6. Seed the database with initial data:
```bash
python seed.py
```

## Running the Application

1. Start the Flask development server:
```bash
# Using flask command
flask run

# OR using the run.py script
python run.py
```

2. Access the application:
- API: http://localhost:5000/api
- Swagger Documentation: http://localhost:5000/api/docs

## Default Users

After seeding the database, the following users are available:

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

## Default Roles and Permissions

The system comes with three predefined roles, each with specific permissions:

| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| Admin    | All permissions (full system access)             |
| Manager  | Manage waste entries, view analytics, view team members, view users |
| Employee | Add waste entries, view own waste entries        |

See [PERMISSIONS.md](PERMISSIONS.md) for details on the permission system.

## Testing

The application includes a comprehensive test suite. To run the tests:

```bash
# Run all tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=app --cov-report=html

# Run a specific test file
python -m pytest tests/test_auth.py

# Run a specific test
python -m pytest tests/test_auth.py::test_login
```

## API Documentation

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get user profile

### Teams

- `POST /api/teams` - Create a new team (Requires 'add_team' permission)
- `GET /api/teams` - Get all teams (Requires 'view_teams' permission)
- `GET /api/teams/<id>` - Get specific team (Requires 'view_teams' permission)
- `PUT /api/teams/<id>` - Update team (Requires 'edit_team' permission)
- `DELETE /api/teams/<id>` - Delete team (Requires 'delete_team' permission)
- `GET /api/teams/<id>/members` - Get team members (Requires 'view_team_members' permission)

### Users

- `GET /api/users` - Get all users (Requires 'view_users' permission)
- `GET /api/users/<id>` - Get specific user (Requires 'view_users' permission)
- `PUT /api/users/<id>` - Update user (Requires 'edit_user' permission)
- `DELETE /api/users/<id>` - Delete user (Requires 'delete_user' permission)

### Roles and Permissions

- `GET /api/roles` - Get all roles (Requires 'view_roles' permission)
- `POST /api/roles` - Create a new role (Requires 'add_role' permission)
- `GET /api/roles/<id>` - Get specific role (Requires 'view_roles' permission)
- `PUT /api/roles/<id>` - Update role (Requires 'edit_role' permission)
- `DELETE /api/roles/<id>` - Delete role (Requires 'delete_role' permission)
- `GET /api/permissions` - Get all permissions (Requires 'view_permissions' permission)
- `POST /api/roles/<id>/permissions` - Assign permissions to a role (Requires 'assign_permissions' permission)

### Waste

- `POST /api/waste` - Create waste entry (Requires 'add_wasteentry' permission)
- `GET /api/waste` - Get waste entries (Requires 'view_wasteentry' permission)
- `GET /api/waste/analytics` - Get waste analytics (Requires 'view_analytics' permission)

## Development

### Project Structure

```
wasteer-tracking-system/
├── app/
│   ├── models/         # Database models
│   │   ├── user.py     # User model
│   │   ├── team.py     # Team model
│   │   ├── role.py     # Role and Permission models
│   │   └── waste.py    # WasteEntry model and WasteType enum
│   ├── routes/         # API routes
│   ├── utils/          # Utility functions
│   │   ├── auth.py     # Authentication and authorization utilities
│   │   └── permission.py # Permission decorators
│   └── __init__.py     # Application factory
├── tests/              # Test files
├── migrations/         # Database migrations
├── seed.py             # Database seeding script
├── setup.sh            # Setup automation script
├── run.py              # Alternative run script
├── .env.example        # Example environment variables
├── requirements.txt    # Project dependencies
├── ARCHITECTURE.md     # Architecture documentation
└── README.md           # This file
```
