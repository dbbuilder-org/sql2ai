"""Schema analysis for AI documentation and optimization suggestions."""

import re
from dataclasses import dataclass
from typing import Optional

import structlog

from models import (
    ColumnInfo,
    DatabaseSchema,
    TableInfo,
    ProcedureInfo,
)

logger = structlog.get_logger()


@dataclass
class AnalysisResult:
    """Result of schema analysis."""

    # AI-generated documentation
    table_purposes: dict[str, str]
    column_purposes: dict[str, dict[str, str]]
    entity_types: dict[str, str]

    # Quality issues
    missing_primary_keys: list[str]
    missing_indexes: list[tuple[str, str]]  # (table, suggested_column)
    naming_violations: list[tuple[str, str, str]]  # (object_type, name, issue)

    # PII detection
    pii_columns: list[tuple[str, str, str]]  # (table, column, pii_type)

    # Optimization suggestions
    index_suggestions: list[dict]
    normalization_issues: list[dict]

    # Complexity metrics
    procedure_complexity: dict[str, int]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_purposes": self.table_purposes,
            "column_purposes": self.column_purposes,
            "entity_types": self.entity_types,
            "quality_issues": {
                "missing_primary_keys": self.missing_primary_keys,
                "missing_indexes": [
                    {"table": t, "column": c} for t, c in self.missing_indexes
                ],
                "naming_violations": [
                    {"type": t, "name": n, "issue": i}
                    for t, n, i in self.naming_violations
                ],
            },
            "pii_columns": [
                {"table": t, "column": c, "type": p} for t, c, p in self.pii_columns
            ],
            "index_suggestions": self.index_suggestions,
            "normalization_issues": self.normalization_issues,
            "procedure_complexity": self.procedure_complexity,
        }


