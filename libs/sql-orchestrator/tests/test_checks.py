"""Tests for SQL Orchestrator check framework."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_checks.py', '/src'))

from models import (
    CheckResult,
    CheckSeverity,
    CheckCategory,
    HealthStatus,
    DatabaseHealth,
)
from checks import (
    Check,
    CheckRegistry,
    LongRunningQueriesCheck,
    HighCPUCheck,
    BlockingSessionsCheck,
    UnencryptedConnectionsCheck,
    ExcessivePermissionsCheck,
    MissingBackupsCheck,
)


class TestCheckResult:
    """Test CheckResult model."""

    def test_create_check_result(self):
        result = CheckResult(
            check_id="TEST001",
            check_name="Test Check",
            category=CheckCategory.PERFORMANCE,
            severity=CheckSeverity.WARNING,
            passed=False,
            message="Test message",
            details={"key": "value"},
            remediation="Fix the issue",
        )
        assert result.check_id == "TEST001"
        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING

    def test_check_result_timestamps(self):
        result = CheckResult(
            check_id="TEST001",
            check_name="Test Check",
            category=CheckCategory.SECURITY,
            severity=CheckSeverity.CRITICAL,
            passed=True,
            message="All good",
        )
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)


class TestCheckRegistry:
    """Test CheckRegistry functionality."""

    def test_register_check(self):
        registry = CheckRegistry()
        check = LongRunningQueriesCheck()
        registry.register(check)
        assert "PERF001" in registry._checks

    def test_get_check(self):
        registry = CheckRegistry()
        check = HighCPUCheck()
        registry.register(check)
        retrieved = registry.get("PERF002")
        assert retrieved is not None
        assert retrieved.check_id == "PERF002"

    def test_get_nonexistent_check(self):
        registry = CheckRegistry()
        result = registry.get("NONEXISTENT")
        assert result is None

    def test_list_checks(self):
        registry = CheckRegistry()
        registry.register(LongRunningQueriesCheck())
        registry.register(HighCPUCheck())
        checks = registry.list_checks()
        assert len(checks) == 2

    def test_get_by_category(self):
        registry = CheckRegistry()
        registry.register(LongRunningQueriesCheck())
        registry.register(HighCPUCheck())
        registry.register(UnencryptedConnectionsCheck())

        perf_checks = registry.get_by_category(CheckCategory.PERFORMANCE)
        assert len(perf_checks) == 2

        sec_checks = registry.get_by_category(CheckCategory.SECURITY)
        assert len(sec_checks) == 1


class TestLongRunningQueriesCheck:
    """Test LongRunningQueriesCheck."""

    @pytest.mark.asyncio
    async def test_check_passes_no_long_queries(self):
        check = LongRunningQueriesCheck(threshold_seconds=300)
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[])

        result = await check.execute(connection)
        assert result.passed is True
        assert result.check_id == "PERF001"

    @pytest.mark.asyncio
    async def test_check_fails_with_long_queries(self):
        check = LongRunningQueriesCheck(threshold_seconds=300)
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"session_id": 1, "duration_seconds": 600, "query_text": "SELECT..."},
            {"session_id": 2, "duration_seconds": 450, "query_text": "UPDATE..."},
        ])

        result = await check.execute(connection)
        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING
        assert len(result.details.get("long_running_queries", [])) == 2


class TestHighCPUCheck:
    """Test HighCPUCheck."""

    @pytest.mark.asyncio
    async def test_check_passes_low_cpu(self):
        check = HighCPUCheck(threshold_percent=80)
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[{"cpu_percent": 45.5}])

        result = await check.execute(connection)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_check_fails_high_cpu(self):
        check = HighCPUCheck(threshold_percent=80)
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[{"cpu_percent": 92.3}])

        result = await check.execute(connection)
        assert result.passed is False
        assert result.severity == CheckSeverity.CRITICAL


class TestBlockingSessionsCheck:
    """Test BlockingSessionsCheck."""

    @pytest.mark.asyncio
    async def test_check_passes_no_blocking(self):
        check = BlockingSessionsCheck()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[])

        result = await check.execute(connection)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_check_fails_with_blocking(self):
        check = BlockingSessionsCheck()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"blocking_session_id": 100, "blocked_session_id": 101, "wait_time_ms": 5000},
        ])

        result = await check.execute(connection)
        assert result.passed is False


class TestSecurityChecks:
    """Test security-related checks."""

    @pytest.mark.asyncio
    async def test_unencrypted_connections_check(self):
        check = UnencryptedConnectionsCheck()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"session_id": 1, "encrypt_option": "FALSE"},
        ])

        result = await check.execute(connection)
        assert result.passed is False
        assert result.category == CheckCategory.SECURITY

    @pytest.mark.asyncio
    async def test_excessive_permissions_check(self):
        check = ExcessivePermissionsCheck()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"principal_name": "app_user", "permission": "CONTROL SERVER"},
        ])

        result = await check.execute(connection)
        assert result.passed is False
        assert "excessive_permissions" in result.details


class TestComplianceChecks:
    """Test compliance-related checks."""

    @pytest.mark.asyncio
    async def test_missing_backups_check(self):
        check = MissingBackupsCheck(max_hours=24)
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"database_name": "TestDB", "hours_since_backup": 48},
        ])

        result = await check.execute(connection)
        assert result.passed is False
        assert result.category == CheckCategory.COMPLIANCE


class TestDatabaseHealth:
    """Test DatabaseHealth model."""

    def test_calculate_health_score(self):
        results = [
            CheckResult(
                check_id="TEST1",
                check_name="Test 1",
                category=CheckCategory.PERFORMANCE,
                severity=CheckSeverity.INFO,
                passed=True,
                message="OK",
            ),
            CheckResult(
                check_id="TEST2",
                check_name="Test 2",
                category=CheckCategory.SECURITY,
                severity=CheckSeverity.WARNING,
                passed=False,
                message="Warning",
            ),
        ]

        health = DatabaseHealth(
            database_name="TestDB",
            check_results=results,
        )

        assert health.overall_status in [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL]
        assert 0 <= health.health_score <= 100

    def test_health_with_critical_failure(self):
        results = [
            CheckResult(
                check_id="TEST1",
                check_name="Test 1",
                category=CheckCategory.SECURITY,
                severity=CheckSeverity.CRITICAL,
                passed=False,
                message="Critical issue",
            ),
        ]

        health = DatabaseHealth(
            database_name="TestDB",
            check_results=results,
        )

        assert health.overall_status == HealthStatus.CRITICAL
