"""Data models for SQL Version."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
import hashlib


class ObjectType(str, Enum):
    """Types of database objects that can be versioned."""
    TABLE = "table"
    VIEW = "view"
    STORED_PROCEDURE = "stored_procedure"
    FUNCTION = "function"
    TRIGGER = "trigger"
    INDEX = "index"
    CONSTRAINT = "constraint"
    TYPE = "type"
    SYNONYM = "synonym"
    SEQUENCE = "sequence"


class ChangeAction(str, Enum):
    """Types of changes to objects."""
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    RENAME = "rename"


@dataclass
class ObjectVersion:
    """A version of a database object."""
    id: str
    object_name: str
    schema_name: str
    object_type: ObjectType
    version_number: int
    definition: str
    content_hash: str
    created_at: datetime
    created_by: str
    message: Optional[str] = None
    parent_version_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def compute_hash(definition: str) -> str:
        """Compute content hash for a definition."""
        # Normalize whitespace for consistent hashing
        normalized = " ".join(definition.split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    @property
    def full_name(self) -> str:
        """Get fully qualified object name."""
        return f"{self.schema_name}.{self.object_name}"


@dataclass
class ObjectHistory:
    """Complete history of a database object."""
    object_name: str
    schema_name: str
    object_type: ObjectType
    versions: list[ObjectVersion] = field(default_factory=list)
    current_version_id: Optional[str] = None

    @property
    def version_count(self) -> int:
        return len(self.versions)

    @property
    def current_version(self) -> Optional[ObjectVersion]:
        if self.current_version_id:
            return next((v for v in self.versions if v.id == self.current_version_id), None)
        return self.versions[-1] if self.versions else None

    @property
    def full_name(self) -> str:
        return f"{self.schema_name}.{self.object_name}"


@dataclass
class VersionDiff:
    """Difference between two versions."""
    from_version_id: Optional[str]
    to_version_id: str
    object_name: str
    schema_name: str
    object_type: ObjectType
    action: ChangeAction
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    context_lines: list[tuple[int, str]] = field(default_factory=list)

    @property
    def additions(self) -> int:
        return len(self.added_lines)

    @property
    def deletions(self) -> int:
        return len(self.removed_lines)

    def to_unified_diff(self) -> str:
        """Generate unified diff format."""
        lines = [
            f"--- a/{self.schema_name}.{self.object_name}",
            f"+++ b/{self.schema_name}.{self.object_name}",
        ]

        for line in self.removed_lines:
            lines.append(f"-{line}")
        for line in self.added_lines:
            lines.append(f"+{line}")

        return "\n".join(lines)


@dataclass
class BlameLine:
    """Attribution for a single line of code."""
    line_number: int
    content: str
    version_id: str
    version_number: int
    author: str
    timestamp: datetime
    commit_message: Optional[str] = None


@dataclass
class BlameResult:
    """Complete blame result for an object."""
    object_name: str
    schema_name: str
    object_type: ObjectType
    lines: list[BlameLine] = field(default_factory=list)

    def get_authors(self) -> list[str]:
        """Get unique authors."""
        return list(set(line.author for line in self.lines))

    def get_line_counts_by_author(self) -> dict[str, int]:
        """Get line counts per author."""
        counts: dict[str, int] = {}
        for line in self.lines:
            counts[line.author] = counts.get(line.author, 0) + 1
        return counts


@dataclass
class Branch:
    """A branch for database object versions."""
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_default: bool = False
    head_versions: dict[str, str] = field(default_factory=dict)  # object_full_name -> version_id

    @property
    def is_main(self) -> bool:
        return self.name in ("main", "master", "production")


@dataclass
class Tag:
    """A tag marking a specific point in version history."""
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    version_snapshot: dict[str, str] = field(default_factory=dict)  # object_full_name -> version_id


@dataclass
class MergeConflict:
    """A merge conflict between branches."""
    object_name: str
    schema_name: str
    object_type: ObjectType
    source_version_id: str
    target_version_id: str
    base_version_id: Optional[str]
    source_content: str
    target_content: str
    base_content: Optional[str]
    conflicting_lines: list[tuple[int, str, str]] = field(default_factory=list)  # (line, source, target)


@dataclass
class MergeResult:
    """Result of a branch merge."""
    source_branch: str
    target_branch: str
    merged_objects: list[str] = field(default_factory=list)
    conflicts: list[MergeConflict] = field(default_factory=list)
    success: bool = True
    message: Optional[str] = None

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


@dataclass
class SyncStatus:
    """Status of synchronization between database and version control."""
    database_name: str
    branch: str
    last_sync: Optional[datetime] = None
    objects_in_sync: int = 0
    objects_ahead: int = 0  # Local changes not in DB
    objects_behind: int = 0  # DB changes not versioned
    modified_objects: list[str] = field(default_factory=list)
    untracked_objects: list[str] = field(default_factory=list)


@dataclass
class VersionControlConfig:
    """Configuration for version control."""
    repository_path: str
    default_branch: str = "main"
    auto_commit: bool = False
    track_ddl_changes: bool = True
    track_data_changes: bool = False
    excluded_schemas: list[str] = field(default_factory=lambda: ["sys", "INFORMATION_SCHEMA"])
    excluded_objects: list[str] = field(default_factory=list)
    commit_author: Optional[str] = None
    commit_email: Optional[str] = None
