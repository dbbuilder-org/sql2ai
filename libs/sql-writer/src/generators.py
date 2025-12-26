"""SQL code generators for different object types."""

from typing import Optional
from models import (
    ColumnDefinition,
    TableDefinition,
    IndexDefinition,
    StoredProcedureDefinition,
    ViewDefinition,
    FunctionDefinition,
    TriggerDefinition,
    ForeignKeyDefinition,
    ParameterDefinition,
    GenerationResult,
    CRUDGenerationRequest,
    CRUDGenerationResult,
    ObjectType,
    TransactionIsolation,
    ErrorHandlingStyle,
    FunctionType,
)


class TableGenerator:
    """Generator for CREATE TABLE statements."""

    def generate(self, table: TableDefinition) -> GenerationResult:
        """Generate CREATE TABLE statement."""
        lines = []

        # Table header
        lines.append(f"CREATE TABLE [{table.schema_name}].[{table.name}]")
        lines.append("(")

        # Columns
        column_defs = []
        for col in table.columns:
            col_def = self._generate_column(col)
            column_defs.append(f"    {col_def}")

        # Primary key constraint
        if table.primary_key_columns:
            pk_name = f"PK_{table.name}"
            pk_cols = ", ".join(f"[{c}]" for c in table.primary_key_columns)
            column_defs.append(f"    CONSTRAINT [{pk_name}] PRIMARY KEY CLUSTERED ({pk_cols})")

        # Foreign keys
        for fk in table.foreign_keys:
            fk_def = self._generate_foreign_key(fk)
            column_defs.append(f"    {fk_def}")

        lines.append(",\n".join(column_defs))
        lines.append(")")

        # Table options
        if table.compression:
            lines.append(f"WITH (DATA_COMPRESSION = {table.compression})")

        # Temporal table
        if table.is_temporal:
            lines.append("WITH (SYSTEM_VERSIONING = ON")
            if table.history_table_name:
                lines.append(f"    (HISTORY_TABLE = [{table.schema_name}].[{table.history_table_name}])")
            lines.append(")")

        lines.append(";")

        # Indexes
        index_scripts = []
        for idx in table.indexes:
            idx_gen = IndexGenerator()
            result = idx_gen.generate(idx)
            index_scripts.append(result.sql_script)

        sql_script = "\n".join(lines)
        if index_scripts:
            sql_script += "\n\n" + "\n\n".join(index_scripts)

        # Rollback script
        rollback = f"DROP TABLE IF EXISTS [{table.schema_name}].[{table.name}];"

        return GenerationResult(
            object_type=ObjectType.TABLE,
            object_name=f"{table.schema_name}.{table.name}",
            sql_script=sql_script,
            rollback_script=rollback,
            dependencies=[],
        )

    def _generate_column(self, col: ColumnDefinition) -> str:
        """Generate column definition."""
        parts = [f"[{col.name}]"]

        # Data type with size
        if col.computed_expression:
            parts.append(f"AS ({col.computed_expression})")
            if col.is_persisted:
                parts.append("PERSISTED")
        else:
            type_str = col.data_type.upper()
            if col.max_length:
                if col.max_length == -1:
                    type_str += "(MAX)"
                else:
                    type_str += f"({col.max_length})"
            elif col.precision is not None:
                if col.scale is not None:
                    type_str += f"({col.precision}, {col.scale})"
                else:
                    type_str += f"({col.precision})"

            parts.append(type_str)

            # Identity
            if col.is_identity:
                parts.append(f"IDENTITY({col.identity_seed}, {col.identity_increment})")

            # Collation
            if col.collation:
                parts.append(f"COLLATE {col.collation}")

            # Nullability
            parts.append("NULL" if col.nullable else "NOT NULL")

            # Default
            if col.default_value:
                parts.append(f"DEFAULT {col.default_value}")

        return " ".join(parts)

    def _generate_foreign_key(self, fk: ForeignKeyDefinition) -> str:
        """Generate foreign key constraint."""
        cols = ", ".join(f"[{c}]" for c in fk.columns)
        ref_cols = ", ".join(f"[{c}]" for c in fk.referenced_columns)

        parts = [
            f"CONSTRAINT [{fk.name}] FOREIGN KEY ({cols})",
            f"REFERENCES [{fk.referenced_table}] ({ref_cols})",
        ]

        if fk.on_delete != "NO ACTION":
            parts.append(f"ON DELETE {fk.on_delete}")
        if fk.on_update != "NO ACTION":
            parts.append(f"ON UPDATE {fk.on_update}")

        return " ".join(parts)


