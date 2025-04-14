from datetime import timedelta
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev-jwt-key'),
            JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
            JWT_TOKEN_LOCATION=["headers"],
            JWT_HEADER_NAME="Authorization",
            JWT_HEADER_TYPE="Bearer",
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.waste import waste_bp
    from app.routes.teams import teams_bp
    from app.routes.users import users_bp
    from app.routes.roles import roles_bp
    from app.routes.permissions import permissions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(waste_bp, url_prefix='/api/waste')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(permissions_bp, url_prefix='/api/permissions')

    # Create a simple index route
    @app.route('/')
    def index():
        return {'message': 'Welcome to Wasteer API'}

    return app 