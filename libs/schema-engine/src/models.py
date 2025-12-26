"""Data models for database schema representation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class DataType(str, Enum):
    """Common database data types."""

    # Numeric
    INT = "int"
    BIGINT = "bigint"
    SMALLINT = "smallint"
    TINYINT = "tinyint"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    FLOAT = "float"
    REAL = "real"
    MONEY = "money"
    BIT = "bit"

    # String
    CHAR = "char"
    VARCHAR = "varchar"
    NCHAR = "nchar"
    NVARCHAR = "nvarchar"
    TEXT = "text"
    NTEXT = "ntext"

    # Date/Time
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    DATETIME2 = "datetime2"
    SMALLDATETIME = "smalldatetime"
    DATETIMEOFFSET = "datetimeoffset"
    TIMESTAMP = "timestamp"

    # Binary
    BINARY = "binary"
    VARBINARY = "varbinary"
    IMAGE = "image"

    # Other
    UNIQUEIDENTIFIER = "uniqueidentifier"
    XML = "xml"
    JSON = "json"
    GEOGRAPHY = "geography"
    GEOMETRY = "geometry"
    HIERARCHYID = "hierarchyid"
    SQL_VARIANT = "sql_variant"

    # PostgreSQL specific
    SERIAL = "serial"
    BIGSERIAL = "bigserial"
    BOOLEAN = "boolean"
    UUID = "uuid"
    JSONB = "jsonb"
    ARRAY = "array"
    BYTEA = "bytea"
    INET = "inet"
    CIDR = "cidr"
    MACADDR = "macaddr"
    TSQUERY = "tsquery"
    TSVECTOR = "tsvector"

    # Unknown
    UNKNOWN = "unknown"


class IndexType(str, Enum):
    """Types of database indexes."""

    CLUSTERED = "clustered"
    NONCLUSTERED = "nonclustered"
    UNIQUE = "unique"
    FULLTEXT = "fulltext"
    SPATIAL = "spatial"
    COLUMNSTORE = "columnstore"
    HASH = "hash"
    BTREE = "btree"
    GIN = "gin"
    GIST = "gist"
    BRIN = "brin"


class ConstraintType(str, Enum):
    """Types of database constraints."""

    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    DEFAULT = "default"
    NOT_NULL = "not_null"


class TriggerTiming(str, Enum):
    """Trigger timing options."""

    BEFORE = "before"
    AFTER = "after"
    INSTEAD_OF = "instead_of"


class TriggerEvent(str, Enum):
    """Trigger event types."""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ColumnInfo:
    """Information about a database column."""

    name: str
    data_type: str
    data_type_normalized: DataType
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_nullable: bool = True
    is_identity: bool = False
    is_computed: bool = False
    is_primary_key: bool = False
    default_value: Optional[str] = None
    computed_definition: Optional[str] = None
    collation: Optional[str] = None
    description: Optional[str] = None
    ordinal_position: int = 0

    # For AI documentation
    inferred_purpose: Optional[str] = None
    sample_values: list[str] = field(default_factory=list)
    is_pii: bool = False
    pii_type: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "data_type_normalized": self.data_type_normalized.value,
            "max_length": self.max_length,
            "precision": self.precision,
            "scale": self.scale,
            "is_nullable": self.is_nullable,
            "is_identity": self.is_identity,
            "is_computed": self.is_computed,
            "is_primary_key": self.is_primary_key,
            "default_value": self.default_value,
            "computed_definition": self.computed_definition,
            "collation": self.collation,
            "description": self.description,
            "ordinal_position": self.ordinal_position,
            "inferred_purpose": self.inferred_purpose,
            "sample_values": self.sample_values,
            "is_pii": self.is_pii,
            "pii_type": self.pii_type,
        }


@dataclass
class IndexInfo:
    """Information about a database index."""

    name: str
    index_type: IndexType
    is_unique: bool = False
    is_primary_key: bool = False
    is_clustered: bool = False
    columns: list[str] = field(default_factory=list)
    included_columns: list[str] = field(default_factory=list)
    filter_definition: Optional[str] = None
    fill_factor: Optional[int] = None
    is_disabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "index_type": self.index_type.value,
            "is_unique": self.is_unique,
            "is_primary_key": self.is_primary_key,
            "is_clustered": self.is_clustered,
            "columns": self.columns,
            "included_columns": self.included_columns,
            "filter_definition": self.filter_definition,
            "fill_factor": self.fill_factor,
            "is_disabled": self.is_disabled,
        }


@dataclass
class ForeignKeyInfo:
    """Information about a foreign key relationship."""

    name: str
    columns: list[str]
    referenced_table: str
    referenced_schema: str
    referenced_columns: list[str]
    on_delete: str = "NO ACTION"
    on_update: str = "NO ACTION"
    is_disabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "columns": self.columns,
            "referenced_table": self.referenced_table,
            "referenced_schema": self.referenced_schema,
            "referenced_columns": self.referenced_columns,
            "on_delete": self.on_delete,
            "on_update": self.on_update,
            "is_disabled": self.is_disabled,
        }


@dataclass
class TableInfo:
    """Information about a database table."""

    name: str
    schema: str
    columns: list[ColumnInfo] = field(default_factory=list)
    indexes: list[IndexInfo] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    primary_key_columns: list[str] = field(default_factory=list)
    row_count: Optional[int] = None
    data_size_bytes: Optional[int] = None
    index_size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None
    is_temporal: bool = False
    temporal_history_table: Optional[str] = None

    # For AI documentation
    inferred_purpose: Optional[str] = None
    inferred_entity_type: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema}.{self.name}"

    def get_column(self, name: str) -> Optional[ColumnInfo]:
        """Get column by name."""
        for col in self.columns:
            if col.name.lower() == name.lower():
                return col
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "full_name": self.full_name,
            "columns": [c.to_dict() for c in self.columns],
            "indexes": [i.to_dict() for i in self.indexes],
            "foreign_keys": [f.to_dict() for f in self.foreign_keys],
            "primary_key_columns": self.primary_key_columns,
            "row_count": self.row_count,
            "data_size_bytes": self.data_size_bytes,
            "index_size_bytes": self.index_size_bytes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "description": self.description,
            "is_temporal": self.is_temporal,
            "temporal_history_table": self.temporal_history_table,
            "inferred_purpose": self.inferred_purpose,
            "inferred_entity_type": self.inferred_entity_type,
        }


@dataclass
class ViewInfo:
    """Information about a database view."""

    name: str
    schema: str
    definition: str
    columns: list[ColumnInfo] = field(default_factory=list)
    is_indexed: bool = False
    is_materialized: bool = False
    referenced_tables: list[str] = field(default_factory=list)
    description: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get fully qualified view name."""
        return f"{self.schema}.{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "full_name": self.full_name,
            "definition": self.definition,
            "columns": [c.to_dict() for c in self.columns],
            "is_indexed": self.is_indexed,
            "is_materialized": self.is_materialized,
            "referenced_tables": self.referenced_tables,
            "description": self.description,
        }


