"""Audit logger implementation with tamper-proof storage."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from pydantic import BaseModel
import structlog
import asyncio

from sql2ai_shared.audit.models import (
    AuditAction,
    AuditEntry,
    AuditQuery,
    AuditSeverity,
    AuditSummary,
    get_action_severity,
)
from sql2ai_shared.tenancy.context import get_current_tenant

logger = structlog.get_logger()


class AuditConfig(BaseModel):
    """Audit logger configuration."""

    enabled: bool = True
    buffer_size: int = 100
    flush_interval_seconds: int = 5
    retention_days: int = 365
    hash_chain_enabled: bool = True
    compliance_frameworks: List[str] = []
    async_write: bool = True


class AuditStorage(ABC):
    """Abstract base class for audit storage backends."""

    @abstractmethod
    async def write(self, entry: AuditEntry) -> None:
        """Write an audit entry."""
        pass

    @abstractmethod
    async def write_batch(self, entries: List[AuditEntry]) -> None:
        """Write multiple audit entries."""
        pass

    @abstractmethod
    async def query(self, query: AuditQuery) -> List[AuditEntry]:
        """Query audit entries."""
        pass

    @abstractmethod
    async def get_by_id(self, entry_id: str) -> Optional[AuditEntry]:
        """Get an audit entry by ID."""
        pass

    @abstractmethod
    async def get_last_hash(self, tenant_id: str) -> Optional[str]:
        """Get the last hash in the chain for a tenant."""
        pass

    @abstractmethod
    async def verify_chain(
        self, tenant_id: str, start_id: str, end_id: str
    ) -> bool:
        """Verify the integrity of the hash chain."""
        pass


class PostgreSQLAuditStorage(AuditStorage):
    """PostgreSQL-based audit storage with hash chain verification."""

    def __init__(self, pool):
        self.pool = pool

    async def write(self, entry: AuditEntry) -> None:
        """Write an audit entry to PostgreSQL."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_log (
                    id, timestamp, user_id, user_email, user_ip, user_agent,
                    session_id, tenant_id, action, severity, resource_type,
                    resource_id, resource_name, details, old_value, new_value,
                    success, error_message, previous_hash, entry_hash,
                    compliance_frameworks, retention_days, immutable
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                    $14, $15, $16, $17, $18, $19, $20, $21, $22, $23
                )
                """,
                entry.id,
                entry.timestamp,
                entry.user_id,
                entry.user_email,
                entry.user_ip,
                entry.user_agent,
                entry.session_id,
                entry.tenant_id,
                entry.action.value,
                entry.severity.value,
                entry.resource_type,
                entry.resource_id,
                entry.resource_name,
                entry.details,
                entry.old_value,
                entry.new_value,
                entry.success,
                entry.error_message,
                entry.previous_hash,
                entry.entry_hash,
                entry.compliance_frameworks,
                entry.retention_days,
                entry.immutable,
            )

    async def write_batch(self, entries: List[AuditEntry]) -> None:
        """Write multiple audit entries."""
        for entry in entries:
            await self.write(entry)

    async def query(self, query: AuditQuery) -> List[AuditEntry]:
        """Query audit entries."""
        conditions = ["tenant_id = $1"]
        params = [query.tenant_id]
        param_idx = 2

        if query.start_date:
            conditions.append(f"timestamp >= ${param_idx}")
            params.append(query.start_date)
            param_idx += 1

        if query.end_date:
            conditions.append(f"timestamp <= ${param_idx}")
            params.append(query.end_date)
            param_idx += 1

        if query.user_id:
            conditions.append(f"user_id = ${param_idx}")
            params.append(query.user_id)
            param_idx += 1

        if query.actions:
            placeholders = ", ".join(
                f"${i}" for i in range(param_idx, param_idx + len(query.actions))
            )
            conditions.append(f"action IN ({placeholders})")
            params.extend(a.value for a in query.actions)
            param_idx += len(query.actions)

        if query.resource_type:
            conditions.append(f"resource_type = ${param_idx}")
            params.append(query.resource_type)
            param_idx += 1

        if query.success is not None:
            conditions.append(f"success = ${param_idx}")
            params.append(query.success)
            param_idx += 1

        where_clause = " AND ".join(conditions)
        order = "DESC" if query.order_desc else "ASC"

        sql = f"""
            SELECT * FROM audit_log
            WHERE {where_clause}
            ORDER BY {query.order_by} {order}
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([query.limit, query.offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [AuditEntry(**dict(row)) for row in rows]

    async def get_by_id(self, entry_id: str) -> Optional[AuditEntry]:
        """Get an audit entry by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM audit_log WHERE id = $1", entry_id
            )
            return AuditEntry(**dict(row)) if row else None

    async def get_last_hash(self, tenant_id: str) -> Optional[str]:
        """Get the last hash in the chain for a tenant."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT entry_hash FROM audit_log
                WHERE tenant_id = $1
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                tenant_id,
            )
            return row["entry_hash"] if row else None

    async def verify_chain(
        self, tenant_id: str, start_id: str, end_id: str
    ) -> bool:
        """Verify the integrity of the hash chain."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, previous_hash, entry_hash FROM audit_log
                WHERE tenant_id = $1
                AND timestamp >= (SELECT timestamp FROM audit_log WHERE id = $2)
                AND timestamp <= (SELECT timestamp FROM audit_log WHERE id = $3)
                ORDER BY timestamp ASC
                """,
                tenant_id,
                start_id,
                end_id,
            )

            if not rows:
                return True

            # Verify chain integrity
            expected_prev_hash = rows[0]["previous_hash"]
            for row in rows:
                if row["previous_hash"] != expected_prev_hash:
                    return False
                expected_prev_hash = row["entry_hash"]

            return True


