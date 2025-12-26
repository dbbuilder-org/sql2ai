"""Compliance scanners for SQL databases."""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

import structlog

from models import (
    AccessControlFinding,
    ComplianceCheck,
    ComplianceFramework,
    ComplianceResult,
    ComplianceStatus,
    EncryptionStatus,
    PIIFinding,
    PIIType,
    Severity,
)

logger = structlog.get_logger()


# Map Presidio entity types to our PIIType
PRESIDIO_TO_PII_TYPE = {
    "EMAIL_ADDRESS": PIIType.EMAIL,
    "PHONE_NUMBER": PIIType.PHONE,
    "CREDIT_CARD": PIIType.CREDIT_CARD,
    "US_SSN": PIIType.SSN,
    "US_PASSPORT": PIIType.PASSPORT,
    "US_DRIVER_LICENSE": PIIType.DRIVERS_LICENSE,
    "IBAN_CODE": PIIType.IBAN,
    "IP_ADDRESS": PIIType.IP_ADDRESS,
    "PERSON": PIIType.PERSON_NAME,
    "LOCATION": PIIType.LOCATION,
    "DATE_TIME": PIIType.DATE_OF_BIRTH,
    "US_BANK_NUMBER": PIIType.BANK_ACCOUNT,
    "MEDICAL_LICENSE": PIIType.MEDICAL_RECORD,
    "NRP": PIIType.PERSON_NAME,  # Non-recognized person
}


class BaseScanner(ABC):
    """Base class for compliance scanners."""

    @abstractmethod
    async def scan(self, connection: Any) -> list[ComplianceResult]:
        """Run compliance scan."""
        pass


