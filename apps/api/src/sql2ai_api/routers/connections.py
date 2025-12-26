"""Database connection management endpoints."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.db.session import get_db
from sql2ai_api.models.connection import Connection, DatabaseType
from sql2ai_api.dependencies.auth import get_tenant_id, get_current_user
from sql2ai_api.services.connections import ConnectionService

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
    include_inactive: bool = False,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectionListResponse:
    """List all database connections for the current tenant."""
    service = ConnectionService(db, tenant_id, user_id)
    connections, total = await service.list_connections(
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )

    return ConnectionListResponse(
        connections=[ConnectionResponse.model_validate(c) for c in connections],
        total=total,
    )


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection: ConnectionCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Create a new database connection with encrypted credentials."""
    service = ConnectionService(db, tenant_id, user_id)

    db_connection = await service.create_connection(
        name=connection.name,
        db_type=connection.db_type,
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=connection.username,
        password=connection.password.get_secret_value(),
        description=connection.description,
        environment=connection.environment,
        tags=connection.tags,
        ssl_mode=connection.ssl_mode,
        trust_server_certificate=connection.trust_server_certificate,
        encrypt=connection.encrypt,
    )

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
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Get connection details by ID."""
    service = ConnectionService(db, tenant_id, user_id)
    connection = await service.get_connection(connection_id)

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
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectionResponse:
    """Update a database connection."""
    service = ConnectionService(db, tenant_id, user_id)

    # Prepare update data
    update_data = update.model_dump(exclude_unset=True, exclude={"password"})
    if update.password:
        update_data["password"] = update.password.get_secret_value()

    connection = await service.update_connection(connection_id, **update_data)

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    return ConnectionResponse.model_validate(connection)


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a database connection."""
    service = ConnectionService(db, tenant_id, user_id)
    success = await service.delete_connection(connection_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )


@router.get("/{connection_id}/databases", response_model=DatabaseListResponse)
async def list_databases(
    connection_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DatabaseListResponse:
    """List databases available on the connection."""
    service = ConnectionService(db, tenant_id, user_id)
    connection = await service.get_connection(connection_id)

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Get decrypted password and query databases
    password = await service.get_decrypted_password(connection)
    databases: List[str] = []

    if password:
        try:
            if connection.db_type == DatabaseType.POSTGRESQL:
                import psycopg2
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    user=connection.username,
                    password=password,
                    connect_timeout=10,
                )
                cursor = conn.cursor()
                cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
                databases = [row[0] for row in cursor.fetchall()]
                conn.close()
            elif connection.db_type == DatabaseType.SQLSERVER:
                import pyodbc
                conn_str = (
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={connection.host},{connection.port};"
                    f"DATABASE=master;"
                    f"UID={connection.username};"
                    f"PWD={password};"
                    f"TrustServerCertificate={'Yes' if connection.trust_server_certificate else 'No'};"
                )
                with pyodbc.connect(conn_str, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sys.databases ORDER BY name")
                    databases = [row[0] for row in cursor.fetchall()]
        except Exception:
            pass  # Return empty list on error

    return DatabaseListResponse(databases=databases)


@router.get("/{connection_id}/schemas", response_model=SchemaListResponse)
async def list_schemas(
    connection_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SchemaListResponse:
    """List schemas in the connection's database."""
    service = ConnectionService(db, tenant_id, user_id)
    connection = await service.get_connection(connection_id)

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    password = await service.get_decrypted_password(connection)
    schemas: List[str] = []

    if password:
        try:
            if connection.db_type == DatabaseType.POSTGRESQL:
                import psycopg2
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    user=connection.username,
                    password=password,
                    connect_timeout=10,
                )
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT schema_name FROM information_schema.schemata
                    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                    ORDER BY schema_name
                """)
                schemas = [row[0] for row in cursor.fetchall()]
                conn.close()
            elif connection.db_type == DatabaseType.SQLSERVER:
                import pyodbc
                conn_str = (
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={connection.host},{connection.port};"
                    f"DATABASE={connection.database};"
                    f"UID={connection.username};"
                    f"PWD={password};"
                    f"TrustServerCertificate={'Yes' if connection.trust_server_certificate else 'No'};"
                )
                with pyodbc.connect(conn_str, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sys.schemas ORDER BY name")
                    schemas = [row[0] for row in cursor.fetchall()]
        except Exception:
            pass  # Return empty list on error

    return SchemaListResponse(schemas=schemas)


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
async def test_saved_connection(
    connection_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectionTestResponse:
    """Test an existing saved connection."""
    service = ConnectionService(db, tenant_id, user_id)
    connection = await service.get_connection(connection_id)

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    result = await service.test_connection(connection)
    return ConnectionTestResponse(**result)
