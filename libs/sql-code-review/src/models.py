"""Data models for SQL Code Review."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any


class Severity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories of code review issues."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    MAINTAINABILITY = "maintainability"
    CORRECTNESS = "correctness"


class ChangeType(str, Enum):
    """Types of schema/code changes."""
    BREAKING = "breaking"
    FEATURE = "feature"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    DEPRECATED = "deprecated"


class ObjectCategory(str, Enum):
    """Database object categories for data dictionary."""
    TABLE = "table"
    VIEW = "view"
    STORED_PROCEDURE = "stored_procedure"
    FUNCTION = "function"
    TRIGGER = "trigger"
    INDEX = "index"
    CONSTRAINT = "constraint"


@dataclass
class ReviewIssue:
    """A code review issue found in SQL code."""
    rule_id: str
    category: IssueCategory
    severity: Severity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class ReviewRule:
    """A code review rule definition."""
    id: str
    name: str
    description: str
    category: IssueCategory
    severity: Severity
    pattern: Optional[str] = None  # Regex pattern
    check_function: Optional[str] = None  # Function name
    enabled: bool = True
    documentation_url: Optional[str] = None


@dataclass
class ReviewResult:
    """Result of code review."""
    file_path: Optional[str]
    code: str
    issues: list[ReviewIssue] = field(default_factory=list)
    duration_ms: int = 0
    rules_checked: int = 0
    lines_of_code: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)

    @property
    def passed(self) -> bool:
        return self.critical_count == 0 and self.high_count == 0


@dataclass
class ReleaseChange:
    """A change entry for release notes."""
    change_type: ChangeType
    object_name: str
    object_type: str
    description: str
    breaking_reason: Optional[str] = None
    migration_notes: Optional[str] = None
    affected_procedures: list[str] = field(default_factory=list)


@dataclass
class ReleaseNotes:
    """Generated release notes."""
    version: str
    release_date: datetime
    summary: str
    changes: list[ReleaseChange] = field(default_factory=list)
    breaking_changes: list[ReleaseChange] = field(default_factory=list)
    migration_sql: Optional[str] = None
    rollback_sql: Optional[str] = None

    def to_markdown(self) -> str:
        """Generate markdown release notes."""
        lines = [
            f"# Release {self.version}",
            f"**Date:** {self.release_date.strftime('%Y-%m-%d')}",
            "",
            "## Summary",
            self.summary,
            "",
        ]

        if self.breaking_changes:
            lines.extend([
                "## Breaking Changes",
                "",
            ])
            for change in self.breaking_changes:
                lines.append(f"- **{change.object_name}**: {change.description}")
                if change.breaking_reason:
                    lines.append(f"  - Reason: {change.breaking_reason}")
                if change.migration_notes:
                    lines.append(f"  - Migration: {change.migration_notes}")
            lines.append("")

        # Group changes by type
        features = [c for c in self.changes if c.change_type == ChangeType.FEATURE]
        fixes = [c for c in self.changes if c.change_type == ChangeType.FIX]
        refactors = [c for c in self.changes if c.change_type == ChangeType.REFACTOR]

        if features:
            lines.extend(["## New Features", ""])
            for change in features:
                lines.append(f"- **{change.object_name}** ({change.object_type}): {change.description}")
            lines.append("")

        if fixes:
            lines.extend(["## Bug Fixes", ""])
            for change in fixes:
                lines.append(f"- **{change.object_name}**: {change.description}")
            lines.append("")

        if refactors:
            lines.extend(["## Refactoring", ""])
            for change in refactors:
                lines.append(f"- **{change.object_name}**: {change.description}")
            lines.append("")

        return "\n".join(lines)


@dataclass
class ColumnDocumentation:
    """Documentation for a table column."""
    name: str
    data_type: str
    nullable: bool
    description: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: Optional[str] = None
    is_pii: bool = False
    pii_category: Optional[str] = None
    sample_values: list[Any] = field(default_factory=list)
    enum_values: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)


@dataclass
class RelationshipDocumentation:
    """Documentation for a table relationship."""
    name: str
    from_table: str
    from_columns: list[str]
    to_table: str
    to_columns: list[str]
    relationship_type: str  # one-to-one, one-to-many, many-to-many
    cascade_delete: bool = False
    cascade_update: bool = False


@dataclass
class ObjectDocumentation:
    """Documentation for a database object."""
    name: str
    schema_name: str
    category: ObjectCategory
    description: str
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    columns: list[ColumnDocumentation] = field(default_factory=list)
    parameters: list[dict] = field(default_factory=list)
    return_type: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    example_usage: Optional[str] = None
    notes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class DataDictionary:
    """Complete data dictionary for a database."""
    database_name: str
    generated_at: datetime
    version: str
    description: str
    objects: list[ObjectDocumentation] = field(default_factory=list)
    relationships: list[RelationshipDocumentation] = field(default_factory=list)
    glossary: dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Generate markdown data dictionary."""
        lines = [
            f"# {self.database_name} Data Dictionary",
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Version:** {self.version}",
            "",
            "## Overview",
            self.description,
            "",
        ]

        # Tables
        tables = [o for o in self.objects if o.category == ObjectCategory.TABLE]
        if tables:
            lines.extend(["## Tables", ""])
            for table in tables:
                lines.extend(self._object_to_markdown(table))
                lines.append("")

        # Views
        views = [o for o in self.objects if o.category == ObjectCategory.VIEW]
        if views:
            lines.extend(["## Views", ""])
            for view in views:
                lines.extend(self._object_to_markdown(view))
                lines.append("")

        # Stored Procedures
        procs = [o for o in self.objects if o.category == ObjectCategory.STORED_PROCEDURE]
        if procs:
            lines.extend(["## Stored Procedures", ""])
            for proc in procs:
                lines.extend(self._object_to_markdown(proc))
                lines.append("")

        # Relationships
        if self.relationships:
            lines.extend(["## Relationships", ""])
            for rel in self.relationships:
                from_cols = ", ".join(rel.from_columns)
                to_cols = ", ".join(rel.to_columns)
                lines.append(f"- **{rel.name}**: {rel.from_table}({from_cols}) → {rel.to_table}({to_cols}) [{rel.relationship_type}]")
            lines.append("")

        # Glossary
        if self.glossary:
            lines.extend(["## Glossary", ""])
            for term, definition in sorted(self.glossary.items()):
                lines.append(f"- **{term}**: {definition}")

        return "\n".join(lines)

    def _object_to_markdown(self, obj: ObjectDocumentation) -> list[str]:
        """Convert object to markdown."""
        lines = [
            f"### {obj.schema_name}.{obj.name}",
            "",
            obj.description,
            "",
        ]

        if obj.columns:
            lines.extend([
                "| Column | Type | Nullable | Description |",
                "|--------|------|----------|-------------|",
            ])
            for col in obj.columns:
                nullable = "Yes" if col.nullable else "No"
                desc = col.description
                if col.is_pii:
                    desc += " [PII]"
                if col.is_primary_key:
                    desc += " [PK]"
                if col.is_foreign_key:
                    desc += f" [FK → {col.foreign_key_reference}]"
                lines.append(f"| {col.name} | {col.data_type} | {nullable} | {desc} |")

        if obj.parameters:
            lines.extend(["", "**Parameters:**", ""])
            for param in obj.parameters:
                lines.append(f"- `@{param['name']}` ({param['type']}): {param.get('description', '')}")

        if obj.example_usage:
            lines.extend([
                "",
                "**Example:**",
                "```sql",
                obj.example_usage,
                "```",
            ])

        return lines

    def to_openapi_schema(self) -> dict:
        """Generate OpenAPI-compatible schema."""
        schemas = {}

        for obj in self.objects:
            if obj.category == ObjectCategory.TABLE:
                properties = {}
                required = []

                for col in obj.columns:
                    prop = {
                        "type": self._sql_to_openapi_type(col.data_type),
                        "description": col.description,
                    }
                    if col.enum_values:
                        prop["enum"] = col.enum_values

                    properties[col.name] = prop

                    if not col.nullable and not col.is_primary_key:
                        required.append(col.name)

                schemas[obj.name] = {
                    "type": "object",
                    "description": obj.description,
                    "properties": properties,
                }
                if required:
                    schemas[obj.name]["required"] = required

        return {
            "openapi": "3.0.0",
            "info": {
                "title": f"{self.database_name} API",
                "version": self.version,
                "description": self.description,
            },
            "components": {
                "schemas": schemas,
            },
        }

    def _sql_to_openapi_type(self, sql_type: str) -> str:
        """Map SQL type to OpenAPI type."""
        sql_type = sql_type.upper()

        if any(t in sql_type for t in ["INT", "BIGINT", "SMALLINT", "TINYINT"]):
            return "integer"
        elif any(t in sql_type for t in ["DECIMAL", "NUMERIC", "FLOAT", "REAL", "MONEY"]):
            return "number"
        elif "BIT" in sql_type:
            return "boolean"
        elif any(t in sql_type for t in ["DATE", "TIME", "DATETIME"]):
            return "string"  # with format: date-time
        else:
            return "string"