class PIIScanner(BaseScanner):
    """Scan for PII/PHI in database data using Presidio."""

    def __init__(
        self,
        sample_size: int = 1000,
        confidence_threshold: float = 0.7,
        entities: Optional[list[str]] = None,
    ):
        self.sample_size = sample_size
        self.confidence_threshold = confidence_threshold
        self.entities = entities or [
            "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "US_SSN", "PERSON", "LOCATION", "IP_ADDRESS",
            "IBAN_CODE", "US_BANK_NUMBER",
        ]
        self._analyzer = None

    def _get_analyzer(self):
        """Get or create Presidio analyzer."""
        if self._analyzer is None:
            try:
                from presidio_analyzer import AnalyzerEngine
                self._analyzer = AnalyzerEngine()
            except ImportError:
                logger.warning("presidio_not_available")
                return None
        return self._analyzer

    async def scan(self, connection: Any) -> list[ComplianceResult]:
        """Scan database for PII."""
        results = []
        findings = await self.scan_for_pii(connection)

        if findings:
            # Group by PII type for reporting
            pii_types = set(f.pii_type for f in findings)

            for pii_type in pii_types:
                type_findings = [f for f in findings if f.pii_type == pii_type]

                results.append(ComplianceResult(
                    check_id=f"PII_{pii_type.value}",
                    check_name=f"{pii_type.value} Detection",
                    framework=ComplianceFramework.GDPR,  # Applies to multiple
                    status=ComplianceStatus.NON_COMPLIANT,
                    message=f"Found {len(type_findings)} columns containing {pii_type.value}",
                    severity=Severity.HIGH if pii_type in [PIIType.SSN, PIIType.CREDIT_CARD] else Severity.MEDIUM,
                    details={
                        "columns": [f"{f.table_name}.{f.column_name}" for f in type_findings],
                        "count": len(type_findings),
                    },
                    remediation="Implement data masking or encryption for sensitive columns",
                ))
        else:
            results.append(ComplianceResult(
                check_id="PII_SCAN",
                check_name="PII Data Scan",
                framework=ComplianceFramework.GDPR,
                status=ComplianceStatus.COMPLIANT,
                message="No unprotected PII detected in scanned data",
                severity=Severity.INFO,
            ))

        return results

    async def scan_for_pii(self, connection: Any) -> list[PIIFinding]:
        """Scan all text columns for PII."""
        analyzer = self._get_analyzer()
        if not analyzer:
            return []

        findings = []

        # Get all string columns
        columns_query = """
        SELECT
            OBJECT_SCHEMA_NAME(c.object_id) + '.' + OBJECT_NAME(c.object_id) AS table_name,
            c.name AS column_name,
            t.name AS data_type
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE t.name IN ('varchar', 'nvarchar', 'char', 'nchar', 'text', 'ntext')
        AND OBJECT_SCHEMA_NAME(c.object_id) NOT IN ('sys', 'INFORMATION_SCHEMA')
        AND c.max_length > 0
        ORDER BY table_name, column_name
        """

        try:
            cursor = await connection.execute(columns_query)
            columns = await cursor.fetchall()

            for table_name, column_name, data_type in columns:
                column_findings = await self._scan_column(
                    connection, analyzer, table_name, column_name
                )
                findings.extend(column_findings)

        except Exception as e:
            logger.error("pii_scan_failed", error=str(e))

        return findings

    async def _scan_column(
        self,
        connection: Any,
        analyzer: Any,
        table_name: str,
        column_name: str,
    ) -> list[PIIFinding]:
        """Scan a specific column for PII."""
        findings = []

        # Sample data from the column
        sample_query = f"""
        SELECT TOP {self.sample_size} [{column_name}]
        FROM {table_name}
        WHERE [{column_name}] IS NOT NULL
        AND LEN([{column_name}]) > 0
        """

        try:
            cursor = await connection.execute(sample_query)
            rows = await cursor.fetchall()

            if not rows:
                return []

            # Analyze each value
            pii_counts: dict[str, int] = {}
            confidence_sums: dict[str, float] = {}

            for row in rows:
                value = str(row[0]) if row[0] else ""
                if not value or len(value) < 3:
                    continue

                try:
                    results = analyzer.analyze(
                        text=value,
                        entities=self.entities,
                        language="en",
                    )

                    for result in results:
                        if result.score >= self.confidence_threshold:
                            entity = result.entity_type
                            pii_counts[entity] = pii_counts.get(entity, 0) + 1
                            confidence_sums[entity] = confidence_sums.get(entity, 0) + result.score

                except Exception:
                    continue

            # Create findings for detected PII types
            for entity_type, count in pii_counts.items():
                if count >= 5:  # Minimum threshold
                    pii_type = PRESIDIO_TO_PII_TYPE.get(entity_type)
                    if pii_type:
                        avg_confidence = confidence_sums[entity_type] / count

                        findings.append(PIIFinding(
                            table_name=table_name,
                            column_name=column_name,
                            pii_type=pii_type,
                            confidence=avg_confidence,
                            sample_count=count,
                            total_rows_scanned=len(rows),
                            remediation=self._get_remediation(pii_type),
                        ))

        except Exception as e:
            logger.debug("column_scan_failed", table=table_name, column=column_name, error=str(e))

        return findings

    def _get_remediation(self, pii_type: PIIType) -> str:
        """Get remediation recommendation for PII type."""
        remediations = {
            PIIType.SSN: "Encrypt SSN data using Always Encrypted or apply data masking",
            PIIType.CREDIT_CARD: "Tokenize credit card numbers, use PCI-compliant vault",
            PIIType.EMAIL: "Apply dynamic data masking for non-privileged users",
            PIIType.PHONE: "Apply dynamic data masking or partial masking",
            PIIType.ADDRESS: "Consider geographic aggregation or masking",
            PIIType.DATE_OF_BIRTH: "Use age ranges instead of exact dates where possible",
            PIIType.IP_ADDRESS: "Hash or anonymize IP addresses for analytics",
        }
        return remediations.get(pii_type, "Consider encrypting or masking this data")