class IndexGenerator:
    """Generator for CREATE INDEX statements."""

    def generate(self, index: IndexDefinition) -> GenerationResult:
        """Generate CREATE INDEX statement."""
        lines = []

        # Index type
        if index.is_unique:
            lines.append("CREATE UNIQUE")
        else:
            lines.append("CREATE")

        if index.is_clustered:
            lines.append("CLUSTERED INDEX")
        else:
            lines.append("NONCLUSTERED INDEX")

        lines.append(f"[{index.name}]")
        lines.append(f"ON [{index.table_name}]")

        # Key columns
        key_cols = ", ".join(f"[{c}]" for c in index.columns)
        lines.append(f"({key_cols})")

        # Include columns
        if index.include_columns:
            inc_cols = ", ".join(f"[{c}]" for c in index.include_columns)
            lines.append(f"INCLUDE ({inc_cols})")

        # Filter
        if index.filter_predicate:
            lines.append(f"WHERE {index.filter_predicate}")

        # Options
        options = []
        if index.fill_factor != 100:
            options.append(f"FILLFACTOR = {index.fill_factor}")
        if index.compression:
            options.append(f"DATA_COMPRESSION = {index.compression}")

        if options:
            lines.append(f"WITH ({', '.join(options)})")

        sql = " ".join(lines) + ";"

        rollback = f"DROP INDEX IF EXISTS [{index.name}] ON [{index.table_name}];"

        return GenerationResult(
            object_type=ObjectType.INDEX,
            object_name=index.name,
            sql_script=sql,
            rollback_script=rollback,
        )


class StoredProcedureGenerator:
    """Generator for stored procedures with best practices."""

    def generate(self, sp: StoredProcedureDefinition) -> GenerationResult:
        """Generate CREATE PROCEDURE statement with error handling."""
        lines = []

        # Header comment
        if sp.description:
            lines.append("/*")
            lines.append(f"    {sp.description}")
            lines.append("*/")

        # Create procedure
        lines.append(f"CREATE OR ALTER PROCEDURE [{sp.schema_name}].[{sp.name}]")

        # Parameters
        if sp.parameters:
            param_defs = []
            for p in sp.parameters:
                param_def = self._generate_parameter(p)
                param_defs.append(f"    {param_def}")
            lines.append(",\n".join(param_defs))

        # Options
        if sp.with_recompile:
            lines.append("WITH RECOMPILE")
        if sp.execute_as:
            lines.append(f"EXECUTE AS {sp.execute_as}")

        lines.append("AS")
        lines.append("BEGIN")
        lines.append("    SET NOCOUNT ON;")

        # Error handling wrapper
        if sp.error_handling == ErrorHandlingStyle.TRY_CATCH:
            lines.append("")
            lines.append("    BEGIN TRY")

            # Transaction
            if sp.uses_transaction:
                lines.append(f"        SET TRANSACTION ISOLATION LEVEL {sp.isolation_level.value};")
                lines.append("        BEGIN TRANSACTION;")
                lines.append("")

            # Body (indented)
            for body_line in sp.body.split("\n"):
                indent = "            " if sp.uses_transaction else "        "
                lines.append(f"{indent}{body_line}")

            if sp.uses_transaction:
                lines.append("")
                lines.append("        COMMIT TRANSACTION;")

            lines.append("    END TRY")
            lines.append("    BEGIN CATCH")
            if sp.uses_transaction:
                lines.append("        IF @@TRANCOUNT > 0")
                lines.append("            ROLLBACK TRANSACTION;")
                lines.append("")
            lines.append("        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();")
            lines.append("        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();")
            lines.append("        DECLARE @ErrorState INT = ERROR_STATE();")
            lines.append("")
            lines.append("        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);")
            lines.append("    END CATCH")
        else:
            # Simple body without try/catch
            if sp.uses_transaction:
                lines.append(f"    SET TRANSACTION ISOLATION LEVEL {sp.isolation_level.value};")
                lines.append("    BEGIN TRANSACTION;")
                lines.append("")

            for body_line in sp.body.split("\n"):
                lines.append(f"    {body_line}")

            if sp.uses_transaction:
                lines.append("")
                lines.append("    COMMIT TRANSACTION;")

        lines.append("END;")

        sql = "\n".join(lines)
        rollback = f"DROP PROCEDURE IF EXISTS [{sp.schema_name}].[{sp.name}];"

        return GenerationResult(
            object_type=ObjectType.STORED_PROCEDURE,
            object_name=f"{sp.schema_name}.{sp.name}",
            sql_script=sql,
            rollback_script=rollback,
            security_notes=self._get_security_notes(sp),
        )

    def _generate_parameter(self, param: ParameterDefinition) -> str:
        """Generate parameter definition."""
        parts = [f"@{param.name}", param.data_type]

        if param.direction == "OUT":
            parts.append("OUTPUT")
        elif param.direction == "INOUT":
            parts.append("OUTPUT")

        if param.default_value:
            parts.append(f"= {param.default_value}")

        return " ".join(parts)

    def _get_security_notes(self, sp: StoredProcedureDefinition) -> list[str]:
        """Get security recommendations for the procedure."""
        notes = []

        if "EXEC(" in sp.body.upper() or "EXECUTE(" in sp.body.upper():
            if "sp_executesql" not in sp.body.lower():
                notes.append("WARNING: Dynamic SQL detected. Use sp_executesql with parameters to prevent SQL injection.")

        if not sp.uses_transaction and any(kw in sp.body.upper() for kw in ["INSERT", "UPDATE", "DELETE"]):
            notes.append("CONSIDER: Data modification without explicit transaction. Consider adding transaction handling.")

        return notes


