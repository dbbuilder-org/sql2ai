"""Schema extraction from various database systems."""

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import structlog

from models import (
    ColumnInfo,
    DatabaseSchema,
    DataType,
    ForeignKeyInfo,
    FunctionInfo,
    IndexInfo,
    IndexType,
    ParameterInfo,
    ProcedureInfo,
    SchemaSnapshot,
    TableInfo,
    TriggerEvent,
    TriggerInfo,
    TriggerTiming,
    ViewInfo,
)

logger = structlog.get_logger()


class SchemaExtractor(ABC):
    """Abstract base class for schema extraction."""

    def __init__(self, connection_string: str):
        """Initialize with connection string.

        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string

    @abstractmethod
    async def extract(
        self,
        include_definitions: bool = True,
        include_row_counts: bool = False,
        schemas: Optional[list[str]] = None,
    ) -> DatabaseSchema:
        """Extract complete database schema.

        Args:
            include_definitions: Include procedure/view definitions
            include_row_counts: Include table row counts (slower)
            schemas: Specific schemas to extract (None = all)

        Returns:
            Complete DatabaseSchema object
        """
        pass

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str, Optional[str]]:
        """Test database connection.

        Returns:
            Tuple of (success, message, server_version)
        """
        pass

    async def create_snapshot(
        self,
        connection_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        label: Optional[str] = None,
        is_baseline: bool = False,
    ) -> SchemaSnapshot:
        """Extract schema and create a snapshot.

        Args:
            connection_id: Connection identifier
            tenant_id: Tenant identifier
            user_id: User who created the snapshot
            label: Optional label for the snapshot
            is_baseline: Whether this is a baseline snapshot

        Returns:
            SchemaSnapshot with extracted schema
        """
        schema = await self.extract()

        # Create content hash for quick comparison
        content_hash = self._create_content_hash(schema)

        return SchemaSnapshot(
            id=str(uuid4()),
            connection_id=connection_id,
            tenant_id=tenant_id,
            schema=schema,
            created_at=datetime.utcnow(),
            created_by=user_id,
            label=label,
            is_baseline=is_baseline,
            content_hash=content_hash,
        )

    def _create_content_hash(self, schema: DatabaseSchema) -> str:
        """Create a hash of schema content for comparison."""
        # Create a stable representation
        content = {
            "tables": sorted([t.full_name for t in schema.tables]),
            "views": sorted([v.full_name for v in schema.views]),
            "procedures": sorted([p.full_name for p in schema.procedures]),
            "table_hashes": {
                t.full_name: self._hash_table(t) for t in schema.tables
            },
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _hash_table(self, table: TableInfo) -> str:
        """Create hash of table structure."""
        content = {
            "columns": [
                {
                    "name": c.name,
                    "type": c.data_type,
                    "nullable": c.is_nullable,
                    "default": c.default_value,
                }
                for c in table.columns
            ],
            "indexes": sorted([i.name for i in table.indexes]),
            "fks": sorted([f.name for f in table.foreign_keys]),
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]


class SQLServerExtractor(SchemaExtractor):
    """Schema extractor for SQL Server databases."""

    async def test_connection(self) -> tuple[bool, str, Optional[str]]:
        """Test SQL Server connection."""
        try:
            import pyodbc

            with pyodbc.connect(self.connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION, @@SERVERNAME")
                row = cursor.fetchone()
                version = row[0].split("\n")[0] if row[0] else None
                server = row[1]

            return True, f"Connected to {server}", version

        except Exception as e:
            return False, f"Connection failed: {str(e)}", None

    async def extract(
        self,
        include_definitions: bool = True,
        include_row_counts: bool = False,
        schemas: Optional[list[str]] = None,
    ) -> DatabaseSchema:
        """Extract SQL Server schema."""
        import pyodbc

        logger.info("starting_schema_extraction", db_type="sqlserver")

        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()

            # Get database info
            cursor.execute("""
                SELECT DB_NAME() as database_name,
                       @@SERVERNAME as server_name,
                       @@VERSION as server_version,
                       DATABASEPROPERTYEX(DB_NAME(), 'Collation') as collation
            """)
            row = cursor.fetchone()

            db_schema = DatabaseSchema(
                database_name=row.database_name,
                server_name=row.server_name,
                server_version=row.server_version.split("\n")[0] if row.server_version else None,
                collation=row.collation,
            )

            # Get schemas
            db_schema.schemas = await self._extract_schemas(cursor, schemas)

            # Extract objects
            db_schema.tables = await self._extract_tables(
                cursor, db_schema.schemas, include_row_counts
            )
            db_schema.views = await self._extract_views(
                cursor, db_schema.schemas, include_definitions
            )
            if include_definitions:
                db_schema.procedures = await self._extract_procedures(cursor, db_schema.schemas)
                db_schema.functions = await self._extract_functions(cursor, db_schema.schemas)
                db_schema.triggers = await self._extract_triggers(cursor, db_schema.schemas)

        logger.info(
            "schema_extraction_complete",
            tables=len(db_schema.tables),
            views=len(db_schema.views),
            procedures=len(db_schema.procedures),
        )

        return db_schema

    async def _extract_schemas(
        self, cursor: Any, filter_schemas: Optional[list[str]]
    ) -> list[str]:
        """Extract schema names."""
        cursor.execute("""
            SELECT name FROM sys.schemas
            WHERE name NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest')
            ORDER BY name
        """)
        all_schemas = [row.name for row in cursor.fetchall()]

        if filter_schemas:
            return [s for s in all_schemas if s in filter_schemas]
        return all_schemas

    async def _extract_tables(
        self,
        cursor: Any,
        schemas: list[str],
        include_row_counts: bool,
    ) -> list[TableInfo]:
        """Extract table information."""
        tables = []

        schema_filter = ",".join(f"'{s}'" for s in schemas)

        # Get tables
        cursor.execute(f"""
            SELECT
                t.name as table_name,
                s.name as schema_name,
                t.create_date,
                t.modify_date,
                ep.value as description,
                t.temporal_type_desc,
                ht.name as history_table_name
            FROM sys.tables t
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = t.object_id
                AND ep.minor_id = 0
                AND ep.name = 'MS_Description'
            LEFT JOIN sys.tables ht ON t.history_table_id = ht.object_id
            WHERE s.name IN ({schema_filter})
            ORDER BY s.name, t.name
        """)

        for row in cursor.fetchall():
            table = TableInfo(
                name=row.table_name,
                schema=row.schema_name,
                created_at=row.create_date,
                modified_at=row.modify_date,
                description=row.description,
                is_temporal=row.temporal_type_desc == "SYSTEM_VERSIONED",
                temporal_history_table=row.history_table_name,
            )

            # Get columns
            table.columns = await self._extract_columns(cursor, table.schema, table.name)

            # Get indexes
            table.indexes = await self._extract_indexes(cursor, table.schema, table.name)

            # Get foreign keys
            table.foreign_keys = await self._extract_foreign_keys(
                cursor, table.schema, table.name
            )

            # Get primary key columns
            table.primary_key_columns = [
                c.name for c in table.columns if c.is_primary_key
            ]

            # Get row count if requested
            if include_row_counts:
                try:
                    cursor.execute(f"""
                        SELECT SUM(p.rows) as row_count
                        FROM sys.partitions p
                        INNER JOIN sys.tables t ON p.object_id = t.object_id
                        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                        WHERE s.name = ? AND t.name = ? AND p.index_id IN (0, 1)
                    """, table.schema, table.name)
                    count_row = cursor.fetchone()
                    table.row_count = count_row.row_count if count_row else None
                except Exception:
                    pass

            tables.append(table)

        return tables

    async def _extract_columns(
        self, cursor: Any, schema: str, table: str
    ) -> list[ColumnInfo]:
        """Extract column information."""
        cursor.execute("""
            SELECT
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                c.is_identity,
                c.is_computed,
                cc.definition as computed_definition,
                dc.definition as default_value,
                c.collation_name,
                ep.value as description,
                c.column_id,
                CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END as is_pk
            FROM sys.columns c
            INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
            INNER JOIN sys.tables tbl ON c.object_id = tbl.object_id
            INNER JOIN sys.schemas s ON tbl.schema_id = s.schema_id
            LEFT JOIN sys.computed_columns cc ON c.object_id = cc.object_id AND c.column_id = cc.column_id
            LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = c.object_id
                AND ep.minor_id = c.column_id
                AND ep.name = 'MS_Description'
            LEFT JOIN (
                SELECT ic.column_id, i.object_id
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                WHERE i.is_primary_key = 1
            ) pk ON pk.object_id = c.object_id AND pk.column_id = c.column_id
            WHERE s.name = ? AND tbl.name = ?
            ORDER BY c.column_id
        """, schema, table)

        columns = []
        for row in cursor.fetchall():
            col = ColumnInfo(
                name=row.column_name,
                data_type=row.data_type,
                data_type_normalized=self._normalize_type(row.data_type),
                max_length=row.max_length if row.max_length != -1 else None,
                precision=row.precision,
                scale=row.scale,
                is_nullable=row.is_nullable,
                is_identity=row.is_identity,
                is_computed=row.is_computed,
                is_primary_key=bool(row.is_pk),
                default_value=row.default_value,
                computed_definition=row.computed_definition,
                collation=row.collation_name,
                description=row.description,
                ordinal_position=row.column_id,
            )
            columns.append(col)

        return columns

    async def _extract_indexes(
        self, cursor: Any, schema: str, table: str
    ) -> list[IndexInfo]:
        """Extract index information."""
        cursor.execute("""
            SELECT
                i.name as index_name,
                i.type_desc,
                i.is_unique,
                i.is_primary_key,
                i.filter_definition,
                i.fill_factor,
                i.is_disabled,
                STRING_AGG(CASE WHEN ic.is_included_column = 0 THEN c.name END, ',')
                    WITHIN GROUP (ORDER BY ic.key_ordinal) as key_columns,
                STRING_AGG(CASE WHEN ic.is_included_column = 1 THEN c.name END, ',')
                    WITHIN GROUP (ORDER BY ic.key_ordinal) as included_columns
            FROM sys.indexes i
            INNER JOIN sys.tables t ON i.object_id = t.object_id
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            WHERE s.name = ? AND t.name = ? AND i.name IS NOT NULL
            GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key,
                     i.filter_definition, i.fill_factor, i.is_disabled
            ORDER BY i.name
        """, schema, table)

        indexes = []
        for row in cursor.fetchall():
            idx = IndexInfo(
                name=row.index_name,
                index_type=self._map_index_type(row.type_desc),
                is_unique=row.is_unique,
                is_primary_key=row.is_primary_key,
                is_clustered=row.type_desc == "CLUSTERED",
                columns=row.key_columns.split(",") if row.key_columns else [],
                included_columns=row.included_columns.split(",") if row.included_columns else [],
                filter_definition=row.filter_definition,
                fill_factor=row.fill_factor if row.fill_factor > 0 else None,
                is_disabled=row.is_disabled,
            )
            indexes.append(idx)

        return indexes

    async def _extract_foreign_keys(
        self, cursor: Any, schema: str, table: str
    ) -> list[ForeignKeyInfo]:
        """Extract foreign key information."""
        cursor.execute("""
            SELECT
                fk.name as fk_name,
                STRING_AGG(c.name, ',') WITHIN GROUP (ORDER BY fkc.constraint_column_id) as columns,
                rs.name as ref_schema,
                rt.name as ref_table,
                STRING_AGG(rc.name, ',') WITHIN GROUP (ORDER BY fkc.constraint_column_id) as ref_columns,
                fk.delete_referential_action_desc as on_delete,
                fk.update_referential_action_desc as on_update,
                fk.is_disabled
            FROM sys.foreign_keys fk
            INNER JOIN sys.tables t ON fk.parent_object_id = t.object_id
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
            INNER JOIN sys.tables rt ON fk.referenced_object_id = rt.object_id
            INNER JOIN sys.schemas rs ON rt.schema_id = rs.schema_id
            INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
            WHERE s.name = ? AND t.name = ?
            GROUP BY fk.name, rs.name, rt.name, fk.delete_referential_action_desc,
                     fk.update_referential_action_desc, fk.is_disabled
            ORDER BY fk.name
        """, schema, table)

        fks = []
        for row in cursor.fetchall():
            fk = ForeignKeyInfo(
                name=row.fk_name,
                columns=row.columns.split(",") if row.columns else [],
                referenced_table=row.ref_table,
                referenced_schema=row.ref_schema,
                referenced_columns=row.ref_columns.split(",") if row.ref_columns else [],
                on_delete=row.on_delete.replace("_", " "),
                on_update=row.on_update.replace("_", " "),
                is_disabled=row.is_disabled,
            )
            fks.append(fk)

        return fks

    async def _extract_views(
        self,
        cursor: Any,
        schemas: list[str],
        include_definitions: bool,
    ) -> list[ViewInfo]:
        """Extract view information."""
        views = []
        schema_filter = ",".join(f"'{s}'" for s in schemas)

        cursor.execute(f"""
            SELECT
                v.name as view_name,
                s.name as schema_name,
                m.definition,
                ep.value as description,
                CASE WHEN i.object_id IS NOT NULL THEN 1 ELSE 0 END as is_indexed
            FROM sys.views v
            INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
            LEFT JOIN sys.sql_modules m ON v.object_id = m.object_id
            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = v.object_id
                AND ep.minor_id = 0
                AND ep.name = 'MS_Description'
            LEFT JOIN sys.indexes i ON v.object_id = i.object_id AND i.index_id = 1
            WHERE s.name IN ({schema_filter})
            ORDER BY s.name, v.name
        """)

        for row in cursor.fetchall():
            view = ViewInfo(
                name=row.view_name,
                schema=row.schema_name,
                definition=row.definition if include_definitions else "",
                is_indexed=bool(row.is_indexed),
                description=row.description,
            )

            # Get columns
            view.columns = await self._extract_view_columns(
                cursor, view.schema, view.name
            )

            views.append(view)

        return views

    async def _extract_view_columns(
        self, cursor: Any, schema: str, view: str
    ) -> list[ColumnInfo]:
        """Extract view column information."""
        cursor.execute("""
            SELECT
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                c.column_id
            FROM sys.columns c
            INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
            INNER JOIN sys.views v ON c.object_id = v.object_id
            INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
            WHERE s.name = ? AND v.name = ?
            ORDER BY c.column_id
        """, schema, view)

        return [
            ColumnInfo(
                name=row.column_name,
                data_type=row.data_type,
                data_type_normalized=self._normalize_type(row.data_type),
                max_length=row.max_length if row.max_length != -1 else None,
                precision=row.precision,
                scale=row.scale,
                is_nullable=row.is_nullable,
                ordinal_position=row.column_id,
            )
            for row in cursor.fetchall()
        ]

    async def _extract_procedures(
        self, cursor: Any, schemas: list[str]
    ) -> list[ProcedureInfo]:
        """Extract stored procedure information."""
        procedures = []
        schema_filter = ",".join(f"'{s}'" for s in schemas)

        cursor.execute(f"""
            SELECT
                p.name as proc_name,
                s.name as schema_name,
                m.definition,
                p.create_date,
                p.modify_date,
                ep.value as description,
                m.is_encrypted
            FROM sys.procedures p
            INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
            LEFT JOIN sys.sql_modules m ON p.object_id = m.object_id
            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = p.object_id
                AND ep.minor_id = 0
                AND ep.name = 'MS_Description'
            WHERE s.name IN ({schema_filter})
            ORDER BY s.name, p.name
        """)

        for row in cursor.fetchall():
            proc = ProcedureInfo(
                name=row.proc_name,
                schema=row.schema_name,
                definition=row.definition or "",
                created_at=row.create_date,
                modified_at=row.modify_date,
                description=row.description,
                is_encrypted=row.is_encrypted,
            )

            # Get parameters
            proc.parameters = await self._extract_parameters(
                cursor, proc.schema, proc.name
            )

            # Analyze definition
            if proc.definition:
                proc.has_cursors = "CURSOR" in proc.definition.upper()
                proc.has_dynamic_sql = "EXEC(" in proc.definition.upper() or "SP_EXECUTESQL" in proc.definition.upper()
                proc.estimated_lines = len(proc.definition.split("\n"))

            procedures.append(proc)

        return procedures

    async def _extract_parameters(
        self, cursor: Any, schema: str, proc: str
    ) -> list[ParameterInfo]:
        """Extract procedure parameters."""
        cursor.execute("""
            SELECT
                p.name as param_name,
                t.name as data_type,
                p.max_length,
                p.precision,
                p.scale,
                p.is_output,
                p.has_default_value,
                p.parameter_id
            FROM sys.parameters p
            INNER JOIN sys.types t ON p.user_type_id = t.user_type_id
            INNER JOIN sys.procedures pr ON p.object_id = pr.object_id
            INNER JOIN sys.schemas s ON pr.schema_id = s.schema_id
            WHERE s.name = ? AND pr.name = ? AND p.parameter_id > 0
            ORDER BY p.parameter_id
        """, schema, proc)

        return [
            ParameterInfo(
                name=row.param_name,
                data_type=row.data_type,
                max_length=row.max_length if row.max_length != -1 else None,
                precision=row.precision,
                scale=row.scale,
                is_output=row.is_output,
                has_default=row.has_default_value,
                ordinal_position=row.parameter_id,
            )
            for row in cursor.fetchall()
        ]

    async def _extract_functions(
        self, cursor: Any, schemas: list[str]
    ) -> list[FunctionInfo]:
        """Extract function information."""
        functions = []
        schema_filter = ",".join(f"'{s}'" for s in schemas)

        cursor.execute(f"""
            SELECT
                o.name as func_name,
                s.name as schema_name,
                m.definition,
                o.create_date,
                o.modify_date,
                o.type_desc,
                CASE WHEN o.type IN ('IF', 'TF') THEN 1 ELSE 0 END as is_table_valued,
                CASE WHEN o.type = 'FN' THEN 1 ELSE 0 END as is_scalar,
                ISNULL(sm.is_deterministic, 0) as is_deterministic
            FROM sys.objects o
            INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
            LEFT JOIN sys.sql_modules m ON o.object_id = m.object_id
            LEFT JOIN sys.sql_modules sm ON o.object_id = sm.object_id
            WHERE o.type IN ('FN', 'IF', 'TF')
            AND s.name IN ({schema_filter})
            ORDER BY s.name, o.name
        """)

        for row in cursor.fetchall():
            func = FunctionInfo(
                name=row.func_name,
                schema=row.schema_name,
                definition=row.definition or "",
                is_table_valued=row.is_table_valued,
                is_scalar=row.is_scalar,
                is_deterministic=row.is_deterministic,
                created_at=row.create_date,
                modified_at=row.modify_date,
            )

            # Get parameters
            func.parameters = await self._extract_function_parameters(
                cursor, func.schema, func.name
            )

            functions.append(func)

        return functions

    async def _extract_function_parameters(
        self, cursor: Any, schema: str, func: str
    ) -> list[ParameterInfo]:
        """Extract function parameters."""
        cursor.execute("""
            SELECT
                p.name as param_name,
                t.name as data_type,
                p.max_length,
                p.precision,
                p.scale,
                p.is_output,
                p.parameter_id
            FROM sys.parameters p
            INNER JOIN sys.types t ON p.user_type_id = t.user_type_id
            INNER JOIN sys.objects o ON p.object_id = o.object_id
            INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
            WHERE s.name = ? AND o.name = ? AND p.parameter_id > 0
            ORDER BY p.parameter_id
        """, schema, func)

        return [
            ParameterInfo(
                name=row.param_name,
                data_type=row.data_type,
                max_length=row.max_length if row.max_length != -1 else None,
                precision=row.precision,
                scale=row.scale,
                is_output=row.is_output,
                ordinal_position=row.parameter_id,
            )
            for row in cursor.fetchall()
        ]

    async def _extract_triggers(
        self, cursor: Any, schemas: list[str]
    ) -> list[TriggerInfo]:
        """Extract trigger information."""
        triggers = []
        schema_filter = ",".join(f"'{s}'" for s in schemas)

        cursor.execute(f"""
            SELECT
                tr.name as trigger_name,
                s.name as schema_name,
                t.name as table_name,
                ts.name as table_schema,
                m.definition,
                tr.is_disabled,
                tr.is_instead_of_trigger,
                te.type_desc as event_type,
                tr.create_date,
                tr.modify_date
            FROM sys.triggers tr
            INNER JOIN sys.tables t ON tr.parent_id = t.object_id
            INNER JOIN sys.schemas s ON tr.schema_id = s.schema_id
            INNER JOIN sys.schemas ts ON t.schema_id = ts.schema_id
            LEFT JOIN sys.sql_modules m ON tr.object_id = m.object_id
            LEFT JOIN sys.trigger_events te ON tr.object_id = te.object_id
            WHERE ts.name IN ({schema_filter})
            ORDER BY ts.name, t.name, tr.name
        """)

        for row in cursor.fetchall():
            events = []
            if row.event_type:
                if "INSERT" in row.event_type:
                    events.append(TriggerEvent.INSERT)
                if "UPDATE" in row.event_type:
                    events.append(TriggerEvent.UPDATE)
                if "DELETE" in row.event_type:
                    events.append(TriggerEvent.DELETE)

            trigger = TriggerInfo(
                name=row.trigger_name,
                schema=row.schema_name,
                table_name=row.table_name,
                table_schema=row.table_schema,
                definition=row.definition or "",
                timing=TriggerTiming.INSTEAD_OF if row.is_instead_of_trigger else TriggerTiming.AFTER,
                events=events,
                is_disabled=row.is_disabled,
                is_instead_of=row.is_instead_of_trigger,
                created_at=row.create_date,
                modified_at=row.modify_date,
            )
            triggers.append(trigger)

        return triggers

    def _normalize_type(self, sql_type: str) -> DataType:
        """Normalize SQL Server type to common type."""
        type_map = {
            "int": DataType.INT,
            "bigint": DataType.BIGINT,
            "smallint": DataType.SMALLINT,
            "tinyint": DataType.TINYINT,
            "decimal": DataType.DECIMAL,
            "numeric": DataType.NUMERIC,
            "float": DataType.FLOAT,
            "real": DataType.REAL,
            "money": DataType.MONEY,
            "bit": DataType.BIT,
            "char": DataType.CHAR,
            "varchar": DataType.VARCHAR,
            "nchar": DataType.NCHAR,
            "nvarchar": DataType.NVARCHAR,
            "text": DataType.TEXT,
            "ntext": DataType.NTEXT,
            "date": DataType.DATE,
            "time": DataType.TIME,
            "datetime": DataType.DATETIME,
            "datetime2": DataType.DATETIME2,
            "smalldatetime": DataType.SMALLDATETIME,
            "datetimeoffset": DataType.DATETIMEOFFSET,
            "timestamp": DataType.TIMESTAMP,
            "binary": DataType.BINARY,
            "varbinary": DataType.VARBINARY,
            "image": DataType.IMAGE,
            "uniqueidentifier": DataType.UNIQUEIDENTIFIER,
            "xml": DataType.XML,
            "geography": DataType.GEOGRAPHY,
            "geometry": DataType.GEOMETRY,
            "hierarchyid": DataType.HIERARCHYID,
            "sql_variant": DataType.SQL_VARIANT,
        }
        return type_map.get(sql_type.lower(), DataType.UNKNOWN)

    def _map_index_type(self, type_desc: str) -> IndexType:
        """Map SQL Server index type to common type."""
        type_map = {
            "CLUSTERED": IndexType.CLUSTERED,
            "NONCLUSTERED": IndexType.NONCLUSTERED,
            "CLUSTERED COLUMNSTORE": IndexType.COLUMNSTORE,
            "NONCLUSTERED COLUMNSTORE": IndexType.COLUMNSTORE,
            "SPATIAL": IndexType.SPATIAL,
            "XML": IndexType.NONCLUSTERED,
        }
        return type_map.get(type_desc, IndexType.NONCLUSTERED)


class PostgreSQLExtractor(SchemaExtractor):
    """Schema extractor for PostgreSQL databases."""

    async def test_connection(self) -> tuple[bool, str, Optional[str]]:
        """Test PostgreSQL connection."""
        try:
            import asyncpg

            conn = await asyncpg.connect(self.connection_string)
            version = await conn.fetchval("SELECT version()")
            await conn.close()

            return True, "Connection successful", version.split(",")[0] if version else None

        except Exception as e:
            return False, f"Connection failed: {str(e)}", None

    async def extract(
        self,
        include_definitions: bool = True,
        include_row_counts: bool = False,
        schemas: Optional[list[str]] = None,
    ) -> DatabaseSchema:
        """Extract PostgreSQL schema."""
        import asyncpg

        logger.info("starting_schema_extraction", db_type="postgresql")

        conn = await asyncpg.connect(self.connection_string)

        try:
            # Get database info
            row = await conn.fetchrow("""
                SELECT
                    current_database() as database_name,
                    inet_server_addr()::text as server_name,
                    version() as server_version
            """)

            db_schema = DatabaseSchema(
                database_name=row["database_name"],
                server_name=row["server_name"],
                server_version=row["server_version"].split(",")[0] if row["server_version"] else None,
            )

            # Get schemas
            if schemas:
                db_schema.schemas = schemas
            else:
                schema_rows = await conn.fetch("""
                    SELECT nspname FROM pg_namespace
                    WHERE nspname NOT LIKE 'pg_%'
                    AND nspname != 'information_schema'
                    ORDER BY nspname
                """)
                db_schema.schemas = [r["nspname"] for r in schema_rows]

            # Extract objects
            db_schema.tables = await self._extract_tables(
                conn, db_schema.schemas, include_row_counts
            )
            db_schema.views = await self._extract_views(
                conn, db_schema.schemas, include_definitions
            )
            if include_definitions:
                db_schema.procedures = await self._extract_procedures(conn, db_schema.schemas)
                db_schema.functions = await self._extract_functions(conn, db_schema.schemas)
                db_schema.triggers = await self._extract_triggers(conn, db_schema.schemas)

        finally:
            await conn.close()

        logger.info(
            "schema_extraction_complete",
            tables=len(db_schema.tables),
            views=len(db_schema.views),
            procedures=len(db_schema.procedures),
        )

        return db_schema

    async def _extract_tables(
        self,
        conn: Any,
        schemas: list[str],
        include_row_counts: bool,
    ) -> list[TableInfo]:
        """Extract table information."""
        tables = []

        # Get tables
        rows = await conn.fetch("""
            SELECT
                c.relname as table_name,
                n.nspname as schema_name,
                obj_description(c.oid) as description
            FROM pg_class c
            INNER JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relkind = 'r'
            AND n.nspname = ANY($1::text[])
            ORDER BY n.nspname, c.relname
        """, schemas)

        for row in rows:
            table = TableInfo(
                name=row["table_name"],
                schema=row["schema_name"],
                description=row["description"],
            )

            # Get columns
            table.columns = await self._extract_columns(
                conn, table.schema, table.name
            )

            # Get indexes
            table.indexes = await self._extract_indexes(
                conn, table.schema, table.name
            )

            # Get foreign keys
            table.foreign_keys = await self._extract_foreign_keys(
                conn, table.schema, table.name
            )

            # Get primary key columns
            table.primary_key_columns = [
                c.name for c in table.columns if c.is_primary_key
            ]

            # Get row count if requested
            if include_row_counts:
                try:
                    count = await conn.fetchval(
                        f'SELECT COUNT(*) FROM "{table.schema}"."{table.name}"'
                    )
                    table.row_count = count
                except Exception:
                    pass

            tables.append(table)

        return tables

    async def _extract_columns(
        self, conn: Any, schema: str, table: str
    ) -> list[ColumnInfo]:
        """Extract column information."""
        rows = await conn.fetch("""
            SELECT
                a.attname as column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
                a.attnotnull as not_null,
                pg_get_expr(d.adbin, d.adrelid) as default_value,
                col_description(c.oid, a.attnum) as description,
                a.attnum as ordinal_position,
                CASE WHEN pk.attname IS NOT NULL THEN true ELSE false END as is_pk,
                CASE WHEN a.attidentity != '' THEN true ELSE false END as is_identity
            FROM pg_attribute a
            INNER JOIN pg_class c ON a.attrelid = c.oid
            INNER JOIN pg_namespace n ON c.relnamespace = n.oid
            LEFT JOIN pg_attrdef d ON a.attrelid = d.adrelid AND a.attnum = d.adnum
            LEFT JOIN (
                SELECT a.attname
                FROM pg_index i
                INNER JOIN pg_attribute a ON i.indrelid = a.attrelid
                INNER JOIN pg_class c ON i.indrelid = c.oid
                INNER JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE i.indisprimary AND a.attnum = ANY(i.indkey)
                AND n.nspname = $1 AND c.relname = $2
            ) pk ON pk.attname = a.attname
            WHERE n.nspname = $1 AND c.relname = $2
            AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
        """, schema, table)

        return [
            ColumnInfo(
                name=row["column_name"],
                data_type=row["data_type"],
                data_type_normalized=self._normalize_type(row["data_type"]),
                is_nullable=not row["not_null"],
                is_primary_key=row["is_pk"],
                is_identity=row["is_identity"],
                default_value=row["default_value"],
                description=row["description"],
                ordinal_position=row["ordinal_position"],
            )
            for row in rows
        ]

    async def _extract_indexes(
        self, conn: Any, schema: str, table: str
    ) -> list[IndexInfo]:
        """Extract index information."""
        rows = await conn.fetch("""
            SELECT
                i.relname as index_name,
                am.amname as index_type,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                array_agg(a.attname ORDER BY k.n) as columns
            FROM pg_index ix
            INNER JOIN pg_class i ON ix.indexrelid = i.oid
            INNER JOIN pg_class t ON ix.indrelid = t.oid
            INNER JOIN pg_namespace n ON t.relnamespace = n.oid
            INNER JOIN pg_am am ON i.relam = am.oid
            CROSS JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS k(attnum, n)
            INNER JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
            WHERE n.nspname = $1 AND t.relname = $2
            GROUP BY i.relname, am.amname, ix.indisunique, ix.indisprimary
            ORDER BY i.relname
        """, schema, table)

        return [
            IndexInfo(
                name=row["index_name"],
                index_type=self._map_index_type(row["index_type"]),
                is_unique=row["is_unique"],
                is_primary_key=row["is_primary"],
                columns=row["columns"],
            )
            for row in rows
        ]

    async def _extract_foreign_keys(
        self, conn: Any, schema: str, table: str
    ) -> list[ForeignKeyInfo]:
        """Extract foreign key information."""
        rows = await conn.fetch("""
            SELECT
                c.conname as fk_name,
                array_agg(a.attname ORDER BY x.n) as columns,
                rn.nspname as ref_schema,
                rc.relname as ref_table,
                array_agg(ra.attname ORDER BY x.n) as ref_columns,
                c.confdeltype as on_delete,
                c.confupdtype as on_update
            FROM pg_constraint c
            INNER JOIN pg_class t ON c.conrelid = t.oid
            INNER JOIN pg_namespace n ON t.relnamespace = n.oid
            INNER JOIN pg_class rc ON c.confrelid = rc.oid
            INNER JOIN pg_namespace rn ON rc.relnamespace = rn.oid
            CROSS JOIN LATERAL unnest(c.conkey, c.confkey) WITH ORDINALITY AS x(col, rcol, n)
            INNER JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = x.col
            INNER JOIN pg_attribute ra ON ra.attrelid = rc.oid AND ra.attnum = x.rcol
            WHERE c.contype = 'f' AND n.nspname = $1 AND t.relname = $2
            GROUP BY c.conname, rn.nspname, rc.relname, c.confdeltype, c.confupdtype
            ORDER BY c.conname
        """, schema, table)

        action_map = {
            "a": "NO ACTION",
            "r": "RESTRICT",
            "c": "CASCADE",
            "n": "SET NULL",
            "d": "SET DEFAULT",
        }

        return [
            ForeignKeyInfo(
                name=row["fk_name"],
                columns=row["columns"],
                referenced_schema=row["ref_schema"],
                referenced_table=row["ref_table"],
                referenced_columns=row["ref_columns"],
                on_delete=action_map.get(row["on_delete"], "NO ACTION"),
                on_update=action_map.get(row["on_update"], "NO ACTION"),
            )
            for row in rows
        ]

    async def _extract_views(
        self,
        conn: Any,
        schemas: list[str],
        include_definitions: bool,
    ) -> list[ViewInfo]:
        """Extract view information."""
        rows = await conn.fetch("""
            SELECT
                c.relname as view_name,
                n.nspname as schema_name,
                pg_get_viewdef(c.oid) as definition,
                obj_description(c.oid) as description,
                c.relkind = 'm' as is_materialized
            FROM pg_class c
            INNER JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relkind IN ('v', 'm')
            AND n.nspname = ANY($1::text[])
            ORDER BY n.nspname, c.relname
        """, schemas)

        views = []
        for row in rows:
            view = ViewInfo(
                name=row["view_name"],
                schema=row["schema_name"],
                definition=row["definition"] if include_definitions else "",
                is_materialized=row["is_materialized"],
                description=row["description"],
            )
            views.append(view)

        return views

    async def _extract_procedures(
        self, conn: Any, schemas: list[str]
    ) -> list[ProcedureInfo]:
        """Extract stored procedure information."""
        rows = await conn.fetch("""
            SELECT
                p.proname as proc_name,
                n.nspname as schema_name,
                pg_get_functiondef(p.oid) as definition,
                obj_description(p.oid) as description
            FROM pg_proc p
            INNER JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE p.prokind = 'p'
            AND n.nspname = ANY($1::text[])
            ORDER BY n.nspname, p.proname
        """, schemas)

        return [
            ProcedureInfo(
                name=row["proc_name"],
                schema=row["schema_name"],
                definition=row["definition"] or "",
                description=row["description"],
            )
            for row in rows
        ]

    async def _extract_functions(
        self, conn: Any, schemas: list[str]
    ) -> list[FunctionInfo]:
        """Extract function information."""
        rows = await conn.fetch("""
            SELECT
                p.proname as func_name,
                n.nspname as schema_name,
                pg_get_functiondef(p.oid) as definition,
                pg_get_function_result(p.oid) as return_type,
                p.proretset as returns_set,
                obj_description(p.oid) as description
            FROM pg_proc p
            INNER JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE p.prokind = 'f'
            AND n.nspname = ANY($1::text[])
            ORDER BY n.nspname, p.proname
        """, schemas)

        return [
            FunctionInfo(
                name=row["func_name"],
                schema=row["schema_name"],
                definition=row["definition"] or "",
                return_type=row["return_type"],
                is_table_valued=row["returns_set"],
                is_scalar=not row["returns_set"],
                description=row["description"],
            )
            for row in rows
        ]

    async def _extract_triggers(
        self, conn: Any, schemas: list[str]
    ) -> list[TriggerInfo]:
        """Extract trigger information."""
        rows = await conn.fetch("""
            SELECT
                t.tgname as trigger_name,
                n.nspname as schema_name,
                c.relname as table_name,
                tn.nspname as table_schema,
                pg_get_triggerdef(t.oid) as definition,
                NOT t.tgenabled::boolean as is_disabled,
                t.tgtype as trigger_type
            FROM pg_trigger t
            INNER JOIN pg_class c ON t.tgrelid = c.oid
            INNER JOIN pg_namespace n ON c.relnamespace = n.oid
            INNER JOIN pg_namespace tn ON c.relnamespace = tn.oid
            WHERE NOT t.tgisinternal
            AND n.nspname = ANY($1::text[])
            ORDER BY n.nspname, c.relname, t.tgname
        """, schemas)

        triggers = []
        for row in rows:
            # Parse trigger type bitmap
            tgtype = row["trigger_type"]
            events = []
            if tgtype & 4:
                events.append(TriggerEvent.INSERT)
            if tgtype & 8:
                events.append(TriggerEvent.DELETE)
            if tgtype & 16:
                events.append(TriggerEvent.UPDATE)

            timing = TriggerTiming.BEFORE if tgtype & 2 else TriggerTiming.AFTER
            if tgtype & 64:
                timing = TriggerTiming.INSTEAD_OF

            trigger = TriggerInfo(
                name=row["trigger_name"],
                schema=row["schema_name"],
                table_name=row["table_name"],
                table_schema=row["table_schema"],
                definition=row["definition"] or "",
                timing=timing,
                events=events,
                is_disabled=row["is_disabled"],
                is_instead_of=timing == TriggerTiming.INSTEAD_OF,
            )
            triggers.append(trigger)

        return triggers

    def _normalize_type(self, pg_type: str) -> DataType:
        """Normalize PostgreSQL type to common type."""
        # Strip array notation
        base_type = pg_type.replace("[]", "").split("(")[0].lower()

        type_map = {
            "integer": DataType.INT,
            "int": DataType.INT,
            "int4": DataType.INT,
            "bigint": DataType.BIGINT,
            "int8": DataType.BIGINT,
            "smallint": DataType.SMALLINT,
            "int2": DataType.SMALLINT,
            "numeric": DataType.NUMERIC,
            "decimal": DataType.DECIMAL,
            "real": DataType.REAL,
            "float4": DataType.REAL,
            "double precision": DataType.FLOAT,
            "float8": DataType.FLOAT,
            "money": DataType.MONEY,
            "boolean": DataType.BOOLEAN,
            "bool": DataType.BOOLEAN,
            "character": DataType.CHAR,
            "char": DataType.CHAR,
            "character varying": DataType.VARCHAR,
            "varchar": DataType.VARCHAR,
            "text": DataType.TEXT,
            "date": DataType.DATE,
            "time": DataType.TIME,
            "timestamp": DataType.TIMESTAMP,
            "timestamp with time zone": DataType.DATETIMEOFFSET,
            "timestamp without time zone": DataType.DATETIME,
            "bytea": DataType.BYTEA,
            "uuid": DataType.UUID,
            "json": DataType.JSON,
            "jsonb": DataType.JSONB,
            "inet": DataType.INET,
            "cidr": DataType.CIDR,
            "macaddr": DataType.MACADDR,
            "serial": DataType.SERIAL,
            "bigserial": DataType.BIGSERIAL,
        }
        return type_map.get(base_type, DataType.UNKNOWN)

    def _map_index_type(self, pg_type: str) -> IndexType:
        """Map PostgreSQL index type to common type."""
        type_map = {
            "btree": IndexType.BTREE,
            "hash": IndexType.HASH,
            "gist": IndexType.GIST,
            "gin": IndexType.GIN,
            "brin": IndexType.BRIN,
        }
        return type_map.get(pg_type.lower(), IndexType.BTREE)
