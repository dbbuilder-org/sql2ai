"""Dependencies for SQL2.AI API routes."""

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    CurrentUser,
    TenantId,
    Context,
    UserRole,
    Permission,
    get_current_user,
    get_tenant_id,
    get_request_context,
    require_permission,
    require_any_permission,
    require_role,
    RequestContext,
)

__all__ = [
    "AuthenticatedUser",
    "CurrentUser",
    "TenantId",
    "Context",
    "UserRole",
    "Permission",
    "get_current_user",
    "get_tenant_id",
    "get_request_context",
    "require_permission",
    "require_any_permission",
    "require_role",
    "RequestContext",
]
