"""Audit log models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ulid import ULID
import hashlib
import json


class AuditAction(str, Enum):
    """Standard audit actions."""

    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    PASSWORD_CHANGE = "auth.password_change"
    MFA_ENABLED = "auth.mfa_enabled"
    MFA_DISABLED = "auth.mfa_disabled"

    # User management
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_SUSPEND = "user.suspend"
    USER_ACTIVATE = "user.activate"

    # Permission changes
    PERMISSION_GRANT = "permission.grant"
    PERMISSION_REVOKE = "permission.revoke"
    ROLE_ASSIGN = "role.assign"
    ROLE_REMOVE = "role.remove"

    # Data access
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"

    # Database operations
    QUERY_EXECUTE = "query.execute"
    SCHEMA_CHANGE = "schema.change"
    MIGRATION_APPLY = "migration.apply"
    MIGRATION_ROLLBACK = "migration.rollback"

    # Connection management
    CONNECTION_CREATE = "connection.create"
    CONNECTION_UPDATE = "connection.update"
    CONNECTION_DELETE = "connection.delete"
    CONNECTION_TEST = "connection.test"

    # AI operations
    AI_QUERY = "ai.query"
    AI_GENERATE = "ai.generate"
    AI_APPROVE = "ai.approve"
    AI_REJECT = "ai.reject"

    # Compliance
    COMPLIANCE_SCAN = "compliance.scan"
    COMPLIANCE_EXCEPTION = "compliance.exception"
    PII_ACCESS = "pii.access"
    PII_REDACT = "pii.redact"

    # System
    CONFIG_CHANGE = "config.change"
    BACKUP_CREATE = "backup.create"
    BACKUP_RESTORE = "backup.restore"

    # Custom
    CUSTOM = "custom"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEntry(BaseModel):
    """Tamper-proof audit log entry."""

    # Identity
    id: str = Field(default_factory=lambda: str(ULID()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Actor
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Tenant
    tenant_id: str

    # Action
    action: AuditAction
    severity: AuditSeverity = AuditSeverity.INFO

    # Resource
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None

    # Details
    details: Dict[str, Any] = Field(default_factory=dict)
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None

    # Outcome
    success: bool = True
    error_message: Optional[str] = None

    # Integrity
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    # Compliance
    compliance_frameworks: List[str] = Field(default_factory=list)
    retention_days: int = 365
    immutable: bool = True

    def compute_hash(self) -> str:
        """Compute hash for tamper detection."""
        # Include all important fields in hash
        hash_content = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "success": self.success,
            "previous_hash": self.previous_hash,
        }

        content_str = json.dumps(hash_content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def set_hash(self, previous_hash: Optional[str] = None) -> None:
        """Set the entry hash with chain reference."""
        self.previous_hash = previous_hash
        self.entry_hash = self.compute_hash()

    def verify_integrity(self) -> bool:
        """Verify the entry hasn't been tampered with."""
        if not self.entry_hash:
            return False
        return self.compute_hash() == self.entry_hash

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class AuditQuery(BaseModel):
    """Query parameters for searching audit logs."""

    tenant_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    actions: Optional[List[AuditAction]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    severity: Optional[List[AuditSeverity]] = None
    success: Optional[bool] = None
    search: Optional[str] = None
    limit: int = 100
    offset: int = 0
    order_by: str = "timestamp"
    order_desc: bool = True


class AuditSummary(BaseModel):
    """Summary of audit activity."""

    tenant_id: str
    period_start: datetime
    period_end: datetime
    total_events: int
    events_by_action: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_user: Dict[str, int]
    failed_events: int
    unique_users: int
    unique_resources: int


# Action severity mappings
ACTION_SEVERITY_MAP: Dict[AuditAction, AuditSeverity] = {
    # Critical
    AuditAction.USER_DELETE: AuditSeverity.CRITICAL,
    AuditAction.SCHEMA_CHANGE: AuditSeverity.CRITICAL,
    AuditAction.MIGRATION_APPLY: AuditSeverity.CRITICAL,
    AuditAction.BACKUP_RESTORE: AuditSeverity.CRITICAL,
    AuditAction.CONFIG_CHANGE: AuditSeverity.CRITICAL,

    # High
    AuditAction.PERMISSION_GRANT: AuditSeverity.HIGH,
    AuditAction.PERMISSION_REVOKE: AuditSeverity.HIGH,
    AuditAction.ROLE_ASSIGN: AuditSeverity.HIGH,
    AuditAction.ROLE_REMOVE: AuditSeverity.HIGH,
    AuditAction.USER_SUSPEND: AuditSeverity.HIGH,
    AuditAction.PII_ACCESS: AuditSeverity.HIGH,
    AuditAction.DATA_EXPORT: AuditSeverity.HIGH,

    # Medium
    AuditAction.USER_CREATE: AuditSeverity.MEDIUM,
    AuditAction.USER_UPDATE: AuditSeverity.MEDIUM,
    AuditAction.CONNECTION_CREATE: AuditSeverity.MEDIUM,
    AuditAction.CONNECTION_DELETE: AuditSeverity.MEDIUM,
    AuditAction.PASSWORD_CHANGE: AuditSeverity.MEDIUM,
    AuditAction.MFA_ENABLED: AuditSeverity.MEDIUM,
    AuditAction.MFA_DISABLED: AuditSeverity.MEDIUM,
    AuditAction.AI_APPROVE: AuditSeverity.MEDIUM,
    AuditAction.AI_REJECT: AuditSeverity.MEDIUM,

    # Low
    AuditAction.LOGIN: AuditSeverity.LOW,
    AuditAction.LOGOUT: AuditSeverity.LOW,
    AuditAction.LOGIN_FAILED: AuditSeverity.LOW,
    AuditAction.QUERY_EXECUTE: AuditSeverity.LOW,
    AuditAction.DATA_READ: AuditSeverity.LOW,

    # Info
    AuditAction.CONNECTION_TEST: AuditSeverity.INFO,
    AuditAction.AI_QUERY: AuditSeverity.INFO,
    AuditAction.COMPLIANCE_SCAN: AuditSeverity.INFO,
}


def get_action_severity(action: AuditAction) -> AuditSeverity:
    """Get the default severity for an action."""
    return ACTION_SEVERITY_MAP.get(action, AuditSeverity.INFO)