class ViewGenerator:
    """Generator for CREATE VIEW statements."""

    def generate(self, view: ViewDefinition) -> GenerationResult:
        """Generate CREATE VIEW statement."""
        lines = []

        if view.description:
            lines.append("/*")
            lines.append(f"    {view.description}")
            lines.append("*/")

        parts = [f"CREATE OR ALTER VIEW [{view.schema_name}].[{view.name}]"]

        if view.is_schema_bound:
            parts.append("WITH SCHEMABINDING")

        lines.append(" ".join(parts))
        lines.append("AS")
        lines.append(view.select_statement)

        if view.with_check_option:
            lines.append("WITH CHECK OPTION")

        lines.append(";")

        sql = "\n".join(lines)
        rollback = f"DROP VIEW IF EXISTS [{view.schema_name}].[{view.name}];"

        return GenerationResult(
            object_type=ObjectType.VIEW,
            object_name=f"{view.schema_name}.{view.name}",
            sql_script=sql,
            rollback_script=rollback,
        )


class FunctionGenerator:
    """Generator for CREATE FUNCTION statements."""

    def generate(self, func: FunctionDefinition) -> GenerationResult:
        """Generate CREATE FUNCTION statement."""
        if func.function_type == FunctionType.SCALAR:
            return self._generate_scalar(func)
        elif func.function_type == FunctionType.INLINE_TABLE:
            return self._generate_inline_table(func)
        else:
            return self._generate_table_valued(func)

    def _generate_scalar(self, func: FunctionDefinition) -> GenerationResult:
        """Generate scalar function."""
        lines = []

        if func.description:
            lines.append(f"-- {func.description}")

        lines.append(f"CREATE OR ALTER FUNCTION [{func.schema_name}].[{func.name}]")

        # Parameters
        if func.parameters:
            lines.append("(")
            param_defs = [f"    @{p.name} {p.data_type}" for p in func.parameters]
            lines.append(",\n".join(param_defs))
            lines.append(")")

        lines.append(f"RETURNS {func.return_type}")

        options = []
        if func.is_schema_bound:
            options.append("SCHEMABINDING")
        if func.is_deterministic:
            options.append("RETURNS NULL ON NULL INPUT")

        if options:
            lines.append(f"WITH {', '.join(options)}")

        lines.append("AS")
        lines.append("BEGIN")
        for body_line in func.body.split("\n"):
            lines.append(f"    {body_line}")
        lines.append("END;")

        sql = "\n".join(lines)
        rollback = f"DROP FUNCTION IF EXISTS [{func.schema_name}].[{func.name}];"

        return GenerationResult(
            object_type=ObjectType.FUNCTION,
            object_name=f"{func.schema_name}.{func.name}",
            sql_script=sql,
            rollback_script=rollback,
        )

    def _generate_inline_table(self, func: FunctionDefinition) -> GenerationResult:
        """Generate inline table-valued function."""
        lines = []

        if func.description:
            lines.append(f"-- {func.description}")

        lines.append(f"CREATE OR ALTER FUNCTION [{func.schema_name}].[{func.name}]")

        if func.parameters:
            lines.append("(")
            param_defs = [f"    @{p.name} {p.data_type}" for p in func.parameters]
            lines.append(",\n".join(param_defs))
            lines.append(")")

        lines.append("RETURNS TABLE")

        if func.is_schema_bound:
            lines.append("WITH SCHEMABINDING")

        lines.append("AS")
        lines.append("RETURN")
        lines.append("(")
        for body_line in func.body.split("\n"):
            lines.append(f"    {body_line}")
        lines.append(");")

        sql = "\n".join(lines)
        rollback = f"DROP FUNCTION IF EXISTS [{func.schema_name}].[{func.name}];"

        return GenerationResult(
            object_type=ObjectType.FUNCTION,
            object_name=f"{func.schema_name}.{func.name}",
            sql_script=sql,
            rollback_script=rollback,
        )

    def _generate_table_valued(self, func: FunctionDefinition) -> GenerationResult:
        """Generate multi-statement table-valued function."""
        lines = []

        if func.description:
            lines.append(f"-- {func.description}")

        lines.append(f"CREATE OR ALTER FUNCTION [{func.schema_name}].[{func.name}]")

        if func.parameters:
            lines.append("(")
            param_defs = [f"    @{p.name} {p.data_type}" for p in func.parameters]
            lines.append(",\n".join(param_defs))
            lines.append(")")

        lines.append("RETURNS @Result TABLE")
        lines.append("(")
        if func.return_table:
            col_defs = []
            for col in func.return_table.columns:
                col_def = f"    [{col.name}] {col.data_type}"
                if not col.nullable:
                    col_def += " NOT NULL"
                col_defs.append(col_def)
            lines.append(",\n".join(col_defs))
        lines.append(")")

        if func.is_schema_bound:
            lines.append("WITH SCHEMABINDING")

        lines.append("AS")
        lines.append("BEGIN")
        for body_line in func.body.split("\n"):
            lines.append(f"    {body_line}")
        lines.append("    RETURN;")
        lines.append("END;")

        sql = "\n".join(lines)
        rollback = f"DROP FUNCTION IF EXISTS [{func.schema_name}].[{func.name}];"

        return GenerationResult(
            object_type=ObjectType.FUNCTION,
            object_name=f"{func.schema_name}.{func.name}",
            sql_script=sql,
            rollback_script=rollback,
        )


