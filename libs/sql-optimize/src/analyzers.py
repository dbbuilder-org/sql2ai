"""Performance analyzers for SQL databases."""

import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

import structlog

from models import (
    FixComplexity,
    IndexAnalysis,
    IssueCategory,
    IssueSeverity,
    MissingIndex,
    OptimizationReport,
    PerformanceIssue,
    QueryAnalysis,
    Recommendation,
    WaitStatistics,
)

logger = structlog.get_logger()


class BaseAnalyzer(ABC):
    """Base class for performance analyzers."""

    @abstractmethod
    async def analyze(self, connection: Any) -> list[PerformanceIssue]:
        """Run analysis and return issues found."""
        pass


class QueryStoreAnalyzer(BaseAnalyzer):
    """Analyze Query Store data for performance issues."""

    def __init__(self, top_n: int = 20, min_execution_count: int = 10):
        self.top_n = top_n
        self.min_execution_count = min_execution_count

    async def analyze(self, connection: Any) -> list[PerformanceIssue]:
        """Analyze Query Store for regressed and expensive queries."""
        issues = []

        # Get top resource-consuming queries
        top_queries = await self._get_top_queries(connection)

        for query in top_queries:
            # Check for plan regression
            if query.has_plan_regression:
                issues.append(PerformanceIssue(
                    id=f"QS_REG_{query.query_hash[:8]}",
                    category=IssueCategory.QUERY,
                    severity=IssueSeverity.HIGH,
                    title=f"Query Plan Regression Detected",
                    description=f"Query {query.query_hash[:16]} has experienced plan regression",
                    affected_object=query.query_hash,
                    impact=f"Performance degraded, avg duration: {query.avg_duration_ms:.0f}ms",
                    metrics={
                        "avg_duration_ms": query.avg_duration_ms,
                        "execution_count": query.execution_count,
                        "plan_count": query.plan_count,
                    },
                ))

            # Check for high CPU queries
            if query.avg_cpu_time_ms > 5000:
                issues.append(PerformanceIssue(
                    id=f"QS_CPU_{query.query_hash[:8]}",
                    category=IssueCategory.CPU,
                    severity=IssueSeverity.MEDIUM if query.avg_cpu_time_ms < 10000 else IssueSeverity.HIGH,
                    title="High CPU Query",
                    description=f"Query consuming excessive CPU time",
                    affected_object=query.query_hash,
                    impact=f"Avg CPU time: {query.avg_cpu_time_ms:.0f}ms per execution",
                    metrics={
                        "avg_cpu_time_ms": query.avg_cpu_time_ms,
                        "execution_count": query.execution_count,
                    },
                ))

            # Check for high I/O queries
            if query.avg_logical_reads > 100000:
                issues.append(PerformanceIssue(
                    id=f"QS_IO_{query.query_hash[:8]}",
                    category=IssueCategory.IO,
                    severity=IssueSeverity.MEDIUM,
                    title="High I/O Query",
                    description=f"Query with excessive logical reads",
                    affected_object=query.query_hash,
                    impact=f"Avg logical reads: {query.avg_logical_reads:,}",
                    metrics={
                        "avg_logical_reads": query.avg_logical_reads,
                        "avg_physical_reads": query.avg_physical_reads,
                    },
                ))

        return issues

    async def _get_top_queries(self, connection: Any) -> list[QueryAnalysis]:
        """Get top queries from Query Store."""
        query = f"""
        SELECT TOP {self.top_n}
            CONVERT(VARCHAR(32), qs.query_hash, 2) AS query_hash,
            SUBSTRING(qt.query_sql_text, 1, 4000) AS query_text,
            qs.count_executions,
            qs.avg_duration / 1000.0 AS avg_duration_ms,
            qs.max_duration / 1000.0 AS max_duration_ms,
            qs.avg_cpu_time / 1000.0 AS avg_cpu_time_ms,
            qs.avg_logical_io_reads AS avg_logical_reads,
            qs.avg_physical_io_reads AS avg_physical_reads,
            qs.avg_logical_io_writes AS avg_writes,
            qs.last_execution_time,
            (SELECT COUNT(DISTINCT plan_id) FROM sys.query_store_plan qp
             WHERE qp.query_id = q.query_id) AS plan_count
        FROM sys.query_store_query q
        JOIN sys.query_store_query_text qt ON q.query_text_id = qt.query_text_id
        JOIN sys.query_store_runtime_stats qs ON q.query_id = qs.query_id
        WHERE qs.count_executions >= {self.min_execution_count}
        ORDER BY qs.avg_duration * qs.count_executions DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()

            return [
                QueryAnalysis(
                    query_hash=row[0],
                    query_text=row[1] or "",
                    execution_count=row[2],
                    avg_duration_ms=row[3],
                    max_duration_ms=row[4],
                    avg_cpu_time_ms=row[5],
                    avg_logical_reads=row[6],
                    avg_physical_reads=row[7],
                    avg_writes=row[8],
                    last_execution=row[9],
                    plan_count=row[10],
                    has_plan_regression=row[10] > 2,
                )
                for row in rows
            ]
        except Exception as e:
            logger.warning("query_store_analysis_failed", error=str(e))
            return []

    async def get_regressed_queries(self, connection: Any, days: int = 7) -> list[QueryAnalysis]:
        """Get queries that have regressed recently."""
        query = f"""
        WITH RecentStats AS (
            SELECT
                q.query_id,
                AVG(rs.avg_duration) AS recent_avg_duration
            FROM sys.query_store_runtime_stats rs
            JOIN sys.query_store_plan p ON rs.plan_id = p.plan_id
            JOIN sys.query_store_query q ON p.query_id = q.query_id
            WHERE rs.last_execution_time > DATEADD(day, -{days}, GETUTCDATE())
            GROUP BY q.query_id
        ),
        OldStats AS (
            SELECT
                q.query_id,
                AVG(rs.avg_duration) AS old_avg_duration
            FROM sys.query_store_runtime_stats rs
            JOIN sys.query_store_plan p ON rs.plan_id = p.plan_id
            JOIN sys.query_store_query q ON p.query_id = q.query_id
            WHERE rs.last_execution_time BETWEEN DATEADD(day, -{days*2}, GETUTCDATE())
                  AND DATEADD(day, -{days}, GETUTCDATE())
            GROUP BY q.query_id
        )
        SELECT TOP 10
            q.query_id,
            CONVERT(VARCHAR(32), q.query_hash, 2) AS query_hash,
            r.recent_avg_duration / 1000.0 AS recent_ms,
            o.old_avg_duration / 1000.0 AS old_ms,
            (r.recent_avg_duration - o.old_avg_duration) / o.old_avg_duration * 100 AS regression_pct
        FROM RecentStats r
        JOIN OldStats o ON r.query_id = o.query_id
        JOIN sys.query_store_query q ON r.query_id = q.query_id
        WHERE r.recent_avg_duration > o.old_avg_duration * 1.5
        ORDER BY regression_pct DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            return [
                QueryAnalysis(
                    query_hash=row[1],
                    query_text="",
                    execution_count=0,
                    avg_duration_ms=row[2],
                    max_duration_ms=0,
                    avg_cpu_time_ms=0,
                    avg_logical_reads=0,
                    avg_physical_reads=0,
                    avg_writes=0,
                    has_plan_regression=True,
                )
                for row in rows
            ]
        except Exception:
            return []


