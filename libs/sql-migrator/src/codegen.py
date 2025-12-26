"""Code generation from database schemas."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

import structlog

from models import CodeLanguage, GeneratedCode

logger = structlog.get_logger()


# Type mappings for different languages
SQL_TO_CSHARP = {
    "int": "int",
    "bigint": "long",
    "smallint": "short",
    "tinyint": "byte",
    "bit": "bool",
    "decimal": "decimal",
    "numeric": "decimal",
    "money": "decimal",
    "smallmoney": "decimal",
    "float": "double",
    "real": "float",
    "datetime": "DateTime",
    "datetime2": "DateTime",
    "date": "DateTime",
    "time": "TimeSpan",
    "datetimeoffset": "DateTimeOffset",
    "char": "string",
    "varchar": "string",
    "nchar": "string",
    "nvarchar": "string",
    "text": "string",
    "ntext": "string",
    "binary": "byte[]",
    "varbinary": "byte[]",
    "image": "byte[]",
    "uniqueidentifier": "Guid",
    "xml": "string",
    "json": "string",
}

SQL_TO_TYPESCRIPT = {
    "int": "number",
    "bigint": "number",
    "smallint": "number",
    "tinyint": "number",
    "bit": "boolean",
    "decimal": "number",
    "numeric": "number",
    "money": "number",
    "smallmoney": "number",
    "float": "number",
    "real": "number",
    "datetime": "Date",
    "datetime2": "Date",
    "date": "Date",
    "time": "string",
    "datetimeoffset": "Date",
    "char": "string",
    "varchar": "string",
    "nchar": "string",
    "nvarchar": "string",
    "text": "string",
    "ntext": "string",
    "binary": "Uint8Array",
    "varbinary": "Uint8Array",
    "image": "Uint8Array",
    "uniqueidentifier": "string",
    "xml": "string",
    "json": "unknown",
}

SQL_TO_ZOD = {
    "int": "z.number().int()",
    "bigint": "z.number().int()",
    "smallint": "z.number().int()",
    "tinyint": "z.number().int().min(0).max(255)",
    "bit": "z.boolean()",
    "decimal": "z.number()",
    "numeric": "z.number()",
    "money": "z.number()",
    "smallmoney": "z.number()",
    "float": "z.number()",
    "real": "z.number()",
    "datetime": "z.date()",
    "datetime2": "z.date()",
    "date": "z.date()",
    "time": "z.string()",
    "datetimeoffset": "z.date()",
    "char": "z.string()",
    "varchar": "z.string()",
    "nchar": "z.string()",
    "nvarchar": "z.string()",
    "text": "z.string()",
    "ntext": "z.string()",
    "binary": "z.instanceof(Uint8Array)",
    "varbinary": "z.instanceof(Uint8Array)",
    "image": "z.instanceof(Uint8Array)",
    "uniqueidentifier": "z.string().uuid()",
    "xml": "z.string()",
    "json": "z.unknown()",
}


class CodeGenerator(ABC):
    """Base class for code generators."""

    @abstractmethod
    def generate(self, schema: Any) -> list[GeneratedCode]:
        """Generate code from schema."""
        pass

    def _pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        # Handle snake_case
        if "_" in name:
            return "".join(word.capitalize() for word in name.split("_"))
        # Handle already PascalCase or camelCase
        return name[0].upper() + name[1:] if name else ""

    def _camel_case(self, name: str) -> str:
        """Convert to camelCase."""
        pascal = self._pascal_case(name)
        return pascal[0].lower() + pascal[1:] if pascal else ""


class DapperGenerator(CodeGenerator):
    """Generate C# Dapper models from database schema."""

    def __init__(
        self,
        namespace: str = "DataModels",
        include_annotations: bool = True,
        include_repository: bool = True,
    ):
        self.namespace = namespace
        self.include_annotations = include_annotations
        self.include_repository = include_repository

    def generate(self, schema: Any) -> list[GeneratedCode]:
        """Generate Dapper models and repositories."""
        results = []

        for table in schema.tables:
            # Generate model class
            model_code = self._generate_model(table)
            results.append(GeneratedCode(
                language=CodeLanguage.CSHARP,
                file_name=f"{self._pascal_case(table.name)}.cs",
                content=model_code,
                source_tables=[table.full_name],
            ))

            # Generate repository
            if self.include_repository:
                repo_code = self._generate_repository(table)
                results.append(GeneratedCode(
                    language=CodeLanguage.CSHARP,
                    file_name=f"{self._pascal_case(table.name)}Repository.cs",
                    content=repo_code,
                    source_tables=[table.full_name],
                ))

        # Generate stored procedure wrappers
        for proc in schema.procedures:
            sp_code = self._generate_sp_wrapper(proc)
            if sp_code:
                results.append(GeneratedCode(
                    language=CodeLanguage.CSHARP,
                    file_name=f"{self._pascal_case(proc.name)}Procedure.cs",
                    content=sp_code,
                    source_tables=[],
                ))

        logger.info(
            "dapper_code_generated",
            models=len(schema.tables),
            procedures=len(schema.procedures),
        )

        return results

    def _generate_model(self, table: Any) -> str:
        """Generate a C# model class."""
        class_name = self._pascal_case(table.name)

        lines = [
            "using System;",
            "using System.ComponentModel.DataAnnotations;",
            "using System.ComponentModel.DataAnnotations.Schema;",
            "",
            f"namespace {self.namespace}",
            "{",
            f"    /// <summary>",
            f"    /// Model for {table.full_name}",
            f"    /// </summary>",
        ]

        if self.include_annotations:
            lines.append(f'    [Table("{table.name}", Schema = "{table.schema}")]')

        lines.append(f"    public class {class_name}")
        lines.append("    {")

        for column in table.columns:
            prop_lines = self._generate_property(column)
            lines.extend(prop_lines)

        lines.append("    }")
        lines.append("}")

        return "\n".join(lines)

    def _generate_property(self, column: Any) -> list[str]:
        """Generate a C# property for a column."""
        lines = []
        prop_name = self._pascal_case(column.name)
        csharp_type = self._get_csharp_type(column)

        # Annotations
        if self.include_annotations:
            if column.is_primary_key:
                lines.append("        [Key]")
            if column.is_identity:
                lines.append("        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]")
            if not column.is_nullable and not column.is_primary_key:
                lines.append("        [Required]")
            if column.max_length and column.max_length > 0:
                lines.append(f"        [MaxLength({column.max_length})]")
            lines.append(f'        [Column("{column.name}")]')

        # Property declaration
        lines.append(f"        public {csharp_type} {prop_name} {{ get; set; }}")
        lines.append("")

        return lines

    def _get_csharp_type(self, column: Any) -> str:
        """Get C# type for a column."""
        base_type = column.data_type_normalized.value.lower()
        csharp_type = SQL_TO_CSHARP.get(base_type, "object")

        # Handle nullability
        if column.is_nullable and csharp_type not in ("string", "byte[]", "object"):
            csharp_type = f"{csharp_type}?"

        return csharp_type

    def _generate_repository(self, table: Any) -> str:
        """Generate a Dapper repository class."""
        class_name = self._pascal_case(table.name)
        pk_columns = table.primary_key_columns or []

        lines = [
            "using System;",
            "using System.Collections.Generic;",
            "using System.Data;",
            "using System.Threading.Tasks;",
            "using Dapper;",
            "",
            f"namespace {self.namespace}.Repositories",
            "{",
            f"    /// <summary>",
            f"    /// Repository for {table.full_name}",
            f"    /// </summary>",
            f"    public class {class_name}Repository",
            "    {",
            "        private readonly IDbConnection _connection;",
            "",
            f"        public {class_name}Repository(IDbConnection connection)",
            "        {",
            "            _connection = connection;",
            "        }",
            "",
        ]

        # GetAll
        lines.extend([
            f"        public async Task<IEnumerable<{class_name}>> GetAllAsync()",
            "        {",
            f'            return await _connection.QueryAsync<{class_name}>(',
            f'                "SELECT * FROM [{table.schema}].[{table.name}]");',
            "        }",
            "",
        ])

        # GetById (if has primary key)
        if pk_columns:
            pk_params = ", ".join(f"{self._get_csharp_type_simple(table, pk)} {self._camel_case(pk)}" for pk in pk_columns)
            pk_where = " AND ".join(f"[{pk}] = @{self._camel_case(pk)}" for pk in pk_columns)
            pk_args = ", ".join(f"new {{ {self._camel_case(pk)} }}" for pk in pk_columns)

            lines.extend([
                f"        public async Task<{class_name}?> GetByIdAsync({pk_params})",
                "        {",
                f'            return await _connection.QueryFirstOrDefaultAsync<{class_name}>(',
                f'                "SELECT * FROM [{table.schema}].[{table.name}] WHERE {pk_where}",',
                f'                {pk_args});',
                "        }",
                "",
            ])

        # Insert
        columns = [c for c in table.columns if not c.is_identity]
        col_names = ", ".join(f"[{c.name}]" for c in columns)
        col_params = ", ".join(f"@{self._pascal_case(c.name)}" for c in columns)

        lines.extend([
            f"        public async Task<int> InsertAsync({class_name} entity)",
            "        {",
            f'            return await _connection.ExecuteAsync(',
            f'                @"INSERT INTO [{table.schema}].[{table.name}] ({col_names})',
            f'                VALUES ({col_params})",',
            "                entity);",
            "        }",
            "",
        ])

        # Update (if has primary key)
        if pk_columns:
            update_cols = [c for c in table.columns if c.name not in pk_columns]
            set_clause = ", ".join(f"[{c.name}] = @{self._pascal_case(c.name)}" for c in update_cols)
            where_clause = " AND ".join(f"[{pk}] = @{self._pascal_case(pk)}" for pk in pk_columns)

            lines.extend([
                f"        public async Task<int> UpdateAsync({class_name} entity)",
                "        {",
                f'            return await _connection.ExecuteAsync(',
                f'                @"UPDATE [{table.schema}].[{table.name}]',
                f'                SET {set_clause}',
                f'                WHERE {where_clause}",',
                "                entity);",
                "        }",
                "",
            ])

        # Delete (if has primary key)
        if pk_columns:
            pk_params = ", ".join(f"{self._get_csharp_type_simple(table, pk)} {self._camel_case(pk)}" for pk in pk_columns)
            where_clause = " AND ".join(f"[{pk}] = @{self._camel_case(pk)}" for pk in pk_columns)

            lines.extend([
                f"        public async Task<int> DeleteAsync({pk_params})",
                "        {",
                f'            return await _connection.ExecuteAsync(',
                f'                "DELETE FROM [{table.schema}].[{table.name}] WHERE {where_clause}",',
                f'                new {{ {", ".join(self._camel_case(pk) for pk in pk_columns)} }});',
                "        }",
            ])

        lines.extend([
            "    }",
            "}",
        ])

        return "\n".join(lines)

    def _get_csharp_type_simple(self, table: Any, column_name: str) -> str:
        """Get simple C# type for a column by name."""
        for col in table.columns:
            if col.name == column_name:
                base_type = col.data_type_normalized.value.lower()
                return SQL_TO_CSHARP.get(base_type, "object")
        return "object"

    def _generate_sp_wrapper(self, proc: Any) -> Optional[str]:
        """Generate stored procedure wrapper."""
        class_name = self._pascal_case(proc.name)

        lines = [
            "using System;",
            "using System.Data;",
            "using System.Threading.Tasks;",
            "using Dapper;",
            "",
            f"namespace {self.namespace}.Procedures",
            "{",
            f"    /// <summary>",
            f"    /// Wrapper for stored procedure {proc.full_name}",
            f"    /// </summary>",
            f"    public static class {class_name}Procedure",
            "    {",
        ]

        # Generate parameters class
        if proc.parameters:
            lines.append(f"        public class Parameters")
            lines.append("        {")
            for param in proc.parameters:
                param_name = self._pascal_case(param.name.lstrip("@"))
                param_type = SQL_TO_CSHARP.get(param.data_type.lower(), "object")
                if param.is_nullable:
                    param_type = f"{param_type}?"
                lines.append(f"            public {param_type} {param_name} {{ get; set; }}")
            lines.append("        }")
            lines.append("")

        # Generate execute method
        lines.extend([
            f"        public static async Task<int> ExecuteAsync(",
            f"            IDbConnection connection,",
            f"            Parameters parameters)",
            "        {",
            f'            return await connection.ExecuteAsync(',
            f'                "[{proc.schema}].[{proc.name}]",',
            f'                parameters,',
            f'                commandType: CommandType.StoredProcedure);',
            "        }",
        ])

        lines.extend([
            "    }",
            "}",
        ])

        return "\n".join(lines)