class EncryptionScanner(BaseScanner):
    """Scan encryption configuration."""

    async def scan(self, connection: Any) -> list[ComplianceResult]:
        """Check encryption status."""
        results = []
        status = await self.get_encryption_status(connection)

        # TDE check
        if status.tde_enabled:
            results.append(ComplianceResult(
                check_id="ENC_TDE",
                check_name="Transparent Data Encryption",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.COMPLIANT,
                message=f"TDE enabled with {status.tde_algorithm}",
                severity=Severity.INFO,
                details={"algorithm": status.tde_algorithm},
            ))
        else:
            results.append(ComplianceResult(
                check_id="ENC_TDE",
                check_name="Transparent Data Encryption",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.NON_COMPLIANT,
                message="TDE is not enabled - data at rest is not encrypted",
                severity=Severity.CRITICAL,
                remediation="Enable TDE: ALTER DATABASE [dbname] SET ENCRYPTION ON",
            ))

        # TLS check
        if status.tls_enforced:
            results.append(ComplianceResult(
                check_id="ENC_TLS",
                check_name="Transport Encryption (TLS)",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.COMPLIANT,
                message=f"TLS enforced, version {status.tls_version or 'unknown'}",
                severity=Severity.INFO,
            ))
        else:
            results.append(ComplianceResult(
                check_id="ENC_TLS",
                check_name="Transport Encryption (TLS)",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.NON_COMPLIANT,
                message="TLS is not enforced for connections",
                severity=Severity.HIGH,
                remediation="Configure SQL Server to require encrypted connections",
            ))

        # Backup encryption
        if status.backup_encryption:
            results.append(ComplianceResult(
                check_id="ENC_BACKUP",
                check_name="Backup Encryption",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.COMPLIANT,
                message="Database backups are encrypted",
                severity=Severity.INFO,
            ))
        else:
            results.append(ComplianceResult(
                check_id="ENC_BACKUP",
                check_name="Backup Encryption",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.NON_COMPLIANT,
                message="Backups are not encrypted",
                severity=Severity.HIGH,
                remediation="Use BACKUP DATABASE ... WITH ENCRYPTION",
            ))

        return results

    async def get_encryption_status(self, connection: Any) -> EncryptionStatus:
        """Get comprehensive encryption status."""
        status = EncryptionStatus()

        # Check TDE
        tde_query = """
        SELECT
            db.is_encrypted,
            ek.encryption_state,
            ek.key_algorithm
        FROM sys.databases db
        LEFT JOIN sys.dm_database_encryption_keys ek
            ON db.database_id = ek.database_id
        WHERE db.database_id = DB_ID()
        """

        try:
            cursor = await connection.execute(tde_query)
            row = await cursor.fetchone()
            if row:
                status.tde_enabled = row[0] == 1 and row[1] == 3
                status.tde_algorithm = row[2]
        except Exception as e:
            logger.debug("tde_check_failed", error=str(e))

        # Check encrypted connections
        tls_query = """
        SELECT encrypt_option, protocol_version
        FROM sys.dm_exec_connections
        WHERE session_id = @@SPID
        """

        try:
            cursor = await connection.execute(tls_query)
            row = await cursor.fetchone()
            if row:
                status.tls_enforced = row[0] == "TRUE"
                status.tls_version = row[1]
        except Exception as e:
            logger.debug("tls_check_failed", error=str(e))

        # Check backup encryption
        backup_query = """
        SELECT TOP 1 encryptor_type
        FROM msdb.dbo.backupset
        WHERE database_name = DB_NAME()
        ORDER BY backup_finish_date DESC
        """

        try:
            cursor = await connection.execute(backup_query)
            row = await cursor.fetchone()
            status.backup_encryption = row and row[0] is not None
        except Exception as e:
            logger.debug("backup_encryption_check_failed", error=str(e))

        # Check Always Encrypted columns
        ae_query = """
        SELECT OBJECT_SCHEMA_NAME(object_id) + '.' + OBJECT_NAME(object_id) + '.' + name
        FROM sys.columns
        WHERE encryption_type IS NOT NULL
        """

        try:
            cursor = await connection.execute(ae_query)
            rows = await cursor.fetchall()
            status.always_encrypted_columns = [r[0] for r in rows] if rows else []
            status.column_encryption = len(status.always_encrypted_columns) > 0
        except Exception as e:
            logger.debug("ae_check_failed", error=str(e))

        return status