@dataclass
class ParameterInfo:
    """Information about a stored procedure or function parameter."""

    name: str
    data_type: str
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_output: bool = False
    has_default: bool = False
    default_value: Optional[str] = None
    ordinal_position: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "max_length": self.max_length,
            "precision": self.precision,
            "scale": self.scale,
            "is_output": self.is_output,
            "has_default": self.has_default,
            "default_value": self.default_value,
            "ordinal_position": self.ordinal_position,
        }


@dataclass
class ProcedureInfo:
    """Information about a stored procedure."""

    name: str
    schema: str
    definition: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None
    is_encrypted: bool = False
    referenced_tables: list[str] = field(default_factory=list)
    referenced_procedures: list[str] = field(default_factory=list)

    # For AI analysis
    complexity_score: Optional[int] = None
    has_cursors: bool = False
    has_dynamic_sql: bool = False
    estimated_lines: int = 0

    @property
    def full_name(self) -> str:
        """Get fully qualified procedure name."""
        return f"{self.schema}.{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "full_name": self.full_name,
            "definition": self.definition,
            "parameters": [p.to_dict() for p in self.parameters],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "description": self.description,
            "is_encrypted": self.is_encrypted,
            "referenced_tables": self.referenced_tables,
            "referenced_procedures": self.referenced_procedures,
            "complexity_score": self.complexity_score,
            "has_cursors": self.has_cursors,
            "has_dynamic_sql": self.has_dynamic_sql,
            "estimated_lines": self.estimated_lines,
        }


@dataclass
class FunctionInfo:
    """Information about a database function."""

    name: str
    schema: str
    definition: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    is_table_valued: bool = False
    is_scalar: bool = True
    is_deterministic: bool = False
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get fully qualified function name."""
        return f"{self.schema}.{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "full_name": self.full_name,
            "definition": self.definition,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "is_table_valued": self.is_table_valued,
            "is_scalar": self.is_scalar,
            "is_deterministic": self.is_deterministic,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "description": self.description,
        }


@dataclass
class TriggerInfo:
    """Information about a database trigger."""

    name: str
    schema: str
    table_name: str
    table_schema: str
    definition: str
    timing: TriggerTiming
    events: list[TriggerEvent] = field(default_factory=list)
    is_disabled: bool = False
    is_instead_of: bool = False
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get fully qualified trigger name."""
        return f"{self.schema}.{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "full_name": self.full_name,
            "table_name": self.table_name,
            "table_schema": self.table_schema,
            "definition": self.definition,
            "timing": self.timing.value,
            "events": [e.value for e in self.events],
            "is_disabled": self.is_disabled,
            "is_instead_of": self.is_instead_of,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "description": self.description,
        }


