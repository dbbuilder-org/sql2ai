"""Domain event types."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from ulid import ULID


class DomainEvent(BaseModel):
    """Base class for all domain events."""

    event_id: str = Field(default_factory=lambda: str(ULID()))
    event_type: str
    tenant_id: str
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


# Query Events
class QueryExecutedEvent(DomainEvent):
    """Emitted when a query is executed."""

    event_type: str = "query.executed"

    # Payload fields
    connection_id: str = ""
    query_hash: str = ""
    duration_ms: float = 0
    rows_affected: int = 0
    success: bool = True
    error: Optional[str] = None


class QueryOptimizedEvent(DomainEvent):
    """Emitted when query optimization is suggested."""

    event_type: str = "query.optimized"

    query_hash: str = ""
    optimization_type: str = ""
    estimated_improvement: float = 0


# Migration Events
class MigrationAppliedEvent(DomainEvent):
    """Emitted when a migration is applied."""

    event_type: str = "migration.applied"

    migration_id: str = ""
    migration_name: str = ""
    connection_id: str = ""
    duration_ms: float = 0
    success: bool = True
    rollback_available: bool = True


class MigrationRolledBackEvent(DomainEvent):
    """Emitted when a migration is rolled back."""

    event_type: str = "migration.rolled_back"

    migration_id: str = ""
    reason: str = ""


# Alert Events
class AlertTriggeredEvent(DomainEvent):
    """Emitted when an alert is triggered."""

    event_type: str = "alert.triggered"

    alert_id: str = ""
    alert_name: str = ""
    severity: str = ""  # info, warning, error, critical
    metric_name: str = ""
    threshold: float = 0
    current_value: float = 0
    message: str = ""


class AlertResolvedEvent(DomainEvent):
    """Emitted when an alert is resolved."""

    event_type: str = "alert.resolved"

    alert_id: str = ""
    resolution: str = ""  # auto, manual, acknowledged


# Compliance Events
class ComplianceViolationEvent(DomainEvent):
    """Emitted when a compliance violation is detected."""

    event_type: str = "compliance.violation"

    violation_id: str = ""
    rule_id: str = ""
    rule_name: str = ""
    framework: str = ""  # SOC2, HIPAA, GDPR, PCI-DSS
    severity: str = ""
    resource_type: str = ""
    resource_id: str = ""
    description: str = ""
    remediation: str = ""


class ComplianceScanCompletedEvent(DomainEvent):
    """Emitted when a compliance scan completes."""

    event_type: str = "compliance.scan_completed"

    scan_id: str = ""
    framework: str = ""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0


# AI Events
class AIRequestEvent(DomainEvent):
    """Emitted when an AI request is made."""

    event_type: str = "ai.request"

    request_id: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_ms: float = 0
    success: bool = True


class AIAgentActionEvent(DomainEvent):
    """Emitted when an AI agent takes an action."""

    event_type: str = "ai.agent_action"

    agent_type: str = ""
    action: str = ""
    requires_approval: bool = False
    auto_approved: bool = False
    result: Optional[str] = None


# Connection Events
class ConnectionCreatedEvent(DomainEvent):
    """Emitted when a database connection is created."""

    event_type: str = "connection.created"

    connection_id: str = ""
    database_type: str = ""  # sqlserver, postgresql
    server: str = ""
    database: str = ""


class ConnectionDeletedEvent(DomainEvent):
    """Emitted when a database connection is deleted."""

    event_type: str = "connection.deleted"

    connection_id: str = ""
    reason: str = ""


# User Events
class UserCreatedEvent(DomainEvent):
    """Emitted when a user is created."""

    event_type: str = "user.created"

    new_user_id: str = ""
    email: str = ""
    role: str = ""


class UserPermissionChangedEvent(DomainEvent):
    """Emitted when user permissions change."""

    event_type: str = "user.permission_changed"

    target_user_id: str = ""
    old_permissions: list = Field(default_factory=list)
    new_permissions: list = Field(default_factory=list)