class TriggerGenerator:
    """Generator for CREATE TRIGGER statements."""

    def generate(self, trigger: TriggerDefinition) -> GenerationResult:
        """Generate CREATE TRIGGER statement."""
        lines = []

        if trigger.description:
            lines.append(f"-- {trigger.description}")

        lines.append(f"CREATE OR ALTER TRIGGER [{trigger.schema_name}].[{trigger.name}]")
        lines.append(f"ON [{trigger.schema_name}].[{trigger.table_name}]")

        # Trigger type
        trigger_action = trigger.trigger_type.value.upper().replace("_", " ")
        lines.append(trigger_action)

        if trigger.not_for_replication:
            lines.append("NOT FOR REPLICATION")

        lines.append("AS")
        lines.append("BEGIN")
        lines.append("    SET NOCOUNT ON;")
        lines.append("")

        for body_line in trigger.body.split("\n"):
            lines.append(f"    {body_line}")

        lines.append("END;")

        if trigger.is_disabled:
            lines.append(f"\nDISABLE TRIGGER [{trigger.schema_name}].[{trigger.name}] ON [{trigger.schema_name}].[{trigger.table_name}];")

        sql = "\n".join(lines)
        rollback = f"DROP TRIGGER IF EXISTS [{trigger.schema_name}].[{trigger.name}];"

        return GenerationResult(
            object_type=ObjectType.TRIGGER,
            object_name=f"{trigger.schema_name}.{trigger.name}",
            sql_script=sql,
            rollback_script=rollback,
        )


