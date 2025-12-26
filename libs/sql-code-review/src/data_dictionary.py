"""Data dictionary generator for databases."""

from datetime import datetime
from typing import Optional, Callable, Awaitable, Any
from dataclasses import dataclass, field

from models import (
    ObjectDocumentation,
    ColumnDocumentation,
    RelationshipDocumentation,
    DataDictionary,
    ObjectCategory,
)


# Type for database query function
DBQueryFunc = Callable[[str], Awaitable[list[dict]]]

# Type for AI completion function
AICompletionFunc = Callable[[str, str], Awaitable[str]]


class DataDictionaryGenerator:
    """Generates data dictionaries from database schemas."""

    def __init__(
        self,
        db_query: Optional[DBQueryFunc] = None,
        ai_completion: Optional[AICompletionFunc] = None,
    ):
        """Initialize generator.

        Args:
            db_query: Async function to execute database queries
            ai_completion: Optional AI function for generating descriptions
        """
        self.db_query = db_query
        self.ai_completion = ai_completion

    async def generate(
        self,
        database_name: str,
        version: str = "1.0.0",
        include_ai_descriptions: bool = True,
    ) -> DataDictionary:
        """Generate data dictionary for a database.

        Args:
            database_name: Name of the database
            version: Version string for the dictionary
            include_ai_descriptions: Whether to generate AI descriptions

        Returns:
            Generated data dictionary
        """
        objects = []
        relationships = []

        # Extract tables
        tables = await self._extract_tables()
        for table in tables:
            doc = await self._document_table(table, include_ai_descriptions)
            objects.append(doc)

        # Extract views
        views = await self._extract_views()
        for view in views:
            doc = await self._document_view(view, include_ai_descriptions)
            objects.append(doc)

        # Extract stored procedures
        procs = await self._extract_procedures()
        for proc in procs:
            doc = await self._document_procedure(proc, include_ai_descriptions)
            objects.append(doc)

        # Extract functions
        funcs = await self._extract_functions()
        for func in funcs:
            doc = await self._document_function(func, include_ai_descriptions)
            objects.append(doc)

        # Extract relationships
        relationships = await self._extract_relationships()

        # Generate glossary
        glossary = await self._generate_glossary(objects) if include_ai_descriptions else {}

        return DataDictionary(
            database_name=database_name,
            generated_at=datetime.utcnow(),
            version=version,
            description=f"Data dictionary for {database_name}",
            objects=objects,
            relationships=relationships,
            glossary=glossary,
        )

    async def _extract_tables(self) -> list[dict]:
        """Extract table metadata from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            t.create_date,
            t.modify_date,
            CAST(ep.value AS NVARCHAR(MAX)) AS description
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = t.object_id
            AND ep.minor_id = 0
            AND ep.name = 'MS_Description'
        WHERE t.is_ms_shipped = 0
        ORDER BY s.name, t.name
        """
        return await self.db_query(query)

    async def _extract_columns(self, schema_name: str, table_name: str) -> list[dict]:
        """Extract column metadata for a table."""
        if not self.db_query:
            return []

        query = f"""
        SELECT
            c.name AS column_name,
            TYPE_NAME(c.user_type_id) AS data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity,
            CAST(ep.value AS NVARCHAR(MAX)) AS description,
            CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key,
            fk.referenced_table,
            fk.referenced_column
        FROM sys.columns c
        JOIN sys.tables t ON c.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = c.object_id
            AND ep.minor_id = c.column_id
            AND ep.name = 'MS_Description'
        LEFT JOIN (
            SELECT ic.object_id, ic.column_id
            FROM sys.index_columns ic
            JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
            WHERE i.is_primary_key = 1
        ) pk ON pk.object_id = c.object_id AND pk.column_id = c.column_id
        LEFT JOIN (
            SELECT
                fkc.parent_object_id,
                fkc.parent_column_id,
                OBJECT_SCHEMA_NAME(fkc.referenced_object_id) + '.' +
                    OBJECT_NAME(fkc.referenced_object_id) AS referenced_table,
                COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS referenced_column
            FROM sys.foreign_key_columns fkc
        ) fk ON fk.parent_object_id = c.object_id AND fk.parent_column_id = c.column_id
        WHERE s.name = '{schema_name}' AND t.name = '{table_name}'
        ORDER BY c.column_id
        """
        return await self.db_query(query)

    async def _extract_views(self) -> list[dict]:
        """Extract view metadata from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            s.name AS schema_name,
            v.name AS view_name,
            v.create_date,
            v.modify_date,
            m.definition,
            CAST(ep.value AS NVARCHAR(MAX)) AS description
        FROM sys.views v
        JOIN sys.schemas s ON v.schema_id = s.schema_id
        JOIN sys.sql_modules m ON v.object_id = m.object_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = v.object_id
            AND ep.minor_id = 0
            AND ep.name = 'MS_Description'
        WHERE v.is_ms_shipped = 0
        ORDER BY s.name, v.name
        """
        return await self.db_query(query)

    async def _extract_procedures(self) -> list[dict]:
        """Extract stored procedure metadata from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            s.name AS schema_name,
            p.name AS procedure_name,
            p.create_date,
            p.modify_date,
            m.definition,
            CAST(ep.value AS NVARCHAR(MAX)) AS description
        FROM sys.procedures p
        JOIN sys.schemas s ON p.schema_id = s.schema_id
        JOIN sys.sql_modules m ON p.object_id = m.object_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = p.object_id
            AND ep.minor_id = 0
            AND ep.name = 'MS_Description'
        WHERE p.is_ms_shipped = 0
        ORDER BY s.name, p.name
        """
        return await self.db_query(query)

    async def _extract_functions(self) -> list[dict]:
        """Extract function metadata from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            s.name AS schema_name,
            o.name AS function_name,
            o.type_desc AS function_type,
            o.create_date,
            o.modify_date,
            m.definition,
            CAST(ep.value AS NVARCHAR(MAX)) AS description
        FROM sys.objects o
        JOIN sys.schemas s ON o.schema_id = s.schema_id
        JOIN sys.sql_modules m ON o.object_id = m.object_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = o.object_id
            AND ep.minor_id = 0
            AND ep.name = 'MS_Description'
        WHERE o.type IN ('FN', 'IF', 'TF')
        ORDER BY s.name, o.name
        """
        return await self.db_query(query)

    async def _extract_parameters(self, schema_name: str, object_name: str) -> list[dict]:
        """Extract parameters for a stored procedure or function."""
        if not self.db_query:
            return []

        query = f"""
        SELECT
            p.name AS parameter_name,
            TYPE_NAME(p.user_type_id) AS data_type,
            p.max_length,
            p.is_output,
            p.has_default_value,
            p.default_value,
            CAST(ep.value AS NVARCHAR(MAX)) AS description
        FROM sys.parameters p
        JOIN sys.objects o ON p.object_id = o.object_id
        JOIN sys.schemas s ON o.schema_id = s.schema_id
        LEFT JOIN sys.extended_properties ep
            ON ep.major_id = p.object_id
            AND ep.minor_id = p.parameter_id
            AND ep.name = 'MS_Description'
        WHERE s.name = '{schema_name}' AND o.name = '{object_name}'
        ORDER BY p.parameter_id
        """
        return await self.db_query(query)

    async def _extract_relationships(self) -> list[RelationshipDocumentation]:
        """Extract foreign key relationships from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            fk.name AS fk_name,
            OBJECT_SCHEMA_NAME(fk.parent_object_id) + '.' +
                OBJECT_NAME(fk.parent_object_id) AS from_table,
            OBJECT_SCHEMA_NAME(fk.referenced_object_id) + '.' +
                OBJECT_NAME(fk.referenced_object_id) AS to_table,
            fk.delete_referential_action_desc AS on_delete,
            fk.update_referential_action_desc AS on_update
        FROM sys.foreign_keys fk
        ORDER BY fk.name
        """

        fks = await self.db_query(query)
        relationships = []

        for fk in fks:
            # Get columns for this FK
            col_query = f"""
            SELECT
                COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS from_column,
                COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS to_column
            FROM sys.foreign_key_columns fkc
            JOIN sys.foreign_keys fk ON fkc.constraint_object_id = fk.object_id
            WHERE fk.name = '{fk["fk_name"]}'
            """
            cols = await self.db_query(col_query)

            from_cols = [c["from_column"] for c in cols]
            to_cols = [c["to_column"] for c in cols]

            relationships.append(RelationshipDocumentation(
                name=fk["fk_name"],
                from_table=fk["from_table"],
                from_columns=from_cols,
                to_table=fk["to_table"],
                to_columns=to_cols,
                relationship_type="many-to-one",  # Default assumption
                cascade_delete=fk["on_delete"] == "CASCADE",
                cascade_update=fk["on_update"] == "CASCADE",
            ))

        return relationships

    async def _document_table(
        self,
        table: dict,
        include_ai: bool,
    ) -> ObjectDocumentation:
        """Document a table."""
        schema_name = table["schema_name"]
        table_name = table["table_name"]

        # Get columns
        columns_data = await self._extract_columns(schema_name, table_name)
        columns = []

        for col in columns_data:
            description = col.get("description") or ""

            # Generate AI description if enabled and no description exists
            if include_ai and self.ai_completion and not description:
                description = await self._generate_column_description(
                    table_name, col["column_name"], col["data_type"]
                )

            columns.append(ColumnDocumentation(
                name=col["column_name"],
                data_type=self._format_data_type(col),
                nullable=bool(col["is_nullable"]),
                description=description,
                is_primary_key=bool(col.get("is_primary_key")),
                is_foreign_key=col.get("referenced_table") is not None,
                foreign_key_reference=col.get("referenced_table"),
            ))

        # Generate table description
        description = table.get("description") or ""
        if include_ai and self.ai_completion and not description:
            description = await self._generate_table_description(
                table_name, [c.name for c in columns]
            )

        return ObjectDocumentation(
            name=table_name,
            schema_name=schema_name,
            category=ObjectCategory.TABLE,
            description=description,
            created_date=table.get("create_date"),
            modified_date=table.get("modify_date"),
            columns=columns,
        )

    async def _document_view(
        self,
        view: dict,
        include_ai: bool,
    ) -> ObjectDocumentation:
        """Document a view."""
        description = view.get("description") or ""

        if include_ai and self.ai_completion and not description:
            description = await self._generate_view_description(
                view["view_name"], view.get("definition", "")
            )

        return ObjectDocumentation(
            name=view["view_name"],
            schema_name=view["schema_name"],
            category=ObjectCategory.VIEW,
            description=description,
            created_date=view.get("create_date"),
            modified_date=view.get("modify_date"),
        )

    async def _document_procedure(
        self,
        proc: dict,
        include_ai: bool,
    ) -> ObjectDocumentation:
        """Document a stored procedure."""
        schema_name = proc["schema_name"]
        proc_name = proc["procedure_name"]

        # Get parameters
        params_data = await self._extract_parameters(schema_name, proc_name)
        parameters = [
            {
                "name": p["parameter_name"].lstrip("@"),
                "type": p["data_type"],
                "is_output": bool(p.get("is_output")),
                "description": p.get("description", ""),
            }
            for p in params_data
        ]

        description = proc.get("description") or ""
        if include_ai and self.ai_completion and not description:
            description = await self._generate_procedure_description(
                proc_name, proc.get("definition", "")
            )

        return ObjectDocumentation(
            name=proc_name,
            schema_name=schema_name,
            category=ObjectCategory.STORED_PROCEDURE,
            description=description,
            created_date=proc.get("create_date"),
            modified_date=proc.get("modify_date"),
            parameters=parameters,
        )

    async def _document_function(
        self,
        func: dict,
        include_ai: bool,
    ) -> ObjectDocumentation:
        """Document a function."""
        schema_name = func["schema_name"]
        func_name = func["function_name"]

        # Get parameters
        params_data = await self._extract_parameters(schema_name, func_name)
        parameters = [
            {
                "name": p["parameter_name"].lstrip("@"),
                "type": p["data_type"],
                "description": p.get("description", ""),
            }
            for p in params_data
        ]

        description = func.get("description") or ""
        if include_ai and self.ai_completion and not description:
            description = await self._generate_function_description(
                func_name, func.get("definition", "")
            )

        return ObjectDocumentation(
            name=func_name,
            schema_name=schema_name,
            category=ObjectCategory.FUNCTION,
            description=description,
            created_date=func.get("create_date"),
            modified_date=func.get("modify_date"),
            parameters=parameters,
        )

    def _format_data_type(self, col: dict) -> str:
        """Format column data type with size."""
        data_type = col["data_type"]
        max_length = col.get("max_length")
        precision = col.get("precision")
        scale = col.get("scale")

        if data_type in ("varchar", "nvarchar", "char", "nchar", "varbinary"):
            if max_length == -1:
                return f"{data_type}(MAX)"
            elif data_type.startswith("n"):
                return f"{data_type}({max_length // 2})"
            else:
                return f"{data_type}({max_length})"
        elif data_type in ("decimal", "numeric"):
            return f"{data_type}({precision}, {scale})"
        else:
            return data_type

    async def _generate_column_description(
        self,
        table_name: str,
        column_name: str,
        data_type: str,
    ) -> str:
        """Generate AI description for a column."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief, clear description for a database column.
The description should explain what data the column stores.
Keep it under 100 characters."""

        user_prompt = f"""Table: {table_name}
Column: {column_name}
Data Type: {data_type}

Generate a description for this column:"""

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""

    async def _generate_table_description(
        self,
        table_name: str,
        columns: list[str],
    ) -> str:
        """Generate AI description for a table."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief, clear description for a database table.
The description should explain the purpose of the table.
Keep it under 200 characters."""

        user_prompt = f"""Table: {table_name}
Columns: {', '.join(columns[:10])}

Generate a description for this table:"""

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""

    async def _generate_view_description(
        self,
        view_name: str,
        definition: str,
    ) -> str:
        """Generate AI description for a view."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief, clear description for a database view.
The description should explain what data the view provides.
Keep it under 200 characters."""

        # Truncate long definitions
        def_excerpt = definition[:500] + "..." if len(definition) > 500 else definition

        user_prompt = f"""View: {view_name}
Definition excerpt: {def_excerpt}

Generate a description for this view:"""

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""

    async def _generate_procedure_description(
        self,
        proc_name: str,
        definition: str,
    ) -> str:
        """Generate AI description for a stored procedure."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief, clear description for a stored procedure.
The description should explain what the procedure does.
Keep it under 200 characters."""

        def_excerpt = definition[:500] + "..." if len(definition) > 500 else definition

        user_prompt = f"""Procedure: {proc_name}
Definition excerpt: {def_excerpt}

Generate a description for this procedure:"""

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""

    async def _generate_function_description(
        self,
        func_name: str,
        definition: str,
    ) -> str:
        """Generate AI description for a function."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief, clear description for a database function.
The description should explain what the function returns.
Keep it under 200 characters."""

        def_excerpt = definition[:500] + "..." if len(definition) > 500 else definition

        user_prompt = f"""Function: {func_name}
Definition excerpt: {def_excerpt}

Generate a description for this function:"""

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""

    async def _generate_glossary(
        self,
        objects: list[ObjectDocumentation],
    ) -> dict[str, str]:
        """Generate a glossary of common terms."""
        if not self.ai_completion:
            return {}

        # Collect unique terms from object and column names
        terms = set()
        for obj in objects:
            # Add camelCase/PascalCase split words
            terms.update(self._extract_words(obj.name))
            for col in obj.columns:
                terms.update(self._extract_words(col.name))

        # Filter to meaningful terms
        terms = {t for t in terms if len(t) > 3 and t.lower() not in (
            "the", "and", "for", "with", "from", "into", "that", "this",
            "name", "date", "type", "code", "data", "info", "list"
        )}

        # Generate definitions for top terms
        glossary = {}
        for term in list(terms)[:20]:  # Limit to 20 terms
            definition = await self._generate_term_definition(term)
            if definition:
                glossary[term] = definition

        return glossary

    def _extract_words(self, name: str) -> list[str]:
        """Extract words from camelCase/PascalCase names."""
        import re
        # Split on camelCase boundaries
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        return [w.lower() for w in words if len(w) > 2]

    async def _generate_term_definition(self, term: str) -> str:
        """Generate definition for a glossary term."""
        if not self.ai_completion:
            return ""

        system_prompt = """You are a database documentation expert.
Generate a brief definition for a business/database term.
Keep it under 100 characters."""

        user_prompt = f"Define the term: {term}"

        try:
            return await self.ai_completion(system_prompt, user_prompt)
        except Exception:
            return ""
