"""Query management and execution endpoints."""

from typing import List, Optional
from datetime import datetime
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.db.session import get_db
from sql2ai_api.models.query import Query, QueryExecution, QueryStatus
from sql2ai_api.models.connection import Connection

router = APIRouter()


# Request/Response Models
class QueryGenerateRequest(BaseModel):
    """Generate SQL from natural language."""

    prompt: str = Field(..., min_length=1, max_length=2000)
    connection_id: str
    context: Optional[str] = None  # Additional schema/context


class QueryGenerateResponse(BaseModel):
    """Generated SQL response."""

    sql: str
    explanation: str
    confidence: float
    model: str
    suggestions: List[str] = []


class QueryOptimizeRequest(BaseModel):
    """Request to optimize a query."""

    sql: str = Field(..., min_length=1)
    connection_id: str
    include_execution_plan: bool = False


class QueryOptimizeResponse(BaseModel):
    """Optimization suggestions."""

    original_sql: str
    optimized_sql: Optional[str] = None
    suggestions: List[dict]
    execution_plan: Optional[dict] = None
    estimated_improvement: Optional[str] = None


class QueryExecuteRequest(BaseModel):
    """Execute a query."""

    sql: str = Field(..., min_length=1)
    connection_id: str
    parameters: Optional[dict] = None
    max_rows: int = Field(default=1000, le=10000)
    timeout_seconds: int = Field(default=30, le=300)


class QueryExecuteResponse(BaseModel):
    """Query execution result."""

    execution_id: str
    status: QueryStatus
    columns: List[str] = []
    rows: List[List] = []
    row_count: int = 0
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class QueryExplainRequest(BaseModel):
    """Explain what a query does."""

    sql: str = Field(..., min_length=1)


class QueryExplainResponse(BaseModel):
    """Query explanation."""

    sql: str
    explanation: str
    tables_used: List[str]
    operations: List[str]


class QueryValidateRequest(BaseModel):
    """Validate SQL syntax."""

    sql: str = Field(..., min_length=1)
    connection_id: str


class QueryValidateResponse(BaseModel):
    """Validation result."""

    valid: bool
    errors: List[dict] = []
    warnings: List[dict] = []