class IndexAnalyzer(BaseAnalyzer):
    """Analyze index usage and find optimization opportunities."""

    async def analyze(self, connection: Any) -> list[PerformanceIssue]:
        """Analyze indexes for issues."""
        issues = []

        # Analyze existing indexes
        indexes = await self._get_index_usage(connection)

        for idx in indexes:
            # Unused indexes
            if idx.is_unused and idx.size_mb > 10:
                issues.append(PerformanceIssue(
                    id=f"IDX_UNUSED_{idx.index_name[:20]}",
                    category=IssueCategory.INDEX,
                    severity=IssueSeverity.MEDIUM,
                    title="Unused Index",
                    description=f"Index {idx.index_name} has no reads but consumes space and slows writes",
                    affected_object=f"{idx.table_name}.{idx.index_name}",
                    impact=f"Wasted space: {idx.size_mb:.1f}MB, Updates: {idx.user_updates:,}",
                    metrics={
                        "size_mb": idx.size_mb,
                        "user_updates": idx.user_updates,
                    },
                ))

            # Duplicate indexes
            if idx.is_duplicate:
                issues.append(PerformanceIssue(
                    id=f"IDX_DUP_{idx.index_name[:20]}",
                    category=IssueCategory.INDEX,
                    severity=IssueSeverity.LOW,
                    title="Duplicate Index",
                    description=f"Index {idx.index_name} duplicates {idx.duplicate_of}",
                    affected_object=f"{idx.table_name}.{idx.index_name}",
                    impact=f"Redundant space: {idx.size_mb:.1f}MB",
                    metrics={"duplicate_of": idx.duplicate_of},
                ))

            # Highly fragmented indexes
            if idx.fragmentation_percent > 30 and idx.size_mb > 100:
                issues.append(PerformanceIssue(
                    id=f"IDX_FRAG_{idx.index_name[:20]}",
                    category=IssueCategory.INDEX,
                    severity=IssueSeverity.MEDIUM if idx.fragmentation_percent < 70 else IssueSeverity.HIGH,
                    title="Fragmented Index",
                    description=f"Index {idx.index_name} is {idx.fragmentation_percent:.0f}% fragmented",
                    affected_object=f"{idx.table_name}.{idx.index_name}",
                    impact=f"Degraded query performance, {idx.size_mb:.1f}MB affected",
                    metrics={
                        "fragmentation_percent": idx.fragmentation_percent,
                        "size_mb": idx.size_mb,
                    },
                ))

        # Check for missing indexes
        missing = await self._get_missing_indexes(connection)
        for mi in missing:
            if mi.improvement_score > 1000:
                issues.append(PerformanceIssue(
                    id=f"IDX_MISS_{mi.table_name.split('.')[-1][:10]}",
                    category=IssueCategory.INDEX,
                    severity=IssueSeverity.MEDIUM if mi.improvement_score < 10000 else IssueSeverity.HIGH,
                    title="Missing Index",
                    description=f"Missing index on {mi.table_name}",
                    affected_object=mi.table_name,
                    impact=f"Could improve performance by {mi.avg_user_impact:.0f}%",
                    metrics={
                        "improvement_score": mi.improvement_score,
                        "user_seeks": mi.user_seeks,
                        "avg_user_impact": mi.avg_user_impact,
                    },
                ))

        return issues

    async def _get_index_usage(self, connection: Any) -> list[IndexAnalysis]:
        """Get index usage statistics."""
        query = """
        SELECT
            OBJECT_SCHEMA_NAME(i.object_id) + '.' + OBJECT_NAME(i.object_id) AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            STUFF((
                SELECT ', ' + c.name
                FROM sys.index_columns ic
                JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 0
                ORDER BY ic.key_ordinal
                FOR XML PATH('')
            ), 1, 2, '') AS key_columns,
            (SELECT SUM(ps.used_page_count) * 8.0 / 1024
             FROM sys.dm_db_partition_stats ps
             WHERE ps.object_id = i.object_id AND ps.index_id = i.index_id) AS size_mb,
            ISNULL(ius.user_seeks, 0) AS user_seeks,
            ISNULL(ius.user_scans, 0) AS user_scans,
            ISNULL(ius.user_lookups, 0) AS user_lookups,
            ISNULL(ius.user_updates, 0) AS user_updates
        FROM sys.indexes i
        LEFT JOIN sys.dm_db_index_usage_stats ius
            ON i.object_id = ius.object_id AND i.index_id = ius.index_id
            AND ius.database_id = DB_ID()
        WHERE i.type > 0
        AND OBJECT_SCHEMA_NAME(i.object_id) NOT IN ('sys', 'INFORMATION_SCHEMA')
        ORDER BY size_mb DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()

            results = []
            for row in rows:
                columns = row[3].split(", ") if row[3] else []
                reads = (row[5] or 0) + (row[6] or 0) + (row[7] or 0)
                updates = row[8] or 0

                idx = IndexAnalysis(
                    table_name=row[0],
                    index_name=row[1] or "",
                    index_type=row[2],
                    columns=columns,
                    size_mb=row[4] or 0,
                    user_seeks=row[5] or 0,
                    user_scans=row[6] or 0,
                    user_lookups=row[7] or 0,
                    user_updates=row[8] or 0,
                    is_unused=(reads == 0 and updates > 100),
                )
                results.append(idx)

            return results
        except Exception as e:
            logger.warning("index_analysis_failed", error=str(e))
            return []

    async def _get_missing_indexes(self, connection: Any) -> list[MissingIndex]:
        """Get missing index recommendations from SQL Server."""
        query = """
        SELECT TOP 20
            OBJECT_SCHEMA_NAME(mid.object_id) + '.' + OBJECT_NAME(mid.object_id) AS table_name,
            mid.equality_columns,
            mid.inequality_columns,
            mid.included_columns,
            migs.unique_compiles,
            migs.user_seeks,
            migs.user_scans,
            migs.avg_total_user_cost,
            migs.avg_user_impact
        FROM sys.dm_db_missing_index_details mid
        JOIN sys.dm_db_missing_index_groups mig ON mid.index_handle = mig.index_handle
        JOIN sys.dm_db_missing_index_group_stats migs ON mig.index_group_handle = migs.group_handle
        WHERE mid.database_id = DB_ID()
        ORDER BY migs.avg_user_impact * migs.avg_total_user_cost * (migs.user_seeks + migs.user_scans) DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()

            return [
                MissingIndex(
                    table_name=row[0],
                    equality_columns=row[1].split(", ") if row[1] else [],
                    inequality_columns=row[2].split(", ") if row[2] else [],
                    included_columns=row[3].split(", ") if row[3] else [],
                    unique_compiles=row[4],
                    user_seeks=row[5],
                    user_scans=row[6],
                    avg_total_user_cost=row[7],
                    avg_user_impact=row[8],
                )
                for row in rows
            ]
        except Exception as e:
            logger.warning("missing_index_analysis_failed", error=str(e))
            return []


