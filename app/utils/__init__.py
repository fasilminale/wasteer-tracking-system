from app.utils.auth import admin_required, manager_required, employee_required, team_access_required
from app.utils.permissions import permission_required, admin_required as new_admin_required

# Export both old and new for backward compatibility during transition
__all__ = [
    'admin_required', 'manager_required', 'employee_required', 'team_access_required',
    'permission_required', 'new_admin_required'
] 