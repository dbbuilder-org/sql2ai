"""Schema comparison and diff generation."""

from typing import Any, Optional

import structlog

from models import (
    ColumnInfo,
    DatabaseSchema,
    DiffItem,
    ForeignKeyInfo,
    IndexInfo,
    ProcedureInfo,
    SchemaDiff,
    SchemaSnapshot,
    TableInfo,
    ViewInfo,
)

logger = structlog.get_logger()


class SchemaDiffer:
    """Compare two database schemas and generate differences."""

    def compare_snapshots(
        self, source: SchemaSnapshot, target: SchemaSnapshot
    ) -> SchemaDiff:
        """Compare two schema snapshots.

        Args:
            source: Source (before) snapshot
            target: Target (after) snapshot

        Returns:
            SchemaDiff with all differences
        """
        return self.compare(
            source.schema,
            target.schema,
            source.id,
            target.id,
        )

    def compare(
        self,
        source: DatabaseSchema,
        target: DatabaseSchema,
        source_id: str = "source",
        target_id: str = "target",
    ) -> SchemaDiff:
        """Compare two database schemas.

        Args:
            source: Source (before) schema
            target: Target (after) schema
            source_id: ID for source snapshot
            target_id: ID for target snapshot

        Returns:
            SchemaDiff with all differences
        """
        logger.info(
            "starting_schema_comparison",
            source=source.database_name,
            target=target.database_name,
        )

        diff = SchemaDiff(
            source_snapshot_id=source_id,
            target_snapshot_id=target_id,
        )

        # Compare tables
        self._compare_tables(source, target, diff)

        # Compare views
        self._compare_views(source, target, diff)

        # Compare procedures
        self._compare_procedures(source, target, diff)

        # Compare functions
        self._compare_functions(source, target, diff)

        logger.info(
            "schema_comparison_complete",
            total_changes=diff.total_changes,
            has_breaking=diff.has_breaking_changes,
        )

        return diff

    def _compare_tables(
        self, source: DatabaseSchema, target: DatabaseSchema, diff: SchemaDiff
    ) -> None:
        """Compare tables between schemas."""
        source_tables = {t.full_name: t for t in source.tables}
        target_tables = {t.full_name: t for t in target.tables}

        source_names = set(source_tables.keys())
        target_names = set(target_tables.keys())

        # Added tables
        for name in target_names - source_names:
            table = target_tables[name]
            diff.differences.append(
                DiffItem(
                    object_type="table",
                    object_name=name,
                    change_type="added",
                    new_value=self._table_summary(table),
                )
            )
            diff.tables_added += 1

        # Removed tables
        for name in source_names - target_names:
            table = source_tables[name]
            diff.differences.append(
                DiffItem(
                    object_type="table",
                    object_name=name,
                    change_type="removed",
                    old_value=self._table_summary(table),
                    breaking_change=True,  # Removing tables is breaking
                )
            )
            diff.tables_removed += 1

        # Modified tables
        for name in source_names & target_names:
            source_table = source_tables[name]
            target_table = target_tables[name]

            table_changes = self._compare_table_details(source_table, target_table)
            if table_changes:
                diff.differences.extend(table_changes)
                diff.tables_modified += 1

                # Count column changes
                for change in table_changes:
                    if change.object_type == "column":
                        if change.change_type == "added":
                            diff.columns_added += 1
                        elif change.change_type == "removed":
                            diff.columns_removed += 1
                        elif change.change_type == "modified":
                            diff.columns_modified += 1

    def _compare_table_details(
        self, source: TableInfo, target: TableInfo
    ) -> list[DiffItem]:
        """Compare details of two tables."""
        changes = []

        # Compare columns
        changes.extend(self._compare_columns(source, target))

        # Compare indexes
        changes.extend(self._compare_indexes(source, target))

        # Compare foreign keys
        changes.extend(self._compare_foreign_keys(source, target))

        return changes

    def _compare_columns(
        self, source: TableInfo, target: TableInfo
    ) -> list[DiffItem]:
        """Compare columns between tables."""
        changes = []
        table_name = source.full_name

        source_cols = {c.name.lower(): c for c in source.columns}
        target_cols = {c.name.lower(): c for c in target.columns}

        source_names = set(source_cols.keys())
        target_names = set(target_cols.keys())

        # Added columns
        for name in target_names - source_names:
            col = target_cols[name]
            changes.append(
                DiffItem(
                    object_type="column",
                    object_name=f"{table_name}.{col.name}",
                    change_type="added",
                    new_value=self._column_summary(col),
                )
            )

        # Removed columns
        for name in source_names - target_names:
            col = source_cols[name]
            changes.append(
                DiffItem(
                    object_type="column",
                    object_name=f"{table_name}.{col.name}",
                    change_type="removed",
                    old_value=self._column_summary(col),
                    breaking_change=True,  # Removing columns is breaking
                )
            )

        # Modified columns
        for name in source_names & target_names:
            source_col = source_cols[name]
            target_col = target_cols[name]

            col_changes = self._compare_column_details(
                source_col, target_col, table_name
            )
            if col_changes:
                changes.append(col_changes)

        return changes

    def _compare_column_details(
        self, source: ColumnInfo, target: ColumnInfo, table_name: str
    ) -> Optional[DiffItem]:
        """Compare details of two columns."""
        details = {}
        breaking = False

        # Data type changes
        if source.data_type != target.data_type:
            details["data_type"] = {
                "from": source.data_type,
                "to": target.data_type,
            }
            # Type changes can be breaking
            breaking = True

        # Max length changes
        if source.max_length != target.max_length:
            details["max_length"] = {
                "from": source.max_length,
                "to": target.max_length,
            }
            # Shrinking is breaking
            if source.max_length and target.max_length:
                if target.max_length < source.max_length:
                    breaking = True

        # Nullability changes
        if source.is_nullable != target.is_nullable:
            details["is_nullable"] = {
                "from": source.is_nullable,
                "to": target.is_nullable,
            }
            # Making non-nullable is breaking
            if source.is_nullable and not target.is_nullable:
                breaking = True

        # Default value changes
        if source.default_value != target.default_value:
            details["default_value"] = {
                "from": source.default_value,
                "to": target.default_value,
            }

        if details:
            return DiffItem(
                object_type="column",
                object_name=f"{table_name}.{source.name}",
                change_type="modified",
                old_value=self._column_summary(source),
                new_value=self._column_summary(target),
                details=details,
                breaking_change=breaking,
            )

        return None

    def _compare_indexes(
        self, source: TableInfo, target: TableInfo
    ) -> list[DiffItem]:
        """Compare indexes between tables."""
        changes = []
        table_name = source.full_name

        source_idx = {i.name.lower(): i for i in source.indexes}
        target_idx = {i.name.lower(): i for i in target.indexes}

        source_names = set(source_idx.keys())
        target_names = set(target_idx.keys())

        # Added indexes
        for name in target_names - source_names:
            idx = target_idx[name]
            changes.append(
                DiffItem(
                    object_type="index",
                    object_name=f"{table_name}.{idx.name}",
                    change_type="added",
                    new_value=self._index_summary(idx),
                )
            )

        # Removed indexes
        for name in source_names - target_names:
            idx = source_idx[name]
            changes.append(
                DiffItem(
                    object_type="index",
                    object_name=f"{table_name}.{idx.name}",
                    change_type="removed",
                    old_value=self._index_summary(idx),
                )
            )

        # Modified indexes
        for name in source_names & target_names:
            source_i = source_idx[name]
            target_i = target_idx[name]

            if self._index_changed(source_i, target_i):
                changes.append(
                    DiffItem(
                        object_type="index",
                        object_name=f"{table_name}.{source_i.name}",
                        change_type="modified",
                        old_value=self._index_summary(source_i),
                        new_value=self._index_summary(target_i),
                    )
                )

        return changes

    def _compare_foreign_keys(
        self, source: TableInfo, target: TableInfo
    ) -> list[DiffItem]:
        """Compare foreign keys between tables."""
        changes = []
        table_name = source.full_name

        source_fks = {f.name.lower(): f for f in source.foreign_keys}
        target_fks = {f.name.lower(): f for f in target.foreign_keys}

        source_names = set(source_fks.keys())
        target_names = set(target_fks.keys())

        # Added foreign keys
        for name in target_names - source_names:
            fk = target_fks[name]
            changes.append(
                DiffItem(
                    object_type="foreign_key",
                    object_name=f"{table_name}.{fk.name}",
                    change_type="added",
                    new_value=self._fk_summary(fk),
                )
            )

        # Removed foreign keys
        for name in source_names - target_names:
            fk = source_fks[name]
            changes.append(
                DiffItem(
                    object_type="foreign_key",
                    object_name=f"{table_name}.{fk.name}",
                    change_type="removed",
                    old_value=self._fk_summary(fk),
                )
            )

        return changes

    def _compare_views(
        self, source: DatabaseSchema, target: DatabaseSchema, diff: SchemaDiff
    ) -> None:
        """Compare views between schemas."""
        source_views = {v.full_name: v for v in source.views}
        target_views = {v.full_name: v for v in target.views}

        source_names = set(source_views.keys())
        target_names = set(target_views.keys())

        # Added views
        for name in target_names - source_names:
            diff.differences.append(
                DiffItem(
                    object_type="view",
                    object_name=name,
                    change_type="added",
                )
            )

        # Removed views
        for name in source_names - target_names:
            diff.differences.append(
                DiffItem(
                    object_type="view",
                    object_name=name,
                    change_type="removed",
                    breaking_change=True,
                )
            )

        # Modified views
        for name in source_names & target_names:
            source_view = source_views[name]
            target_view = target_views[name]

            if source_view.definition != target_view.definition:
                diff.differences.append(
                    DiffItem(
                        object_type="view",
                        object_name=name,
                        change_type="modified",
                        details={"definition_changed": True},
                    )
                )

    def _compare_procedures(
        self, source: DatabaseSchema, target: DatabaseSchema, diff: SchemaDiff
    ) -> None:
        """Compare procedures between schemas."""
        source_procs = {p.full_name: p for p in source.procedures}
        target_procs = {p.full_name: p for p in target.procedures}

        source_names = set(source_procs.keys())
        target_names = set(target_procs.keys())

        # Added procedures
        for name in target_names - source_names:
            diff.differences.append(
                DiffItem(
                    object_type="procedure",
                    object_name=name,
                    change_type="added",
                )
            )
            diff.procedures_added += 1

        # Removed procedures
        for name in source_names - target_names:
            diff.differences.append(
                DiffItem(
                    object_type="procedure",
                    object_name=name,
                    change_type="removed",
                    breaking_change=True,
                )
            )
            diff.procedures_removed += 1

        # Modified procedures
        for name in source_names & target_names:
            source_proc = source_procs[name]
            target_proc = target_procs[name]

            proc_changed = self._compare_procedure_details(
                source_proc, target_proc, name
            )
            if proc_changed:
                diff.differences.append(proc_changed)
                diff.procedures_modified += 1

    def _compare_procedure_details(
        self, source: ProcedureInfo, target: ProcedureInfo, name: str
    ) -> Optional[DiffItem]:
        """Compare procedure details."""
        details = {}
        breaking = False

        # Definition changed
        if source.definition != target.definition:
            details["definition_changed"] = True

        # Parameter changes
        source_params = {p.name.lower(): p for p in source.parameters}
        target_params = {p.name.lower(): p for p in target.parameters}

        added_params = set(target_params.keys()) - set(source_params.keys())
        removed_params = set(source_params.keys()) - set(target_params.keys())

        if added_params:
            details["parameters_added"] = list(added_params)
        if removed_params:
            details["parameters_removed"] = list(removed_params)
            breaking = True  # Removing parameters is breaking

        # Check for required parameter changes
        for param_name in set(source_params.keys()) & set(target_params.keys()):
            source_param = source_params[param_name]
            target_param = target_params[param_name]

            if source_param.data_type != target_param.data_type:
                if "parameter_type_changes" not in details:
                    details["parameter_type_changes"] = {}
                details["parameter_type_changes"][param_name] = {
                    "from": source_param.data_type,
                    "to": target_param.data_type,
                }
                breaking = True

        if details:
            return DiffItem(
                object_type="procedure",
                object_name=name,
                change_type="modified",
                details=details,
                breaking_change=breaking,
            )

        return None

    def _compare_functions(
        self, source: DatabaseSchema, target: DatabaseSchema, diff: SchemaDiff
    ) -> None:
        """Compare functions between schemas."""
        source_funcs = {f.full_name: f for f in source.functions}
        target_funcs = {f.full_name: f for f in target.functions}

        source_names = set(source_funcs.keys())
        target_names = set(target_funcs.keys())

        # Added functions
        for name in target_names - source_names:
            diff.differences.append(
                DiffItem(
                    object_type="function",
                    object_name=name,
                    change_type="added",
                )
            )

        # Removed functions
        for name in source_names - target_names:
            diff.differences.append(
                DiffItem(
                    object_type="function",
                    object_name=name,
                    change_type="removed",
                    breaking_change=True,
                )
            )

        # Modified functions
        for name in source_names & target_names:
            source_func = source_funcs[name]
            target_func = target_funcs[name]

            if source_func.definition != target_func.definition:
                diff.differences.append(
                    DiffItem(
                        object_type="function",
                        object_name=name,
                        change_type="modified",
                        details={"definition_changed": True},
                    )
                )

    def _table_summary(self, table: TableInfo) -> dict[str, Any]:
        """Create a summary of a table."""
        return {
            "name": table.full_name,
            "column_count": len(table.columns),
            "index_count": len(table.indexes),
            "has_primary_key": bool(table.primary_key_columns),
        }

    def _column_summary(self, column: ColumnInfo) -> dict[str, Any]:
        """Create a summary of a column."""
        return {
            "name": column.name,
            "data_type": column.data_type,
            "is_nullable": column.is_nullable,
            "max_length": column.max_length,
            "default_value": column.default_value,
        }

    def _index_summary(self, index: IndexInfo) -> dict[str, Any]:
        """Create a summary of an index."""
        return {
            "name": index.name,
            "type": index.index_type.value,
            "is_unique": index.is_unique,
            "columns": index.columns,
            "included_columns": index.included_columns,
        }

    def _fk_summary(self, fk: ForeignKeyInfo) -> dict[str, Any]:
        """Create a summary of a foreign key."""
        return {
            "name": fk.name,
            "columns": fk.columns,
            "references": f"{fk.referenced_schema}.{fk.referenced_table}",
            "referenced_columns": fk.referenced_columns,
            "on_delete": fk.on_delete,
            "on_update": fk.on_update,
        }

    def _index_changed(self, source: IndexInfo, target: IndexInfo) -> bool:
        """Check if an index has changed."""
        return (
            source.columns != target.columns
            or source.included_columns != target.included_columns
            or source.is_unique != target.is_unique
            or source.filter_definition != target.filter_definition
        )