class WaitStatsAnalyzer(BaseAnalyzer):
    """Analyze wait statistics for bottleneck detection."""

    # Wait type categories and descriptions
    WAIT_CATEGORIES = {
        "PAGEIOLATCH": ("IO", "Page I/O latch waits - disk read/write delays"),
        "WRITELOG": ("IO", "Transaction log write waits"),
        "LCK_M": ("Blocking", "Lock waits due to blocking"),
        "CXPACKET": ("Parallelism", "Parallel query coordination waits"),
        "SOS_SCHEDULER_YIELD": ("CPU", "CPU scheduler yielding - high CPU usage"),
        "ASYNC_NETWORK_IO": ("Network", "Client network delays"),
        "OLEDB": ("External", "Linked server or external data access"),
        "RESOURCE_SEMAPHORE": ("Memory", "Query memory grant waits"),
        "THREADPOOL": ("Worker", "Thread pool exhaustion"),
        "PAGELATCH": ("Memory", "In-memory page latch contention"),
    }

    async def analyze(self, connection: Any) -> list[PerformanceIssue]:
        """Analyze wait statistics."""
        issues = []

        waits = await self._get_wait_stats(connection)

        for wait in waits[:10]:  # Focus on top waits
            if wait.wait_time_ms < 60000:  # Skip if less than 1 minute total
                continue

            severity = IssueSeverity.LOW
            if wait.wait_time_ms > 3600000:  # 1 hour
                severity = IssueSeverity.HIGH
            elif wait.wait_time_ms > 600000:  # 10 minutes
                severity = IssueSeverity.MEDIUM

            issues.append(PerformanceIssue(
                id=f"WAIT_{wait.wait_type[:20]}",
                category=IssueCategory(wait.category.lower()) if wait.category.lower() in [c.value for c in IssueCategory] else IssueCategory.CONFIGURATION,
                severity=severity,
                title=f"High Wait Time: {wait.wait_type}",
                description=wait.description or f"Significant time spent in {wait.wait_type} waits",
                affected_object=wait.wait_type,
                impact=f"Total wait: {wait.wait_time_ms/1000:.0f}s, Tasks: {wait.waiting_tasks_count:,}",
                metrics={
                    "wait_time_ms": wait.wait_time_ms,
                    "waiting_tasks_count": wait.waiting_tasks_count,
                    "resource_wait_time_ms": wait.resource_wait_time_ms,
                },
            ))

        return issues

    async def _get_wait_stats(self, connection: Any) -> list[WaitStatistics]:
        """Get wait statistics from SQL Server."""
        # Exclude benign waits
        excluded = "'BROKER_EVENTHANDLER','BROKER_RECEIVE_WAITFOR','BROKER_TASK_STOP'," \
                   "'BROKER_TO_FLUSH','BROKER_TRANSMITTER','CHECKPOINT_QUEUE'," \
                   "'CHKPT','CLR_AUTO_EVENT','CLR_MANUAL_EVENT','CLR_SEMAPHORE'," \
                   "'DBMIRROR_DBM_EVENT','DBMIRROR_EVENTS_QUEUE','DBMIRROR_WORKER_QUEUE'," \
                   "'DBMIRRORING_CMD','DIRTY_PAGE_POLL','DISPATCHER_QUEUE_SEMAPHORE'," \
                   "'EXECSYNC','FSAGENT','FT_IFTS_SCHEDULER_IDLE_WAIT','FT_IFTSHC_MUTEX'," \
                   "'HADR_CLUSAPI_CALL','HADR_FILESTREAM_IOMGR_IOCOMPLETION'," \
                   "'HADR_LOGCAPTURE_WAIT','HADR_NOTIFICATION_DEQUEUE'," \
                   "'HADR_TIMER_TASK','HADR_WORK_QUEUE','LAZYWRITER_SLEEP'," \
                   "'LOGMGR_QUEUE','MEMORY_ALLOCATION_EXT','ONDEMAND_TASK_QUEUE'," \
                   "'PARALLEL_REDO_DRAIN_WORKER','PARALLEL_REDO_LOG_CACHE'," \
                   "'PREEMPTIVE_OS_FLUSHFILEBUFFERS','PREEMPTIVE_XE_GETTARGETSTATE'," \
                   "'PVS_PREALLOCATE','PWAIT_ALL_COMPONENTS_INITIALIZED'," \
                   "'PWAIT_DIRECTLOGCONSUMER_GETNEXT','QDS_ASYNC_QUEUE'," \
                   "'QDS_CLEANUP_STALE_QUERIES_TASK_MAIN_LOOP_SLEEP'," \
                   "'QDS_PERSIST_TASK_MAIN_LOOP_SLEEP','QDS_SHUTDOWN_QUEUE'," \
                   "'REDO_THREAD_PENDING_WORK','REQUEST_FOR_DEADLOCK_SEARCH'," \
                   "'RESOURCE_QUEUE','SERVER_IDLE_CHECK','SLEEP_BPOOL_FLUSH'," \
                   "'SLEEP_DBSTARTUP','SLEEP_DCOMSTARTUP','SLEEP_MASTERDBREADY'," \
                   "'SLEEP_MASTERMDREADY','SLEEP_MASTERUPGRADED','SLEEP_MSDBSTARTUP'," \
                   "'SLEEP_SYSTEMTASK','SLEEP_TASK','SLEEP_TEMPDBSTARTUP'," \
                   "'SNI_HTTP_ACCEPT','SOS_WORK_DISPATCHER','SP_SERVER_DIAGNOSTICS_SLEEP'," \
                   "'SQLTRACE_BUFFER_FLUSH','SQLTRACE_INCREMENTAL_FLUSH_SLEEP'," \
                   "'SQLTRACE_WAIT_ENTRIES','UCS_SESSION_REGISTRATION'," \
                   "'WAIT_FOR_RESULTS','WAIT_XTP_CKPT_CLOSE','WAIT_XTP_HOST_WAIT'," \
                   "'WAIT_XTP_OFFLINE_CKPT_NEW_LOG','WAIT_XTP_RECOVERY'," \
                   "'WAITFOR','WAITFOR_TASKSHUTDOWN','XE_BUFFERMGR_ALLPROCESSED_EVENT'," \
                   "'XE_DISPATCHER_JOIN','XE_DISPATCHER_WAIT','XE_TIMER_EVENT'"

        query = f"""
        SELECT
            wait_type,
            waiting_tasks_count,
            wait_time_ms,
            signal_wait_time_ms
        FROM sys.dm_os_wait_stats
        WHERE wait_type NOT IN ({excluded})
        AND wait_time_ms > 0
        ORDER BY wait_time_ms DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()

            results = []
            for row in rows:
                wait_type = row[0]
                category, description = self._categorize_wait(wait_type)

                results.append(WaitStatistics(
                    wait_type=wait_type,
                    waiting_tasks_count=row[1],
                    wait_time_ms=row[2],
                    signal_wait_time_ms=row[3],
                    category=category,
                    description=description,
                ))

            return results
        except Exception as e:
            logger.warning("wait_stats_analysis_failed", error=str(e))
            return []

    def _categorize_wait(self, wait_type: str) -> tuple[str, str]:
        """Categorize a wait type."""
        for prefix, (category, desc) in self.WAIT_CATEGORIES.items():
            if wait_type.startswith(prefix):
                return category, desc
        return "Other", f"Wait type: {wait_type}"


class RecommendationEngine:
    """Generate recommendations from issues."""

    def generate_recommendations(
        self,
        issues: list[PerformanceIssue],
        index_analysis: list[IndexAnalysis],
        missing_indexes: list[MissingIndex],
    ) -> list[Recommendation]:
        """Generate recommendations from analysis results."""
        recommendations = []

        for issue in issues:
            rec = self._create_recommendation(issue, index_analysis, missing_indexes)
            if rec:
                recommendations.append(rec)

        return recommendations

    def _create_recommendation(
        self,
        issue: PerformanceIssue,
        index_analysis: list[IndexAnalysis],
        missing_indexes: list[MissingIndex],
    ) -> Optional[Recommendation]:
        """Create a recommendation for an issue."""

        if issue.category == IssueCategory.INDEX:
            if "Unused" in issue.title:
                return Recommendation(
                    id=f"REC_{issue.id}",
                    issue_id=issue.id,
                    title="Drop Unused Index",
                    description=f"Consider dropping {issue.affected_object} to improve write performance",
                    fix_script=f"DROP INDEX [{issue.affected_object.split('.')[-1]}] ON {'.'.join(issue.affected_object.split('.')[:-1])};",
                    complexity=FixComplexity.SIMPLE,
                    estimated_improvement="Faster INSERT/UPDATE/DELETE operations",
                    risk_level="low",
                    requires_testing=True,
                )

            if "Fragmented" in issue.title:
                frag = issue.metrics.get("fragmentation_percent", 0)
                if frag > 30:
                    return Recommendation(
                        id=f"REC_{issue.id}",
                        issue_id=issue.id,
                        title="Rebuild Index" if frag > 70 else "Reorganize Index",
                        description=f"{'Rebuild' if frag > 70 else 'Reorganize'} {issue.affected_object}",
                        fix_script=f"ALTER INDEX [{issue.affected_object.split('.')[-1]}] ON {'.'.join(issue.affected_object.split('.')[:-1])} {'REBUILD' if frag > 70 else 'REORGANIZE'};",
                        complexity=FixComplexity.MODERATE if frag > 70 else FixComplexity.SIMPLE,
                        estimated_improvement=f"Up to {min(frag, 50):.0f}% faster reads",
                        risk_level="low",
                    )

            if "Missing" in issue.title:
                # Find the corresponding missing index
                for mi in missing_indexes:
                    if mi.table_name == issue.affected_object:
                        return Recommendation(
                            id=f"REC_{issue.id}",
                            issue_id=issue.id,
                            title="Create Missing Index",
                            description=f"Create suggested index on {mi.table_name}",
                            fix_script=mi.create_statement,
                            complexity=FixComplexity.MODERATE,
                            estimated_improvement=f"Up to {mi.avg_user_impact:.0f}% improvement",
                            risk_level="medium",
                            requires_testing=True,
                            prerequisites=["Test in non-production environment first"],
                        )

        if issue.category == IssueCategory.QUERY:
            if "Regression" in issue.title:
                return Recommendation(
                    id=f"REC_{issue.id}",
                    issue_id=issue.id,
                    title="Force Previous Plan",
                    description="Use Query Store to force the previous good plan",
                    fix_script=f"-- Force good plan using Query Store\nEXEC sp_query_store_force_plan @query_id = <query_id>, @plan_id = <good_plan_id>;",
                    complexity=FixComplexity.SIMPLE,
                    estimated_improvement="Restore previous performance level",
                    risk_level="low",
                )

        return None
