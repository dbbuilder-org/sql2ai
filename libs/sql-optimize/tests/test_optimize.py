"""Tests for SQL Optimize module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_optimize.py', '/src'))

from models import (
    PerformanceIssue,
    IssueSeverity,
    IssueCategory,
    Recommendation,
    RecommendationPriority,
    QueryInfo,
    IndexRecommendation,
    WaitStatistic,
    HealthScore,
)
from analyzers import (
    QueryStoreAnalyzer,
    IndexAnalyzer,
    WaitStatsAnalyzer,
)
from optimizer import SQLOptimizer


class TestPerformanceIssue:
    """Test PerformanceIssue model."""

    def test_create_issue(self):
        issue = PerformanceIssue(
            issue_id="PERF001",
            category=IssueCategory.QUERY,
            severity=IssueSeverity.HIGH,
            title="Slow query detected",
            description="Query taking over 30 seconds",
            affected_object="dbo.GetAllOrders",
            metrics={"avg_duration_ms": 35000, "execution_count": 100},
        )
        assert issue.issue_id == "PERF001"
        assert issue.severity == IssueSeverity.HIGH


class TestRecommendation:
    """Test Recommendation model."""

    def test_create_recommendation(self):
        rec = Recommendation(
            recommendation_id="REC001",
            priority=RecommendationPriority.HIGH,
            title="Add missing index",
            description="Adding this index could improve query performance by 80%",
            fix_script="CREATE INDEX idx_orders_customer ON Orders(CustomerId)",
            estimated_impact=0.8,
        )
        assert rec.priority == RecommendationPriority.HIGH
        assert rec.estimated_impact == 0.8


class TestQueryStoreAnalyzer:
    """Test QueryStoreAnalyzer."""

    @pytest.mark.asyncio
    async def test_get_top_queries(self):
        analyzer = QueryStoreAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "query_id": 1,
                "query_text": "SELECT * FROM Orders WHERE CustomerId = @p1",
                "avg_duration_ms": 500,
                "execution_count": 10000,
                "avg_cpu_time_ms": 200,
                "avg_logical_reads": 5000,
            },
            {
                "query_id": 2,
                "query_text": "SELECT * FROM Products WHERE Category = @p1",
                "avg_duration_ms": 200,
                "execution_count": 50000,
                "avg_cpu_time_ms": 100,
                "avg_logical_reads": 1000,
            },
        ])

        queries = await analyzer.get_top_queries(connection, top_n=10)
        assert len(queries) == 2
        assert all(isinstance(q, QueryInfo) for q in queries)

    @pytest.mark.asyncio
    async def test_detect_regressed_queries(self):
        analyzer = QueryStoreAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "query_id": 1,
                "query_text": "SELECT * FROM Orders",
                "old_avg_duration_ms": 100,
                "new_avg_duration_ms": 500,
                "regression_percent": 400,
            },
        ])

        regressed = await analyzer.detect_regressions(connection)
        assert len(regressed) == 1
        assert regressed[0]["regression_percent"] >= 100

    @pytest.mark.asyncio
    async def test_analyze_plan_changes(self):
        analyzer = QueryStoreAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "query_id": 1,
                "plan_id": 10,
                "is_forced_plan": False,
                "last_execution_time": datetime.utcnow(),
            },
        ])

        plans = await analyzer.get_plan_history(connection, query_id=1)
        assert len(plans) >= 0


class TestIndexAnalyzer:
    """Test IndexAnalyzer."""

    @pytest.mark.asyncio
    async def test_get_missing_indexes(self):
        analyzer = IndexAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "table_name": "Orders",
                "equality_columns": "CustomerId",
                "inequality_columns": "OrderDate",
                "included_columns": "TotalAmount",
                "user_seeks": 10000,
                "user_scans": 500,
                "avg_total_user_cost": 50.5,
                "avg_user_impact": 85.5,
            },
        ])

        missing = await analyzer.get_missing_indexes(connection)
        assert len(missing) == 1
        assert isinstance(missing[0], IndexRecommendation)
        assert missing[0].estimated_impact > 0

    @pytest.mark.asyncio
    async def test_get_unused_indexes(self):
        analyzer = IndexAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "index_name": "idx_old_unused",
                "table_name": "Orders",
                "user_seeks": 0,
                "user_scans": 0,
                "user_lookups": 0,
                "user_updates": 1000,
                "size_mb": 50.5,
            },
        ])

        unused = await analyzer.get_unused_indexes(connection)
        assert len(unused) == 1
        assert unused[0]["user_seeks"] == 0

    @pytest.mark.asyncio
    async def test_get_fragmentation(self):
        analyzer = IndexAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "index_name": "PK_Orders",
                "table_name": "Orders",
                "avg_fragmentation_percent": 45.5,
                "page_count": 10000,
            },
        ])

        fragmented = await analyzer.get_fragmented_indexes(connection, threshold=30)
        assert len(fragmented) == 1
        assert fragmented[0]["avg_fragmentation_percent"] > 30


class TestWaitStatsAnalyzer:
    """Test WaitStatsAnalyzer."""

    @pytest.mark.asyncio
    async def test_get_top_waits(self):
        analyzer = WaitStatsAnalyzer()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {
                "wait_type": "PAGEIOLATCH_SH",
                "wait_time_ms": 100000,
                "waiting_tasks_count": 5000,
                "signal_wait_time_ms": 1000,
            },
            {
                "wait_type": "LCK_M_X",
                "wait_time_ms": 50000,
                "waiting_tasks_count": 1000,
                "signal_wait_time_ms": 500,
            },
        ])

        waits = await analyzer.get_top_waits(connection, top_n=10)
        assert len(waits) == 2
        assert all(isinstance(w, WaitStatistic) for w in waits)

    def test_categorize_waits(self):
        analyzer = WaitStatsAnalyzer()

        assert analyzer.categorize("PAGEIOLATCH_SH") == "IO"
        assert analyzer.categorize("LCK_M_X") == "LOCKING"
        assert analyzer.categorize("CXPACKET") == "PARALLELISM"
        assert analyzer.categorize("SOS_SCHEDULER_YIELD") == "CPU"
        assert analyzer.categorize("ASYNC_NETWORK_IO") == "NETWORK"


class TestSQLOptimizer:
    """Test SQLOptimizer main class."""

    @pytest.mark.asyncio
    async def test_full_analysis(self):
        optimizer = SQLOptimizer()
        connection = MagicMock()

        with patch.object(optimizer.query_store_analyzer, 'get_top_queries') as mock_qs, \
             patch.object(optimizer.index_analyzer, 'get_missing_indexes') as mock_idx, \
             patch.object(optimizer.wait_stats_analyzer, 'get_top_waits') as mock_ws:

            mock_qs.return_value = []
            mock_idx.return_value = []
            mock_ws.return_value = []

            result = await optimizer.analyze(connection)

            assert result is not None
            assert hasattr(result, 'issues')
            assert hasattr(result, 'recommendations')

    @pytest.mark.asyncio
    async def test_generate_recommendations(self):
        optimizer = SQLOptimizer()
        connection = MagicMock()

        issues = [
            PerformanceIssue(
                issue_id="PERF001",
                category=IssueCategory.INDEX,
                severity=IssueSeverity.HIGH,
                title="Missing index",
                description="Missing index on Orders.CustomerId",
                affected_object="Orders",
            ),
        ]

        recommendations = optimizer.generate_recommendations(issues)
        assert len(recommendations) > 0
        assert all(isinstance(r, Recommendation) for r in recommendations)

    def test_calculate_health_score(self):
        optimizer = SQLOptimizer()

        issues = [
            PerformanceIssue(
                issue_id="PERF001",
                category=IssueCategory.QUERY,
                severity=IssueSeverity.LOW,
                title="Minor issue",
                description="...",
                affected_object="...",
            ),
            PerformanceIssue(
                issue_id="PERF002",
                category=IssueCategory.INDEX,
                severity=IssueSeverity.MEDIUM,
                title="Medium issue",
                description="...",
                affected_object="...",
            ),
        ]

        score = optimizer.calculate_health_score(issues)
        assert isinstance(score, HealthScore)
        assert 0 <= score.overall_score <= 100

    def test_prioritize_recommendations(self):
        optimizer = SQLOptimizer()

        recommendations = [
            Recommendation(
                recommendation_id="REC001",
                priority=RecommendationPriority.LOW,
                title="Low priority",
                description="...",
                estimated_impact=0.1,
            ),
            Recommendation(
                recommendation_id="REC002",
                priority=RecommendationPriority.CRITICAL,
                title="Critical",
                description="...",
                estimated_impact=0.9,
            ),
            Recommendation(
                recommendation_id="REC003",
                priority=RecommendationPriority.HIGH,
                title="High priority",
                description="...",
                estimated_impact=0.7,
            ),
        ]

        prioritized = optimizer.prioritize_recommendations(recommendations)
        assert prioritized[0].priority == RecommendationPriority.CRITICAL
        assert prioritized[-1].priority == RecommendationPriority.LOW
