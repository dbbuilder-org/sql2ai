"""API endpoints for SQL Migrator."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Add migrator library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-migrator/src")
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class GenerateCodeRequest(BaseModel):
    """Request to generate code from schema."""

    language: str = Field(..., description="Language: csharp, typescript, zod")
    namespace: Optional[str] = Field("DataModels", description="Namespace for C#")
    include_repository: bool = Field(True, description="Include repository classes")


class GeneratedCodeResponse(BaseModel):
    """Response with generated code."""

    language: str
    file_name: str
    content: str
    source_tables: list[str]


class CreateMigrationRequest(BaseModel):
    """Request to create a migration from diff."""

    name: str = Field(..., description="Migration name")
    version: str = Field(..., description="Version string (e.g., 1.0.0)")
    description: Optional[str] = Field(None, description="Migration description")


class MigrationStepResponse(BaseModel):
    """Response for a migration step."""

    order: int
    description: str
    forward_sql: str
    rollback_sql: Optional[str]


class BreakingChangeResponse(BaseModel):
    """Response for a breaking change."""

    type: str
    severity: str
    object_name: str
    description: str
    data_loss_risk: bool
    remediation: Optional[str]


class MigrationResponse(BaseModel):
    """Response for a migration."""

    id: str
    name: str
    version: str
    description: str
    dialect: str
    status: str
    checksum: str
    steps: list[MigrationStepResponse]
    breaking_changes: list[BreakingChangeResponse]
    has_breaking_changes: bool
    has_data_loss_risk: bool
    requires_downtime: bool


class ExecuteMigrationRequest(BaseModel):
    """Request to execute a migration."""

    dry_run: bool = Field(False, description="If true, validate without executing")


class ExecutionResultResponse(BaseModel):
    """Response for migration execution."""

    migration_id: str
    success: bool
    status: str
    steps_executed: int
    steps_total: int
    duration_ms: int
    error_message: Optional[str]
    error_step: Optional[int]


# Endpoints

@router.post(
    "/connections/{connection_id}/generate",
    response_model=list[GeneratedCodeResponse],
)
async def generate_code(
    connection_id: str,
    request: GenerateCodeRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_EXPORT])
    ),
):
    """Generate code from database schema.

    Generates Dapper models (C#), TypeScript types, or Zod schemas
    from the current database schema.
    """
    from codegen import DapperGenerator, TypeScriptGenerator, ZodSchemaGenerator
    from models import CodeLanguage

    # Get schema for the connection
    # In production, this would fetch from the schema service
    schema = await _get_schema_for_connection(connection_id, user.tenant_id)

    if request.language.lower() == "csharp":
        generator = DapperGenerator(
            namespace=request.namespace or "DataModels",
            include_repository=request.include_repository,
        )
    elif request.language.lower() == "typescript":
        generator = TypeScriptGenerator()
    elif request.language.lower() == "zod":
        generator = ZodSchemaGenerator()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.language}. Use csharp, typescript, or zod."
        )

    generated = generator.generate(schema)

    return [
        GeneratedCodeResponse(
            language=code.language.value,
            file_name=code.file_name,
            content=code.content,
            source_tables=code.source_tables,
        )
        for code in generated
    ]


@router.post(
    "/connections/{connection_id}/compare/{target_connection_id}/migration",
    response_model=MigrationResponse,
)
async def create_migration_from_comparison(
    connection_id: str,
    target_connection_id: str,
    request: CreateMigrationRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_WRITE])
    ),
):
    """Create a migration from comparing two database schemas.

    Compares the source and target database schemas and generates
    a migration with forward and rollback scripts.
    """
    from generator import MigrationGenerator
    from differ import SchemaDiffer

    # Get schemas for both connections
    source_schema = await _get_schema_for_connection(connection_id, user.tenant_id)
    target_schema = await _get_schema_for_connection(target_connection_id, user.tenant_id)

    # Compare schemas
    differ = SchemaDiffer()
    diff = differ.compare(source_schema, target_schema)

    if not diff.has_changes:
        raise HTTPException(
            status_code=400,
            detail="No differences found between schemas"
        )

    # Generate migration
    generator = MigrationGenerator(dialect="sqlserver")
    migration = generator.generate_from_diff(
        diff=diff,
        name=request.name,
        version=request.version,
        description=request.description,
    )

    return _migration_to_response(migration)


@router.get("/migrations/{migration_id}")
async def get_migration(
    migration_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_READ])
    ),
):
    """Get a migration by ID."""
    # In production, fetch from database
    raise HTTPException(status_code=404, detail="Migration not found")


@router.get("/migrations/{migration_id}/script")
async def get_migration_script(
    migration_id: str,
    script_type: str = Query("forward", description="forward or rollback"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_READ])
    ),
):
    """Get the SQL script for a migration."""
    # In production, fetch migration and return script
    raise HTTPException(status_code=404, detail="Migration not found")


@router.post(
    "/connections/{connection_id}/migrations/{migration_id}/execute",
    response_model=ExecutionResultResponse,
)
async def execute_migration(
    connection_id: str,
    migration_id: str,
    request: ExecuteMigrationRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_EXECUTE])
    ),
):
    """Execute a migration against a database.

    Applies the migration to the target database. Use dry_run=true
    to validate without making changes.
    """
    from executor import MigrationExecutor

    # In production:
    # 1. Fetch migration by ID
    # 2. Get database connection
    # 3. Execute migration

    raise HTTPException(status_code=501, detail="Not implemented - requires live database connection")


@router.post(
    "/connections/{connection_id}/migrations/{migration_id}/rollback",
    response_model=ExecutionResultResponse,
)
async def rollback_migration(
    connection_id: str,
    migration_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_EXECUTE])
    ),
):
    """Rollback a previously applied migration."""
    raise HTTPException(status_code=501, detail="Not implemented - requires live database connection")


@router.get("/connections/{connection_id}/migrations")
async def list_migrations(
    connection_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_READ])
    ),
):
    """List migrations for a connection."""
    # In production, query migrations table
    return []


@router.get("/connections/{connection_id}/migrations/pending")
async def list_pending_migrations(
    connection_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_READ])
    ),
):
    """List pending migrations that haven't been applied yet."""
    return []


# Helper functions

async def _get_schema_for_connection(connection_id: str, tenant_id: str):
    """Get schema for a connection. Placeholder for production implementation."""
    # In production, this would:
    # 1. Get connection details from database
    # 2. Extract schema using schema-engine
    # 3. Return DatabaseSchema object

    # For now, return a mock schema
    import models as schema_models

    return schema_models.DatabaseSchema(
        database_name="MockDB",
        tables=[
            schema_models.TableInfo(
                name="Users",
                schema="dbo",
                columns=[
                    schema_models.ColumnInfo(
                        name="Id",
                        data_type="int",
                        data_type_normalized=schema_models.DataType.INT,
                        is_primary_key=True,
                        is_identity=True,
                        ordinal_position=1,
                    ),
                    schema_models.ColumnInfo(
                        name="Email",
                        data_type="nvarchar(255)",
                        data_type_normalized=schema_models.DataType.NVARCHAR,
                        max_length=255,
                        is_nullable=False,
                        ordinal_position=2,
                    ),
                ],
                primary_key_columns=["Id"],
            ),
        ],
    )


def _migration_to_response(migration) -> MigrationResponse:
    """Convert Migration to response model."""
    return MigrationResponse(
        id=migration.id,
        name=migration.name,
        version=migration.version,
        description=migration.description,
        dialect=migration.dialect,
        status=migration.status.value,
        checksum=migration.checksum,
        steps=[
            MigrationStepResponse(
                order=s.order,
                description=s.description,
                forward_sql=s.forward_sql,
                rollback_sql=s.rollback_sql,
            )
            for s in migration.steps
        ],
        breaking_changes=[
            BreakingChangeResponse(
                type=bc.change_type,
                severity=bc.severity.value,
                object_name=bc.object_name,
                description=bc.description,
                data_loss_risk=bc.data_loss_risk,
                remediation=bc.remediation,
            )
            for bc in migration.breaking_changes
        ],
        has_breaking_changes=migration.has_breaking_changes,
        has_data_loss_risk=migration.has_data_loss_risk,
        requires_downtime=migration.requires_downtime,
    )
