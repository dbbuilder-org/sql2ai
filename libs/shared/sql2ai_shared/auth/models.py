"""Authentication models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """User model."""

    id: str
    email: EmailStr
    name: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    email_verified: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles or "admin" in self.roles

    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(self.has_role(role) for role in roles)


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # User ID
    email: str
    roles: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
    iat: int  # Issued at
    exp: int  # Expiration
    jti: Optional[str] = None  # JWT ID (for revocation)
    type: str = "access"  # access, refresh, api_key


class AuthResult(BaseModel):
    """Result of an authentication attempt."""

    success: bool
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # Seconds
    error: Optional[str] = None
    error_description: Optional[str] = None


class Permission(BaseModel):
    """Permission model."""

    resource: str
    action: str  # create, read, update, delete, execute, *

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"

    @classmethod
    def from_string(cls, permission: str) -> "Permission":
        parts = permission.split(":")
        return cls(resource=parts[0], action=parts[1] if len(parts) > 1 else "*")


class Role(BaseModel):
    """Role model with permissions."""

    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if role has a specific permission."""
        for perm in self.permissions:
            if perm.resource in (resource, "*") and perm.action in (action, "*"):
                return True
        return False


# Predefined roles
PREDEFINED_ROLES = {
    "admin": Role(
        id="admin",
        name="Administrator",
        description="Full system access",
        permissions=[Permission(resource="*", action="*")],
    ),
    "dba": Role(
        id="dba",
        name="Database Administrator",
        description="Database management access",
        permissions=[
            Permission(resource="connections", action="*"),
            Permission(resource="queries", action="*"),
            Permission(resource="migrations", action="*"),
            Permission(resource="monitoring", action="*"),
            Permission(resource="ai", action="read"),
        ],
    ),
    "developer": Role(
        id="developer",
        name="Developer",
        description="Development access",
        permissions=[
            Permission(resource="connections", action="read"),
            Permission(resource="queries", action="*"),
            Permission(resource="ai", action="*"),
        ],
    ),
    "viewer": Role(
        id="viewer",
        name="Viewer",
        description="Read-only access",
        permissions=[
            Permission(resource="connections", action="read"),
            Permission(resource="queries", action="read"),
            Permission(resource="monitoring", action="read"),
        ],
    ),
}
