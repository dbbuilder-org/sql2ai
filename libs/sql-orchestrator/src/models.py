"""Data models for SQL Orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class CheckSeverity(str, Enum):
    """Severity levels for check results."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CheckCategory(str, Enum):
    """Categories of checks."""

    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    AVAILABILITY = "availability"
    CONFIGURATION = "configuration"
    SCHEMA = "schema"


class CheckStatus(str, Enum):
    """Status of a check execution."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    """Result of a single check execution."""

    check_id: str
    check_name: str
    category: CheckCategory
    severity: CheckSeverity
    status: CheckStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    affected_objects: list[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int = 0
    before_snapshot: Optional[dict] = None
    after_snapshot: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "category": self.category.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "remediation": self.remediation,
            "affected_objects": self.affected_objects,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "before_snapshot": self.before_snapshot,
            "after_snapshot": self.after_snapshot,
        }


@dataclass
class CheckDefinition:
    """Definition of a check that can be executed."""

    id: str
    name: str
    description: str
    category: CheckCategory
    default_severity: CheckSeverity
    query: Optional[str] = None
    script: Optional[str] = None
    parameters: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    frameworks: list[str] = field(default_factory=list)  # e.g., ["SOC2", "HIPAA"]
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "default_severity": self.default_severity.value,
            "query": self.query,
            "script": self.script,
            "parameters": self.parameters,
            "enabled": self.enabled,
            "frameworks": self.frameworks,
            "tags": self.tags,
        }


@dataclass
class ScheduledCheck:
    """A check scheduled to run on a cron schedule."""

    check_id: str
    cron_expression: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    connection_ids: list[str] = field(default_factory=list)  # Empty = all connections


@dataclass
class CheckExecution:
    """Record of a check execution batch."""

    id: str
    tenant_id: str
    connection_id: str
    trigger_type: str
    trigger_source: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    results: list[CheckResult] = field(default_factory=list)
    status: CheckStatus = CheckStatus.PENDING
    error_message: Optional[str] = None

    @property
    def duration_ms(self) -> int:
        """Calculate total duration in milliseconds."""
        if not self.completed_at:
            return 0
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)

    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for r in self.results if r.status == CheckStatus.PASSED)

    @property
    def failed_count(self) -> int:
        """Count of failed checks."""
        return sum(1 for r in self.results if r.status == CheckStatus.FAILED)

    @property
    def warning_count(self) -> int:
        """Count of warning checks."""
        return sum(1 for r in self.results if r.status == CheckStatus.WARNING)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "connection_id": self.connection_id,
            "trigger_type": self.trigger_type,
            "trigger_source": self.trigger_source,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "summary": {
                "total": len(self.results),
                "passed": self.passed_count,
                "failed": self.failed_count,
                "warnings": self.warning_count,
            },
            "results": [r.to_dict() for r in self.results],
            "error_message": self.error_message,
        }


@dataclass
class DatabaseHealth:
    """Overall health status of a database."""

    connection_id: str
    connection_name: str
    overall_status: CheckStatus
    last_check: datetime
    checks_passed: int
    checks_failed: int
    checks_warning: int
    critical_issues: list[CheckResult] = field(default_factory=list)
    performance_score: float = 100.0
    security_score: float = 100.0
    compliance_score: float = 100.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "connection_id": self.connection_id,
            "connection_name": self.connection_name,
            "overall_status": self.overall_status.value,
            "last_check": self.last_check.isoformat(),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "checks_warning": self.checks_warning,
            "critical_issues": [i.to_dict() for i in self.critical_issues],
            "scores": {
                "performance": self.performance_score,
                "security": self.security_score,
                "compliance": self.compliance_score,
            },
        }


@dataclass
class OrchestratorConfig:
    """Configuration for the SQL Orchestrator."""

    tenant_id: str
    enabled: bool = True
    check_timeout_seconds: int = 300
    max_concurrent_checks: int = 5
    retention_days: int = 90
    alert_on_critical: bool = True
    alert_on_failure: bool = True
    alert_webhook_url: Optional[str] = None
    excluded_checks: list[str] = field(default_factory=list)
    custom_checks: list[CheckDefinition] = field(default_factory=list)