class SavedQueryCreate(BaseModel):
    """Create a saved query."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sql: str = Field(..., min_length=1)
    connection_id: str
    tags: dict = Field(default_factory=dict)
    is_shared: bool = False


class SavedQueryResponse(BaseModel):
    """Saved query response."""

    id: str
    name: str
    description: Optional[str]
    sql: str
    connection_id: str
    is_ai_generated: bool
    ai_prompt: Optional[str]
    is_shared: bool
    tags: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryHistoryResponse(BaseModel):
    """Query execution history."""

    executions: List[dict]
    total: int


# AI Generation Endpoints
@router.post("/generate", response_model=QueryGenerateResponse)
async def generate_query(
    request: QueryGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryGenerateResponse:
    """Generate SQL from natural language using AI."""
    # Verify connection exists
    result = await db.execute(
        select(Connection).where(
            Connection.id == request.connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Get schema context from connection
    # TODO: Call AI service to generate SQL
    # This is a placeholder implementation

    generated_sql = f"-- Generated from: {request.prompt}\nSELECT * FROM table_name LIMIT 10;"

    return QueryGenerateResponse(
        sql=generated_sql,
        explanation="This query selects all columns from table_name with a limit of 10 rows.",
        confidence=0.85,
        model="gpt-4",
        suggestions=[
            "Consider adding specific column names instead of SELECT *",
            "Add WHERE clause to filter results",
        ],
    )


@router.post("/optimize", response_model=QueryOptimizeResponse)
async def optimize_query(
    request: QueryOptimizeRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryOptimizeResponse:
    """Analyze and optimize a SQL query."""
    # Verify connection exists
    result = await db.execute(
        select(Connection).where(
            Connection.id == request.connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Implement actual optimization logic with AI
    # This is a placeholder implementation

    suggestions = [
        {
            "type": "index",
            "severity": "warning",
            "message": "Consider adding an index on frequently queried columns",
            "recommendation": "CREATE INDEX idx_column ON table_name(column_name);",
        },
    ]

    return QueryOptimizeResponse(
        original_sql=request.sql,
        optimized_sql=request.sql,  # Would be optimized version
        suggestions=suggestions,
        execution_plan=None,
        estimated_improvement="10-20% faster",
    )


@router.post("/execute", response_model=QueryExecuteResponse)
async def execute_query(
    request: QueryExecuteRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
) -> QueryExecuteResponse:
    """Execute a SQL query against a connection."""
    import time
    from uuid import uuid4

    # Verify connection exists
    result = await db.execute(
        select(Connection).where(
            Connection.id == request.connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Get tenant_id and user_id from auth context
    tenant_id = "00000000-0000-0000-0000-000000000000"
    user_id = "00000000-0000-0000-0000-000000000000"

    # Compute SQL hash for tracking
    sql_hash = hashlib.sha256(request.sql.encode()).hexdigest()[:64]

    # Create execution record
    execution = QueryExecution(
        tenant_id=tenant_id,
        connection_id=request.connection_id,
        sql=request.sql,
        sql_hash=sql_hash,
        status=QueryStatus.PENDING,
        executed_by=user_id,
        client_ip=http_request.client.host if http_request.client else None,
        client_user_agent=http_request.headers.get("user-agent"),
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # TODO: Actually execute the query against the target database
    # This would involve:
    # 1. Getting credentials from Vault
    # 2. Building connection to target DB
    # 3. Executing query with timeout
    # 4. Streaming results back

    start_time = time.time()

    # Placeholder response
    execution.status = QueryStatus.COMPLETED
    execution.started_at = datetime.utcnow()
    execution.completed_at = datetime.utcnow()
    execution.duration_ms = (time.time() - start_time) * 1000
    execution.result_row_count = 0
    execution.result_preview = {"columns": [], "sample_rows": []}

    await db.commit()

    return QueryExecuteResponse(
        execution_id=execution.id,
        status=execution.status,
        columns=[],
        rows=[],
        row_count=0,
        duration_ms=execution.duration_ms,
    )


@router.post("/explain", response_model=QueryExplainResponse)
async def explain_query(
    request: QueryExplainRequest,
) -> QueryExplainResponse:
    """Get a natural language explanation of what a SQL query does."""
    # TODO: Use AI to explain the query
    # This is a placeholder implementation

    return QueryExplainResponse(
        sql=request.sql,
        explanation="This query performs a data selection operation.",
        tables_used=["table_name"],
        operations=["SELECT", "FROM"],
    )


@router.post("/validate", response_model=QueryValidateResponse)
async def validate_query(
    request: QueryValidateRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryValidateResponse:
    """Validate SQL syntax and semantics."""
    # Verify connection exists
    result = await db.execute(
        select(Connection).where(
            Connection.id == request.connection_id,
            Connection.deleted_at.is_(None),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # TODO: Implement actual validation
    # This would involve parsing the SQL and checking syntax

    return QueryValidateResponse(
        valid=True,
        errors=[],
        warnings=[],
    )


# Saved Queries CRUD
@router.get("/saved", response_model=List[SavedQueryResponse])
async def list_saved_queries(
    connection_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[SavedQueryResponse]:
    """List saved queries."""
    query = select(Query)

    if connection_id:
        query = query.where(Query.connection_id == connection_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    queries = result.scalars().all()

    return [SavedQueryResponse.model_validate(q) for q in queries]


@router.post("/saved", response_model=SavedQueryResponse, status_code=status.HTTP_201_CREATED)
async def save_query(
    query: SavedQueryCreate,
    db: AsyncSession = Depends(get_db),
) -> SavedQueryResponse:
    """Save a query for later use."""
    # TODO: Get tenant_id and user_id from auth context
    tenant_id = "00000000-0000-0000-0000-000000000000"
    user_id = "00000000-0000-0000-0000-000000000000"

    saved_query = Query(
        tenant_id=tenant_id,
        name=query.name,
        description=query.description,
        sql=query.sql,
        connection_id=query.connection_id,
        created_by=user_id,
        is_shared=query.is_shared,
        tags=query.tags,
    )

    db.add(saved_query)
    await db.commit()
    await db.refresh(saved_query)

    return SavedQueryResponse.model_validate(saved_query)


@router.get("/saved/{query_id}", response_model=SavedQueryResponse)
async def get_saved_query(
    query_id: str,
    db: AsyncSession = Depends(get_db),
) -> SavedQueryResponse:
    """Get a saved query by ID."""
    result = await db.execute(
        select(Query).where(Query.id == query_id)
    )
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    return SavedQueryResponse.model_validate(query)


@router.delete("/saved/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_query(
    query_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a saved query."""
    result = await db.execute(
        select(Query).where(Query.id == query_id)
    )
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    await db.delete(query)
    await db.commit()


# Execution History
@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    connection_id: Optional[str] = None,
    status_filter: Optional[QueryStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> QueryHistoryResponse:
    """Get query execution history."""
    query = select(QueryExecution).order_by(QueryExecution.created_at.desc())

    if connection_id:
        query = query.where(QueryExecution.connection_id == connection_id)

    if status_filter:
        query = query.where(QueryExecution.status == status_filter)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    executions = result.scalars().all()

    # Get total count
    count_query = select(QueryExecution)
    if connection_id:
        count_query = count_query.where(QueryExecution.connection_id == connection_id)
    if status_filter:
        count_query = count_query.where(QueryExecution.status == status_filter)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return QueryHistoryResponse(
        executions=[
            {
                "id": e.id,
                "sql": e.sql[:200] + "..." if len(e.sql) > 200 else e.sql,
                "status": e.status.value,
                "duration_ms": e.duration_ms,
                "row_count": e.result_row_count,
                "created_at": e.created_at.isoformat(),
                "error": e.error_message,
            }
            for e in executions
        ],
        total=total,
    )


@router.get("/history/{execution_id}")
async def get_execution_details(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get details of a specific query execution."""
    result = await db.execute(
        select(QueryExecution).where(QueryExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    return {
        "id": execution.id,
        "sql": execution.sql,
        "status": execution.status.value,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "duration_ms": execution.duration_ms,
        "rows_affected": execution.rows_affected,
        "result_preview": execution.result_preview,
        "error_message": execution.error_message,
        "error_code": execution.error_code,
        "ai_explanation": execution.ai_explanation,
        "ai_optimization_suggestions": execution.ai_optimization_suggestions,
    }
