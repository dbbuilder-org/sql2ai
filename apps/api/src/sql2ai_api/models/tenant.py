"""Tenant model for multi-tenancy."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql2ai_api.db.base import BaseModel

if TYPE_CHECKING:
    from sql2ai_api.models.user import User
    from sql2ai_api.models.connection import Connection


class TenantTier(str, Enum):
    """Tenant subscription tiers."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(BaseModel):
    """Tenant/organization model."""

    __tablename__ = "tenants"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Subscription
    tier: Mapped[TenantTier] = mapped_column(
        SQLEnum(TenantTier),
        default=TenantTier.FREE,
        nullable=False,
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Limits based on tier
    max_connections: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_queries_per_day: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Usage tracking
    queries_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    queries_reset_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="tenant")
    connections: Mapped[List["Connection"]] = relationship("Connection", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant {self.name} ({self.tier.value})>"

    @property
    def is_enterprise(self) -> bool:
        return self.tier == TenantTier.ENTERPRISE

    @property
    def is_paid(self) -> bool:
        return self.tier in (TenantTier.PRO, TenantTier.ENTERPRISE)

    def can_add_connection(self, current_count: int) -> bool:
        """Check if tenant can add another connection."""
        return current_count < self.max_connections

    def can_execute_query(self) -> bool:
        """Check if tenant can execute more queries today."""
        return self.queries_today < self.max_queries_per_day

    def increment_query_count(self) -> None:
        """Increment daily query count."""
        self.queries_today += 1
