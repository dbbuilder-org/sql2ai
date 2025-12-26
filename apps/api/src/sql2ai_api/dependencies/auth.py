"""Authentication dependencies for FastAPI routes."""

from typing import Annotated, Optional, List
from enum import Enum
from functools import wraps

import structlog
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from sql2ai_api.middleware.auth import ClerkUser

logger = structlog.get_logger()


class UserRole(str, Enum):
    """User roles for access control."""

    OWNER = "owner"
    ADMIN = "admin"
    DBA = "dba"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Granular permissions for access control."""

    # Connection permissions
    CONNECTIONS_READ = "connections:read"
    CONNECTIONS_WRITE = "connections:write"
    CONNECTIONS_DELETE = "connections:delete"

    # Query permissions
    QUERIES_EXECUTE = "queries:execute"
    QUERIES_EXECUTE_DDL = "queries:execute_ddl"  # CREATE, ALTER, DROP
    QUERIES_EXECUTE_DML = "queries:execute_dml"  # INSERT, UPDATE, DELETE

    # Schema permissions
    SCHEMA_READ = "schema:read"
    SCHEMA_EXPORT = "schema:export"

    # AI permissions
    AI_GENERATE = "ai:generate"
    AI_OPTIMIZE = "ai:optimize"
    AI_REVIEW = "ai:review"

    # Migration permissions
    MIGRATIONS_READ = "migrations:read"
    MIGRATIONS_WRITE = "migrations:write"
    MIGRATIONS_EXECUTE = "migrations:execute"

    # Compliance permissions
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_SCAN = "compliance:scan"

    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_BILLING = "admin:billing"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_AUDIT = "admin:audit"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[UserRole, List[Permission]] = {
    UserRole.OWNER: list(Permission),  # All permissions
    UserRole.ADMIN: [
        Permission.CONNECTIONS_READ,
        Permission.CONNECTIONS_WRITE,
        Permission.CONNECTIONS_DELETE,
        Permission.QUERIES_EXECUTE,
        Permission.QUERIES_EXECUTE_DDL,
        Permission.QUERIES_EXECUTE_DML,
        Permission.SCHEMA_READ,
        Permission.SCHEMA_EXPORT,
        Permission.AI_GENERATE,
        Permission.AI_OPTIMIZE,
        Permission.AI_REVIEW,
        Permission.MIGRATIONS_READ,
        Permission.MIGRATIONS_WRITE,
        Permission.MIGRATIONS_EXECUTE,
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_SCAN,
        Permission.ADMIN_USERS,
        Permission.ADMIN_SETTINGS,
    ],
    UserRole.DBA: [
        Permission.CONNECTIONS_READ,
        Permission.CONNECTIONS_WRITE,
        Permission.QUERIES_EXECUTE,
        Permission.QUERIES_EXECUTE_DDL,
        Permission.QUERIES_EXECUTE_DML,
        Permission.SCHEMA_READ,
        Permission.SCHEMA_EXPORT,
        Permission.AI_GENERATE,
        Permission.AI_OPTIMIZE,
        Permission.AI_REVIEW,
        Permission.MIGRATIONS_READ,
        Permission.MIGRATIONS_WRITE,
        Permission.MIGRATIONS_EXECUTE,
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_SCAN,
    ],
    UserRole.DEVELOPER: [
        Permission.CONNECTIONS_READ,
        Permission.QUERIES_EXECUTE,
        Permission.QUERIES_EXECUTE_DML,
        Permission.SCHEMA_READ,
        Permission.AI_GENERATE,
        Permission.AI_OPTIMIZE,
        Permission.MIGRATIONS_READ,
    ],
    UserRole.VIEWER: [
        Permission.CONNECTIONS_READ,
        Permission.QUERIES_EXECUTE,
        Permission.SCHEMA_READ,
    ],
}


class AuthenticatedUser(BaseModel):
    """Authenticated user with resolved permissions."""

    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    org_id: Optional[str] = None
    org_role: Optional[str] = None
    tenant_id: str
    role: UserRole
    permissions: List[Permission]

    @property
    def display_name(self) -> str:
        """Get user display name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.email:
            return self.email.split("@")[0]
        return self.id

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(p in self.permissions for p in permissions)