def generate_migration_script(diff: SchemaDiff, dialect: str = "sqlserver") -> str:
    """Generate a migration script from a diff.

    Args:
        diff: Schema diff to generate migration for
        dialect: SQL dialect (sqlserver, postgresql)

    Returns:
        SQL migration script
    """
    lines = [
        "-- Migration script generated by SQL2.AI",
        f"-- Source: {diff.source_snapshot_id}",
        f"-- Target: {diff.target_snapshot_id}",
        f"-- Total changes: {diff.total_changes}",
        "",
    ]

    if diff.has_breaking_changes:
        lines.append("-- WARNING: This migration contains breaking changes!")
        lines.append("")

    for item in diff.differences:
        if item.change_type == "added":
            if item.object_type == "table":
                lines.append(f"-- TODO: Add table {item.object_name}")
            elif item.object_type == "column":
                lines.append(f"-- ALTER TABLE ... ADD COLUMN {item.object_name}")
            elif item.object_type == "index":
                lines.append(f"-- CREATE INDEX {item.object_name}")

        elif item.change_type == "removed":
            if item.object_type == "table":
                lines.append(f"-- DROP TABLE {item.object_name}")
            elif item.object_type == "column":
                lines.append(f"-- ALTER TABLE ... DROP COLUMN {item.object_name}")
            elif item.object_type == "index":
                lines.append(f"-- DROP INDEX {item.object_name}")

        elif item.change_type == "modified":
            lines.append(f"-- TODO: Modify {item.object_type} {item.object_name}")
            if item.details:
                for key, value in item.details.items():
                    lines.append(f"--   {key}: {value}")

        lines.append("")

    return "\n".join(lines)
