"""Database connection management endpoints."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.db.session import get_db
from sql2ai_api.models.connection import Connection, DatabaseType

router = APIRouter()


# Request/Response Models
class ConnectionBase(BaseModel):
    """Base connection fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    db_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., gt=0, le=65535)
    database: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=1, max_length=255)
    environment: str = "development"
    tags: dict = Field(default_factory=dict)


class ConnectionCreate(ConnectionBase):
    """Create a new database connection."""

    password: SecretStr

    # SQL Server specific
    trust_server_certificate: bool = False
    encrypt: bool = True

    # SSL
    ssl_mode: Optional[str] = None


class ConnectionUpdate(BaseModel):
    """Update connection fields."""

    name: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    environment: Optional[str] = None
    tags: Optional[dict] = None
    is_active: Optional[bool] = None


class ConnectionResponse(ConnectionBase):
    """Connection response model."""

    id: str
    is_active: bool
    last_connected_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConnectionListResponse(BaseModel):
    """List of connections response."""

    connections: List[ConnectionResponse]
    total: int


class ConnectionTestRequest(BaseModel):
    """Test connection parameters."""

    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: SecretStr
    ssl_mode: Optional[str] = None
    trust_server_certificate: bool = False
    encrypt: bool = True


class ConnectionTestResponse(BaseModel):
    """Connection test result."""

    success: bool
    message: str
    server_version: Optional[str] = None
    latency_ms: Optional[float] = None


class DatabaseListResponse(BaseModel):
    """List of databases on a connection."""

    databases: List[str]


class SchemaListResponse(BaseModel):
    """List of schemas in a database."""

    schemas: List[str]


# Endpoints
@router.get("/", response_model=ConnectionListResponse)
async def list_connections(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> ConnectionListResponse:
    """List all database connections for the current tenant."""
    # TODO: Filter by tenant_id from auth context
    result = await db.execute(
        select(Connection)
        .where(Connection.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
    )
    connections = result.scalars().all()

    count_result = await db.execute(
        select(Connection).where(Connection.deleted_at.is_(None))
    )
    total = len(count_result.scalars().all())

    return ConnectionListResponse(
        connections=[ConnectionResponse.model_validate(c) for c in connections],
        total=total,
    )


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Create a new database connection."""
    # TODO: Get tenant_id and user_id from auth context
    tenant_id = "00000000-0000-0000-0000-000000000000"  # Placeholder
    user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder

    # TODO: Store password securely in Vault
    password_secret_id = None  # Would be Vault secret ID

    db_connection = Connection(
        tenant_id=tenant_id,
        name=connection.name,
        description=connection.description,
        db_type=connection.db_type,
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=connection.username,
        password_secret_id=password_secret_id,
        trust_server_certificate=connection.trust_server_certificate,
        encrypt=connection.encrypt,
        ssl_mode=connection.ssl_mode,
        environment=connection.environment,
        tags=connection.tags,
        created_by=user_id,
        updated_by=user_id,
    )

    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)

    return ConnectionResponse.model_validate(db_connection)


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    connection: ConnectionTestRequest,
) -> ConnectionTestResponse:
    """Test database connection without saving."""
    import time

    start_time = time.time()

    try:
        # Build connection string based on database type
        if connection.db_type == DatabaseType.SQLSERVER:
            import pyodbc

            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={connection.host},{connection.port};"
                f"DATABASE={connection.database};"
                f"UID={connection.username};"
                f"PWD={connection.password.get_secret_value()};"
                f"TrustServerCertificate={'Yes' if connection.trust_server_certificate else 'No'};"
                f"Encrypt={'Yes' if connection.encrypt else 'No'};"
            )

            with pyodbc.connect(conn_str, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]

            latency_ms = (time.time() - start_time) * 1000

            return ConnectionTestResponse(
                success=True,
                message="Connection successful",
                server_version=version.split("\n")[0] if version else None,
                latency_ms=round(latency_ms, 2),
            )

        elif connection.db_type == DatabaseType.POSTGRESQL:
            import asyncpg

            # For async driver, we need to handle differently
            # Using sync approach for test
            import psycopg2

            conn = psycopg2.connect(
                host=connection.host,
                port=connection.port,
                database=connection.database,
                user=connection.username,
                password=connection.password.get_secret_value(),
                connect_timeout=10,
            )

            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            conn.close()

            latency_ms = (time.time() - start_time) * 1000

            return ConnectionTestResponse(
                success=True,
                message="Connection successful",
                server_version=version.split(",")[0] if version else None,
                latency_ms=round(latency_ms, 2),
            )

        else:
            return ConnectionTestResponse(
                success=False,
                message=f"Database type {connection.db_type.value} not yet supported",
            )

    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Get connection details by ID."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    return ConnectionResponse.model_validate(connection)


@router.patch("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: str,
    update: ConnectionUpdate,
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Update a database connection."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Update fields
    update_data = update.model_dump(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        setattr(connection, field, value)

    # Handle password update separately (would store in Vault)
    if update.password:
        # TODO: Store new password in Vault
        pass

    await db.commit()
    await db.refresh(connection)

    return ConnectionResponse.model_validate(connection)


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a database connection."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Soft delete
    connection.deleted_at = datetime.utcnow()
    await db.commit()


@router.get("/{connection_id}/databases", response_model=DatabaseListResponse)
async def list_databases(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> DatabaseListResponse:
    """List databases available on the connection."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Actually query the database for available databases
    # This would require getting the password from Vault and connecting
    databases: List[str] = []

    return DatabaseListResponse(databases=databases)


@router.get("/{connection_id}/schemas", response_model=SchemaListResponse)
async def list_schemas(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
) -> SchemaListResponse:
    """List schemas in the connection's database."""
    result = await db.execute(
        select(Connection).where(
            Connection.id == connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Actually query the database for schemas
    schemas: List[str] = []

    return SchemaListResponse(schemas=schemas)