class AccessControlScanner(BaseScanner):
    """Scan access control configuration."""

    async def scan(self, connection: Any) -> list[ComplianceResult]:
        """Check access control configuration."""
        results = []
        findings = await self.get_access_findings(connection)

        excessive = [f for f in findings if f.is_excessive]

        if excessive:
            results.append(ComplianceResult(
                check_id="ACCESS_EXCESSIVE",
                check_name="Excessive Privileges",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.NON_COMPLIANT,
                message=f"Found {len(excessive)} users/roles with excessive privileges",
                severity=Severity.HIGH,
                details={
                    "findings": [f.to_dict() for f in excessive[:10]],
                },
                remediation="Review and revoke unnecessary permissions",
            ))
        else:
            results.append(ComplianceResult(
                check_id="ACCESS_EXCESSIVE",
                check_name="Excessive Privileges",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.COMPLIANT,
                message="No excessive privileges detected",
                severity=Severity.INFO,
            ))

        # Check for public role permissions
        public_perms = [f for f in findings if f.principal_name.lower() == "public"]
        if public_perms:
            results.append(ComplianceResult(
                check_id="ACCESS_PUBLIC",
                check_name="Public Role Permissions",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.NON_COMPLIANT,
                message=f"Public role has {len(public_perms)} explicit permissions",
                severity=Severity.MEDIUM,
                details={
                    "permissions": [f"{f.permission} on {f.object_name}" for f in public_perms],
                },
                remediation="Remove permissions from public role",
            ))

        return results

    async def get_access_findings(self, connection: Any) -> list[AccessControlFinding]:
        """Get access control findings."""
        findings = []

        # Check for high-privilege assignments
        priv_query = """
        SELECT
            dp.name AS principal_name,
            dp.type_desc AS principal_type,
            perm.permission_name,
            ISNULL(OBJECT_SCHEMA_NAME(perm.major_id) + '.' + OBJECT_NAME(perm.major_id), 'DATABASE') AS object_name,
            ISNULL(o.type_desc, 'DATABASE') AS object_type
        FROM sys.database_permissions perm
        JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
        LEFT JOIN sys.objects o ON perm.major_id = o.object_id
        WHERE perm.state = 'G'
        AND dp.name NOT IN ('dbo', 'guest', 'INFORMATION_SCHEMA', 'sys')
        ORDER BY dp.name, object_name
        """

        try:
            cursor = await connection.execute(priv_query)
            rows = await cursor.fetchall()

            excessive_perms = {"CONTROL", "ALTER", "TAKE OWNERSHIP", "ALTER ANY"}

            for row in rows:
                is_excessive = row[2] in excessive_perms

                findings.append(AccessControlFinding(
                    principal_name=row[0],
                    principal_type=row[1],
                    permission=row[2],
                    object_name=row[3],
                    object_type=row[4],
                    is_excessive=is_excessive,
                    recommendation="Consider using more granular permissions" if is_excessive else None,
                ))

        except Exception as e:
            logger.debug("access_scan_failed", error=str(e))

        return findings


class AuditScanner(BaseScanner):
    """Scan audit configuration."""

    async def scan(self, connection: Any) -> list[ComplianceResult]:
        """Check audit configuration."""
        results = []

        # Check for SQL Server Audit
        audit_query = """
        SELECT
            a.name AS audit_name,
            a.status_desc,
            s.name AS spec_name,
            s.is_state_enabled
        FROM sys.server_audits a
        LEFT JOIN sys.server_audit_specifications s
            ON a.audit_guid = s.audit_guid
        WHERE a.is_state_enabled = 1
        """

        try:
            cursor = await connection.execute(audit_query)
            rows = await cursor.fetchall()

            if rows:
                results.append(ComplianceResult(
                    check_id="AUDIT_CONFIG",
                    check_name="SQL Server Audit",
                    framework=ComplianceFramework.SOC2,
                    status=ComplianceStatus.COMPLIANT,
                    message=f"Found {len(rows)} active audit configuration(s)",
                    severity=Severity.INFO,
                    details={"audits": [r[0] for r in rows]},
                ))
            else:
                results.append(ComplianceResult(
                    check_id="AUDIT_CONFIG",
                    check_name="SQL Server Audit",
                    framework=ComplianceFramework.SOC2,
                    status=ComplianceStatus.NON_COMPLIANT,
                    message="No active SQL Server Audit found",
                    severity=Severity.HIGH,
                    remediation="Create and enable SQL Server Audit for compliance tracking",
                ))

        except Exception as e:
            results.append(ComplianceResult(
                check_id="AUDIT_CONFIG",
                check_name="SQL Server Audit",
                framework=ComplianceFramework.SOC2,
                status=ComplianceStatus.ERROR,
                message=f"Failed to check audit configuration: {str(e)}",
                severity=Severity.MEDIUM,
            ))

        return results
