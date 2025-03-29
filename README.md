# Waste Management System

A Flask-based waste management system that helps organizations track and manage their waste disposal.

## Features

- User authentication with JWT
- Role-based access control (Admin, Manager, Employee)
- Team management
- Waste entry tracking
- Waste analytics and reporting

## System Architecture

For details on the system architecture, database schema, and permission model, see the [ARCHITECTURE.md](ARCHITECTURE.md) document.

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

- `POST /api/teams` - Create a new team (Admin only)
- `GET /api/teams` - Get all teams (Admin) or team (Manager)
- `GET /api/teams/<id>` - Get specific team
- `PUT /api/teams/<id>` - Update team (Admin only)
- `DELETE /api/teams/<id>` - Delete team (Admin only)
- `GET /api/teams/<id>/members` - Get team members

### Users

- `GET /api/users` - Get all users (Admin only)
- `GET /api/users/<id>` - Get specific user (Admin only)
- `PUT /api/users/<id>` - Update user (Admin only)
- `DELETE /api/users/<id>` - Delete user (Admin only)

### Waste

- `POST /api/waste` - Create waste entry (Employee/Manager)
- `GET /api/waste` - Get waste entries
- `GET /api/waste/analytics` - Get waste analytics (Manager/Admin)

## Development

### Project Structure

```
wasteer-tracking-system/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── utils/          # Utility functions
│   └── __init__.py     # Application factory
├── tests/              # Test files
├── migrations/         # Database migrations
├── seed.py             # Database seeding script
├── setup.sh            # Setup automation script
├── run.py              # Alternative run script
├── .env.example        # Example environment variables
├── requirements.txt    # Project dependencies
└── README.md           # This file
```
