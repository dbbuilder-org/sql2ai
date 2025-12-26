"""Main SQL Compliance engine."""

import time
from datetime import datetime
from typing import Any, Optional

import structlog

from models import (
    ComplianceFramework,
    ComplianceReport,
    ComplianceStatus,
)
from scanner import (
    AccessControlScanner,
    AuditScanner,
    EncryptionScanner,
    PIIScanner,
)

logger = structlog.get_logger()


# Framework-specific checks
FRAMEWORK_CHECKS = {
    ComplianceFramework.SOC2: [
        "ENC_TDE", "ENC_TLS", "ENC_BACKUP",
        "AUDIT_CONFIG", "ACCESS_EXCESSIVE",
    ],
    ComplianceFramework.HIPAA: [
        "ENC_TDE", "ENC_TLS", "ENC_BACKUP",
        "AUDIT_CONFIG", "ACCESS_EXCESSIVE",
        "PII_MEDICAL_RECORD", "PII_SSN",
    ],
    ComplianceFramework.PCI_DSS: [
        "ENC_TDE", "ENC_TLS", "ENC_BACKUP",
        "AUDIT_CONFIG", "ACCESS_EXCESSIVE",
        "PII_CREDIT_CARD", "PII_BANK_ACCOUNT",
    ],
    ComplianceFramework.GDPR: [
        "ENC_TDE", "ENC_TLS",
        "AUDIT_CONFIG", "ACCESS_EXCESSIVE",
        "PII_EMAIL", "PII_PHONE", "PII_ADDRESS",
        "PII_SSN", "PII_DATE_OF_BIRTH",
    ],
}


