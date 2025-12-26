"""User model."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql2ai_api.db.base import BaseModel, TenantMixin

if TYPE_CHECKING:
    from sql2ai_api.models.tenant import Tenant


class UserRole(str, Enum):
    """User roles within a tenant."""

    OWNER = "owner"
    ADMIN = "admin"
    DBA = "dba"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class User(BaseModel, TenantMixin):
    """User model."""

    __tablename__ = "users"

    # Identity (from Clerk)
    clerk_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Profile
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.DEVELOPER,
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.email

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN)

    @property
    def is_owner(self) -> bool:
        """Check if user is the tenant owner."""
        return self.role == UserRole.OWNER

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN)

    def can_manage_connections(self) -> bool:
        """Check if user can manage database connections."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN, UserRole.DBA)

    def can_execute_queries(self) -> bool:
        """Check if user can execute queries."""
        return self.role != UserRole.VIEWER
