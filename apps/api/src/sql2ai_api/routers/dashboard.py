"""Dashboard API router for SQL2.AI."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta

from sql2ai_api.dependencies.auth import get_current_user, get_tenant_id

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
    executed_at: str
    connection_name: str


class ConnectionHealth(BaseModel):
    """Connection health status."""
    id: str
    name: str
    status: str  # connected, error, connecting
    last_checked: str


class DashboardData(BaseModel):
    """Complete dashboard data."""
    stats: DashboardStats
    recent_queries: list[RecentQuery]
    connection_health: list[ConnectionHealth]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get dashboard statistics for the current tenant."""
    # TODO: Implement actual database queries
    # For now, return mock data
    return DashboardStats(
        total_connections=5,
        active_connections=3,
        queries_today=42,
        queries_this_week=287,
        ai_tokens_used=15420,
        avg_response_time_ms=145.3,
    )


@router.get("", response_model=DashboardData)
async def get_dashboard_data(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get complete dashboard data including stats, recent queries, and connection health."""
    stats = DashboardStats(
        total_connections=5,
        active_connections=3,
        queries_today=42,
        queries_this_week=287,
        ai_tokens_used=15420,
        avg_response_time_ms=145.3,
    )

    recent_queries = [
        RecentQuery(
            id="q1",
            name="Get Active Customers",
            sql="SELECT * FROM Customers WHERE IsActive = 1",
            execution_time_ms=45,
            executed_at=(datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            connection_name="Production SQL Server",
        ),
        RecentQuery(
            id="q2",
            name="Monthly Revenue",
            sql="SELECT SUM(Amount) FROM Orders WHERE OrderDate >= '2024-01-01'",
            execution_time_ms=230,
            executed_at=(datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            connection_name="Analytics PostgreSQL",
        ),
        RecentQuery(
            id="q3",
            name="User Sessions",
            sql="SELECT COUNT(*) FROM Sessions WHERE CreatedAt > NOW() - INTERVAL '24 hours'",
            execution_time_ms=12,
            executed_at=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
            connection_name="Development Database",
        ),
    ]

    connection_health = [
        ConnectionHealth(
            id="c1",
            name="Production SQL Server",
            status="connected",
            last_checked=datetime.utcnow().isoformat(),
        ),
        ConnectionHealth(
            id="c2",
            name="Analytics PostgreSQL",
            status="connected",
            last_checked=datetime.utcnow().isoformat(),
        ),
        ConnectionHealth(
            id="c3",
            name="Development Database",
            status="error",
            last_checked=(datetime.utcnow() - timedelta(minutes=2)).isoformat(),
        ),
    ]

    return DashboardData(
        stats=stats,
        recent_queries=recent_queries,
        connection_health=connection_health,
    )
