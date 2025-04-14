# Permission System 

## Core Concepts

- **Permissions**: Individual capabilities to perform actions
- **Roles**: Collections of permissions
- **Users**: Assigned roles and optionally superuser status

## Permission Codes

Permission codes follow `[action]_[resource]` format:

- `view_wasteentry`: View waste entries
- `edit_user`: Edit user information
- `delete_team`: Delete a team

## Built-in Permissions

### Waste Entries
- `manage_wasteentry`: All waste entry operations
- `add_wasteentry`: Add entries
- `edit_wasteentry`: Edit entries
- `delete_wasteentry`: Delete entries
- `view_wasteentry`: View entries

### Analytics
- `view_analytics`: Access analytics

### User Management
- `manage_user`: All user operations
- `view_users`: View users
- `add_user`: Add users
- `edit_user`: Edit users
- `delete_user`: Delete users

### Team Management
- `manage_team`: All team operations
- `view_teams`: View teams
- `add_team`: Add teams
- `edit_team`: Edit teams
- `delete_team`: Delete teams
- `view_team_members`: View members

### Role Management
- `manage_role`: All role operations
- `view_roles`: View roles
- `add_role`: Add roles
- `edit_role`: Edit roles
- `delete_role`: Delete roles

### Permission Management
- `view_permissions`: View permissions
- `assign_permissions`: Assign permissions to roles

## Default Roles

### Admin
All permissions + `is_superuser` flag

### Manager
- All waste entry permissions
- View analytics
- View teams
- View team members
- View users

### Employee
- Add waste entries
- View own waste entries

## Using Permissions

### Protecting Routes

```python
@bp.route('/waste', methods=['GET'])
@permission_required('view_wasteentry')
def get_waste_entries():
    # Route code...
```

### In-Code Checks

```python
if user.has_permission('edit_wasteentry'):
    # Can edit
else:
    # Cannot edit
```

### Data Filtering

```python
# Base query
query = WasteEntry.query

# Apply filters
if user.is_superuser:
    # All data
elif user.has_permission('view_analytics'):
    # Team data
    query = query.filter(WasteEntry.team_id == user.team_id)
else:
    # User data
    query = query.filter(WasteEntry.user_id == user.id)
```

## Extending the System

### Adding Permissions

```python
new_permission = Permission(
    code='view_reports',
    name='Can view reports'
)
db.session.add(new_permission)
db.session.commit()
```

### Creating Roles

```python
new_role = Role(name='Supervisor')
db.session.add(new_role)
db.session.commit()

# Assign permissions
permissions = Permission.query.filter(
    Permission.code.in_(['view_wasteentry', 'view_analytics'])
).all()
new_role.permissions = permissions
db.session.commit()
```