class CRUDGenerator:
    """Generator for CRUD stored procedures."""

    def __init__(self, table_columns: list[ColumnDefinition]):
        """Initialize with table column definitions."""
        self.table_columns = table_columns
        self.sp_generator = StoredProcedureGenerator()

    def generate(self, request: CRUDGenerationRequest) -> CRUDGenerationResult:
        """Generate all requested CRUD procedures."""
        procedures = []

        if request.include_create:
            procedures.append(self._generate_create(request))

        if request.include_read:
            procedures.append(self._generate_read(request))

        if request.include_update:
            procedures.append(self._generate_update(request))

        if request.include_delete:
            procedures.append(self._generate_delete(request))

        if request.include_list:
            procedures.append(self._generate_list(request))

        if request.include_search:
            procedures.append(self._generate_search(request))

        # Combine scripts
        combined = "\n\nGO\n\n".join(p.sql_script for p in procedures)
        rollback = "\n".join(p.rollback_script for p in procedures if p.rollback_script)

        return CRUDGenerationResult(
            table_name=request.table_name,
            procedures=procedures,
            combined_script=combined,
            rollback_script=rollback,
        )

    def _generate_create(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate INSERT procedure."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        # Parameters for non-identity, non-computed columns
        params = []
        insert_cols = []
        insert_vals = []

        for col in self.table_columns:
            if col.is_identity or col.computed_expression:
                continue

            params.append(ParameterDefinition(
                name=col.name,
                data_type=self._get_param_type(col),
            ))
            insert_cols.append(f"[{col.name}]")
            insert_vals.append(f"@{col.name}")

        # Output parameter for identity
        identity_col = next((c for c in self.table_columns if c.is_identity), None)
        if identity_col:
            params.append(ParameterDefinition(
                name=f"{identity_col.name}",
                data_type=identity_col.data_type,
                direction="OUT",
            ))

        body_lines = [
            f"INSERT INTO {table}",
            f"({', '.join(insert_cols)})",
            f"VALUES ({', '.join(insert_vals)});",
        ]

        if identity_col:
            body_lines.append(f"\nSET @{identity_col.name} = SCOPE_IDENTITY();")

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_Create",
            schema_name=request.schema_name,
            parameters=params,
            body="\n".join(body_lines),
            description=f"Insert a new record into {request.table_name}",
        )

        return self.sp_generator.generate(sp)

    def _generate_read(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate SELECT by PK procedure."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        # Find primary key columns
        pk_cols = [c for c in self.table_columns if c.is_primary_key or c.is_identity]
        if not pk_cols:
            pk_cols = [self.table_columns[0]]  # Fallback to first column

        params = [
            ParameterDefinition(name=c.name, data_type=self._get_param_type(c))
            for c in pk_cols
        ]

        where_clause = " AND ".join(f"[{c.name}] = @{c.name}" for c in pk_cols)

        body = f"SELECT * FROM {table} WHERE {where_clause};"

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_GetById",
            schema_name=request.schema_name,
            parameters=params,
            body=body,
            description=f"Get a {request.table_name} record by primary key",
            uses_transaction=False,
        )

        return self.sp_generator.generate(sp)

    def _generate_update(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate UPDATE procedure."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        pk_cols = [c for c in self.table_columns if c.is_primary_key or c.is_identity]
        if not pk_cols:
            pk_cols = [self.table_columns[0]]

        params = []
        set_clauses = []

        for col in self.table_columns:
            params.append(ParameterDefinition(
                name=col.name,
                data_type=self._get_param_type(col),
            ))

            if col not in pk_cols and not col.computed_expression:
                set_clauses.append(f"[{col.name}] = @{col.name}")

        # Concurrency check
        if request.include_concurrency:
            params.append(ParameterDefinition(
                name=request.concurrency_column,
                data_type="ROWVERSION",
            ))

        where_clause = " AND ".join(f"[{c.name}] = @{c.name}" for c in pk_cols)
        if request.include_concurrency:
            where_clause += f" AND [{request.concurrency_column}] = @{request.concurrency_column}"

        body_lines = [
            f"UPDATE {table}",
            f"SET {', '.join(set_clauses)}",
            f"WHERE {where_clause};",
            "",
            "IF @@ROWCOUNT = 0",
            "    RAISERROR('Record not found or concurrency conflict', 16, 1);",
        ]

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_Update",
            schema_name=request.schema_name,
            parameters=params,
            body="\n".join(body_lines),
            description=f"Update a {request.table_name} record",
        )

        return self.sp_generator.generate(sp)

    def _generate_delete(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate DELETE procedure (soft or hard)."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        pk_cols = [c for c in self.table_columns if c.is_primary_key or c.is_identity]
        if not pk_cols:
            pk_cols = [self.table_columns[0]]

        params = [
            ParameterDefinition(name=c.name, data_type=self._get_param_type(c))
            for c in pk_cols
        ]

        where_clause = " AND ".join(f"[{c.name}] = @{c.name}" for c in pk_cols)

        if request.soft_delete:
            body = f"UPDATE {table} SET [{request.soft_delete_column}] = 1 WHERE {where_clause};"
        else:
            body = f"DELETE FROM {table} WHERE {where_clause};"

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_Delete",
            schema_name=request.schema_name,
            parameters=params,
            body=body,
            description=f"{'Soft delete' if request.soft_delete else 'Delete'} a {request.table_name} record",
        )

        return self.sp_generator.generate(sp)

    def _generate_list(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate list/pagination procedure."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        params = [
            ParameterDefinition(name="PageNumber", data_type="INT", default_value="1"),
            ParameterDefinition(name="PageSize", data_type="INT", default_value="50"),
        ]

        # Find a good order by column
        pk_cols = [c for c in self.table_columns if c.is_primary_key or c.is_identity]
        order_col = pk_cols[0].name if pk_cols else self.table_columns[0].name

        where_clause = ""
        if request.soft_delete:
            where_clause = f"WHERE [{request.soft_delete_column}] = 0"

        body_lines = [
            f"SELECT *",
            f"FROM {table}",
        ]
        if where_clause:
            body_lines.append(where_clause)

        body_lines.extend([
            f"ORDER BY [{order_col}]",
            "OFFSET (@PageNumber - 1) * @PageSize ROWS",
            "FETCH NEXT @PageSize ROWS ONLY;",
        ])

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_List",
            schema_name=request.schema_name,
            parameters=params,
            body="\n".join(body_lines),
            description=f"List {request.table_name} records with pagination",
            uses_transaction=False,
        )

        return self.sp_generator.generate(sp)

    def _generate_search(self, request: CRUDGenerationRequest) -> GenerationResult:
        """Generate search procedure."""
        table = f"[{request.schema_name}].[{request.table_name}]"

        params = [
            ParameterDefinition(name="SearchTerm", data_type="NVARCHAR(255)"),
            ParameterDefinition(name="PageNumber", data_type="INT", default_value="1"),
            ParameterDefinition(name="PageSize", data_type="INT", default_value="50"),
        ]

        # Find searchable columns (string types)
        string_cols = [c for c in self.table_columns
                       if c.data_type.upper() in ("NVARCHAR", "VARCHAR", "CHAR", "NCHAR", "TEXT", "NTEXT")]

        if not string_cols:
            string_cols = self.table_columns[:1]  # Fallback

        search_conditions = " OR ".join(f"[{c.name}] LIKE '%' + @SearchTerm + '%'" for c in string_cols)

        pk_cols = [c for c in self.table_columns if c.is_primary_key or c.is_identity]
        order_col = pk_cols[0].name if pk_cols else self.table_columns[0].name

        body_lines = [
            f"SELECT *",
            f"FROM {table}",
            f"WHERE ({search_conditions})",
        ]

        if request.soft_delete:
            body_lines.append(f"    AND [{request.soft_delete_column}] = 0")

        body_lines.extend([
            f"ORDER BY [{order_col}]",
            "OFFSET (@PageNumber - 1) * @PageSize ROWS",
            "FETCH NEXT @PageSize ROWS ONLY;",
        ])

        sp = StoredProcedureDefinition(
            name=f"usp_{request.table_name}_Search",
            schema_name=request.schema_name,
            parameters=params,
            body="\n".join(body_lines),
            description=f"Search {request.table_name} records",
            uses_transaction=False,
        )

        return self.sp_generator.generate(sp)

    def _get_param_type(self, col: ColumnDefinition) -> str:
        """Get SQL parameter type from column."""
        type_str = col.data_type.upper()
        if col.max_length:
            if col.max_length == -1:
                type_str += "(MAX)"
            else:
                type_str += f"({col.max_length})"
        elif col.precision is not None:
            if col.scale is not None:
                type_str += f"({col.precision}, {col.scale})"
            else:
                type_str += f"({col.precision})"
        return type_str
