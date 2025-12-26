"""SQL2.AI Schema Engine - Database metadata extraction and analysis."""

from schema_engine.models import (
    DatabaseSchema,
    TableInfo,
    ColumnInfo,
    IndexInfo,
    ForeignKeyInfo,
    ViewInfo,
    ProcedureInfo,
    FunctionInfo,
    TriggerInfo,
    SchemaSnapshot,
    SchemaDiff,
)
from schema_engine.extractors import (
    SchemaExtractor,
    SQLServerExtractor,
    PostgreSQLExtractor,
)
from schema_engine.analyzer import SchemaAnalyzer
from schema_engine.differ import SchemaDiffer

__all__ = [
    # Models
    "DatabaseSchema",
    "TableInfo",
    "ColumnInfo",
    "IndexInfo",
    "ForeignKeyInfo",
    "ViewInfo",
    "ProcedureInfo",
    "FunctionInfo",
    "TriggerInfo",
    "SchemaSnapshot",
    "SchemaDiff",
    # Extractors
    "SchemaExtractor",
    "SQLServerExtractor",
    "PostgreSQLExtractor",
    # Analysis
    "SchemaAnalyzer",
    "SchemaDiffer",
]
