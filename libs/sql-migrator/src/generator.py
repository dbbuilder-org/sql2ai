"""Migration generator from schema diffs."""

import uuid
from datetime import datetime
from typing import Any, Optional

import structlog

from models import (
    Migration,
    MigrationStep,
    MigrationPlan,
    BreakingChange,
    BreakingChangeSeverity,
)

logger = structlog.get_logger()


class MigrationGenerator:
    """Generates migrations from schema differences."""

    def __init__(self, dialect: str = "sqlserver"):
        """Initialize generator.

        Args:
            dialect: SQL dialect (sqlserver, postgresql)
        """
        self.dialect = dialect

    def generate_from_diff(
        self,
        diff: Any,  # SchemaDiff from schema-engine
        name: str,
        version: str,
        description: Optional[str] = None,
    ) -> Migration:
        """Generate a migration from a schema diff.

        Args:
            diff: Schema diff object
            name: Migration name
            version: Version string (e.g., "1.0.0")
            description: Optional description

        Returns:
            Generated Migration
        """
        migration = Migration(
            id=str(uuid.uuid4()),
            name=name,
            version=version,
            description=description or f"Migration {name}",
            dialect=self.dialect,
        )

        step_order = 1

        # Process differences
        for difference in diff.differences:
            steps, breaking = self._process_difference(difference, step_order)
            migration.steps.extend(steps)
            migration.breaking_changes.extend(breaking)
            step_order += len(steps)

        logger.info(
            "migration_generated",
            name=name,
            steps=len(migration.steps),
            breaking_changes=len(migration.breaking_changes),
        )

        return migration

    def _process_difference(
        self,
        diff: Any,
        start_order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Process a single difference into migration steps."""
        steps = []
        breaking_changes = []
        order = start_order

        object_type = diff.object_type
        change_type = diff.change_type
        object_name = diff.object_name

        if object_type == "table":
            s, bc = self._generate_table_change(diff, order)
            steps.extend(s)
            breaking_changes.extend(bc)

        elif object_type == "column":
            s, bc = self._generate_column_change(diff, order)
            steps.extend(s)
            breaking_changes.extend(bc)

        elif object_type == "index":
            s, bc = self._generate_index_change(diff, order)
            steps.extend(s)
            breaking_changes.extend(bc)

        elif object_type == "constraint":
            s, bc = self._generate_constraint_change(diff, order)
            steps.extend(s)
            breaking_changes.extend(bc)

        elif object_type == "procedure":
            s, bc = self._generate_procedure_change(diff, order)
            steps.extend(s)
            breaking_changes.extend(bc)

        return steps, breaking_changes

    def _generate_table_change(
        self,
        diff: Any,
        order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for table changes."""
        steps = []
        breaking = []

        if diff.change_type == "added":
            # Create table
            forward = self._generate_create_table(diff)
            rollback = f"DROP TABLE {diff.object_name};"

            steps.append(MigrationStep(
                order=order,
                description=f"Create table {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        elif diff.change_type == "removed":
            # Drop table - breaking change
            forward = f"DROP TABLE {diff.object_name};"
            rollback = None  # Cannot easily rollback table drop

            steps.append(MigrationStep(
                order=order,
                description=f"Drop table {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
                requires_lock=True,
            ))

            breaking.append(BreakingChange(
                change_type="table_removed",
                severity=BreakingChangeSeverity.CRITICAL,
                object_name=diff.object_name,
                description=f"Table {diff.object_name} will be dropped",
                data_loss_risk=True,
                remediation="Backup table data before migration",
            ))

        return steps, breaking

    def _generate_column_change(
        self,
        diff: Any,
        order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for column changes."""
        steps = []
        breaking = []

        table_name = diff.parent_name if hasattr(diff, "parent_name") else diff.object_name.split(".")[0]
        column_name = diff.object_name.split(".")[-1] if "." in diff.object_name else diff.object_name

        if diff.change_type == "added":
            # Add column
            col_def = self._get_column_definition(diff.new_value)
            forward = f"ALTER TABLE {table_name} ADD {column_name} {col_def};"
            rollback = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"

            steps.append(MigrationStep(
                order=order,
                description=f"Add column {column_name} to {table_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        elif diff.change_type == "removed":
            # Drop column - breaking change
            forward = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
            rollback = None

            steps.append(MigrationStep(
                order=order,
                description=f"Drop column {column_name} from {table_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

            breaking.append(BreakingChange(
                change_type="column_removed",
                severity=BreakingChangeSeverity.HIGH,
                object_name=diff.object_name,
                description=f"Column {column_name} will be dropped from {table_name}",
                data_loss_risk=True,
                remediation="Update dependent code and backup data",
            ))

        elif diff.change_type == "modified":
            # Alter column
            s, bc = self._generate_column_modification(diff, order, table_name, column_name)
            steps.extend(s)
            breaking.extend(bc)

        return steps, breaking

    def _generate_column_modification(
        self,
        diff: Any,
        order: int,
        table_name: str,
        column_name: str,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for column modifications."""
        steps = []
        breaking = []

        details = diff.details if hasattr(diff, "details") else {}

        # Type change
        if "data_type" in details:
            new_type = details["data_type"].get("new", "")
            old_type = details["data_type"].get("old", "")

            if self.dialect == "sqlserver":
                forward = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} {new_type};"
            else:
                forward = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {new_type};"

            rollback = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} {old_type};"

            steps.append(MigrationStep(
                order=order,
                description=f"Change {column_name} type from {old_type} to {new_type}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

            # Check if type change could cause data loss
            if self._is_narrowing_conversion(old_type, new_type):
                breaking.append(BreakingChange(
                    change_type="type_changed",
                    severity=BreakingChangeSeverity.HIGH,
                    object_name=diff.object_name,
                    description=f"Type change from {old_type} to {new_type} may cause data truncation",
                    data_loss_risk=True,
                    remediation="Verify data fits within new type constraints",
                ))

        # Nullability change
        if "is_nullable" in details:
            new_nullable = details["is_nullable"].get("new", True)

            if not new_nullable:
                # Making NOT NULL - breaking change
                if self.dialect == "sqlserver":
                    forward = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} NOT NULL;"
                else:
                    forward = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL;"

                rollback = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} NULL;"

                steps.append(MigrationStep(
                    order=order + len(steps),
                    description=f"Make {column_name} NOT NULL",
                    forward_sql=forward,
                    rollback_sql=rollback,
                ))

                breaking.append(BreakingChange(
                    change_type="constraint_added",
                    severity=BreakingChangeSeverity.MEDIUM,
                    object_name=diff.object_name,
                    description=f"Column {column_name} will no longer accept NULL values",
                    data_loss_risk=False,
                    remediation="Ensure no NULL values exist before migration",
                ))

        return steps, breaking

    def _generate_index_change(
        self,
        diff: Any,
        order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for index changes."""
        steps = []
        breaking = []

        if diff.change_type == "added":
            index_def = self._get_index_definition(diff.new_value)
            forward = index_def
            rollback = f"DROP INDEX {diff.object_name};"

            steps.append(MigrationStep(
                order=order,
                description=f"Create index {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        elif diff.change_type == "removed":
            forward = f"DROP INDEX {diff.object_name};"
            rollback = None

            steps.append(MigrationStep(
                order=order,
                description=f"Drop index {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        return steps, breaking

    def _generate_constraint_change(
        self,
        diff: Any,
        order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for constraint changes."""
        steps = []
        breaking = []

        table_name = diff.parent_name if hasattr(diff, "parent_name") else ""

        if diff.change_type == "added":
            constraint_def = self._get_constraint_definition(diff.new_value)
            forward = f"ALTER TABLE {table_name} ADD CONSTRAINT {diff.object_name} {constraint_def};"
            rollback = f"ALTER TABLE {table_name} DROP CONSTRAINT {diff.object_name};"

            steps.append(MigrationStep(
                order=order,
                description=f"Add constraint {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

            breaking.append(BreakingChange(
                change_type="constraint_added",
                severity=BreakingChangeSeverity.MEDIUM,
                object_name=diff.object_name,
                description=f"New constraint {diff.object_name} will be enforced",
                data_loss_risk=False,
                remediation="Ensure existing data satisfies constraint",
            ))

        elif diff.change_type == "removed":
            forward = f"ALTER TABLE {table_name} DROP CONSTRAINT {diff.object_name};"
            rollback = None

            steps.append(MigrationStep(
                order=order,
                description=f"Drop constraint {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        return steps, breaking

    def _generate_procedure_change(
        self,
        diff: Any,
        order: int,
    ) -> tuple[list[MigrationStep], list[BreakingChange]]:
        """Generate steps for stored procedure changes."""
        steps = []
        breaking = []

        if diff.change_type == "added":
            definition = diff.new_value.get("definition", "") if diff.new_value else ""
            forward = definition
            rollback = f"DROP PROCEDURE {diff.object_name};"

            steps.append(MigrationStep(
                order=order,
                description=f"Create procedure {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        elif diff.change_type == "modified":
            definition = diff.new_value.get("definition", "") if diff.new_value else ""
            # Replace CREATE with ALTER
            forward = definition.replace("CREATE PROCEDURE", "ALTER PROCEDURE", 1)
            rollback = diff.old_value.get("definition", "") if diff.old_value else None

            steps.append(MigrationStep(
                order=order,
                description=f"Modify procedure {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

        elif diff.change_type == "removed":
            forward = f"DROP PROCEDURE {diff.object_name};"
            rollback = diff.old_value.get("definition", "") if diff.old_value else None

            steps.append(MigrationStep(
                order=order,
                description=f"Drop procedure {diff.object_name}",
                forward_sql=forward,
                rollback_sql=rollback,
            ))

            breaking.append(BreakingChange(
                change_type="procedure_removed",
                severity=BreakingChangeSeverity.HIGH,
                object_name=diff.object_name,
                description=f"Stored procedure {diff.object_name} will be dropped",
                data_loss_risk=False,
                remediation="Update application code that calls this procedure",
            ))

        return steps, breaking

    def _generate_create_table(self, diff: Any) -> str:
        """Generate CREATE TABLE statement."""
        table_name = diff.object_name
        columns = diff.new_value.get("columns", []) if diff.new_value else []

        col_defs = []
        for col in columns:
            col_def = self._get_column_definition(col)
            col_defs.append(f"    {col['name']} {col_def}")

        return f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);"

    def _get_column_definition(self, column: dict) -> str:
        """Get column definition for DDL."""
        parts = [column.get("data_type", "varchar(255)")]

        if not column.get("is_nullable", True):
            parts.append("NOT NULL")

        if column.get("default_value"):
            parts.append(f"DEFAULT {column['default_value']}")

        if column.get("is_identity"):
            if self.dialect == "sqlserver":
                parts.append("IDENTITY(1,1)")
            else:
                parts.append("GENERATED ALWAYS AS IDENTITY")

        return " ".join(parts)

    def _get_index_definition(self, index: dict) -> str:
        """Get CREATE INDEX statement."""
        name = index.get("name", "IX_unnamed")
        table = index.get("table", "")
        columns = index.get("columns", [])
        unique = "UNIQUE " if index.get("is_unique") else ""

        return f"CREATE {unique}INDEX {name} ON {table} ({', '.join(columns)});"

    def _get_constraint_definition(self, constraint: dict) -> str:
        """Get constraint definition."""
        ctype = constraint.get("type", "").upper()

        if ctype == "PRIMARY KEY":
            columns = constraint.get("columns", [])
            return f"PRIMARY KEY ({', '.join(columns)})"
        elif ctype == "FOREIGN KEY":
            columns = constraint.get("columns", [])
            ref_table = constraint.get("referenced_table", "")
            ref_columns = constraint.get("referenced_columns", [])
            return f"FOREIGN KEY ({', '.join(columns)}) REFERENCES {ref_table} ({', '.join(ref_columns)})"
        elif ctype == "UNIQUE":
            columns = constraint.get("columns", [])
            return f"UNIQUE ({', '.join(columns)})"
        elif ctype == "CHECK":
            expression = constraint.get("expression", "1=1")
            return f"CHECK ({expression})"

        return ""

    def _is_narrowing_conversion(self, old_type: str, new_type: str) -> bool:
        """Check if type conversion could cause data loss."""
        # Simplified check - expand as needed
        narrowing_patterns = [
            ("varchar", "char"),
            ("nvarchar", "varchar"),
            ("bigint", "int"),
            ("int", "smallint"),
            ("smallint", "tinyint"),
            ("decimal", "int"),
            ("float", "int"),
        ]

        old_lower = old_type.lower()
        new_lower = new_type.lower()

        for old_pattern, new_pattern in narrowing_patterns:
            if old_pattern in old_lower and new_pattern in new_lower:
                return True

        return False

    def create_plan(
        self,
        migrations: list[Migration],
    ) -> MigrationPlan:
        """Create an execution plan for multiple migrations.

        Args:
            migrations: List of migrations to plan

        Returns:
            MigrationPlan with execution order
        """
        # Topological sort based on dependencies
        execution_order = self._topological_sort(migrations)

        total_breaking = sum(len(m.breaking_changes) for m in migrations)
        requires_downtime = any(m.requires_downtime for m in migrations)
        estimated_duration = sum(
            sum(s.estimated_duration_ms for s in m.steps)
            for m in migrations
        )

        return MigrationPlan(
            migrations=migrations,
            execution_order=execution_order,
            total_breaking_changes=total_breaking,
            requires_downtime=requires_downtime,
            estimated_duration_ms=estimated_duration,
        )

    def _topological_sort(self, migrations: list[Migration]) -> list[str]:
        """Sort migrations by dependencies."""
        # Build dependency graph
        graph: dict[str, list[str]] = {m.id: m.dependencies for m in migrations}
        in_degree: dict[str, int] = {m.id: 0 for m in migrations}

        for deps in graph.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Kahn's algorithm
        queue = [m_id for m_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for m_id, deps in graph.items():
                if current in deps:
                    in_degree[m_id] -= 1
                    if in_degree[m_id] == 0:
                        queue.append(m_id)

        return result