@dataclass
class DatabaseSchema:
    """Complete database schema representation."""

    database_name: str
    server_name: Optional[str] = None
    server_version: Optional[str] = None
    collation: Optional[str] = None
    tables: list[TableInfo] = field(default_factory=list)
    views: list[ViewInfo] = field(default_factory=list)
    procedures: list[ProcedureInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    triggers: list[TriggerInfo] = field(default_factory=list)
    schemas: list[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.utcnow)

    def get_table(self, name: str, schema: str = "dbo") -> Optional[TableInfo]:
        """Get table by name and schema."""
        for table in self.tables:
            if table.name.lower() == name.lower() and table.schema.lower() == schema.lower():
                return table
        return None

    def get_view(self, name: str, schema: str = "dbo") -> Optional[ViewInfo]:
        """Get view by name and schema."""
        for view in self.views:
            if view.name.lower() == name.lower() and view.schema.lower() == schema.lower():
                return view
        return None

    def get_procedure(self, name: str, schema: str = "dbo") -> Optional[ProcedureInfo]:
        """Get procedure by name and schema."""
        for proc in self.procedures:
            if proc.name.lower() == name.lower() and proc.schema.lower() == schema.lower():
                return proc
        return None

    @property
    def table_count(self) -> int:
        """Get total table count."""
        return len(self.tables)

    @property
    def view_count(self) -> int:
        """Get total view count."""
        return len(self.views)

    @property
    def procedure_count(self) -> int:
        """Get total procedure count."""
        return len(self.procedures)

    @property
    def total_columns(self) -> int:
        """Get total column count across all tables."""
        return sum(len(t.columns) for t in self.tables)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "database_name": self.database_name,
            "server_name": self.server_name,
            "server_version": self.server_version,
            "collation": self.collation,
            "tables": [t.to_dict() for t in self.tables],
            "views": [v.to_dict() for v in self.views],
            "procedures": [p.to_dict() for p in self.procedures],
            "functions": [f.to_dict() for f in self.functions],
            "triggers": [t.to_dict() for t in self.triggers],
            "schemas": self.schemas,
            "extracted_at": self.extracted_at.isoformat(),
            "summary": {
                "table_count": self.table_count,
                "view_count": self.view_count,
                "procedure_count": self.procedure_count,
                "total_columns": self.total_columns,
            },
        }


@dataclass
class SchemaSnapshot:
    """A point-in-time snapshot of a database schema."""

    id: str
    connection_id: str
    tenant_id: str
    schema: DatabaseSchema
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    label: Optional[str] = None
    is_baseline: bool = False

    # Hash for quick comparison
    content_hash: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "tenant_id": self.tenant_id,
            "schema": self.schema.to_dict(),
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "label": self.label,
            "is_baseline": self.is_baseline,
            "content_hash": self.content_hash,
        }


@dataclass
class DiffItem:
    """A single difference between two schemas."""

    object_type: str  # table, column, index, procedure, etc.
    object_name: str
    change_type: str  # added, removed, modified
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    details: dict[str, Any] = field(default_factory=dict)
    breaking_change: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "object_type": self.object_type,
            "object_name": self.object_name,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "details": self.details,
            "breaking_change": self.breaking_change,
        }


@dataclass
class SchemaDiff:
    """Differences between two schema snapshots."""

    source_snapshot_id: str
    target_snapshot_id: str
    differences: list[DiffItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Summary stats
    tables_added: int = 0
    tables_removed: int = 0
    tables_modified: int = 0
    columns_added: int = 0
    columns_removed: int = 0
    columns_modified: int = 0
    procedures_added: int = 0
    procedures_removed: int = 0
    procedures_modified: int = 0

    @property
    def has_breaking_changes(self) -> bool:
        """Check if any differences are breaking changes."""
        return any(d.breaking_change for d in self.differences)

    @property
    def total_changes(self) -> int:
        """Get total number of changes."""
        return len(self.differences)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_snapshot_id": self.source_snapshot_id,
            "target_snapshot_id": self.target_snapshot_id,
            "differences": [d.to_dict() for d in self.differences],
            "created_at": self.created_at.isoformat(),
            "summary": {
                "tables_added": self.tables_added,
                "tables_removed": self.tables_removed,
                "tables_modified": self.tables_modified,
                "columns_added": self.columns_added,
                "columns_removed": self.columns_removed,
                "columns_modified": self.columns_modified,
                "procedures_added": self.procedures_added,
                "procedures_removed": self.procedures_removed,
                "procedures_modified": self.procedures_modified,
                "total_changes": self.total_changes,
                "has_breaking_changes": self.has_breaking_changes,
            },
        }