class SQLCompliance:
    """Automated compliance checking with PII/PHI detection."""

    def __init__(
        self,
        connection_provider: Any,
        pii_sample_size: int = 1000,
        pii_confidence_threshold: float = 0.7,
    ):
        """Initialize compliance engine.

        Args:
            connection_provider: Function to get database connection
            pii_sample_size: Number of rows to sample for PII detection
            pii_confidence_threshold: Minimum confidence for PII detection
        """
        self.connection_provider = connection_provider

        self._pii_scanner = PIIScanner(
            sample_size=pii_sample_size,
            confidence_threshold=pii_confidence_threshold,
        )
        self._encryption_scanner = EncryptionScanner()
        self._access_scanner = AccessControlScanner()
        self._audit_scanner = AuditScanner()

    async def scan(
        self,
        connection_id: str,
        frameworks: Optional[list[ComplianceFramework]] = None,
        include_pii_scan: bool = True,
        database_name: Optional[str] = None,
    ) -> ComplianceReport:
        """Run comprehensive compliance scan.

        Args:
            connection_id: Database connection ID
            frameworks: Frameworks to check (default: all)
            include_pii_scan: Include PII data scanning
            database_name: Optional database name override

        Returns:
            ComplianceReport with findings
        """
        start_time = time.perf_counter()

        frameworks = frameworks or list(ComplianceFramework)

        logger.info(
            "compliance_scan_started",
            connection_id=connection_id,
            frameworks=[f.value for f in frameworks],
            include_pii=include_pii_scan,
        )

        report = ComplianceReport(
            connection_id=connection_id,
            database_name=database_name or "Unknown",
            frameworks=frameworks,
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

            # Run encryption checks
            logger.debug("running_encryption_scan")
            try:
                enc_results = await self._encryption_scanner.scan(connection)
                report.check_results.extend(enc_results)
                report.encryption_status = await self._encryption_scanner.get_encryption_status(connection)
            except Exception as e:
                logger.warning("encryption_scan_error", error=str(e))

            # Run audit checks
            logger.debug("running_audit_scan")
            try:
                audit_results = await self._audit_scanner.scan(connection)
                report.check_results.extend(audit_results)
            except Exception as e:
                logger.warning("audit_scan_error", error=str(e))

            # Run access control checks
            logger.debug("running_access_scan")
            try:
                access_results = await self._access_scanner.scan(connection)
                report.check_results.extend(access_results)
                report.access_findings = await self._access_scanner.get_access_findings(connection)
            except Exception as e:
                logger.warning("access_scan_error", error=str(e))

            # Run PII scan if requested
            if include_pii_scan:
                logger.debug("running_pii_scan")
                try:
                    pii_results = await self._pii_scanner.scan(connection)
                    report.check_results.extend(pii_results)
                    report.pii_findings = await self._pii_scanner.scan_for_pii(connection)
                except Exception as e:
                    logger.warning("pii_scan_error", error=str(e))

            # Filter results by requested frameworks
            report.check_results = [
                r for r in report.check_results
                if r.framework in frameworks
            ]

            # Calculate overall status
            report.calculate_status()

            report.duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.info(
                "compliance_scan_completed",
                connection_id=connection_id,
                status=report.overall_status.value,
                checks=len(report.check_results),
                pii_findings=len(report.pii_findings),
                duration_ms=report.duration_ms,
            )

        except Exception as e:
            logger.error(
                "compliance_scan_failed",
                connection_id=connection_id,
                error=str(e),
            )
            report.duration_ms = int((time.perf_counter() - start_time) * 1000)
            report.overall_status = ComplianceStatus.ERROR

        return report

    async def scan_framework(
        self,
        connection_id: str,
        framework: ComplianceFramework,
    ) -> ComplianceReport:
        """Run compliance scan for a specific framework.

        Args:
            connection_id: Database connection ID
            framework: Compliance framework to check

        Returns:
            ComplianceReport for the framework
        """
        # Determine if PII scan is needed for this framework
        pii_needed = framework in [
            ComplianceFramework.HIPAA,
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.GDPR,
            ComplianceFramework.CCPA,
        ]

        return await self.scan(
            connection_id=connection_id,
            frameworks=[framework],
            include_pii_scan=pii_needed,
        )

    async def generate_evidence(
        self,
        connection_id: str,
        framework: ComplianceFramework,
    ) -> dict:
        """Generate compliance evidence for auditors.

        Args:
            connection_id: Database connection ID
            framework: Framework for evidence generation

        Returns:
            Evidence package as dict
        """
        report = await self.scan_framework(connection_id, framework)

        evidence = {
            "framework": framework.value,
            "generated_at": datetime.utcnow().isoformat(),
            "database": report.database_name,
            "overall_status": report.overall_status.value,
            "summary": {
                "total_checks": report.total_checks,
                "compliant": report.compliant_checks,
                "non_compliant": report.non_compliant_checks,
            },
            "controls": [],
        }

        # Group results by category
        for result in report.check_results:
            control = {
                "control_id": result.check_id,
                "control_name": result.check_name,
                "status": result.status.value,
                "evidence": result.evidence,
                "details": result.details,
                "tested_at": result.checked_at.isoformat(),
            }

            if result.status == ComplianceStatus.NON_COMPLIANT:
                control["remediation"] = result.remediation

            evidence["controls"].append(control)

        return evidence

    async def get_quick_status(
        self,
        connection_id: str,
        frameworks: Optional[list[ComplianceFramework]] = None,
    ) -> dict:
        """Get quick compliance status without full scan.

        Args:
            connection_id: Database connection ID
            frameworks: Frameworks to check

        Returns:
            Quick status dict
        """
        frameworks = frameworks or list(ComplianceFramework)

        try:
            connection = await self.connection_provider(connection_id)

            # Quick checks
            status = {
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "frameworks": {},
            }

            for framework in frameworks:
                framework_status = {
                    "status": "unknown",
                    "quick_checks": {},
                }

                # TDE check
                try:
                    cursor = await connection.execute(
                        "SELECT is_encrypted FROM sys.databases WHERE database_id = DB_ID()"
                    )
                    row = await cursor.fetchone()
                    framework_status["quick_checks"]["tde"] = row and row[0] == 1
                except Exception:
                    framework_status["quick_checks"]["tde"] = None

                # Audit check
                try:
                    cursor = await connection.execute(
                        "SELECT COUNT(*) FROM sys.server_audits WHERE is_state_enabled = 1"
                    )
                    row = await cursor.fetchone()
                    framework_status["quick_checks"]["audit"] = row and row[0] > 0
                except Exception:
                    framework_status["quick_checks"]["audit"] = None

                # Determine quick status
                checks = framework_status["quick_checks"]
                if all(v for v in checks.values() if v is not None):
                    framework_status["status"] = "likely_compliant"
                elif any(v is False for v in checks.values()):
                    framework_status["status"] = "likely_non_compliant"
                else:
                    framework_status["status"] = "unknown"

                status["frameworks"][framework.value] = framework_status

            return status

        except Exception as e:
            logger.error("quick_status_failed", error=str(e))
            return {
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }
