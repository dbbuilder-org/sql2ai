"""Data models for SQL Writer."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ObjectType(str, Enum):
    """Types of database objects that can be generated."""
    TABLE = "table"
    INDEX = "index"
    VIEW = "view"
    STORED_PROCEDURE = "stored_procedure"
    FUNCTION = "function"
    TRIGGER = "trigger"
    CONSTRAINT = "constraint"


class FunctionType(str, Enum):
    """Types of SQL functions."""
    SCALAR = "scalar"
    TABLE_VALUED = "table_valued"
    INLINE_TABLE = "inline_table"


class TriggerType(str, Enum):
    """Types of SQL triggers."""
    AFTER_INSERT = "after_insert"
    AFTER_UPDATE = "after_update"
    AFTER_DELETE = "after_delete"
    INSTEAD_OF_INSERT = "instead_of_insert"
    INSTEAD_OF_UPDATE = "instead_of_update"
    INSTEAD_OF_DELETE = "instead_of_delete"


class TransactionIsolation(str, Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
    SNAPSHOT = "SNAPSHOT"


class ErrorHandlingStyle(str, Enum):
    """Error handling approaches."""
    TRY_CATCH = "try_catch"
    RETURN_CODE = "return_code"
    RAISERROR = "raiserror"
    THROW = "throw"


@dataclass
class ColumnDefinition:
    """Definition of a table column."""
    name: str
    data_type: str
    nullable: bool = True
    default_value: Optional[str] = None
    is_primary_key: bool = False
    is_identity: bool = False
    identity_seed: int = 1
    identity_increment: int = 1
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    collation: Optional[str] = None
    computed_expression: Optional[str] = None
    is_persisted: bool = False
    description: Optional[str] = None


@dataclass
class IndexDefinition:
    """Definition of an index."""
    name: str
    table_name: str
    columns: list[str]
    is_unique: bool = False
    is_clustered: bool = False
    include_columns: list[str] = field(default_factory=list)
    filter_predicate: Optional[str] = None
    fill_factor: int = 100
    compression: Optional[str] = None


@dataclass
class ForeignKeyDefinition:
    """Definition of a foreign key."""
    name: str
    columns: list[str]
    referenced_table: str
    referenced_columns: list[str]
    on_delete: str = "NO ACTION"
    on_update: str = "NO ACTION"


@dataclass
class TableDefinition:
    """Complete table definition."""
    name: str
    schema_name: str = "dbo"
    columns: list[ColumnDefinition] = field(default_factory=list)
    primary_key_columns: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKeyDefinition] = field(default_factory=list)
    indexes: list[IndexDefinition] = field(default_factory=list)
    is_temporal: bool = False
    history_table_name: Optional[str] = None
    compression: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ParameterDefinition:
    """Definition of a stored procedure/function parameter."""
    name: str
    data_type: str
    direction: str = "IN"  # IN, OUT, INOUT
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass
class StoredProcedureDefinition:
    """Definition of a stored procedure."""
    name: str
    schema_name: str = "dbo"
    parameters: list[ParameterDefinition] = field(default_factory=list)
    body: str = ""
    description: Optional[str] = None
    uses_transaction: bool = True
    isolation_level: TransactionIsolation = TransactionIsolation.READ_COMMITTED
    error_handling: ErrorHandlingStyle = ErrorHandlingStyle.TRY_CATCH
    with_recompile: bool = False
    execute_as: Optional[str] = None
    audit_table: Optional[str] = None


@dataclass
class ViewDefinition:
    """Definition of a view."""
    name: str
    schema_name: str = "dbo"
    select_statement: str = ""
    with_check_option: bool = False
    is_schema_bound: bool = False
    description: Optional[str] = None


@dataclass
class FunctionDefinition:
    """Definition of a function."""
    name: str
    schema_name: str = "dbo"
    function_type: FunctionType = FunctionType.SCALAR
    parameters: list[ParameterDefinition] = field(default_factory=list)
    return_type: Optional[str] = None  # For scalar functions
    return_table: Optional[TableDefinition] = None  # For table-valued
    body: str = ""
    is_deterministic: bool = False
    is_schema_bound: bool = False
    description: Optional[str] = None


@dataclass
class TriggerDefinition:
    """Definition of a trigger."""
    name: str
    table_name: str
    schema_name: str = "dbo"
    trigger_type: TriggerType = TriggerType.AFTER_INSERT
    body: str = ""
    is_disabled: bool = False
    not_for_replication: bool = False
    description: Optional[str] = None


@dataclass
class GenerationRequest:
    """Request for AI-powered code generation."""
    prompt: str
    object_type: ObjectType
    context_tables: list[str] = field(default_factory=list)
    context_schema: Optional[str] = None
    security_requirements: list[str] = field(default_factory=list)
    performance_hints: list[str] = field(default_factory=list)
    include_error_handling: bool = True
    include_audit_logging: bool = False
    include_comments: bool = True


@dataclass
class GenerationResult:
    """Result of code generation."""
    object_type: ObjectType
    object_name: str
    sql_script: str
    rollback_script: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    security_notes: list[str] = field(default_factory=list)
    performance_notes: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class CRUDGenerationRequest:
    """Request to generate CRUD procedures for a table."""
    table_name: str
    schema_name: str = "dbo"
    include_create: bool = True
    include_read: bool = True
    include_update: bool = True
    include_delete: bool = True
    include_list: bool = True
    include_search: bool = False
    soft_delete: bool = False
    soft_delete_column: str = "IsDeleted"
    audit_table: Optional[str] = None
    include_concurrency: bool = False
    concurrency_column: str = "RowVersion"


@dataclass
class CRUDGenerationResult:
    """Result of CRUD generation."""
    table_name: str
    procedures: list[GenerationResult]
    combined_script: str
    rollback_script: str
