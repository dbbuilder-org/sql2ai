"""SQLAlchemy declarative base and common mixins."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, String, func, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    type_annotation_map = {
        str: String(255),
    }


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin:
    """Mixin for multi-tenant models with RLS support."""

    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )


class AuditMixin:
    """Mixin for audit tracking."""

    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    updated_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with common fields (id, created_at, updated_at)."""

    __abstract__ = True


class TenantModel(BaseModel, TenantMixin):
    """Base model for tenant-scoped entities."""

    __abstract__ = True


class AuditedTenantModel(TenantModel, AuditMixin, SoftDeleteMixin):
    """Base model for tenant-scoped entities with full audit trail."""

    __abstract__ = True
