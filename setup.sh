#!/bin/bash

# Wasteer Setup Script
# This script helps set up the Wasteer waste tracking system

echo "Setting up Wasteer waste tracking system..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://$(whoami)@localhost/wasteer
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF
    echo ".env file created with default values. Please update it if needed."
else
    echo ".env file already exists. Skipping creation."
fi

# Create database
echo "Creating database..."
createdb wasteer || echo "Database already exists or could not be created. Please check PostgreSQL configuration."

# Initialize database
echo "Initializing database..."
flask db init || echo "Database already initialized."
flask db migrate -m "Initial migration"
flask db upgrade

# Seed database
echo "Seeding database with initial data..."
python seed.py

echo "Setup completed successfully!"
echo "You can now run the application with: flask run" 