async def get_current_user(request: Request) -> AuthenticatedUser:
    """Get the current authenticated user from request state.

    This dependency should be used on all protected routes.
    """
    clerk_user: Optional[ClerkUser] = getattr(request.state, "user", None)

    if not clerk_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Determine role from org_role or default to developer
    role_mapping = {
        "admin": UserRole.ADMIN,
        "org:admin": UserRole.ADMIN,
        "owner": UserRole.OWNER,
        "org:owner": UserRole.OWNER,
        "dba": UserRole.DBA,
        "developer": UserRole.DEVELOPER,
        "viewer": UserRole.VIEWER,
    }

    org_role = clerk_user.org_role or "developer"
    role = role_mapping.get(org_role.lower(), UserRole.DEVELOPER)

    # Get permissions for role
    permissions = ROLE_PERMISSIONS.get(role, [])

    return AuthenticatedUser(
        id=clerk_user.id,
        email=clerk_user.email,
        first_name=clerk_user.first_name,
        last_name=clerk_user.last_name,
        org_id=clerk_user.org_id,
        org_role=clerk_user.org_role,
        tenant_id=clerk_user.org_id or clerk_user.id,
        role=role,
        permissions=permissions,
    )


# Type alias for dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


async def get_tenant_id(request: Request) -> str:
    """Get the current tenant ID from request state."""
    tenant_id: Optional[str] = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(status_code=401, detail="No tenant context")

    return tenant_id


# Type alias for tenant dependency
TenantId = Annotated[str, Depends(get_tenant_id)]


def require_permission(permission: Permission):
    """Dependency factory for permission checks.

    Usage:
        @router.get("/admin/users")
        async def list_users(
            user: CurrentUser,
            _: Annotated[None, Depends(require_permission(Permission.ADMIN_USERS))]
        ):
            ...
    """

    async def check_permission(user: CurrentUser) -> None:
        if not user.has_permission(permission):
            logger.warning(
                "permission_denied",
                user_id=user.id,
                permission=permission.value,
            )
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission.value}",
            )

    return check_permission


def require_any_permission(*permissions: Permission):
    """Dependency factory for checking any of multiple permissions."""

    async def check_permissions(user: CurrentUser) -> None:
        if not user.has_any_permission(list(permissions)):
            logger.warning(
                "permission_denied",
                user_id=user.id,
                required_any=", ".join(p.value for p in permissions),
            )
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permissions. Need one of: {', '.join(p.value for p in permissions)}",
            )

    return check_permissions


def require_role(role: UserRole):
    """Dependency factory for role checks.

    Usage:
        @router.get("/admin/settings")
        async def get_settings(
            user: CurrentUser,
            _: Annotated[None, Depends(require_role(UserRole.ADMIN))]
        ):
            ...
    """
    role_hierarchy = {
        UserRole.OWNER: 5,
        UserRole.ADMIN: 4,
        UserRole.DBA: 3,
        UserRole.DEVELOPER: 2,
        UserRole.VIEWER: 1,
    }

    async def check_role(user: CurrentUser) -> None:
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(role, 0)

        if user_level < required_level:
            logger.warning(
                "role_denied",
                user_id=user.id,
                user_role=user.role.value,
                required_role=role.value,
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient role. Required: {role.value}",
            )

    return check_role


class RequestContext(BaseModel):
    """Context information for a request."""

    user_id: str
    tenant_id: str
    request_id: str
    org_id: Optional[str] = None


async def get_request_context(
    request: Request,
    user: CurrentUser,
    tenant_id: TenantId,
) -> RequestContext:
    """Get full request context for logging and tracking."""
    return RequestContext(
        user_id=user.id,
        tenant_id=tenant_id,
        request_id=getattr(request.state, "request_id", "unknown"),
        org_id=user.org_id,
    )


# Type alias for context dependency
Context = Annotated[RequestContext, Depends(get_request_context)]