class SchemaAnalyzer:
    """Analyzes database schemas for documentation and optimization."""

    # Common PII column patterns
    PII_PATTERNS = {
        "email": [r"email", r"e_mail", r"emailaddress"],
        "phone": [r"phone", r"mobile", r"cell", r"fax", r"telephone"],
        "ssn": [r"ssn", r"social.*security", r"sin"],
        "name": [r"first.*name", r"last.*name", r"full.*name", r"sur.*name"],
        "address": [r"address", r"street", r"city", r"zip", r"postal", r"country"],
        "dob": [r"dob", r"birth.*date", r"date.*birth", r"birthday"],
        "credit_card": [r"credit.*card", r"card.*number", r"pan", r"ccn"],
        "ip_address": [r"ip.*address", r"ip_addr", r"client.*ip"],
        "password": [r"password", r"passwd", r"pwd", r"hash", r"secret"],
    }

    # Common naming conventions
    NAMING_CONVENTIONS = {
        "pascal_case": r"^[A-Z][a-zA-Z0-9]*$",
        "snake_case": r"^[a-z][a-z0-9_]*$",
        "camel_case": r"^[a-z][a-zA-Z0-9]*$",
    }

    def __init__(self, preferred_convention: str = "pascal_case"):
        """Initialize analyzer.

        Args:
            preferred_convention: Preferred naming convention
        """
        self.preferred_convention = preferred_convention

    def analyze(self, schema: DatabaseSchema) -> AnalysisResult:
        """Analyze a database schema.

        Args:
            schema: DatabaseSchema to analyze

        Returns:
            AnalysisResult with findings
        """
        logger.info("starting_schema_analysis", database=schema.database_name)

        result = AnalysisResult(
            table_purposes={},
            column_purposes={},
            entity_types={},
            missing_primary_keys=[],
            missing_indexes=[],
            naming_violations=[],
            pii_columns=[],
            index_suggestions=[],
            normalization_issues=[],
            procedure_complexity={},
        )

        # Analyze tables
        for table in schema.tables:
            self._analyze_table(table, result)

        # Analyze procedures
        for proc in schema.procedures:
            self._analyze_procedure(proc, result)

        # Find relationship patterns
        self._analyze_relationships(schema, result)

        logger.info(
            "schema_analysis_complete",
            tables_analyzed=len(schema.tables),
            pii_columns_found=len(result.pii_columns),
            issues_found=len(result.missing_primary_keys) + len(result.naming_violations),
        )

        return result

    def _analyze_table(self, table: TableInfo, result: AnalysisResult) -> None:
        """Analyze a single table."""
        # Infer table purpose
        result.table_purposes[table.full_name] = self._infer_table_purpose(table)
        result.entity_types[table.full_name] = self._infer_entity_type(table)

        # Check for primary key
        if not table.primary_key_columns:
            result.missing_primary_keys.append(table.full_name)

        # Check naming conventions
        if not self._matches_convention(table.name):
            result.naming_violations.append(
                ("table", table.full_name, f"Does not match {self.preferred_convention}")
            )

        # Analyze columns
        result.column_purposes[table.full_name] = {}
        for column in table.columns:
            self._analyze_column(table, column, result)

        # Check for missing indexes on foreign key columns
        fk_columns = set()
        for fk in table.foreign_keys:
            fk_columns.update(fk.columns)

        indexed_columns = set()
        for idx in table.indexes:
            if idx.columns:
                indexed_columns.add(idx.columns[0])

        for fk_col in fk_columns:
            if fk_col not in indexed_columns:
                result.missing_indexes.append((table.full_name, fk_col))
                result.index_suggestions.append({
                    "table": table.full_name,
                    "column": fk_col,
                    "reason": "Foreign key column without index",
                    "suggested_index": f"IX_{table.name}_{fk_col}",
                })

    def _analyze_column(
        self, table: TableInfo, column: ColumnInfo, result: AnalysisResult
    ) -> None:
        """Analyze a single column."""
        # Infer column purpose
        result.column_purposes[table.full_name][column.name] = self._infer_column_purpose(
            column, table
        )

        # Check naming
        if not self._matches_convention(column.name):
            result.naming_violations.append(
                ("column", f"{table.full_name}.{column.name}", f"Does not match {self.preferred_convention}")
            )

        # Detect PII
        pii_type = self._detect_pii(column)
        if pii_type:
            result.pii_columns.append((table.full_name, column.name, pii_type))
            column.is_pii = True
            column.pii_type = pii_type

    def _analyze_procedure(self, proc: ProcedureInfo, result: AnalysisResult) -> None:
        """Analyze a stored procedure."""
        complexity = self._calculate_complexity(proc)
        result.procedure_complexity[proc.full_name] = complexity

        # Check naming
        if not self._matches_convention(proc.name):
            result.naming_violations.append(
                ("procedure", proc.full_name, f"Does not match {self.preferred_convention}")
            )

    def _analyze_relationships(
        self, schema: DatabaseSchema, result: AnalysisResult
    ) -> None:
        """Analyze relationships between tables."""
        # Find potential missing foreign keys
        for table in schema.tables:
            for column in table.columns:
                # Check for columns that look like foreign keys but aren't defined
                if self._looks_like_foreign_key(column):
                    has_fk = any(
                        column.name in fk.columns for fk in table.foreign_keys
                    )
                    if not has_fk:
                        result.normalization_issues.append({
                            "table": table.full_name,
                            "column": column.name,
                            "issue": "Column appears to be a foreign key but has no constraint",
                            "suggestion": "Consider adding a foreign key constraint",
                        })

    def _infer_table_purpose(self, table: TableInfo) -> str:
        """Infer the purpose of a table from its name and structure."""
        name_lower = table.name.lower()

        # Common patterns
        if name_lower.endswith("log") or name_lower.endswith("logs"):
            return "Audit/logging table for tracking changes or events"
        if name_lower.endswith("history"):
            return "Historical records table for tracking changes over time"
        if name_lower.startswith("dim_"):
            return "Dimension table for data warehouse"
        if name_lower.startswith("fact_"):
            return "Fact table for data warehouse"
        if "user" in name_lower:
            return "User account information"
        if "customer" in name_lower:
            return "Customer records"
        if "order" in name_lower:
            return "Order/transaction records"
        if "product" in name_lower:
            return "Product catalog"
        if "invoice" in name_lower:
            return "Invoice/billing records"
        if "setting" in name_lower or "config" in name_lower:
            return "Configuration/settings storage"
        if "lookup" in name_lower or "type" in name_lower:
            return "Lookup/reference data table"

        # Check column patterns
        has_timestamps = any(
            c.name.lower() in ("createdat", "created_at", "updatedat", "updated_at")
            for c in table.columns
        )
        has_status = any("status" in c.name.lower() for c in table.columns)

        if has_timestamps and has_status:
            return "Entity table with lifecycle tracking"

        return "Data storage table"

    def _infer_entity_type(self, table: TableInfo) -> str:
        """Infer the entity type from table structure."""
        name_lower = table.name.lower()

        # Check for junction/bridge tables
        fk_count = len(table.foreign_keys)
        if fk_count >= 2 and len(table.columns) <= fk_count + 3:
            return "junction_table"

        # Check for lookup tables
        if len(table.columns) <= 3 and any(
            c.name.lower() in ("name", "code", "value", "description")
            for c in table.columns
        ):
            return "lookup_table"

        # Check for audit tables
        if name_lower.endswith("log") or name_lower.endswith("audit"):
            return "audit_table"

        return "entity_table"

    def _infer_column_purpose(self, column: ColumnInfo, table: TableInfo) -> str:
        """Infer the purpose of a column."""
        name_lower = column.name.lower()

        # Identity columns
        if column.is_identity or column.is_primary_key:
            return "Primary identifier for the record"

        # Foreign keys
        if name_lower.endswith("id") and not column.is_primary_key:
            return f"Reference to related entity"

        # Common patterns
        patterns = {
            "createdat": "Record creation timestamp",
            "created_at": "Record creation timestamp",
            "createdby": "User who created the record",
            "created_by": "User who created the record",
            "updatedat": "Last modification timestamp",
            "updated_at": "Last modification timestamp",
            "updatedby": "User who last modified the record",
            "updated_by": "User who last modified the record",
            "deletedat": "Soft deletion timestamp",
            "deleted_at": "Soft deletion timestamp",
            "isactive": "Whether the record is active",
            "is_active": "Whether the record is active",
            "isdeleted": "Whether the record is soft-deleted",
            "is_deleted": "Whether the record is soft-deleted",
            "status": "Current status of the record",
            "name": "Display name",
            "description": "Detailed description",
            "email": "Email address",
            "phone": "Phone number",
            "address": "Physical address",
            "amount": "Monetary amount",
            "quantity": "Count or quantity",
            "price": "Unit price",
            "total": "Calculated total",
            "notes": "Additional notes or comments",
            "comments": "User comments",
        }

        for pattern, purpose in patterns.items():
            if pattern in name_lower:
                return purpose

        # Type-based inference
        if column.data_type_normalized.value in ("datetime", "datetime2", "timestamp"):
            return "Timestamp field"
        if column.data_type_normalized.value in ("decimal", "money", "numeric"):
            return "Numeric/monetary value"
        if column.data_type_normalized.value == "bit":
            return "Boolean flag"

        return "Data field"

    def _detect_pii(self, column: ColumnInfo) -> Optional[str]:
        """Detect if a column likely contains PII."""
        name_lower = column.name.lower()

        for pii_type, patterns in self.PII_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower):
                    return pii_type

        return None

    def _matches_convention(self, name: str) -> bool:
        """Check if a name matches the preferred convention."""
        pattern = self.NAMING_CONVENTIONS.get(self.preferred_convention)
        if not pattern:
            return True
        return bool(re.match(pattern, name))

    def _looks_like_foreign_key(self, column: ColumnInfo) -> bool:
        """Check if a column looks like a foreign key."""
        name_lower = column.name.lower()

        # Common FK patterns
        if name_lower.endswith("id") and not column.is_primary_key:
            return True
        if name_lower.endswith("_id"):
            return True
        if name_lower.startswith("fk_"):
            return True

        return False

    def _calculate_complexity(self, proc: ProcedureInfo) -> int:
        """Calculate procedure complexity score."""
        if not proc.definition:
            return 0

        score = 0
        definition_upper = proc.definition.upper()

        # Count control flow statements
        score += definition_upper.count("IF ") * 2
        score += definition_upper.count("WHILE ") * 3
        score += definition_upper.count("CURSOR ") * 5
        score += definition_upper.count("TRY") * 2
        score += definition_upper.count("CATCH") * 2
        score += definition_upper.count("CASE ") * 1

        # Count joins
        score += definition_upper.count(" JOIN ") * 1

        # Count subqueries
        score += definition_upper.count("SELECT ") - 1  # Minus the main select

        # Dynamic SQL is complex
        if "EXEC(" in definition_upper or "SP_EXECUTESQL" in definition_upper:
            score += 10

        # Parameter count
        score += len(proc.parameters)

        # Line count factor
        score += proc.estimated_lines // 20

        return score
