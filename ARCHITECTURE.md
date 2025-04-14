# Waste Management System - Architecture Overview

This document provides a high-level overview of the system architecture. For a detailed explanation of the permission system, please see [PERMISSIONS.md](PERMISSIONS.md). For general system information and setup instructions, see [README.md](README.md).

## System Structure

The waste management system follows a layered architecture with clear separation of concerns:

```
┌─────────────────┐
│    API Layer    │  Routes handle HTTP requests and responses
├─────────────────┤
│  Service Layer  │  Business logic, permissions, and data manipulation
├─────────────────┤
│   Data Layer    │  Database models and data access
└─────────────────┘
```

### Key Components

1. **Flask Application Factory** (`app/__init__.py`)
   - Provides application configuration
   - Initializes extensions (SQLAlchemy, JWT, Migrations)
   - Registers route blueprints

2. **Models** (`app/models/`)
   - Define database schema
   - Implement business rules and constraints
   - Handle data serialization through to_dict methods

3. **Routes** (`app/routes/`)
   - Handle API requests
   - Validate input
   - Apply authorization decorators
   - Return appropriate responses

4. **Utilities** (`app/utils/`)
   - Authentication helpers
   - Decorators for permission checks
   - Response formatting

## Database Schema

The system uses PostgreSQL with the following schema and relationships:

![Entity Relationship Diagram](ERD.png)

### Entity Relationships

- A **User** belongs to one **Team** (optional for admin)
- A **User** has one **Role**
- A **Team** has many **Users**
- A **WasteEntry** belongs to one **User** and one **Team**
- A **Team** has many **WasteEntries**
- A **User** has many **WasteEntries**
- A **Role** has many **Permissions** (many-to-many relationship)
- A **Permission** can belong to many **Roles** (many-to-many relationship)

## Permission Model

The system implements a fine-grained permission-based access control model. Each action in the system is protected by a specific permission code. Roles are collections of permissions that can be assigned to users.

### Permission Types

The system includes the following permission types:

| Category       | Permission Code      | Description                                     |
|----------------|----------------------|-------------------------------------------------|
| Waste Entries  | manage_wasteentry    | Can manage waste entries (create, read, update, delete) |
|                | add_wasteentry       | Can add waste entry                             |
|                | edit_wasteentry      | Can edit waste entry                            |
|                | delete_wasteentry    | Can delete waste entry                          |
|                | view_wasteentry      | Can view waste entry                            |
| Analytics      | view_analytics       | Can view analytics                              |
| User Management| manage_user          | Can manage users (create, read, update, delete) |
|                | view_users           | Can view users                                  |
|                | add_user             | Can add users                                   |
|                | edit_user            | Can edit users                                  |
|                | delete_user          | Can delete users                                |
| Team Management| manage_team          | Can manage teams (create, read, update, delete) |
|                | view_teams           | Can view teams                                  |
|                | add_team             | Can add teams                                   |
|                | edit_team            | Can edit teams                                  |
|                | delete_team          | Can delete teams                                |
|                | view_team_members    | Can view team members                           |
| Role Management| manage_role          | Can manage roles (create, read, update, delete) |
|                | view_roles           | Can view roles                                  |
|                | add_role             | Can add roles                                   |
|                | edit_role            | Can edit roles                                  |
|                | delete_role          | Can delete roles                                |
| Permission Mgmt| view_permissions     | Can view permissions                            |
|                | assign_permissions   | Can assign permissions to roles                 |

### Default Roles

The system comes with three predefined roles, each with specific permissions:

| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| Admin    | All permissions (full system access)             |
| Manager  | Waste entry management, analytics, team viewing, user viewing |
| Employee | Add and view own waste entries                    |

### Superuser Flag

In addition to the role-permission system, there is a special `is_superuser` flag on the User model. Users with this flag set to `True` bypass the permission system and have full access to all features. This is typically reserved for system administrators.

### Implementation

#### Models

The permission system is implemented through these key models:

1. **Permission Model**
```python
class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

2. **Role Model with Many-to-Many Relationship to Permissions**
```python
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')
```

3. **User Model with Role Relationship**
```python
class User(db.Model):
    # ...existing fields...
    is_superuser = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # Relationships
    role = db.relationship('Role', backref='users')
    
    def has_permission(self, permission_code):
        if self.is_superuser:
            return True
        return any(p.code == permission_code for p in self.role.permissions)
```

#### Permission Checking

Permissions are enforced through a decorator in `app/utils/decorators.py`:

```python
def permission_required(permission_code):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({"message": "User not found"}), 404
                
            if not user.has_permission(permission_code):
                return jsonify({"message": "Insufficient permissions"}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

This decorator is used on API routes:

```python
@waste_bp.route('', methods=['GET'])
@permission_required('view_wasteentry')
def get_waste_entries():
    # Implementation...
```

#### Data Filtering Based on User Role

Beyond the route-level permission check, the system also implements data filtering based on user roles:

```python
# Example from get_waste_entries():
user_id = get_jwt_identity()
user = db.session.get(User, user_id)

# Base query
query = WasteEntry.query

# Apply filters based on user permissions
if team_id and user.is_superuser:
    query = query.filter(WasteEntry.team_id == team_id)
elif user.has_permission('view_analytics'):  # Manager-level permission
    query = query.filter(WasteEntry.team_id == user.team_id)
else:  # Regular employee
    query = query.filter(WasteEntry.user_id == user.id)
```

This multi-layered permission model ensures:
1. Data isolation between teams
2. Proper access control based on user roles and permissions
3. Team-level access for managers
4. Overall system access for admins
5. Restricted access for employees to their own entries only

The system maintains security and privacy by applying permissions at both the route level and the data query level, ensuring users can only access and modify data they are authorized to handle.

## API Structure

The API is organized into modules by resource type:

- `auth_bp`: Authentication routes (`/api/auth/*`)
- `teams_bp`: Team management routes (`/api/teams/*`)
- `users_bp`: User management routes (`/api/users/*`)
- `waste_bp`: Waste entry and analytics routes (`/api/waste/*`)
- `roles_bp`: Role management routes (`/api/roles/*`)
- `permissions_bp`: Permission view routes (`/api/permissions/*`)

Each blueprint encapsulates the routes related to a particular resource domain, making the codebase modular and maintainable.

## Security Considerations

1. **Authentication**: JWT (JSON Web Tokens) with expiration
2. **Password Security**: Passwords are hashed using werkzeug.security
3. **Authorization**: Layered permission checks (route level and data level)
4. **Input Validation**: All user inputs are validated
5. **Error Handling**: Proper error responses with appropriate HTTP status codes
6. **Database Security**: Parameterized queries through SQLAlchemy ORM

## Future Improvements

Potential future improvements to the architecture:

1. **Caching Layer**: Add Redis for caching frequently accessed data
2. **Async Processing**: Add Celery for background task processing
3. **Monitoring**: Add Prometheus/Grafana for system monitoring
4. **API Documentation**: Add Swagger/OpenAPI integration
5. **Containerization**: Docker and Kubernetes deployment configuration
6. **Microservices**: Split into microservices as the system grows 