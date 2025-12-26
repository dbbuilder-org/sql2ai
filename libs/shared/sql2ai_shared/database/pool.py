"""Connection pool management for database connections."""

from typing import Dict, Optional
from contextlib import asynccontextmanager
import asyncio
import structlog

from sql2ai_shared.database.connection import (
    DatabaseConfig,
    DatabaseConnection,
    DatabaseType,
    QueryResult,
)
from sql2ai_shared.tenancy.context import get_current_tenant

logger = structlog.get_logger()


class ConnectionPool:
    """Connection pool for managing database connections.

    Features:
    - Per-tenant connection isolation
    - Connection health checks
    - Automatic reconnection
    - Pool size management
    """

    def __init__(
        self,
        config: DatabaseConfig,
        min_size: int = 1,
        max_size: int = 10,
        max_idle_time: int = 300,
    ):
        self.config = config
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time

        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._size = 0
        self._lock = asyncio.Lock()
        self._closed = False

    async def initialize(self) -> None:
        """Initialize the pool with minimum connections."""
        for _ in range(self.min_size):
            conn = await self._create_connection()
            await self._pool.put(conn)

        logger.info(
            "connection_pool_initialized",
            db_type=self.config.db_type,
            min_size=self.min_size,
            max_size=self.max_size,
        )

    async def _create_connection(self) -> DatabaseConnection:
        """Create a new database connection."""
        from sql2ai_shared.database.connection import create_connection

        async with self._lock:
            if self._size >= self.max_size:
                raise RuntimeError("Connection pool exhausted")

            conn = create_connection(self.config)
            await conn.connect()
            self._size += 1

            logger.debug(
                "connection_created",
                pool_size=self._size,
                max_size=self.max_size,
            )

            return conn

    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        conn = None
        try:
            # Try to get a connection from the pool
            try:
                conn = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                # Pool is empty, create a new connection if possible
                if self._size < self.max_size:
                    conn = await self._create_connection()
                else:
                    # Wait for a connection to become available
                    conn = await asyncio.wait_for(
                        self._pool.get(),
                        timeout=self.config.connection_timeout,
                    )

            # Verify connection is still valid
            if not conn.is_connected:
                await conn.connect()

            yield conn

        finally:
            if conn is not None:
                # Return connection to pool
                try:
                    self._pool.put_nowait(conn)
                except asyncio.QueueFull:
                    # Pool is full, close the connection
                    await conn.disconnect()
                    async with self._lock:
                        self._size -= 1

    async def execute(
        self, query: str, params: Optional[Dict] = None
    ) -> QueryResult:
        """Execute a query using a pooled connection."""
        async with self.acquire() as conn:
            return await conn.execute(query, params)

    async def close(self) -> None:
        """Close all connections in the pool."""
        self._closed = True

        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                await conn.disconnect()
            except asyncio.QueueEmpty:
                break

        async with self._lock:
            self._size = 0

        logger.info("connection_pool_closed")

    @property
    def size(self) -> int:
        """Current number of connections in the pool."""
        return self._size

    @property
    def available(self) -> int:
        """Number of available connections."""
        return self._pool.qsize()


class TenantConnectionManager:
    """Manages connection pools per tenant.

    Each tenant gets their own isolated connection pool
    to prevent cross-tenant data access.
    """

    def __init__(self):
        self._pools: Dict[str, ConnectionPool] = {}
        self._configs: Dict[str, DatabaseConfig] = {}
        self._lock = asyncio.Lock()

    async def register_tenant(
        self,
        tenant_id: str,
        config: DatabaseConfig,
        min_size: int = 1,
        max_size: int = 10,
    ) -> None:
        """Register a tenant with their database configuration."""
        async with self._lock:
            if tenant_id in self._pools:
                # Close existing pool
                await self._pools[tenant_id].close()

            pool = ConnectionPool(
                config=config,
                min_size=min_size,
                max_size=max_size,
            )
            await pool.initialize()

            self._pools[tenant_id] = pool
            self._configs[tenant_id] = config

            logger.info(
                "tenant_pool_registered",
                tenant_id=tenant_id,
                db_type=config.db_type,
            )

    async def unregister_tenant(self, tenant_id: str) -> None:
        """Unregister a tenant and close their connection pool."""
        async with self._lock:
            if tenant_id in self._pools:
                await self._pools[tenant_id].close()
                del self._pools[tenant_id]
                del self._configs[tenant_id]

                logger.info("tenant_pool_unregistered", tenant_id=tenant_id)

    def get_pool(self, tenant_id: Optional[str] = None) -> ConnectionPool:
        """Get the connection pool for a tenant."""
        if tenant_id is None:
            tenant = get_current_tenant()
            if tenant is None:
                raise RuntimeError("No tenant context available")
            tenant_id = tenant.id

        if tenant_id not in self._pools:
            raise RuntimeError(f"No connection pool for tenant: {tenant_id}")

        return self._pools[tenant_id]

    @asynccontextmanager
    async def acquire(self, tenant_id: Optional[str] = None):
        """Acquire a connection for the current or specified tenant."""
        pool = self.get_pool(tenant_id)
        async with pool.acquire() as conn:
            yield conn

    async def execute(
        self,
        query: str,
        params: Optional[Dict] = None,
        tenant_id: Optional[str] = None,
    ) -> QueryResult:
        """Execute a query for the current or specified tenant."""
        pool = self.get_pool(tenant_id)
        return await pool.execute(query, params)

    async def close_all(self) -> None:
        """Close all tenant connection pools."""
        async with self._lock:
            for tenant_id, pool in self._pools.items():
                await pool.close()
                logger.info("tenant_pool_closed", tenant_id=tenant_id)

            self._pools.clear()
            self._configs.clear()


# Global pool instances
_default_pool: Optional[ConnectionPool] = None
_tenant_manager: Optional[TenantConnectionManager] = None


def get_pool() -> ConnectionPool:
    """Get the default connection pool."""
    global _default_pool
    if _default_pool is None:
        raise RuntimeError("Default connection pool not initialized")
    return _default_pool


async def create_pool(
    config: DatabaseConfig,
    min_size: int = 1,
    max_size: int = 10,
) -> ConnectionPool:
    """Create and initialize the default connection pool."""
    global _default_pool

    _default_pool = ConnectionPool(
        config=config,
        min_size=min_size,
        max_size=max_size,
    )
    await _default_pool.initialize()
    return _default_pool


def get_tenant_manager() -> TenantConnectionManager:
    """Get the tenant connection manager."""
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = TenantConnectionManager()
    return _tenant_manager
