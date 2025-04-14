# Permission System Documentation

## Overview

The Waste Management System implements a fine-grained permission-based access control system. This document explains how it works, how to use it, and how to extend it.

## Core Concepts

The permission system is built around three main concepts:

1. **Permissions**: Individual capabilities to perform actions in the system
2. **Roles**: Collections of permissions
3. **Users**: Assigned roles and optionally superuser status

## Permission Codes

Each permission has a unique code that represents an action in the system. Permission codes follow a naming convention:

```
[action]_[resource]
```

For example:
- `view_wasteentry`: Permission to view waste entries
- `edit_user`: Permission to edit user information
- `delete_team`: Permission to delete a team

## Built-in Permissions

The system comes with the following built-in permissions:

### Waste Entries
- `manage_wasteentry`: Can perform all actions on waste entries
- `add_wasteentry`: Can add waste entries
- `edit_wasteentry`: Can edit waste entries
- `delete_wasteentry`: Can delete waste entries
- `view_wasteentry`: Can view waste entries

### Analytics
- `view_analytics`: Can view analytics data

### User Management
- `manage_user`: Can perform all actions on users
- `view_users`: Can view user information
- `add_user`: Can add users
- `edit_user`: Can edit user information
- `delete_user`: Can delete users

### Team Management
- `manage_team`: Can perform all actions on teams
- `view_teams`: Can view teams
- `add_team`: Can add teams
- `edit_team`: Can edit team information
- `delete_team`: Can delete teams
- `view_team_members`: Can view team members

### Role Management
- `manage_role`: Can perform all actions on roles
- `view_roles`: Can view roles
- `add_role`: Can add roles
- `edit_role`: Can edit role information
- `delete_role`: Can delete roles

### Permission Management
- `view_permissions`: Can view permissions
- `assign_permissions`: Can assign permissions to roles

## Default Roles

The system includes three default roles with the following permissions:

### Admin
Admins have all permissions and can perform any action in the system. Additionally, Admin users typically have the `is_superuser` flag set to `True`, which bypasses permission checks entirely.

### Manager
Managers have the following permissions:
- All waste entry permissions (`manage_wasteentry`)
- View analytics (`view_analytics`)
- View team information (`view_teams`)
- View team members (`view_team_members`) 
- View users (`view_users`)

Managers are restricted to their own team's data in most contexts.

### Employee
Employees have minimal permissions:
- Add waste entries (`add_wasteentry`)
- View their own waste entries (`view_wasteentry`)

Employees can only see and modify their own data.

## Using Permissions in Code

### Protecting Routes

Routes are protected using the `permission_required` decorator:

```python
from app.utils.decorators import permission_required

@bp.route('/waste', methods=['GET'])
@permission_required('view_wasteentry')
def get_waste_entries():
    # This route is only accessible to users with 'view_wasteentry' permission
    ...
```

### Checking Permissions in Code

You can also check permissions directly in code:

```python
# Get current user
user_id = get_jwt_identity()
user = db.session.get(User, user_id)

# Check permission
if user.has_permission('edit_wasteentry'):
    # User can edit waste entries
    ...
else:
    # User cannot edit waste entries
    ...
```

### Filtering Data Based on Permissions

Beyond the route-level permission check, you should filter data based on the user's role:

```python
# Base query
query = WasteEntry.query

# Filter based on user's role
if user.is_superuser:
    # Superusers see all entries (optionally filtered by team)
    if team_id:
        query = query.filter(WasteEntry.team_id == team_id)
elif user.has_permission('view_analytics'):
    # Managers see their team's entries
    query = query.filter(WasteEntry.team_id == user.team_id)
else:
    # Regular employees see only their own entries
    query = query.filter(WasteEntry.user_id == user.id)
```

## Extending the Permission System

### Adding New Permissions

To add a new permission:

1. Add the permission to the database:

```python
new_permission = Permission(
    code='view_reports',
    name='Can view reports'
)
db.session.add(new_permission)
db.session.commit()
```

2. Assign the permission to roles:

```python
admin_role = Role.query.filter_by(name='Admin').first()
manager_role = Role.query.filter_by(name='Manager').first()

admin_role.permissions.append(new_permission)
manager_role.permissions.append(new_permission)
db.session.commit()
```

1. Use the permission in code:

```python
@bp.route('/reports', methods=['GET'])
@permission_required('view_reports')
def get_reports():
    ...
```

### Creating New Roles

To create a new role:

1. Add the role to the database:

```python
new_role = Role(name='Supervisor')
db.session.add(new_role)
db.session.commit()
```

2. Assign permissions to the role:

```python
permissions = Permission.query.filter(
    Permission.code.in_(['view_wasteentry', 'view_analytics'])
).all()

new_role.permissions = permissions
db.session.commit()
```

3. Assign the role to users:

```python
user = User.query.get(user_id)
user.role_id = new_role.id
db.session.commit()
```
