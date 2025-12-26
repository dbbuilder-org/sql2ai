"""Dashboard API router for SQL2.AI."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.db.session import get_db
from sql2ai_api.dependencies.auth import get_tenant_id
from sql2ai_api.services.dashboard import DashboardService

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_connections: int
    active_connections: int
    queries_today: int
    queries_this_week: int
    ai_tokens_used: int
    avg_response_time_ms: float


class RecentQuery(BaseModel):
    """Recent query for dashboard."""
    id: str
    name: str
    sql: str
    execution_time_ms: int
    executed_at: Optional[str] = None
    connection_name: str
    status: Optional[str] = None


class ConnectionHealth(BaseModel):
    """Connection health status."""
    id: str
    name: str
    status: str  # connected, error, idle, inactive, unknown
    last_checked: str
    error: Optional[str] = None


class QueryTrend(BaseModel):
    """Query trend data point."""
    date: str
    queries: int


class TopQuery(BaseModel):
    """Top executed query."""
    sql_hash: str
    sql: str
    execution_count: int
    avg_duration_ms: float


class DashboardData(BaseModel):
    """Complete dashboard data."""
    stats: DashboardStats
    recent_queries: list[RecentQuery]
    connection_health: list[ConnectionHealth]


class DashboardDataExtended(DashboardData):
    """Extended dashboard data with trends."""
    query_trends: list[QueryTrend]
    top_queries: list[TopQuery]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the current tenant."""
    service = DashboardService(db, tenant_id)
    stats = await service.get_stats()

    return DashboardStats(**stats)


@router.get("", response_model=DashboardData)
async def get_dashboard_data(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Get complete dashboard data including stats, recent queries, and connection health."""
    service = DashboardService(db, tenant_id)

    stats_data = await service.get_stats()
    recent_queries_data = await service.get_recent_queries(limit=10)
    connection_health_data = await service.get_connection_health()

    return DashboardData(
        stats=DashboardStats(**stats_data),
        recent_queries=[RecentQuery(**q) for q in recent_queries_data],
        connection_health=[ConnectionHealth(**c) for c in connection_health_data],
    )


@router.get("/extended", response_model=DashboardDataExtended)
async def get_dashboard_data_extended(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Get extended dashboard data including trends and top queries."""
    service = DashboardService(db, tenant_id)

    stats_data = await service.get_stats()
    recent_queries_data = await service.get_recent_queries(limit=10)
    connection_health_data = await service.get_connection_health()
    query_trends_data = await service.get_query_trends(days=7)
    top_queries_data = await service.get_top_queries(limit=5)

    return DashboardDataExtended(
        stats=DashboardStats(**stats_data),
        recent_queries=[RecentQuery(**q) for q in recent_queries_data],
        connection_health=[ConnectionHealth(**c) for c in connection_health_data],
        query_trends=[QueryTrend(**t) for t in query_trends_data],
        top_queries=[TopQuery(**q) for q in top_queries_data],
    )
