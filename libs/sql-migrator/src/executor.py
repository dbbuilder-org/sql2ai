"""Migration executor for applying migrations to databases."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import structlog

from models import Migration, MigrationStatus, MigrationStep

logger = structlog.get_logger()


@dataclass
class ExecutionResult:
    """Result of a migration execution."""

    migration_id: str
    success: bool
    status: MigrationStatus
    steps_executed: int
    steps_total: int
    duration_ms: int
    error_message: Optional[str] = None
    error_step: Optional[int] = None
    applied_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "migration_id": self.migration_id,
            "success": self.success,
            "status": self.status.value,
            "steps_executed": self.steps_executed,
            "steps_total": self.steps_total,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "error_step": self.error_step,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
        }


@dataclass
class RollbackResult:
    """Result of a rollback execution."""

    migration_id: str
    success: bool
    steps_rolled_back: int
    duration_ms: int
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "migration_id": self.migration_id,
            "success": self.success,
            "steps_rolled_back": self.steps_rolled_back,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
        }


class MigrationExecutor:
    """Executes migrations against a database."""

    def __init__(
        self,
        connection: Any,
        dialect: str = "sqlserver",
        dry_run: bool = False,
        transaction_per_step: bool = False,
    ):
        """Initialize executor.

        Args:
            connection: Database connection
            dialect: SQL dialect (sqlserver, postgresql)
            dry_run: If True, don't actually execute, just validate
            transaction_per_step: If True, commit after each step
        """
        self.connection = connection
        self.dialect = dialect
        self.dry_run = dry_run
        self.transaction_per_step = transaction_per_step
        self._migration_table_created = False

    async def ensure_migration_table(self):
        """Ensure migration tracking table exists."""
        if self._migration_table_created:
            return

        if self.dialect == "sqlserver":
            sql = """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__migrations')
            BEGIN
                CREATE TABLE __migrations (
                    id NVARCHAR(100) PRIMARY KEY,
                    name NVARCHAR(255) NOT NULL,
                    version NVARCHAR(50) NOT NULL,
                    checksum NVARCHAR(32) NOT NULL,
                    applied_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
                    applied_by NVARCHAR(255),
                    duration_ms INT,
                    status NVARCHAR(20) NOT NULL
                )
            END
            """
        else:
            sql = """
            CREATE TABLE IF NOT EXISTS __migrations (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                version VARCHAR(50) NOT NULL,
                checksum VARCHAR(32) NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
                applied_by VARCHAR(255),
                duration_ms INT,
                status VARCHAR(20) NOT NULL
            )
            """

        if not self.dry_run:
            await self.connection.execute(sql)

        self._migration_table_created = True

    async def get_applied_migrations(self) -> list[dict]:
        """Get list of already applied migrations."""
        await self.ensure_migration_table()

        sql = """
        SELECT id, name, version, checksum, applied_at, status
        FROM __migrations
        ORDER BY applied_at
        """

        try:
            cursor = await self.connection.execute(sql)
            rows = await cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "version": r[2],
                    "checksum": r[3],
                    "applied_at": r[4],
                    "status": r[5],
                }
                for r in rows
            ]
        except Exception:
            return []

    async def is_applied(self, migration_id: str) -> bool:
        """Check if a migration has been applied."""
        applied = await self.get_applied_migrations()
        return any(m["id"] == migration_id for m in applied)

    async def execute(
        self,
        migration: Migration,
        applied_by: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a migration.

        Args:
            migration: Migration to execute
            applied_by: User/system applying the migration

        Returns:
            ExecutionResult with status
        """
        start_time = time.perf_counter()
        steps_executed = 0

        logger.info(
            "migration_execution_started",
            migration_id=migration.id,
            name=migration.name,
            steps=len(migration.steps),
            dry_run=self.dry_run,
        )

        # Check if already applied
        if await self.is_applied(migration.id):
            return ExecutionResult(
                migration_id=migration.id,
                success=False,
                status=MigrationStatus.FAILED,
                steps_executed=0,
                steps_total=len(migration.steps),
                duration_ms=0,
                error_message="Migration already applied",
            )

        await self.ensure_migration_table()

        try:
            # Execute steps in order
            for step in sorted(migration.steps, key=lambda s: s.order):
                if self.dry_run:
                    logger.info(
                        "dry_run_step",
                        step=step.order,
                        description=step.description,
                    )
                    steps_executed += 1
                    continue

                try:
                    await self._execute_step(step)
                    steps_executed += 1

                    if self.transaction_per_step:
                        await self.connection.commit()

                except Exception as e:
                    duration = int((time.perf_counter() - start_time) * 1000)

                    logger.error(
                        "migration_step_failed",
                        migration_id=migration.id,
                        step=step.order,
                        error=str(e),
                    )

                    # Try to rollback executed steps
                    if not self.transaction_per_step:
                        try:
                            await self.connection.rollback()
                        except Exception:
                            pass

                    return ExecutionResult(
                        migration_id=migration.id,
                        success=False,
                        status=MigrationStatus.FAILED,
                        steps_executed=steps_executed,
                        steps_total=len(migration.steps),
                        duration_ms=duration,
                        error_message=str(e),
                        error_step=step.order,
                    )

            duration = int((time.perf_counter() - start_time) * 1000)

            # Record migration
            if not self.dry_run:
                await self._record_migration(migration, applied_by, duration)
                await self.connection.commit()

            migration.status = MigrationStatus.APPLIED
            migration.applied_at = datetime.utcnow()
            migration.applied_by = applied_by

            logger.info(
                "migration_execution_completed",
                migration_id=migration.id,
                steps_executed=steps_executed,
                duration_ms=duration,
            )

            return ExecutionResult(
                migration_id=migration.id,
                success=True,
                status=MigrationStatus.APPLIED,
                steps_executed=steps_executed,
                steps_total=len(migration.steps),
                duration_ms=duration,
                applied_at=datetime.utcnow(),
            )

        except Exception as e:
            duration = int((time.perf_counter() - start_time) * 1000)

            logger.error(
                "migration_execution_failed",
                migration_id=migration.id,
                error=str(e),
            )

            return ExecutionResult(
                migration_id=migration.id,
                success=False,
                status=MigrationStatus.FAILED,
                steps_executed=steps_executed,
                steps_total=len(migration.steps),
                duration_ms=duration,
                error_message=str(e),
            )

    async def _execute_step(self, step: MigrationStep):
        """Execute a single migration step."""
        logger.debug(
            "executing_step",
            order=step.order,
            description=step.description,
        )

        # Split SQL into statements and execute each
        statements = self._split_statements(step.forward_sql)

        for statement in statements:
            statement = statement.strip()
            if statement:
                await self.connection.execute(statement)

    def _split_statements(self, sql: str) -> list[str]:
        """Split SQL into individual statements."""
        # Handle GO statements for SQL Server
        if self.dialect == "sqlserver":
            # Split on GO (case insensitive, whole word)
            import re
            statements = re.split(r'\bGO\b', sql, flags=re.IGNORECASE)
        else:
            # Split on semicolons for other dialects
            statements = sql.split(';')

        return [s.strip() for s in statements if s.strip()]

    async def _record_migration(
        self,
        migration: Migration,
        applied_by: Optional[str],
        duration_ms: int,
    ):
        """Record migration in tracking table."""
        sql = """
        INSERT INTO __migrations (id, name, version, checksum, applied_by, duration_ms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        await self.connection.execute(
            sql,
            migration.id,
            migration.name,
            migration.version,
            migration.checksum,
            applied_by,
            duration_ms,
            MigrationStatus.APPLIED.value,
        )

    async def rollback(self, migration: Migration) -> RollbackResult:
        """Rollback a migration.

        Args:
            migration: Migration to rollback

        Returns:
            RollbackResult with status
        """
        start_time = time.perf_counter()
        steps_rolled_back = 0

        logger.info(
            "migration_rollback_started",
            migration_id=migration.id,
            name=migration.name,
        )

        try:
            # Execute rollback steps in reverse order
            for step in sorted(migration.steps, key=lambda s: s.order, reverse=True):
                if not step.rollback_sql:
                    logger.warning(
                        "no_rollback_sql",
                        step=step.order,
                        description=step.description,
                    )
                    continue

                if self.dry_run:
                    logger.info(
                        "dry_run_rollback_step",
                        step=step.order,
                        description=step.description,
                    )
                    steps_rolled_back += 1
                    continue

                try:
                    statements = self._split_statements(step.rollback_sql)
                    for statement in statements:
                        if statement.strip():
                            await self.connection.execute(statement)
                    steps_rolled_back += 1

                except Exception as e:
                    duration = int((time.perf_counter() - start_time) * 1000)

                    logger.error(
                        "rollback_step_failed",
                        migration_id=migration.id,
                        step=step.order,
                        error=str(e),
                    )

                    return RollbackResult(
                        migration_id=migration.id,
                        success=False,
                        steps_rolled_back=steps_rolled_back,
                        duration_ms=duration,
                        error_message=str(e),
                    )

            duration = int((time.perf_counter() - start_time) * 1000)

            # Update migration record
            if not self.dry_run:
                await self._update_migration_status(
                    migration.id,
                    MigrationStatus.ROLLED_BACK,
                )
                await self.connection.commit()

            migration.status = MigrationStatus.ROLLED_BACK

            logger.info(
                "migration_rollback_completed",
                migration_id=migration.id,
                steps_rolled_back=steps_rolled_back,
                duration_ms=duration,
            )

            return RollbackResult(
                migration_id=migration.id,
                success=True,
                steps_rolled_back=steps_rolled_back,
                duration_ms=duration,
            )

        except Exception as e:
            duration = int((time.perf_counter() - start_time) * 1000)

            logger.error(
                "migration_rollback_failed",
                migration_id=migration.id,
                error=str(e),
            )

            return RollbackResult(
                migration_id=migration.id,
                success=False,
                steps_rolled_back=steps_rolled_back,
                duration_ms=duration,
                error_message=str(e),
            )

    async def _update_migration_status(self, migration_id: str, status: MigrationStatus):
        """Update migration status in tracking table."""
        sql = "UPDATE __migrations SET status = ? WHERE id = ?"
        await self.connection.execute(sql, status.value, migration_id)

    async def validate(self, migration: Migration) -> tuple[bool, list[str]]:
        """Validate a migration before execution.

        Args:
            migration: Migration to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for empty migration
        if not migration.steps:
            errors.append("Migration has no steps")

        # Check for missing rollback scripts
        steps_without_rollback = [
            s for s in migration.steps if not s.rollback_sql
        ]
        if steps_without_rollback:
            for step in steps_without_rollback:
                errors.append(f"Step {step.order} has no rollback script")

        # Check checksum
        if migration.checksum != migration._calculate_checksum():
            errors.append("Migration checksum mismatch - content may have been modified")

        # Syntax validation (basic)
        for step in migration.steps:
            sql_errors = self._validate_sql_syntax(step.forward_sql)
            for err in sql_errors:
                errors.append(f"Step {step.order} SQL error: {err}")

        return len(errors) == 0, errors

    def _validate_sql_syntax(self, sql: str) -> list[str]:
        """Basic SQL syntax validation."""
        errors = []

        # Check for common issues
        sql_upper = sql.upper()

        # Check for dangerous patterns
        dangerous_patterns = [
            ("DROP DATABASE", "DROP DATABASE statements are not allowed"),
            ("TRUNCATE", "TRUNCATE statements require explicit approval"),
            ("xp_", "Extended stored procedures (xp_) are not allowed"),
            ("sp_configure", "sp_configure is not allowed in migrations"),
        ]

        for pattern, message in dangerous_patterns:
            if pattern in sql_upper:
                errors.append(message)

        return errors
