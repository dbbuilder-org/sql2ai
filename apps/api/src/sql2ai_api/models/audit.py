"""Audit log model for compliance tracking."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from sql2ai_api.db.base import BaseModel, TenantMixin


class AuditAction(str, Enum):
    """Types of auditable actions."""

    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

    # CRUD operations
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    # Query operations
    QUERY_EXECUTE = "query_execute"
    QUERY_SAVE = "query_save"

    # Connection operations
    CONNECTION_TEST = "connection_test"
    CONNECTION_ACTIVATE = "connection_activate"
    CONNECTION_DEACTIVATE = "connection_deactivate"

    # AI operations
    AI_QUERY_GENERATE = "ai_query_generate"
    AI_QUERY_APPROVE = "ai_query_approve"
    AI_QUERY_REJECT = "ai_query_reject"

    # Compliance operations
    COMPLIANCE_SCAN = "compliance_scan"
    COMPLIANCE_REPORT = "compliance_report"

    # Admin operations
    USER_INVITE = "user_invite"
    USER_REMOVE = "user_remove"
    ROLE_CHANGE = "role_change"
    SETTINGS_UPDATE = "settings_update"

    # Billing
    SUBSCRIPTION_CREATE = "subscription_create"
    SUBSCRIPTION_UPDATE = "subscription_update"
    SUBSCRIPTION_CANCEL = "subscription_cancel"


class AuditLog(BaseModel, TenantMixin):
    """Audit log entry for compliance tracking.

    Implements hash-chaining for tamper-proof audit trail.
    """

    __tablename__ = "audit_logs"

    # Action
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction),
        nullable=False,
        index=True,
    )

    # Resource being acted upon
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Actor
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Change tracking
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Request context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Hash chain for tamper detection
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Compliance tagging
    compliance_frameworks: Mapped[list] = mapped_column(JSONB, default=list)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action.value} on {self.resource_type}>"

    def compute_hash(self) -> str:
        """Compute hash for this entry including previous hash."""
        import hashlib
        import json

        data = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "previous_hash": self.previous_hash,
        }

        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_hash(self) -> bool:
        """Verify entry hash matches computed hash."""
        return self.entry_hash == self.compute_hash()

    @classmethod
    def create_entry(
        cls,
        tenant_id: str,
        action: AuditAction,
        resource_type: str,
        user_id: str,
        user_email: str,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        previous_hash: Optional[str] = None,
        compliance_frameworks: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Create a new audit log entry with computed hash."""
        entry = cls(
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            previous_hash=previous_hash,
            compliance_frameworks=compliance_frameworks or [],
            metadata=metadata or {},
        )

        # Compute and set the entry hash
        entry.entry_hash = entry.compute_hash()

        return entry
