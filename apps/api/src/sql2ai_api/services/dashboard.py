"""Dashboard service with real database queries."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.models.connection import Connection
from sql2ai_api.models.query import Query, QueryExecution, QueryStatus
from sql2ai_api.models.tenant import Tenant


class DashboardService:
    """Service for dashboard statistics and data."""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def get_stats(self) -> dict:
        """Get dashboard statistics."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        # Connection counts
        total_connections = await self.db.scalar(
            select(func.count()).where(
                Connection.tenant_id == self.tenant_id,
                Connection.deleted_at.is_(None),
            )
        ) or 0

        active_connections = await self.db.scalar(
            select(func.count()).where(
                Connection.tenant_id == self.tenant_id,
                Connection.deleted_at.is_(None),
                Connection.is_active == True,
                Connection.last_error.is_(None),
            )
        ) or 0

        # Query counts
        queries_today = await self.db.scalar(
            select(func.count()).where(
                QueryExecution.tenant_id == self.tenant_id,
                QueryExecution.created_at >= today_start,
            )
        ) or 0

        queries_this_week = await self.db.scalar(
            select(func.count()).where(
                QueryExecution.tenant_id == self.tenant_id,
                QueryExecution.created_at >= week_start,
            )
        ) or 0

        # Average response time (last 100 queries)
        avg_query = select(func.avg(QueryExecution.duration_ms)).where(
            QueryExecution.tenant_id == self.tenant_id,
            QueryExecution.status == QueryStatus.COMPLETED,
            QueryExecution.duration_ms.isnot(None),
        ).limit(100)
        avg_response_time = await self.db.scalar(avg_query) or 0.0

        # AI token usage (from tenant record)
        tenant = await self.db.scalar(
            select(Tenant).where(Tenant.id == self.tenant_id)
        )
        ai_tokens_used = tenant.queries_today if tenant else 0

        return {
            "total_connections": total_connections,
            "active_connections": active_connections,
            "queries_today": queries_today,
            "queries_this_week": queries_this_week,
            "ai_tokens_used": ai_tokens_used,
            "avg_response_time_ms": round(avg_response_time, 2),
        }

    async def get_recent_queries(self, limit: int = 10) -> list[dict]:
        """Get recent query executions."""
        # Join with connections to get connection name
        query = (
            select(QueryExecution, Connection.name.label("connection_name"))
            .join(Connection, QueryExecution.connection_id == Connection.id)
            .where(QueryExecution.tenant_id == self.tenant_id)
            .order_by(desc(QueryExecution.created_at))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        recent = []
        for execution, connection_name in rows:
            # Try to get saved query name
            query_name = "Ad-hoc Query"
            if execution.query_id:
                saved_query = await self.db.scalar(
                    select(Query).where(Query.id == execution.query_id)
                )
                if saved_query:
                    query_name = saved_query.name

            recent.append({
                "id": execution.id,
                "name": query_name,
                "sql": execution.sql[:100] + "..." if len(execution.sql) > 100 else execution.sql,
                "execution_time_ms": int(execution.duration_ms or 0),
                "executed_at": execution.created_at.isoformat() if execution.created_at else None,
                "connection_name": connection_name,
                "status": execution.status.value,
            })

        return recent

    async def get_connection_health(self) -> list[dict]:
        """Get health status of all connections."""
        result = await self.db.execute(
            select(Connection).where(
                Connection.tenant_id == self.tenant_id,
                Connection.deleted_at.is_(None),
            ).order_by(Connection.name)
        )
        connections = result.scalars().all()

        health = []
        for conn in connections:
            if not conn.is_active:
                status = "inactive"
            elif conn.last_error:
                status = "error"
            elif conn.last_connected_at:
                # Check if connected recently (within 5 minutes)
                if datetime.utcnow() - conn.last_connected_at < timedelta(minutes=5):
                    status = "connected"
                else:
                    status = "idle"
            else:
                status = "unknown"

            health.append({
                "id": conn.id,
                "name": conn.name,
                "status": status,
                "last_checked": (
                    conn.last_connected_at.isoformat()
                    if conn.last_connected_at
                    else conn.updated_at.isoformat()
                ),
                "error": conn.last_error,
            })

        return health

    async def get_query_trends(self, days: int = 7) -> list[dict]:
        """Get query execution trends over time."""
        now = datetime.utcnow()
        trends = []

        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            count = await self.db.scalar(
                select(func.count()).where(
                    QueryExecution.tenant_id == self.tenant_id,
                    QueryExecution.created_at >= day_start,
                    QueryExecution.created_at < day_end,
                )
            ) or 0

            trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "queries": count,
            })

        return trends

    async def get_top_queries(self, limit: int = 5) -> list[dict]:
        """Get most frequently executed queries."""
        query = (
            select(
                QueryExecution.sql_hash,
                func.count().label("execution_count"),
                func.avg(QueryExecution.duration_ms).label("avg_duration"),
                func.max(QueryExecution.sql).label("sql"),
            )
            .where(QueryExecution.tenant_id == self.tenant_id)
            .group_by(QueryExecution.sql_hash)
            .order_by(desc("execution_count"))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "sql_hash": row.sql_hash,
                "sql": row.sql[:100] + "..." if len(row.sql) > 100 else row.sql,
                "execution_count": row.execution_count,
                "avg_duration_ms": round(row.avg_duration or 0, 2),
            }
            for row in rows
        ]
