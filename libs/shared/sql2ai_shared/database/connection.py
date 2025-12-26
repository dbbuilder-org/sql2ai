"""Database connection abstractions for SQL Server and PostgreSQL."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator
from contextlib import asynccontextmanager
from pydantic import BaseModel, SecretStr
import structlog

logger = structlog.get_logger()


class DatabaseType(str, Enum):
    """Supported database types."""

    SQLSERVER = "sqlserver"
    POSTGRESQL = "postgresql"


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: SecretStr
    ssl_mode: str = "require"
    connection_timeout: int = 30
    command_timeout: int = 30
    application_name: str = "sql2ai"

    # SQL Server specific
    trust_server_certificate: bool = False
    encrypt: bool = True

    # PostgreSQL specific
    schema: str = "public"

    @property
    def connection_string(self) -> str:
        """Generate connection string for the database type."""
        if self.db_type == DatabaseType.SQLSERVER:
            return (
                f"mssql+aioodbc:///?odbc_connect="
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password.get_secret_value()};"
                f"Encrypt={'yes' if self.encrypt else 'no'};"
                f"TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'};"
                f"Connection Timeout={self.connection_timeout};"
                f"Application Name={self.application_name}"
            )
        else:  # PostgreSQL
            return (
                f"postgresql+asyncpg://{self.username}:"
                f"{self.password.get_secret_value()}@"
                f"{self.host}:{self.port}/{self.database}"
                f"?ssl={self.ssl_mode}"
            )


class QueryResult(BaseModel):
    """Result of a database query."""

    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    affected_rows: Optional[int] = None


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Execute a query and return results."""
        pass

    @abstractmethod
    async def execute_many(
        self, query: str, params_list: List[Dict[str, Any]]
    ) -> int:
        """Execute a query multiple times with different parameters."""
        pass

    @abstractmethod
    async def stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream query results in batches."""
        pass

    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a transaction."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions."""
        await self.begin_transaction()
        try:
            yield self
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL connection implementation using asyncpg."""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self._conn = None
        self._transaction = None

    async def connect(self) -> None:
        """Establish PostgreSQL connection."""
        import asyncpg

        self._conn = await asyncpg.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password.get_secret_value(),
            timeout=self.config.connection_timeout,
            command_timeout=self.config.command_timeout,
        )
        self._connected = True
        logger.info(
            "postgresql_connected",
            host=self.config.host,
            database=self.config.database,
        )

    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._conn:
            await self._conn.close()
            self._connected = False
            logger.info("postgresql_disconnected")

    async def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Execute a query and return results."""
        import time

        start = time.perf_counter()

        if params:
            # Convert dict params to positional for asyncpg
            result = await self._conn.fetch(query, *params.values())
        else:
            result = await self._conn.fetch(query)

        elapsed_ms = (time.perf_counter() - start) * 1000

        if result:
            columns = list(result[0].keys()) if result else []
            rows = [dict(r) for r in result]
        else:
            columns = []
            rows = []

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=elapsed_ms,
        )

    async def execute_many(
        self, query: str, params_list: List[Dict[str, Any]]
    ) -> int:
        """Execute a query multiple times with different parameters."""
        count = 0
        for params in params_list:
            await self._conn.execute(query, *params.values())
            count += 1
        return count

    async def stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream query results in batches."""
        if params:
            async with self._conn.transaction():
                async for record in self._conn.cursor(query, *params.values()):
                    yield dict(record)
        else:
            async with self._conn.transaction():
                async for record in self._conn.cursor(query):
                    yield dict(record)

    async def begin_transaction(self) -> None:
        """Begin a transaction."""
        self._transaction = self._conn.transaction()
        await self._transaction.start()

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._transaction:
            await self._transaction.commit()
            self._transaction = None

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._transaction:
            await self._transaction.rollback()
            self._transaction = None


class SQLServerConnection(DatabaseConnection):
    """SQL Server connection implementation using aioodbc."""

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self._conn = None
        self._cursor = None
        self._in_transaction = False

    async def connect(self) -> None:
        """Establish SQL Server connection."""
        import aioodbc

        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.config.host},{self.config.port};"
            f"DATABASE={self.config.database};"
            f"UID={self.config.username};"
            f"PWD={self.config.password.get_secret_value()};"
            f"Encrypt={'yes' if self.config.encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if self.config.trust_server_certificate else 'no'};"
            f"Connection Timeout={self.config.connection_timeout};"
            f"Application Name={self.config.application_name}"
        )

        self._conn = await aioodbc.connect(dsn=conn_str, autocommit=True)
        self._connected = True
        logger.info(
            "sqlserver_connected",
            host=self.config.host,
            database=self.config.database,
        )

    async def disconnect(self) -> None:
        """Close SQL Server connection."""
        if self._cursor:
            await self._cursor.close()
        if self._conn:
            await self._conn.close()
            self._connected = False
            logger.info("sqlserver_disconnected")

    async def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Execute a query and return results."""
        import time

        start = time.perf_counter()
        cursor = await self._conn.cursor()

        try:
            if params:
                await cursor.execute(query, list(params.values()))
            else:
                await cursor.execute(query)

            # Try to fetch results
            try:
                rows_raw = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = [dict(zip(columns, row)) for row in rows_raw]
            except Exception:
                # Query didn't return results (INSERT, UPDATE, etc.)
                columns = []
                rows = []

            elapsed_ms = (time.perf_counter() - start) * 1000

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=elapsed_ms,
                affected_rows=cursor.rowcount if cursor.rowcount >= 0 else None,
            )
        finally:
            await cursor.close()

    async def execute_many(
        self, query: str, params_list: List[Dict[str, Any]]
    ) -> int:
        """Execute a query multiple times with different parameters."""
        cursor = await self._conn.cursor()
        try:
            count = 0
            for params in params_list:
                await cursor.execute(query, list(params.values()))
                count += 1
            return count
        finally:
            await cursor.close()

    async def stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream query results in batches."""
        cursor = await self._conn.cursor()
        try:
            if params:
                await cursor.execute(query, list(params.values()))
            else:
                await cursor.execute(query)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            while True:
                rows = await cursor.fetchmany(batch_size)
                if not rows:
                    break
                for row in rows:
                    yield dict(zip(columns, row))
        finally:
            await cursor.close()

    async def begin_transaction(self) -> None:
        """Begin a transaction."""
        await self._conn.execute("BEGIN TRANSACTION")
        self._in_transaction = True

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._in_transaction:
            await self._conn.execute("COMMIT TRANSACTION")
            self._in_transaction = False

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._in_transaction:
            await self._conn.execute("ROLLBACK TRANSACTION")
            self._in_transaction = False


def create_connection(config: DatabaseConfig) -> DatabaseConnection:
    """Factory function to create a database connection."""
    if config.db_type == DatabaseType.POSTGRESQL:
        return PostgreSQLConnection(config)
    elif config.db_type == DatabaseType.SQLSERVER:
        return SQLServerConnection(config)
    else:
        raise ValueError(f"Unsupported database type: {config.db_type}")