class TypeScriptGenerator(CodeGenerator):
    """Generate TypeScript types from database schema."""

    def __init__(
        self,
        export_style: str = "interface",  # interface or type
        include_enums: bool = True,
    ):
        self.export_style = export_style
        self.include_enums = include_enums

    def generate(self, schema: Any) -> list[GeneratedCode]:
        """Generate TypeScript types."""
        results = []

        # Generate types for each table
        type_lines = [
            "// Auto-generated TypeScript types",
            f"// Generated: {datetime.utcnow().isoformat()}",
            "",
        ]

        for table in schema.tables:
            type_lines.extend(self._generate_type(table))
            type_lines.append("")

        results.append(GeneratedCode(
            language=CodeLanguage.TYPESCRIPT,
            file_name="models.ts",
            content="\n".join(type_lines),
            source_tables=[t.full_name for t in schema.tables],
        ))

        logger.info(
            "typescript_code_generated",
            types=len(schema.tables),
        )

        return results

    def _generate_type(self, table: Any) -> list[str]:
        """Generate TypeScript interface/type for a table."""
        type_name = self._pascal_case(table.name)
        lines = []

        if self.export_style == "interface":
            lines.append(f"export interface {type_name} {{")
        else:
            lines.append(f"export type {type_name} = {{")

        for column in table.columns:
            prop_name = self._camel_case(column.name)
            ts_type = self._get_ts_type(column)
            optional = "?" if column.is_nullable else ""
            lines.append(f"  {prop_name}{optional}: {ts_type};")

        lines.append("}")

        return lines

    def _get_ts_type(self, column: Any) -> str:
        """Get TypeScript type for a column."""
        base_type = column.data_type_normalized.value.lower()
        return SQL_TO_TYPESCRIPT.get(base_type, "unknown")


