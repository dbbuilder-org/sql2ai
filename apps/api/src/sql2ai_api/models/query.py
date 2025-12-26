"""Query and execution models."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql2ai_api.db.base import BaseModel, TenantMixin


class QueryStatus(str, Enum):
    """Query execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Query(BaseModel, TenantMixin):
    """Saved query model."""

    __tablename__ = "queries"

    # Query content
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sql: Mapped[str] = mapped_column(Text, nullable=False)

    # Source
    connection_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("connections.id"),
        nullable=False,
    )

    # AI metadata
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Ownership
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # Sharing
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)

    # Tags and metadata
    tags: Mapped[dict] = mapped_column(JSONB, default=dict)

    def __repr__(self) -> str:
        return f"<Query {self.name}>"


class QueryExecution(BaseModel, TenantMixin):
    """Query execution history."""

    __tablename__ = "query_executions"

    # References
    query_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("queries.id"),
        nullable=True,
    )
    connection_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("connections.id"),
        nullable=False,
    )

    # Query content (for ad-hoc queries)
    sql: Mapped[str] = mapped_column(Text, nullable=False)
    sql_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Execution details
    status: Mapped[QueryStatus] = mapped_column(
        SQLEnum(QueryStatus),
        default=QueryStatus.PENDING,
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Performance metrics
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rows_affected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bytes_scanned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Results (for small result sets)
    result_preview: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    result_row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # AI analysis
    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_optimization_suggestions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # User
    executed_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # Client context
    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    client_user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<QueryExecution {self.id} ({self.status.value})>"

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get duration in seconds."""
        if self.duration_ms:
            return self.duration_ms / 1000
        return None

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == QueryStatus.COMPLETED

    @property
    def is_running(self) -> bool:
        """Check if query is still running."""
        return self.status in (QueryStatus.PENDING, QueryStatus.RUNNING)
