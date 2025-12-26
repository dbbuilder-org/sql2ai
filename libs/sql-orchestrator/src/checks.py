"""Check implementations for SQL Orchestrator."""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

import structlog

from models import (
    CheckCategory,
    CheckDefinition,
    CheckResult,
    CheckSeverity,
    CheckStatus,
)

logger = structlog.get_logger()


class BaseCheck(ABC):
    """Base class for all checks."""

    def __init__(self, definition: CheckDefinition):
        self.definition = definition
        self.id = definition.id
        self.name = definition.name
        self.category = definition.category
        self.severity = definition.default_severity

    @abstractmethod
    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        """Execute the check and return result."""
        pass

    def _create_result(
        self,
        status: CheckStatus,
        message: str,
        details: Optional[dict] = None,
        remediation: Optional[str] = None,
        affected_objects: Optional[list[str]] = None,
        duration_ms: int = 0,
    ) -> CheckResult:
        """Create a check result."""
        return CheckResult(
            check_id=self.id,
            check_name=self.name,
            category=self.category,
            severity=self.severity,
            status=status,
            message=message,
            details=details or {},
            remediation=remediation,
            affected_objects=affected_objects or [],
            duration_ms=duration_ms,
        )


class PerformanceCheck(BaseCheck):
    """Performance-related checks."""

    pass


class SecurityCheck(BaseCheck):
    """Security-related checks."""

    pass


class ComplianceCheck(BaseCheck):
    """Compliance-related checks."""

    pass


# Built-in check implementations

class MissingIndexCheck(PerformanceCheck):
    """Check for missing indexes on foreign key columns."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()

        query = """
        SELECT
            OBJECT_SCHEMA_NAME(fk.parent_object_id) AS schema_name,
            OBJECT_NAME(fk.parent_object_id) AS table_name,
            COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS column_name,
            fk.name AS fk_name
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc
            ON fk.object_id = fkc.constraint_object_id
        WHERE NOT EXISTS (
            SELECT 1 FROM sys.index_columns ic
            WHERE ic.object_id = fkc.parent_object_id
            AND ic.column_id = fkc.parent_column_id
        )
        ORDER BY schema_name, table_name
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            duration = int((time.perf_counter() - start) * 1000)

            if not rows:
                return self._create_result(
                    status=CheckStatus.PASSED,
                    message="All foreign key columns have indexes",
                    duration_ms=duration,
                )

            affected = [f"{r[0]}.{r[1]}.{r[2]}" for r in rows]
            return self._create_result(
                status=CheckStatus.WARNING,
                message=f"Found {len(rows)} foreign key columns without indexes",
                details={"missing_indexes": [
                    {"schema": r[0], "table": r[1], "column": r[2], "fk": r[3]}
                    for r in rows
                ]},
                remediation="Create indexes on foreign key columns to improve join performance",
                affected_objects=affected,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check missing indexes: {str(e)}",
                duration_ms=duration,
            )


class FragmentedIndexCheck(PerformanceCheck):
    """Check for fragmented indexes."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()
        threshold = self.definition.parameters.get("fragmentation_threshold", 30)

        query = f"""
        SELECT
            OBJECT_SCHEMA_NAME(ips.object_id) AS schema_name,
            OBJECT_NAME(ips.object_id) AS table_name,
            i.name AS index_name,
            ips.avg_fragmentation_in_percent,
            ips.page_count
        FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
        INNER JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
        WHERE ips.avg_fragmentation_in_percent > {threshold}
        AND ips.page_count > 1000
        AND i.name IS NOT NULL
        ORDER BY ips.avg_fragmentation_in_percent DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            duration = int((time.perf_counter() - start) * 1000)

            if not rows:
                return self._create_result(
                    status=CheckStatus.PASSED,
                    message=f"No indexes with fragmentation above {threshold}%",
                    duration_ms=duration,
                )

            critical = [r for r in rows if r[3] > 80]
            affected = [f"{r[0]}.{r[1]}.{r[2]}" for r in rows]

            return self._create_result(
                status=CheckStatus.FAILED if critical else CheckStatus.WARNING,
                message=f"Found {len(rows)} fragmented indexes ({len(critical)} critical)",
                details={"fragmented_indexes": [
                    {"schema": r[0], "table": r[1], "index": r[2],
                     "fragmentation": round(r[3], 2), "pages": r[4]}
                    for r in rows
                ]},
                remediation="Rebuild or reorganize fragmented indexes during maintenance window",
                affected_objects=affected,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check index fragmentation: {str(e)}",
                duration_ms=duration,
            )


