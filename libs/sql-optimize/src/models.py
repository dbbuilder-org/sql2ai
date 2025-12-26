"""Data models for SQL Optimize."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class IssueSeverity(str, Enum):
    """Severity levels for performance issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories of performance issues."""

    QUERY = "query"
    INDEX = "index"
    STATISTICS = "statistics"
    BLOCKING = "blocking"
    DEADLOCK = "deadlock"
    MEMORY = "memory"
    IO = "io"
    CPU = "cpu"
    TEMPDB = "tempdb"
    CONFIGURATION = "configuration"


class FixComplexity(str, Enum):
    """Complexity of applying a fix."""

    TRIVIAL = "trivial"  # One-click, no risk
    SIMPLE = "simple"  # Minor change, low risk
    MODERATE = "moderate"  # Requires review
    COMPLEX = "complex"  # Significant change, needs planning
    REQUIRES_DOWNTIME = "requires_downtime"  # Maintenance window needed


@dataclass
class PerformanceIssue:
    """A detected performance issue."""

    id: str
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    affected_object: str
    impact: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_object": self.affected_object,
            "impact": self.impact,
            "detected_at": self.detected_at.isoformat(),
            "metrics": self.metrics,
        }


@dataclass
class Recommendation:
    """A performance optimization recommendation."""

    id: str
    issue_id: str
    title: str
    description: str
    fix_script: Optional[str] = None
    rollback_script: Optional[str] = None
    complexity: FixComplexity = FixComplexity.SIMPLE
    estimated_improvement: Optional[str] = None
    risk_level: str = "low"
    requires_testing: bool = False
    prerequisites: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "fix_script": self.fix_script,
            "rollback_script": self.rollback_script,
            "complexity": self.complexity.value,
            "estimated_improvement": self.estimated_improvement,
            "risk_level": self.risk_level,
            "requires_testing": self.requires_testing,
            "prerequisites": self.prerequisites,
        }


@dataclass
class QueryAnalysis:
    """Analysis of a specific query."""

    query_hash: str
    query_text: str
    execution_count: int
    avg_duration_ms: float
    max_duration_ms: float
    avg_cpu_time_ms: float
    avg_logical_reads: int
    avg_physical_reads: int
    avg_writes: int
    last_execution: Optional[datetime] = None
    plan_count: int = 1
    has_plan_regression: bool = False
    issues: list[PerformanceIssue] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_hash": self.query_hash,
            "query_text": self.query_text[:500] + "..." if len(self.query_text) > 500 else self.query_text,
            "execution_count": self.execution_count,
            "avg_duration_ms": self.avg_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "avg_cpu_time_ms": self.avg_cpu_time_ms,
            "avg_logical_reads": self.avg_logical_reads,
            "avg_physical_reads": self.avg_physical_reads,
            "avg_writes": self.avg_writes,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "plan_count": self.plan_count,
            "has_plan_regression": self.has_plan_regression,
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": [r.to_dict() for r in self.recommendations],
        }


@dataclass
class IndexAnalysis:
    """Analysis of index usage and recommendations."""

    table_name: str
    index_name: str
    index_type: str
    columns: list[str]
    included_columns: list[str] = field(default_factory=list)
    size_mb: float = 0
    fragmentation_percent: float = 0
    user_seeks: int = 0
    user_scans: int = 0
    user_lookups: int = 0
    user_updates: int = 0
    is_unused: bool = False
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    maintenance_recommendation: Optional[str] = None

    @property
    def read_write_ratio(self) -> float:
        """Calculate read/write ratio."""
        reads = self.user_seeks + self.user_scans + self.user_lookups
        if self.user_updates == 0:
            return float("inf") if reads > 0 else 0
        return reads / self.user_updates

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "index_name": self.index_name,
            "index_type": self.index_type,
            "columns": self.columns,
            "included_columns": self.included_columns,
            "size_mb": self.size_mb,
            "fragmentation_percent": self.fragmentation_percent,
            "usage": {
                "seeks": self.user_seeks,
                "scans": self.user_scans,
                "lookups": self.user_lookups,
                "updates": self.user_updates,
                "read_write_ratio": self.read_write_ratio if self.read_write_ratio != float("inf") else "inf",
            },
            "is_unused": self.is_unused,
            "is_duplicate": self.is_duplicate,
            "duplicate_of": self.duplicate_of,
            "maintenance_recommendation": self.maintenance_recommendation,
        }


@dataclass
class MissingIndex:
    """A missing index suggestion."""

    table_name: str
    equality_columns: list[str]
    inequality_columns: list[str]
    included_columns: list[str]
    unique_compiles: int
    user_seeks: int
    user_scans: int
    avg_total_user_cost: float
    avg_user_impact: float
    suggested_index_name: str = ""
    create_statement: str = ""

    @property
    def improvement_score(self) -> float:
        """Calculate improvement score."""
        return self.avg_user_impact * self.avg_total_user_cost * (self.user_seeks + self.user_scans)

    def __post_init__(self):
        """Generate index name and create statement."""
        if not self.suggested_index_name:
            cols = "_".join(self.equality_columns[:2]) if self.equality_columns else "cols"
            self.suggested_index_name = f"IX_{self.table_name.split('.')[-1]}_{cols}"

        if not self.create_statement:
            key_cols = self.equality_columns + self.inequality_columns
            self.create_statement = f"CREATE NONCLUSTERED INDEX [{self.suggested_index_name}] ON {self.table_name} ({', '.join(key_cols)})"
            if self.included_columns:
                self.create_statement += f" INCLUDE ({', '.join(self.included_columns)})"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "equality_columns": self.equality_columns,
            "inequality_columns": self.inequality_columns,
            "included_columns": self.included_columns,
            "stats": {
                "unique_compiles": self.unique_compiles,
                "user_seeks": self.user_seeks,
                "user_scans": self.user_scans,
                "avg_total_user_cost": self.avg_total_user_cost,
                "avg_user_impact": self.avg_user_impact,
                "improvement_score": self.improvement_score,
            },
            "suggested_index_name": self.suggested_index_name,
            "create_statement": self.create_statement,
        }


@dataclass
class WaitStatistics:
    """Wait statistics analysis."""

    wait_type: str
    waiting_tasks_count: int
    wait_time_ms: int
    signal_wait_time_ms: int
    category: str = ""
    description: str = ""
    recommendation: Optional[str] = None

    @property
    def resource_wait_time_ms(self) -> int:
        """Calculate resource wait time."""
        return self.wait_time_ms - self.signal_wait_time_ms

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "wait_type": self.wait_type,
            "waiting_tasks_count": self.waiting_tasks_count,
            "wait_time_ms": self.wait_time_ms,
            "signal_wait_time_ms": self.signal_wait_time_ms,
            "resource_wait_time_ms": self.resource_wait_time_ms,
            "category": self.category,
            "description": self.description,
            "recommendation": self.recommendation,
        }


@dataclass
class OptimizationReport:
    """Complete optimization report for a database."""

    connection_id: str
    database_name: str
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int = 0

    # Analysis results
    top_queries: list[QueryAnalysis] = field(default_factory=list)
    index_analysis: list[IndexAnalysis] = field(default_factory=list)
    missing_indexes: list[MissingIndex] = field(default_factory=list)
    wait_statistics: list[WaitStatistics] = field(default_factory=list)

    # Issues and recommendations
    issues: list[PerformanceIssue] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)

    # Summary metrics
    health_score: float = 100.0
    critical_issues: int = 0
    high_issues: int = 0
    total_issues: int = 0

    def calculate_health_score(self) -> float:
        """Calculate overall health score."""
        score = 100.0

        # Deduct for issues
        for issue in self.issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 20
            elif issue.severity == IssueSeverity.HIGH:
                score -= 10
            elif issue.severity == IssueSeverity.MEDIUM:
                score -= 5
            elif issue.severity == IssueSeverity.LOW:
                score -= 2

        return max(0, min(100, score))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        self.health_score = self.calculate_health_score()
        self.critical_issues = sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)
        self.high_issues = sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH)
        self.total_issues = len(self.issues)

        return {
            "connection_id": self.connection_id,
            "database_name": self.database_name,
            "analyzed_at": self.analyzed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "summary": {
                "health_score": self.health_score,
                "critical_issues": self.critical_issues,
                "high_issues": self.high_issues,
                "total_issues": self.total_issues,
                "recommendations_count": len(self.recommendations),
            },
            "top_queries": [q.to_dict() for q in self.top_queries[:10]],
            "index_analysis": [i.to_dict() for i in self.index_analysis],
            "missing_indexes": [m.to_dict() for m in self.missing_indexes[:10]],
            "wait_statistics": [w.to_dict() for w in self.wait_statistics[:10]],
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": [r.to_dict() for r in self.recommendations],
        }
