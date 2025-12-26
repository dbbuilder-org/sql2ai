"""API endpoints for SQL Writer."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Add writer library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-writer/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class GenerateTableRequest(BaseModel):
    """Request to generate a table."""

    name: str = Field(..., description="Table name")
    schema_name: str = Field("dbo", description="Schema name")
    columns: list[dict] = Field(..., description="Column definitions")
    primary_key_columns: list[str] = Field(default_factory=list)
    description: Optional[str] = None


class GenerateProcedureRequest(BaseModel):
    """Request to generate a stored procedure."""

    name: str = Field(..., description="Procedure name")
    schema_name: str = Field("dbo", description="Schema name")
    parameters: list[dict] = Field(default_factory=list)
    body: str = Field(..., description="Procedure body")
    description: Optional[str] = None
    use_transaction: bool = True
    include_error_handling: bool = True


class GenerateCRUDRequest(BaseModel):
    """Request to generate CRUD procedures."""

    table_name: str = Field(..., description="Table name")
    schema_name: str = Field("dbo", description="Schema name")
    columns: list[dict] = Field(..., description="Table column definitions")
    include_create: bool = True
    include_read: bool = True
    include_update: bool = True
    include_delete: bool = True
    include_list: bool = True
    include_search: bool = False
    soft_delete: bool = False
    include_audit: bool = False


class GenerateFromPromptRequest(BaseModel):
    """Request for AI-powered generation."""

    prompt: str = Field(..., description="Natural language description")
    object_type: str = Field(..., description="table, view, stored_procedure, function, trigger")
    context_tables: list[str] = Field(default_factory=list)
    include_error_handling: bool = True
    include_audit_logging: bool = False


class GenerationResponse(BaseModel):
    """Response for code generation."""

    object_type: str
    object_name: str
    sql_script: str
    rollback_script: Optional[str]
    warnings: list[str] = []
    security_notes: list[str] = []
    performance_notes: list[str] = []


class CRUDGenerationResponse(BaseModel):
    """Response for CRUD generation."""

    table_name: str
    procedures: list[GenerationResponse]
    combined_script: str
    rollback_script: str


# Endpoints

@router.post("/table", response_model=GenerationResponse)
async def generate_table(
    request: GenerateTableRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """Generate CREATE TABLE statement.

    Generates a complete CREATE TABLE statement with proper
    constraints, indexes, and formatting.
    """
    from writer import SQLWriter
    from models import TableDefinition, ColumnDefinition

    writer = SQLWriter()

    # Convert request to model
    columns = [
        ColumnDefinition(
            name=col["name"],
            data_type=col["data_type"],
            nullable=col.get("nullable", True),
            is_primary_key=col["name"] in request.primary_key_columns,
            is_identity=col.get("is_identity", False),
            max_length=col.get("max_length"),
        )
        for col in request.columns
    ]

    table = TableDefinition(
        name=request.name,
        schema_name=request.schema_name,
        columns=columns,
        primary_key_columns=request.primary_key_columns,
        description=request.description,
    )

    result = writer.generate_table(table)

    return GenerationResponse(
        object_type=result.object_type.value,
        object_name=result.object_name,
        sql_script=result.sql_script,
        rollback_script=result.rollback_script,
        warnings=result.warnings,
        security_notes=result.security_notes,
    )


@router.post("/procedure", response_model=GenerationResponse)
async def generate_procedure(
    request: GenerateProcedureRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """Generate stored procedure.

    Generates a stored procedure with proper error handling,
    transaction management, and formatting.
    """
    from writer import SQLWriter
    from models import StoredProcedureDefinition, ParameterDefinition

    writer = SQLWriter()

    parameters = [
        ParameterDefinition(
            name=p["name"],
            data_type=p["data_type"],
            direction=p.get("direction", "IN"),
            default_value=p.get("default_value"),
        )
        for p in request.parameters
    ]

    sp = StoredProcedureDefinition(
        name=request.name,
        schema_name=request.schema_name,
        parameters=parameters,
        body=request.body,
        description=request.description,
        uses_transaction=request.use_transaction,
    )

    result = writer.generate_stored_procedure(sp)

    return GenerationResponse(
        object_type=result.object_type.value,
        object_name=result.object_name,
        sql_script=result.sql_script,
        rollback_script=result.rollback_script,
        warnings=result.warnings,
        security_notes=result.security_notes,
    )


@router.post("/crud", response_model=CRUDGenerationResponse)
async def generate_crud(
    request: GenerateCRUDRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """Generate CRUD stored procedures.

    Generates Create, Read, Update, Delete, and List procedures
    for a table with proper error handling.
    """
    from writer import SQLWriter
    from models import ColumnDefinition, CRUDGenerationRequest

    writer = SQLWriter()

    columns = [
        ColumnDefinition(
            name=col["name"],
            data_type=col["data_type"],
            nullable=col.get("nullable", True),
            is_primary_key=col.get("is_primary_key", False),
            is_identity=col.get("is_identity", False),
            max_length=col.get("max_length"),
        )
        for col in request.columns
    ]

    crud_request = CRUDGenerationRequest(
        table_name=request.table_name,
        schema_name=request.schema_name,
        include_create=request.include_create,
        include_read=request.include_read,
        include_update=request.include_update,
        include_delete=request.include_delete,
        include_list=request.include_list,
        include_search=request.include_search,
        soft_delete=request.soft_delete,
    )

    result = writer.generate_crud_procedures(columns, crud_request)

    return CRUDGenerationResponse(
        table_name=result.table_name,
        procedures=[
            GenerationResponse(
                object_type=p.object_type.value,
                object_name=p.object_name,
                sql_script=p.sql_script,
                rollback_script=p.rollback_script,
                warnings=p.warnings,
                security_notes=p.security_notes,
            )
            for p in result.procedures
        ],
        combined_script=result.combined_script,
        rollback_script=result.rollback_script,
    )


@router.post("/trigger/audit", response_model=GenerationResponse)
async def generate_audit_trigger(
    table_name: str,
    audit_table_name: str,
    schema_name: str = "dbo",
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """Generate an audit trigger for a table.

    Creates a trigger that logs all INSERT, UPDATE, and DELETE
    operations to an audit table.
    """
    from writer import SQLWriter

    writer = SQLWriter()
    result = writer.generate_audit_trigger(
        table_name=table_name,
        audit_table_name=audit_table_name,
        schema_name=schema_name,
    )

    return GenerationResponse(
        object_type=result.object_type.value,
        object_name=result.object_name,
        sql_script=result.sql_script,
        rollback_script=result.rollback_script,
        warnings=result.warnings,
    )


@router.post("/from-prompt", response_model=GenerationResponse)
async def generate_from_prompt(
    request: GenerateFromPromptRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """Generate SQL code from natural language prompt.

    Uses AI to generate DDL or stored procedures from
    a natural language description.
    """
    from writer import SQLWriter
    from models import ObjectType, GenerationRequest

    # Map string to ObjectType
    type_map = {
        "table": ObjectType.TABLE,
        "view": ObjectType.VIEW,
        "stored_procedure": ObjectType.STORED_PROCEDURE,
        "function": ObjectType.FUNCTION,
        "trigger": ObjectType.TRIGGER,
    }

    object_type = type_map.get(request.object_type.lower())
    if not object_type:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid object_type. Must be one of: {list(type_map.keys())}"
        )

    # AI completion would be configured in production
    async def mock_ai_completion(system: str, user: str) -> str:
        raise HTTPException(
            status_code=501,
            detail="AI generation requires LLM configuration"
        )

    writer = SQLWriter(ai_completion=mock_ai_completion)

    gen_request = GenerationRequest(
        prompt=request.prompt,
        object_type=object_type,
        context_tables=request.context_tables,
        include_error_handling=request.include_error_handling,
        include_audit_logging=request.include_audit_logging,
    )

    try:
        result = await writer.generate_from_prompt(gen_request)
        return GenerationResponse(
            object_type=result.object_type.value,
            object_name=result.object_name,
            sql_script=result.sql_script,
            rollback_script=result.rollback_script,
            warnings=result.warnings,
            security_notes=result.security_notes,
            performance_notes=result.performance_notes,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_GENERATE])
    ),
):
    """List available code generation templates.

    Returns available templates for common patterns like
    fund transfers, upserts, and pagination.
    """
    return {
        "templates": [
            {
                "id": "funds_transfer",
                "name": "Funds Transfer Procedure",
                "description": "Stored procedure for transferring funds with proper locking and audit",
            },
            {
                "id": "upsert",
                "name": "Upsert (MERGE) Procedure",
                "description": "MERGE-based upsert procedure for efficient inserts/updates",
            },
            {
                "id": "pagination",
                "name": "Pagination Function",
                "description": "Inline table-valued function for efficient pagination",
            },
            {
                "id": "audit_trigger",
                "name": "Audit Trigger",
                "description": "Trigger for tracking all changes to a table",
            },
            {
                "id": "soft_delete_trigger",
                "name": "Soft Delete Trigger",
                "description": "Trigger that archives deleted records instead of removing them",
            },
        ]
    }