class TDEEncryptionCheck(SecurityCheck):
    """Check if Transparent Data Encryption is enabled."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()

        query = """
        SELECT
            db.name AS database_name,
            db.is_encrypted,
            ek.encryption_state,
            ek.key_algorithm,
            ek.key_length
        FROM sys.databases db
        LEFT JOIN sys.dm_database_encryption_keys ek
            ON db.database_id = ek.database_id
        WHERE db.database_id = DB_ID()
        """

        try:
            cursor = await connection.execute(query)
            row = await cursor.fetchone()
            duration = int((time.perf_counter() - start) * 1000)

            if not row:
                return self._create_result(
                    status=CheckStatus.ERROR,
                    message="Could not determine encryption status",
                    duration_ms=duration,
                )

            is_encrypted = row[1] == 1
            encryption_state = row[2]

            if is_encrypted and encryption_state == 3:
                return self._create_result(
                    status=CheckStatus.PASSED,
                    message="Database has TDE encryption enabled and active",
                    details={
                        "algorithm": row[3],
                        "key_length": row[4],
                        "state": "encrypted"
                    },
                    duration_ms=duration,
                )

            return self._create_result(
                status=CheckStatus.FAILED,
                message="Database does not have TDE encryption enabled",
                remediation="Enable TDE using ALTER DATABASE SET ENCRYPTION ON",
                details={"is_encrypted": is_encrypted, "state": encryption_state},
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check TDE status: {str(e)}",
                duration_ms=duration,
            )


class WeakPasswordPolicyCheck(SecurityCheck):
    """Check for SQL logins without password policy enforcement."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()

        query = """
        SELECT
            name,
            is_policy_checked,
            is_expiration_checked,
            create_date,
            modify_date
        FROM sys.sql_logins
        WHERE is_disabled = 0
        AND (is_policy_checked = 0 OR is_expiration_checked = 0)
        AND name NOT LIKE '##%'
        ORDER BY name
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            duration = int((time.perf_counter() - start) * 1000)

            if not rows:
                return self._create_result(
                    status=CheckStatus.PASSED,
                    message="All SQL logins have password policy enforced",
                    duration_ms=duration,
                )

            affected = [r[0] for r in rows]
            return self._create_result(
                status=CheckStatus.FAILED,
                message=f"Found {len(rows)} SQL logins without proper password policy",
                details={"weak_logins": [
                    {"name": r[0], "policy_checked": r[1], "expiration_checked": r[2]}
                    for r in rows
                ]},
                remediation="ALTER LOGIN [login_name] WITH CHECK_POLICY = ON, CHECK_EXPIRATION = ON",
                affected_objects=affected,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check password policies: {str(e)}",
                duration_ms=duration,
            )


class AuditConfigurationCheck(ComplianceCheck):
    """Check if SQL Server Audit is properly configured."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()

        query = """
        SELECT
            a.name AS audit_name,
            a.status_desc,
            a.type_desc AS destination,
            s.name AS spec_name,
            s.is_state_enabled
        FROM sys.server_audits a
        LEFT JOIN sys.server_audit_specifications s
            ON a.audit_guid = s.audit_guid
        WHERE a.is_state_enabled = 1
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            duration = int((time.perf_counter() - start) * 1000)

            if not rows:
                return self._create_result(
                    status=CheckStatus.FAILED,
                    message="No active SQL Server Audit found",
                    remediation="Create and enable a SQL Server Audit for compliance tracking",
                    duration_ms=duration,
                )

            return self._create_result(
                status=CheckStatus.PASSED,
                message=f"Found {len(rows)} active audit configuration(s)",
                details={"audits": [
                    {"audit": r[0], "status": r[1], "destination": r[2],
                     "spec": r[3], "enabled": r[4]}
                    for r in rows
                ]},
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check audit configuration: {str(e)}",
                duration_ms=duration,
            )


class BackupRecencyCheck(ComplianceCheck):
    """Check if databases have recent backups."""

    async def execute(self, connection: Any, **kwargs) -> CheckResult:
        start = time.perf_counter()
        max_hours = self.definition.parameters.get("max_backup_age_hours", 24)

        query = f"""
        SELECT
            d.name AS database_name,
            d.recovery_model_desc,
            MAX(b.backup_finish_date) AS last_backup,
            DATEDIFF(HOUR, MAX(b.backup_finish_date), GETDATE()) AS hours_since_backup
        FROM sys.databases d
        LEFT JOIN msdb.dbo.backupset b ON d.name = b.database_name
        WHERE d.database_id > 4
        AND d.state_desc = 'ONLINE'
        GROUP BY d.name, d.recovery_model_desc
        HAVING MAX(b.backup_finish_date) IS NULL
            OR DATEDIFF(HOUR, MAX(b.backup_finish_date), GETDATE()) > {max_hours}
        ORDER BY hours_since_backup DESC
        """

        try:
            cursor = await connection.execute(query)
            rows = await cursor.fetchall()
            duration = int((time.perf_counter() - start) * 1000)

            if not rows:
                return self._create_result(
                    status=CheckStatus.PASSED,
                    message=f"All databases backed up within {max_hours} hours",
                    duration_ms=duration,
                )

            no_backup = [r for r in rows if r[2] is None]
            old_backup = [r for r in rows if r[2] is not None]

            affected = [r[0] for r in rows]
            return self._create_result(
                status=CheckStatus.CRITICAL if no_backup else CheckStatus.FAILED,
                message=f"Found {len(rows)} databases with backup issues ({len(no_backup)} never backed up)",
                details={
                    "no_backup": [{"database": r[0], "recovery_model": r[1]} for r in no_backup],
                    "old_backup": [
                        {"database": r[0], "last_backup": str(r[2]), "hours_ago": r[3]}
                        for r in old_backup
                    ],
                },
                remediation=f"Ensure all databases are backed up at least every {max_hours} hours",
                affected_objects=affected,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((time.perf_counter() - start) * 1000)
            return self._create_result(
                status=CheckStatus.ERROR,
                message=f"Failed to check backup recency: {str(e)}",
                duration_ms=duration,
            )


class CheckRegistry:
    """Registry of all available checks."""

    def __init__(self):
        self._checks: dict[str, type[BaseCheck]] = {}
        self._definitions: dict[str, CheckDefinition] = {}
        self._register_builtin_checks()

    def _register_builtin_checks(self):
        """Register built-in checks."""
        builtin = [
            (MissingIndexCheck, CheckDefinition(
                id="PERF001",
                name="Missing Foreign Key Indexes",
                description="Detects foreign key columns without indexes",
                category=CheckCategory.PERFORMANCE,
                default_severity=CheckSeverity.MEDIUM,
                frameworks=["SOC2"],
                tags=["performance", "indexes"],
            )),
            (FragmentedIndexCheck, CheckDefinition(
                id="PERF002",
                name="Fragmented Indexes",
                description="Detects indexes with high fragmentation",
                category=CheckCategory.PERFORMANCE,
                default_severity=CheckSeverity.MEDIUM,
                parameters={"fragmentation_threshold": 30},
                frameworks=["SOC2"],
                tags=["performance", "indexes", "maintenance"],
            )),
            (TDEEncryptionCheck, CheckDefinition(
                id="SEC001",
                name="TDE Encryption",
                description="Checks if Transparent Data Encryption is enabled",
                category=CheckCategory.SECURITY,
                default_severity=CheckSeverity.CRITICAL,
                frameworks=["SOC2", "HIPAA", "PCI-DSS", "GDPR"],
                tags=["security", "encryption", "compliance"],
            )),
            (WeakPasswordPolicyCheck, CheckDefinition(
                id="SEC002",
                name="Password Policy Enforcement",
                description="Checks for SQL logins without password policy",
                category=CheckCategory.SECURITY,
                default_severity=CheckSeverity.HIGH,
                frameworks=["SOC2", "HIPAA", "PCI-DSS"],
                tags=["security", "authentication", "compliance"],
            )),
            (AuditConfigurationCheck, CheckDefinition(
                id="COMP001",
                name="Audit Configuration",
                description="Checks if SQL Server Audit is configured",
                category=CheckCategory.COMPLIANCE,
                default_severity=CheckSeverity.HIGH,
                frameworks=["SOC2", "HIPAA", "PCI-DSS", "GDPR"],
                tags=["compliance", "audit", "security"],
            )),
            (BackupRecencyCheck, CheckDefinition(
                id="COMP002",
                name="Backup Recency",
                description="Checks if databases have recent backups",
                category=CheckCategory.COMPLIANCE,
                default_severity=CheckSeverity.CRITICAL,
                parameters={"max_backup_age_hours": 24},
                frameworks=["SOC2", "HIPAA"],
                tags=["compliance", "backup", "disaster-recovery"],
            )),
        ]

        for check_class, definition in builtin:
            self.register(check_class, definition)

    def register(self, check_class: type[BaseCheck], definition: CheckDefinition):
        """Register a check."""
        self._checks[definition.id] = check_class
        self._definitions[definition.id] = definition
        logger.debug("check_registered", check_id=definition.id, name=definition.name)

    def get_check(self, check_id: str) -> Optional[BaseCheck]:
        """Get a check instance by ID."""
        if check_id not in self._checks:
            return None
        return self._checks[check_id](self._definitions[check_id])

    def get_definition(self, check_id: str) -> Optional[CheckDefinition]:
        """Get a check definition by ID."""
        return self._definitions.get(check_id)

    def list_checks(
        self,
        category: Optional[CheckCategory] = None,
        framework: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[CheckDefinition]:
        """List available checks with optional filtering."""
        results = []
        for definition in self._definitions.values():
            if not definition.enabled:
                continue
            if category and definition.category != category:
                continue
            if framework and framework not in definition.frameworks:
                continue
            if tags and not any(t in definition.tags for t in tags):
                continue
            results.append(definition)
        return results

    def get_checks_for_framework(self, framework: str) -> list[BaseCheck]:
        """Get all checks applicable to a compliance framework."""
        checks = []
        for check_id, definition in self._definitions.items():
            if framework in definition.frameworks and definition.enabled:
                checks.append(self._checks[check_id](definition))
        return checks