class AuditLogger:
    """Main audit logger with buffering and hash chaining."""

    def __init__(
        self,
        config: AuditConfig,
        storage: Optional[AuditStorage] = None,
    ):
        self.config = config
        self.storage = storage
        self._buffer: List[AuditEntry] = []
        self._last_hash: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the audit logger (begins periodic flushing)."""
        if self.config.async_write:
            self._flush_task = asyncio.create_task(self._periodic_flush())
            logger.info("audit_logger_started")

    async def stop(self) -> None:
        """Stop the audit logger and flush remaining entries."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        await self._flush()
        logger.info("audit_logger_stopped")

    async def _periodic_flush(self) -> None:
        """Periodically flush the buffer."""
        while True:
            await asyncio.sleep(self.config.flush_interval_seconds)
            await self._flush()

    async def _flush(self) -> None:
        """Flush buffered entries to storage."""
        async with self._lock:
            if not self._buffer or not self.storage:
                return

            entries = self._buffer.copy()
            self._buffer.clear()

        try:
            await self.storage.write_batch(entries)
            logger.debug("audit_entries_flushed", count=len(entries))
        except Exception as e:
            logger.error("audit_flush_failed", error=str(e))
            # Re-add entries to buffer
            async with self._lock:
                self._buffer = entries + self._buffer

    async def log(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
    ) -> AuditEntry:
        """Log an audit event."""
        if not self.config.enabled:
            return None

        # Get tenant context
        tenant = get_current_tenant()
        tenant_id = tenant.id if tenant else "unknown"

        # Create entry
        entry = AuditEntry(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            user_ip=user_ip,
            user_agent=user_agent,
            session_id=session_id,
            action=action,
            severity=severity or get_action_severity(action),
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details or {},
            old_value=old_value,
            new_value=new_value,
            success=success,
            error_message=error_message,
            compliance_frameworks=self.config.compliance_frameworks,
            retention_days=self.config.retention_days,
        )

        # Add hash chain
        if self.config.hash_chain_enabled:
            previous_hash = self._last_hash.get(tenant_id)
            if not previous_hash and self.storage:
                previous_hash = await self.storage.get_last_hash(tenant_id)
            entry.set_hash(previous_hash)
            self._last_hash[tenant_id] = entry.entry_hash

        # Log to structured logger
        logger.info(
            "audit_event",
            audit_id=entry.id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            success=success,
        )

        # Buffer or write directly
        if self.config.async_write:
            async with self._lock:
                self._buffer.append(entry)
                if len(self._buffer) >= self.config.buffer_size:
                    asyncio.create_task(self._flush())
        elif self.storage:
            await self.storage.write(entry)

        return entry

    async def query(self, query: AuditQuery) -> List[AuditEntry]:
        """Query audit logs."""
        if not self.storage:
            return []
        return await self.storage.query(query)

    async def get_summary(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> AuditSummary:
        """Get audit summary for a period."""
        query = AuditQuery(
            tenant_id=tenant_id,
            start_date=period_start,
            end_date=period_end,
            limit=10000,
        )

        entries = await self.query(query)

        events_by_action: Dict[str, int] = {}
        events_by_severity: Dict[str, int] = {}
        events_by_user: Dict[str, int] = {}
        users = set()
        resources = set()
        failed = 0

        for entry in entries:
            events_by_action[entry.action.value] = (
                events_by_action.get(entry.action.value, 0) + 1
            )
            events_by_severity[entry.severity.value] = (
                events_by_severity.get(entry.severity.value, 0) + 1
            )

            if entry.user_id:
                events_by_user[entry.user_id] = (
                    events_by_user.get(entry.user_id, 0) + 1
                )
                users.add(entry.user_id)

            resources.add(f"{entry.resource_type}:{entry.resource_id}")

            if not entry.success:
                failed += 1

        return AuditSummary(
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            total_events=len(entries),
            events_by_action=events_by_action,
            events_by_severity=events_by_severity,
            events_by_user=events_by_user,
            failed_events=failed,
            unique_users=len(users),
            unique_resources=len(resources),
        )

    async def verify_integrity(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        """Verify the integrity of the audit log chain."""
        if not self.storage:
            return True

        query = AuditQuery(
            tenant_id=tenant_id,
            start_date=start_date or datetime.utcnow() - timedelta(days=30),
            end_date=end_date or datetime.utcnow(),
            limit=10000,
            order_desc=False,
        )

        entries = await self.query(query)
        if not entries:
            return True

        # Verify each entry's hash
        for entry in entries:
            if not entry.verify_integrity():
                logger.error(
                    "audit_integrity_violation",
                    entry_id=entry.id,
                    tenant_id=tenant_id,
                )
                return False

        # Verify chain linkage
        for i in range(1, len(entries)):
            if entries[i].previous_hash != entries[i - 1].entry_hash:
                logger.error(
                    "audit_chain_broken",
                    entry_id=entries[i].id,
                    expected_hash=entries[i - 1].entry_hash,
                    actual_hash=entries[i].previous_hash,
                )
                return False

        return True


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        raise RuntimeError("Audit logger not initialized")
    return _audit_logger


async def create_audit_logger(
    config: AuditConfig,
    storage: Optional[AuditStorage] = None,
) -> AuditLogger:
    """Create and initialize the global audit logger."""
    global _audit_logger

    _audit_logger = AuditLogger(config, storage)
    await _audit_logger.start()
    return _audit_logger
