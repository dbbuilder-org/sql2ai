"""Data models for SQL Migrator."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MigrationStatus(str, Enum):
    """Status of a migration."""

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class BreakingChangeSeverity(str, Enum):
    """Severity of a breaking change."""

    CRITICAL = "critical"  # Data loss, requires downtime
    HIGH = "high"  # May cause errors in dependent code
    MEDIUM = "medium"  # Behavior change, requires review
    LOW = "low"  # Cosmetic or minor impact


class CodeLanguage(str, Enum):
    """Supported code generation languages."""

    CSHARP = "csharp"  # C# for Dapper
    TYPESCRIPT = "typescript"  # TypeScript types
    ZOD = "zod"  # Zod schemas for validation


@dataclass
class BreakingChange:
    """A breaking change in a migration."""

    change_type: str  # column_removed, type_changed, constraint_added, etc.
    severity: BreakingChangeSeverity
    object_name: str
    description: str
    data_loss_risk: bool = False
    remediation: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "type": self.change_type,
            "severity": self.severity.value,
            "object": self.object_name,
            "description": self.description,
            "data_loss_risk": self.data_loss_risk,
            "remediation": self.remediation,
        }


@dataclass
class MigrationStep:
    """A single step in a migration."""

    order: int
    description: str
    forward_sql: str
    rollback_sql: Optional[str] = None
    is_transactional: bool = True
    requires_lock: bool = False
    estimated_duration_ms: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "order": self.order,
            "description": self.description,
            "forward_sql": self.forward_sql,
            "rollback_sql": self.rollback_sql,
            "is_transactional": self.is_transactional,
            "requires_lock": self.requires_lock,
            "estimated_duration_ms": self.estimated_duration_ms,
        }


@dataclass
class Migration:
    """A database migration."""

    id: str
    name: str
    version: str
    description: str
    dialect: str  # sqlserver, postgresql
    steps: list[MigrationStep] = field(default_factory=list)
    breaking_changes: list[BreakingChange] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    status: MigrationStatus = MigrationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = None
    applied_by: Optional[str] = None
    checksum: Optional[str] = None

    def __post_init__(self):
        """Calculate checksum if not provided."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of migration content."""
        content = "".join(step.forward_sql for step in self.steps)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def forward_script(self) -> str:
        """Get the full forward migration script."""
        lines = [
            f"-- Migration: {self.name}",
            f"-- Version: {self.version}",
            f"-- Generated: {self.created_at.isoformat()}",
            f"-- Checksum: {self.checksum}",
            "",
        ]

        for step in sorted(self.steps, key=lambda s: s.order):
            lines.append(f"-- Step {step.order}: {step.description}")
            lines.append(step.forward_sql)
            lines.append("")

        return "\n".join(lines)

    @property
    def rollback_script(self) -> str:
        """Get the full rollback script."""
        lines = [
            f"-- Rollback: {self.name}",
            f"-- Version: {self.version}",
            "",
        ]

        # Rollback in reverse order
        for step in sorted(self.steps, key=lambda s: s.order, reverse=True):
            if step.rollback_sql:
                lines.append(f"-- Undo Step {step.order}: {step.description}")
                lines.append(step.rollback_sql)
                lines.append("")

        return "\n".join(lines)

    @property
    def has_breaking_changes(self) -> bool:
        """Check if migration has breaking changes."""
        return len(self.breaking_changes) > 0

    @property
    def has_data_loss_risk(self) -> bool:
        """Check if migration has data loss risk."""
        return any(bc.data_loss_risk for bc in self.breaking_changes)

    @property
    def requires_downtime(self) -> bool:
        """Check if migration requires downtime."""
        return any(
            bc.severity == BreakingChangeSeverity.CRITICAL
            for bc in self.breaking_changes
        ) or any(step.requires_lock for step in self.steps)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dialect": self.dialect,
            "status": self.status.value,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "applied_by": self.applied_by,
            "dependencies": self.dependencies,
            "steps": [s.to_dict() for s in self.steps],
            "breaking_changes": [bc.to_dict() for bc in self.breaking_changes],
            "has_breaking_changes": self.has_breaking_changes,
            "has_data_loss_risk": self.has_data_loss_risk,
            "requires_downtime": self.requires_downtime,
        }


@dataclass
class GeneratedCode:
    """Generated code from schema."""

    language: CodeLanguage
    file_name: str
    content: str
    source_tables: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "language": self.language.value,
            "file_name": self.file_name,
            "content": self.content,
            "source_tables": self.source_tables,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class MigrationPlan:
    """A plan for executing multiple migrations."""

    migrations: list[Migration] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    total_breaking_changes: int = 0
    requires_downtime: bool = False
    estimated_duration_ms: int = 0
    generated_code: list[GeneratedCode] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "migrations": [m.to_dict() for m in self.migrations],
            "execution_order": self.execution_order,
            "total_breaking_changes": self.total_breaking_changes,
            "requires_downtime": self.requires_downtime,
            "estimated_duration_ms": self.estimated_duration_ms,
            "generated_code": [gc.to_dict() for gc in self.generated_code],
        }
