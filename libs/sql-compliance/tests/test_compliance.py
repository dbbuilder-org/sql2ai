"""Tests for SQL Compliance module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_compliance.py', '/src'))

from models import (
    ComplianceFramework,
    ComplianceCheck,
    ComplianceResult,
    ComplianceSeverity,
    PIIType,
    PIIFinding,
    EncryptionStatus,
    ComplianceReport,
)
from scanner import (
    PIIScanner,
    EncryptionScanner,
    AccessControlScanner,
    AuditConfigScanner,
)
from compliance import SQLCompliance


class TestComplianceFramework:
    """Test ComplianceFramework enum."""

    def test_framework_values(self):
        assert ComplianceFramework.SOC2.value == "SOC2"
        assert ComplianceFramework.HIPAA.value == "HIPAA"
        assert ComplianceFramework.GDPR.value == "GDPR"
        assert ComplianceFramework.PCI_DSS.value == "PCI_DSS"
        assert ComplianceFramework.FERPA.value == "FERPA"


class TestPIIType:
    """Test PIIType enum."""

    def test_pii_types(self):
        assert PIIType.EMAIL in list(PIIType)
        assert PIIType.SSN in list(PIIType)
        assert PIIType.CREDIT_CARD in list(PIIType)
        assert PIIType.PHONE in list(PIIType)
        assert PIIType.ADDRESS in list(PIIType)


class TestPIIFinding:
    """Test PIIFinding model."""

    def test_create_pii_finding(self):
        finding = PIIFinding(
            table_name="customers",
            column_name="email",
            pii_type=PIIType.EMAIL,
            confidence=0.95,
            sample_count=100,
            is_encrypted=False,
        )
        assert finding.table_name == "customers"
        assert finding.pii_type == PIIType.EMAIL
        assert finding.confidence == 0.95


class TestComplianceResult:
    """Test ComplianceResult model."""

    def test_create_compliance_result(self):
        result = ComplianceResult(
            check_id="SOC2-001",
            framework=ComplianceFramework.SOC2,
            control_name="Access Control",
            passed=True,
            severity=ComplianceSeverity.INFO,
            message="Access controls properly configured",
        )
        assert result.passed is True
        assert result.framework == ComplianceFramework.SOC2


class TestPIIScanner:
    """Test PIIScanner."""

    @pytest.mark.asyncio
    async def test_scan_detects_email(self):
        scanner = PIIScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"column_name": "email", "sample_data": "test@example.com"},
        ])

        with patch.object(scanner, '_analyze_with_presidio') as mock_presidio:
            mock_presidio.return_value = [
                PIIFinding(
                    table_name="users",
                    column_name="email",
                    pii_type=PIIType.EMAIL,
                    confidence=0.99,
                    sample_count=1,
                    is_encrypted=False,
                )
            ]
            findings = await scanner.scan_table(connection, "users")
            assert len(findings) > 0
            assert any(f.pii_type == PIIType.EMAIL for f in findings)

    @pytest.mark.asyncio
    async def test_scan_detects_ssn(self):
        scanner = PIIScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"column_name": "ssn", "sample_data": "123-45-6789"},
        ])

        with patch.object(scanner, '_analyze_with_presidio') as mock_presidio:
            mock_presidio.return_value = [
                PIIFinding(
                    table_name="employees",
                    column_name="ssn",
                    pii_type=PIIType.SSN,
                    confidence=0.98,
                    sample_count=1,
                    is_encrypted=False,
                )
            ]
            findings = await scanner.scan_table(connection, "employees")
            assert any(f.pii_type == PIIType.SSN for f in findings)

    @pytest.mark.asyncio
    async def test_scan_detects_credit_card(self):
        scanner = PIIScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"column_name": "card_number", "sample_data": "4111111111111111"},
        ])

        with patch.object(scanner, '_analyze_with_presidio') as mock_presidio:
            mock_presidio.return_value = [
                PIIFinding(
                    table_name="payments",
                    column_name="card_number",
                    pii_type=PIIType.CREDIT_CARD,
                    confidence=0.97,
                    sample_count=1,
                    is_encrypted=False,
                )
            ]
            findings = await scanner.scan_table(connection, "payments")
            assert any(f.pii_type == PIIType.CREDIT_CARD for f in findings)


class TestEncryptionScanner:
    """Test EncryptionScanner."""

    @pytest.mark.asyncio
    async def test_check_tde_enabled(self):
        scanner = EncryptionScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"database_name": "TestDB", "is_encrypted": True},
        ])

        status = await scanner.check_tde(connection)
        assert status.tde_enabled is True

    @pytest.mark.asyncio
    async def test_check_tde_disabled(self):
        scanner = EncryptionScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"database_name": "TestDB", "is_encrypted": False},
        ])

        status = await scanner.check_tde(connection)
        assert status.tde_enabled is False

    @pytest.mark.asyncio
    async def test_check_connection_encryption(self):
        scanner = EncryptionScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"session_id": 1, "encrypt_option": "TRUE"},
            {"session_id": 2, "encrypt_option": "TRUE"},
        ])

        result = await scanner.check_connection_encryption(connection)
        assert result.all_encrypted is True

    @pytest.mark.asyncio
    async def test_check_backup_encryption(self):
        scanner = EncryptionScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"backup_set_id": 1, "is_encrypted": True},
        ])

        result = await scanner.check_backup_encryption(connection)
        assert result.backups_encrypted is True


class TestAccessControlScanner:
    """Test AccessControlScanner."""

    @pytest.mark.asyncio
    async def test_detect_excessive_permissions(self):
        scanner = AccessControlScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"principal_name": "app_user", "permission_name": "CONTROL SERVER"},
            {"principal_name": "dev_user", "permission_name": "ALTER ANY DATABASE"},
        ])

        findings = await scanner.check_excessive_permissions(connection)
        assert len(findings) == 2
        assert any(f["permission_name"] == "CONTROL SERVER" for f in findings)

    @pytest.mark.asyncio
    async def test_detect_orphaned_users(self):
        scanner = AccessControlScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"user_name": "old_user", "login_name": None},
        ])

        findings = await scanner.check_orphaned_users(connection)
        assert len(findings) == 1

    @pytest.mark.asyncio
    async def test_check_sa_login_disabled(self):
        scanner = AccessControlScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"name": "sa", "is_disabled": True},
        ])

        result = await scanner.check_sa_disabled(connection)
        assert result is True


class TestAuditConfigScanner:
    """Test AuditConfigScanner."""

    @pytest.mark.asyncio
    async def test_check_audit_enabled(self):
        scanner = AuditConfigScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"audit_id": 1, "name": "ServerAudit", "status": 1},
        ])

        result = await scanner.check_audit_configuration(connection)
        assert result.audit_enabled is True

    @pytest.mark.asyncio
    async def test_check_login_auditing(self):
        scanner = AuditConfigScanner()
        connection = MagicMock()
        connection.execute = AsyncMock(return_value=[
            {"config_name": "login_mode", "config_value": 2},  # Both success and failure
        ])

        result = await scanner.check_login_auditing(connection)
        assert result.login_auditing_enabled is True


class TestSQLCompliance:
    """Test SQLCompliance main class."""

    @pytest.mark.asyncio
    async def test_run_soc2_checks(self):
        compliance = SQLCompliance()
        connection = MagicMock()

        with patch.object(compliance, '_run_framework_checks') as mock_checks:
            mock_checks.return_value = [
                ComplianceResult(
                    check_id="SOC2-001",
                    framework=ComplianceFramework.SOC2,
                    control_name="Access Control",
                    passed=True,
                    severity=ComplianceSeverity.INFO,
                    message="Passed",
                ),
            ]
            results = await compliance.check_compliance(
                connection,
                frameworks=[ComplianceFramework.SOC2],
            )
            assert len(results) > 0
            assert all(r.framework == ComplianceFramework.SOC2 for r in results)

    @pytest.mark.asyncio
    async def test_run_hipaa_checks(self):
        compliance = SQLCompliance()
        connection = MagicMock()

        with patch.object(compliance, '_run_framework_checks') as mock_checks:
            mock_checks.return_value = [
                ComplianceResult(
                    check_id="HIPAA-001",
                    framework=ComplianceFramework.HIPAA,
                    control_name="PHI Protection",
                    passed=False,
                    severity=ComplianceSeverity.CRITICAL,
                    message="Unencrypted PHI detected",
                ),
            ]
            results = await compliance.check_compliance(
                connection,
                frameworks=[ComplianceFramework.HIPAA],
            )
            assert any(r.severity == ComplianceSeverity.CRITICAL for r in results)

    def test_generate_compliance_report(self):
        compliance = SQLCompliance()
        results = [
            ComplianceResult(
                check_id="SOC2-001",
                framework=ComplianceFramework.SOC2,
                control_name="Access Control",
                passed=True,
                severity=ComplianceSeverity.INFO,
                message="Passed",
            ),
            ComplianceResult(
                check_id="SOC2-002",
                framework=ComplianceFramework.SOC2,
                control_name="Encryption",
                passed=False,
                severity=ComplianceSeverity.HIGH,
                message="TDE not enabled",
            ),
        ]

        report = compliance.generate_report(results)
        assert isinstance(report, ComplianceReport)
        assert report.total_checks == 2
        assert report.passed_checks == 1
        assert report.failed_checks == 1

    def test_calculate_compliance_score(self):
        compliance = SQLCompliance()
        results = [
            ComplianceResult(
                check_id="SOC2-001",
                framework=ComplianceFramework.SOC2,
                control_name="Test 1",
                passed=True,
                severity=ComplianceSeverity.INFO,
                message="OK",
            ),
            ComplianceResult(
                check_id="SOC2-002",
                framework=ComplianceFramework.SOC2,
                control_name="Test 2",
                passed=True,
                severity=ComplianceSeverity.INFO,
                message="OK",
            ),
        ]

        score = compliance.calculate_score(results)
        assert score == 100.0

    def test_get_remediation_steps(self):
        compliance = SQLCompliance()
        result = ComplianceResult(
            check_id="SOC2-001",
            framework=ComplianceFramework.SOC2,
            control_name="TDE Encryption",
            passed=False,
            severity=ComplianceSeverity.HIGH,
            message="TDE not enabled",
        )

        remediation = compliance.get_remediation(result)
        assert remediation is not None
        assert len(remediation.steps) > 0
