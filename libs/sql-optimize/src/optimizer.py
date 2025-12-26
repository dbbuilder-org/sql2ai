"""Main SQL Optimizer implementation."""

import time
from datetime import datetime
from typing import Any, Optional

import structlog

from analyzers import (
    IndexAnalyzer,
    QueryStoreAnalyzer,
    RecommendationEngine,
    WaitStatsAnalyzer,
)
from models import OptimizationReport

logger = structlog.get_logger()


class SQLOptimizer:
    """Deep performance analysis with AI-driven remediation."""

    def __init__(
        self,
        connection_provider: Any,
        include_query_store: bool = True,
        include_index_analysis: bool = True,
        include_wait_stats: bool = True,
    ):
        """Initialize the optimizer.

        Args:
            connection_provider: Function to get database connection
            include_query_store: Include Query Store analysis
            include_index_analysis: Include index analysis
            include_wait_stats: Include wait statistics analysis
        """
        self.connection_provider = connection_provider
        self.include_query_store = include_query_store
        self.include_index_analysis = include_index_analysis
        self.include_wait_stats = include_wait_stats

        self._query_analyzer = QueryStoreAnalyzer()
        self._index_analyzer = IndexAnalyzer()
        self._wait_analyzer = WaitStatsAnalyzer()
        self._recommendation_engine = RecommendationEngine()

    async def analyze(
        self,
        connection_id: str,
        database_name: Optional[str] = None,
    ) -> OptimizationReport:
        """Run comprehensive performance analysis.

        Args:
            connection_id: Database connection ID
            database_name: Optional database name override

        Returns:
            OptimizationReport with findings
        """
        start_time = time.perf_counter()

        logger.info(
            "optimization_analysis_started",
            connection_id=connection_id,
            database_name=database_name,
        )

        report = OptimizationReport(
            connection_id=connection_id,
            database_name=database_name or "Unknown",
        )

        try:
            connection = await self.connection_provider(connection_id)

            # Get database name if not provided
            if not database_name:
                try:
                    cursor = await connection.execute("SELECT DB_NAME()")
                    row = await cursor.fetchone()
                    report.database_name = row[0] if row else "Unknown"
                except Exception:
                    pass

            # Run Query Store analysis
            if self.include_query_store:
                logger.debug("running_query_store_analysis")
                try:
                    query_issues = await self._query_analyzer.analyze(connection)
                    report.issues.extend(query_issues)

                    # Get top queries
                    report.top_queries = await self._query_analyzer._get_top_queries(connection)
                except Exception as e:
                    logger.warning("query_store_analysis_error", error=str(e))

            # Run index analysis
            if self.include_index_analysis:
                logger.debug("running_index_analysis")
                try:
                    index_issues = await self._index_analyzer.analyze(connection)
                    report.issues.extend(index_issues)

                    # Get detailed index info
                    report.index_analysis = await self._index_analyzer._get_index_usage(connection)
                    report.missing_indexes = await self._index_analyzer._get_missing_indexes(connection)
                except Exception as e:
                    logger.warning("index_analysis_error", error=str(e))

            # Run wait stats analysis
            if self.include_wait_stats:
                logger.debug("running_wait_stats_analysis")
                try:
                    wait_issues = await self._wait_analyzer.analyze(connection)
                    report.issues.extend(wait_issues)

                    report.wait_statistics = await self._wait_analyzer._get_wait_stats(connection)
                except Exception as e:
                    logger.warning("wait_stats_analysis_error", error=str(e))

            # Generate recommendations
            report.recommendations = self._recommendation_engine.generate_recommendations(
                issues=report.issues,
                index_analysis=report.index_analysis,
                missing_indexes=report.missing_indexes,
            )

            # Calculate health score
            report.health_score = report.calculate_health_score()

            report.duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.info(
                "optimization_analysis_completed",
                connection_id=connection_id,
                issues_found=len(report.issues),
                recommendations=len(report.recommendations),
                health_score=report.health_score,
                duration_ms=report.duration_ms,
            )

        except Exception as e:
            logger.error(
                "optimization_analysis_failed",
                connection_id=connection_id,
                error=str(e),
            )
            report.duration_ms = int((time.perf_counter() - start_time) * 1000)

        return report

    async def get_quick_health(self, connection_id: str) -> dict:
        """Get quick health check without full analysis.

        Args:
            connection_id: Database connection ID

        Returns:
            Quick health status dict
        """
        try:
            connection = await self.connection_provider(connection_id)

            # Quick checks
            checks = {}

            # Check for blocking
            blocking_query = """
            SELECT COUNT(*) FROM sys.dm_exec_requests
            WHERE blocking_session_id > 0
            """
            try:
                cursor = await connection.execute(blocking_query)
                row = await cursor.fetchone()
                checks["active_blocking"] = row[0] if row else 0
            except Exception:
                checks["active_blocking"] = -1

            # Check CPU pressure
            cpu_query = """
            SELECT AVG(runnable_tasks_count) FROM sys.dm_os_schedulers
            WHERE scheduler_id < 255
            """
            try:
                cursor = await connection.execute(cpu_query)
                row = await cursor.fetchone()
                checks["avg_runnable_tasks"] = float(row[0]) if row and row[0] else 0
            except Exception:
                checks["avg_runnable_tasks"] = -1

            # Check memory pressure
            memory_query = """
            SELECT
                (SELECT cntr_value FROM sys.dm_os_performance_counters
                 WHERE counter_name = 'Page life expectancy' AND object_name LIKE '%Buffer Manager%') AS ple,
                (SELECT cntr_value FROM sys.dm_os_performance_counters
                 WHERE counter_name = 'Memory Grants Pending' AND object_name LIKE '%Memory Manager%') AS pending_grants
            """
            try:
                cursor = await connection.execute(memory_query)
                row = await cursor.fetchone()
                checks["page_life_expectancy"] = row[0] if row else -1
                checks["pending_memory_grants"] = row[1] if row else -1
            except Exception:
                checks["page_life_expectancy"] = -1
                checks["pending_memory_grants"] = -1

            # Calculate quick health score
            score = 100
            if checks["active_blocking"] > 0:
                score -= min(checks["active_blocking"] * 5, 20)
            if checks["avg_runnable_tasks"] > 5:
                score -= min((checks["avg_runnable_tasks"] - 5) * 5, 20)
            if checks["page_life_expectancy"] >= 0 and checks["page_life_expectancy"] < 300:
                score -= 20
            if checks["pending_memory_grants"] > 0:
                score -= min(checks["pending_memory_grants"] * 10, 20)

            return {
                "connection_id": connection_id,
                "health_score": max(0, score),
                "status": "healthy" if score >= 80 else "degraded" if score >= 50 else "critical",
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error("quick_health_check_failed", error=str(e))
            return {
                "connection_id": connection_id,
                "health_score": -1,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def analyze_query(
        self,
        connection_id: str,
        query_text: str,
    ) -> dict:
        """Analyze a specific query for optimization opportunities.

        Args:
            connection_id: Database connection ID
            query_text: SQL query to analyze

        Returns:
            Query analysis results
        """
        try:
            connection = await self.connection_provider(connection_id)

            # Get estimated execution plan
            plan_query = f"SET SHOWPLAN_XML ON; {query_text}"

            issues = []
            recommendations = []

            # Parse query for common issues
            query_upper = query_text.upper()

            # Check for SELECT *
            if "SELECT *" in query_upper or "SELECT  *" in query_upper:
                issues.append({
                    "type": "anti_pattern",
                    "title": "SELECT * Usage",
                    "description": "Using SELECT * retrieves all columns which may be unnecessary",
                    "recommendation": "Specify only the columns you need",
                })

            # Check for missing WHERE clause on UPDATE/DELETE
            if ("UPDATE " in query_upper or "DELETE " in query_upper) and " WHERE " not in query_upper:
                issues.append({
                    "type": "dangerous",
                    "title": "Missing WHERE Clause",
                    "description": "UPDATE/DELETE without WHERE affects all rows",
                    "recommendation": "Add a WHERE clause to limit affected rows",
                })

            # Check for NOLOCK hint
            if "NOLOCK" in query_upper or "READ UNCOMMITTED" in query_upper:
                issues.append({
                    "type": "warning",
                    "title": "NOLOCK Hint",
                    "description": "NOLOCK can return dirty/inconsistent data",
                    "recommendation": "Consider using READ COMMITTED SNAPSHOT instead",
                })

            # Check for cursors
            if "DECLARE CURSOR" in query_upper or "CURSOR FOR" in query_upper:
                issues.append({
                    "type": "performance",
                    "title": "Cursor Usage",
                    "description": "Cursors are typically slower than set-based operations",
                    "recommendation": "Refactor to use set-based operations if possible",
                })

            # Check for functions on indexed columns
            if any(f"({col})" in query_upper for col in ["CONVERT(", "CAST(", "DATEPART(", "YEAR(", "MONTH("]):
                issues.append({
                    "type": "performance",
                    "title": "Function on Column",
                    "description": "Functions on columns in WHERE clause prevent index usage",
                    "recommendation": "Move function to the comparison value side",
                })

            return {
                "query_text": query_text[:500],
                "issues": issues,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error("query_analysis_failed", error=str(e))
            return {
                "query_text": query_text[:500],
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat(),
            }