class ZodSchemaGenerator(CodeGenerator):
    """Generate Zod validation schemas from database schema."""

    def generate(self, schema: Any) -> list[GeneratedCode]:
        """Generate Zod schemas."""
        results = []

        lines = [
            "// Auto-generated Zod schemas",
            f"// Generated: {datetime.utcnow().isoformat()}",
            "",
            "import { z } from 'zod';",
            "",
        ]

        for table in schema.tables:
            lines.extend(self._generate_schema(table))
            lines.append("")

        results.append(GeneratedCode(
            language=CodeLanguage.ZOD,
            file_name="schemas.ts",
            content="\n".join(lines),
            source_tables=[t.full_name for t in schema.tables],
        ))

        logger.info(
            "zod_schemas_generated",
            schemas=len(schema.tables),
        )

        return results

    def _generate_schema(self, table: Any) -> list[str]:
        """Generate Zod schema for a table."""
        schema_name = self._camel_case(table.name) + "Schema"
        type_name = self._pascal_case(table.name)

        lines = [
            f"export const {schema_name} = z.object({{",
        ]

        for column in table.columns:
            prop_name = self._camel_case(column.name)
            zod_type = self._get_zod_type(column)
            lines.append(f"  {prop_name}: {zod_type},")

        lines.append("});")
        lines.append("")
        lines.append(f"export type {type_name} = z.infer<typeof {schema_name}>;")

        return lines

    def _get_zod_type(self, column: Any) -> str:
        """Get Zod type for a column."""
        base_type = column.data_type_normalized.value.lower()
        zod_type = SQL_TO_ZOD.get(base_type, "z.unknown()")

        # Handle max length for strings
        if base_type in ("varchar", "nvarchar", "char", "nchar") and column.max_length:
            zod_type = f"z.string().max({column.max_length})"

        # Handle nullability
        if column.is_nullable:
            zod_type = f"{zod_type}.nullable()"

        return zod_type
