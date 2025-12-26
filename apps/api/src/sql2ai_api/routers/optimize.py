"""API endpoints for SQL Optimize."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Add optimize library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-optimize/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class AnalyzeRequest(BaseModel):
    """Request for performance analysis."""

    include_query_store: bool = Field(True, description="Include Query Store analysis")
    include_index_analysis: bool = Field(True, description="Include index analysis")
    include_wait_stats: bool = Field(True, description="Include wait statistics")


class QueryAnalysisRequest(BaseModel):
    """Request to analyze a specific query."""

    query_text: str = Field(..., description="SQL query to analyze")


class IssueResponse(BaseModel):
    """Response for a performance issue."""

    id: str
    category: str
    severity: str
    title: str
    description: str
    affected_object: str
    impact: str
    metrics: dict


class RecommendationResponse(BaseModel):
    """Response for a recommendation."""

    id: str
    issue_id: str
    title: str
    description: str
    fix_script: Optional[str]
    complexity: str
    estimated_improvement: Optional[str]
    risk_level: str


class MissingIndexResponse(BaseModel):
    """Response for a missing index."""

    table_name: str
    equality_columns: list[str]
    inequality_columns: list[str]
    included_columns: list[str]
    improvement_score: float
    suggested_index_name: str
    create_statement: str


class OptimizationReportResponse(BaseModel):
    """Response for optimization report."""

    connection_id: str
    database_name: str
    health_score: float
    duration_ms: int
    summary: dict
    issues: list[IssueResponse]
    recommendations: list[RecommendationResponse]
    missing_indexes: list[MissingIndexResponse]


class HealthCheckResponse(BaseModel):
    """Response for quick health check."""

    connection_id: str
    health_score: float
    status: str
    checks: dict
    timestamp: str


# Placeholder for optimizer instance
_optimizer = None


def get_optimizer():
    """Get the optimizer instance."""
    global _optimizer
    if _optimizer is None:
        raise HTTPException(
            status_code=503,
            detail="Optimizer not initialized"
        )
    return _optimizer


# Endpoints

@router.post(
    "/connections/{connection_id}/analyze",
    response_model=OptimizationReportResponse,
)
async def analyze_database(
    connection_id: str,
    request: AnalyzeRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_OPTIMIZE])
    ),
):
    """Run comprehensive performance analysis.

    Analyzes Query Store data, index usage, wait statistics,
    and generates optimization recommendations.
    """
    from optimizer import SQLOptimizer
    from models import OptimizationReport

    # In production, get actual connection
    async def mock_provider(conn_id):
        raise HTTPException(status_code=501, detail="Requires live database connection")

    optimizer = SQLOptimizer(
        connection_provider=mock_provider,
        include_query_store=request.include_query_store,
        include_index_analysis=request.include_index_analysis,
        include_wait_stats=request.include_wait_stats,
    )

    try:
        report = await optimizer.analyze(connection_id)
        return _report_to_response(report)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/connections/{connection_id}/health",
    response_model=HealthCheckResponse,
)
async def quick_health_check(
    connection_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get quick health check without full analysis.

    Returns key health indicators like blocking, CPU pressure,
    and memory pressure.
    """
    # In production, use actual optimizer
    return HealthCheckResponse(
        connection_id=connection_id,
        health_score=-1,
        status="unavailable",
        checks={},
        timestamp="",
    )


@router.post("/connections/{connection_id}/analyze-query")
async def analyze_query(
    connection_id: str,
    request: QueryAnalysisRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_OPTIMIZE])
    ),
):
    """Analyze a specific query for optimization opportunities.

    Checks for common anti-patterns and suggests improvements.
    """
    from optimizer import SQLOptimizer

    async def mock_provider(conn_id):
        return None

    optimizer = SQLOptimizer(connection_provider=mock_provider)

    try:
        result = await optimizer.analyze_query(connection_id, request.query_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}/missing-indexes")
async def get_missing_indexes(
    connection_id: str,
    limit: int = Query(20, ge=1, le=100),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get missing index recommendations.

    Returns SQL Server's missing index suggestions ordered by
    potential improvement.
    """
    # In production, query actual database
    return []


@router.get("/connections/{connection_id}/fragmented-indexes")
async def get_fragmented_indexes(
    connection_id: str,
    threshold: float = Query(30, ge=0, le=100, description="Fragmentation threshold"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get fragmented indexes above threshold.

    Returns indexes with fragmentation above the specified threshold.
    """
    # In production, query actual database
    return []


@router.get("/connections/{connection_id}/wait-stats")
async def get_wait_statistics(
    connection_id: str,
    limit: int = Query(20, ge=1, le=100),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get current wait statistics.

    Returns top wait types excluding benign system waits.
    """
    # In production, query actual database
    return []


@router.get("/connections/{connection_id}/top-queries")
async def get_top_queries(
    connection_id: str,
    metric: str = Query("duration", description="Sort by: duration, cpu, reads, writes"),
    limit: int = Query(20, ge=1, le=100),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.QUERY_EXECUTE])
    ),
):
    """Get top resource-consuming queries from Query Store.

    Returns queries sorted by the specified metric.
    """
    valid_metrics = ["duration", "cpu", "reads", "writes"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {valid_metrics}"
        )

    # In production, query Query Store
    return []


# Helper functions

def _report_to_response(report) -> OptimizationReportResponse:
    """Convert OptimizationReport to response model."""
    return OptimizationReportResponse(
        connection_id=report.connection_id,
        database_name=report.database_name,
        health_score=report.health_score,
        duration_ms=report.duration_ms,
        summary={
            "critical_issues": report.critical_issues,
            "high_issues": report.high_issues,
            "total_issues": report.total_issues,
            "recommendations": len(report.recommendations),
        },
        issues=[
            IssueResponse(
                id=i.id,
                category=i.category.value,
                severity=i.severity.value,
                title=i.title,
                description=i.description,
                affected_object=i.affected_object,
                impact=i.impact,
                metrics=i.metrics,
            )
            for i in report.issues
        ],
        recommendations=[
            RecommendationResponse(
                id=r.id,
                issue_id=r.issue_id,
                title=r.title,
                description=r.description,
                fix_script=r.fix_script,
                complexity=r.complexity.value,
                estimated_improvement=r.estimated_improvement,
                risk_level=r.risk_level,
            )
            for r in report.recommendations
        ],
        missing_indexes=[
            MissingIndexResponse(
                table_name=m.table_name,
                equality_columns=m.equality_columns,
                inequality_columns=m.inequality_columns,
                included_columns=m.included_columns,
                improvement_score=m.improvement_score,
                suggested_index_name=m.suggested_index_name,
                create_statement=m.create_statement,
            )
            for m in report.missing_indexes
        ],
    )
