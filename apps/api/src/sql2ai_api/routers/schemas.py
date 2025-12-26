"""Schema analysis endpoints with authentication and encryption."""

from typing import Optional, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.db.session import get_db
from sql2ai_api.dependencies.auth import CurrentUser, Permission, require_permission
from sql2ai_api.models.connection import Connection
from sql2ai_api.services.schema import SchemaService

logger = structlog.get_logger()

router = APIRouter()


# Response models
class SchemaResponse(BaseModel):
    """Database schema response."""

    database_name: str
    server_name: Optional[str] = None
    server_version: Optional[str] = None
    tables: List[dict]
    views: List[dict]
    procedures: List[dict]
    functions: List[dict]
    triggers: List[dict]
    summary: dict


class AnalysisResponse(BaseModel):
    """Schema analysis response."""

    table_purposes: dict
    column_purposes: dict
    entity_types: dict
    quality_issues: dict
    pii_columns: List[dict]
    index_suggestions: List[dict]
    normalization_issues: List[dict]
    procedure_complexity: dict


class SnapshotResponse(BaseModel):
    """Schema snapshot response."""

    id: str
    connection_id: str
    tenant_id: str
    created_at: str
    created_by: Optional[str] = None
    label: Optional[str] = None
    is_baseline: bool
    content_hash: Optional[str] = None


class DiffResponse(BaseModel):
    """Schema diff response."""

    source_snapshot_id: str
    target_snapshot_id: str
    differences: List[dict]
    summary: dict


class SchemaExtractRequest(BaseModel):
    """Request to extract schema."""

    include_definitions: bool = True
    include_row_counts: bool = False
    schemas: Optional[List[str]] = None


class CompareRequest(BaseModel):
    """Request to compare schemas."""

    source_connection_id: str
    target_connection_id: str


class SnapshotRequest(BaseModel):
    """Request to create snapshot."""

    label: Optional[str] = None
    is_baseline: bool = False


# Service instance
_schema_service = SchemaService()


async def get_connection_with_access(
    connection_id: str,
    user: CurrentUser,
    db: AsyncSession,
) -> Connection:
    """Get a connection and verify user has access."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.tenant_id == user.tenant_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    return connection


@router.get("/", response_model=List[SnapshotResponse])
async def list_snapshots(
    user: CurrentUser,
    connection_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[SnapshotResponse]:
    """List schema snapshots for the tenant.

    Requires: schema:read permission
    """
    if not user.has_permission(Permission.SCHEMA_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: schema:read",
        )

    # TODO: Implement snapshot storage and retrieval
    # For now, return empty list
    logger.info(
        "listing_snapshots",
        user_id=user.id,
        tenant_id=user.tenant_id,
        connection_id=connection_id,
    )

    return []


@router.post("/{connection_id}/extract", response_model=SchemaResponse)
async def extract_schema(
    connection_id: str,
    request: SchemaExtractRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SchemaResponse:
    """Extract schema from a database connection.

    Requires: schema:read permission
    """
    if not user.has_permission(Permission.SCHEMA_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: schema:read",
        )

    connection = await get_connection_with_access(connection_id, user, db)

    try:
        schema = await _schema_service.extract_schema(
            connection=connection,
            user_id=user.id,
            tenant_id=user.tenant_id,
            db=db,
            include_definitions=request.include_definitions,
            include_row_counts=request.include_row_counts,
            schemas=request.schemas,
        )

        return SchemaResponse(**schema)

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "schema_extraction_failed",
            connection_id=connection_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema extraction failed: {str(e)}",
        )


@router.post("/{connection_id}/analyze", response_model=AnalysisResponse)
async def analyze_schema(
    connection_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """Analyze a database schema for documentation and optimization suggestions.

    Requires: schema:read permission
    """
    if not user.has_permission(Permission.SCHEMA_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: schema:read",
        )

    connection = await get_connection_with_access(connection_id, user, db)

    try:
        analysis = await _schema_service.analyze_schema(
            connection=connection,
            user_id=user.id,
            tenant_id=user.tenant_id,
            db=db,
        )

        return AnalysisResponse(**analysis)

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "schema_analysis_failed",
            connection_id=connection_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema analysis failed: {str(e)}",
        )


@router.post("/{connection_id}/snapshot", response_model=SnapshotResponse)
async def create_snapshot(
    connection_id: str,
    request: SnapshotRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> SnapshotResponse:
    """Create a schema snapshot for versioning.

    Requires: schema:export permission
    """
    if not user.has_permission(Permission.SCHEMA_EXPORT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: schema:export",
        )

    connection = await get_connection_with_access(connection_id, user, db)

    try:
        snapshot = await _schema_service.create_snapshot(
            connection=connection,
            user_id=user.id,
            tenant_id=user.tenant_id,
            db=db,
            label=request.label,
            is_baseline=request.is_baseline,
        )

        # TODO: Store snapshot in database

        return SnapshotResponse(
            id=snapshot["id"],
            connection_id=snapshot["connection_id"],
            tenant_id=snapshot["tenant_id"],
            created_at=snapshot["created_at"],
            created_by=snapshot["created_by"],
            label=snapshot["label"],
            is_baseline=snapshot["is_baseline"],
            content_hash=snapshot["content_hash"],
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "snapshot_creation_failed",
            connection_id=connection_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Snapshot creation failed: {str(e)}",
        )


@router.post("/compare", response_model=DiffResponse)
async def compare_schemas(
    request: CompareRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> DiffResponse:
    """Compare schemas between two connections.

    Requires: schema:read permission
    """
    if not user.has_permission(Permission.SCHEMA_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: schema:read",
        )

    # Get both connections
    source_conn = await get_connection_with_access(
        request.source_connection_id, user, db
    )
    target_conn = await get_connection_with_access(
        request.target_connection_id, user, db
    )

    try:
        # Extract both schemas
        source_schema = await _schema_service.extract_schema(
            connection=source_conn,
            user_id=user.id,
            tenant_id=user.tenant_id,
            db=db,
        )

        target_schema = await _schema_service.extract_schema(
            connection=target_conn,
            user_id=user.id,
            tenant_id=user.tenant_id,
            db=db,
        )

        # Compare
        diff = await _schema_service.compare_schemas(
            {"id": request.source_connection_id, "schema": source_schema},
            {"id": request.target_connection_id, "schema": target_schema},
        )

        return DiffResponse(**diff)

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "schema_comparison_failed",
            source_id=request.source_connection_id,
            target_id=request.target_connection_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema comparison failed: {str(e)}",
        )


@router.get("/{connection_id}/test")
async def test_connection(
    connection_id: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Test a database connection.

    Requires: connections:read permission
    """
    if not user.has_permission(Permission.CONNECTIONS_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission: connections:read",
        )

    connection = await get_connection_with_access(connection_id, user, db)

    try:
        result = await _schema_service.test_connection(
            connection=connection,
            user_id=user.id,
            tenant_id=user.tenant_id,
        )

        return result

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "connection_test_failed",
            connection_id=connection_id,
            error=str(e),
        )
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
        }
