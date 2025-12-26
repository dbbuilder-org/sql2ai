"""Connection service with real database operations."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.models.connection import Connection, DatabaseType
from sql2ai_api.security.encryption import EncryptionService


class ConnectionService:
    """Service for managing database connections."""

    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.encryption = EncryptionService()

    async def list_connections(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> tuple[list[Connection], int]:
        """List connections for the tenant."""
        query = select(Connection).where(
            Connection.tenant_id == self.tenant_id,
            Connection.deleted_at.is_(None),
        )

        if not include_inactive:
            query = query.where(Connection.is_active == True)

        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total = await self.db.scalar(count_query) or 0

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Connection.created_at.desc())
        result = await self.db.execute(query)
        connections = list(result.scalars().all())

        return connections, total

    async def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get a connection by ID."""
        result = await self.db.execute(
            select(Connection).where(
                Connection.id == connection_id,
                Connection.tenant_id == self.tenant_id,
                Connection.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_connection(
        self,
        name: str,
        db_type: DatabaseType,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        description: Optional[str] = None,
        environment: str = "development",
        tags: Optional[dict] = None,
        ssl_mode: Optional[str] = None,
        trust_server_certificate: bool = False,
        encrypt: bool = True,
    ) -> Connection:
        """Create a new database connection with encrypted credentials."""
        # Encrypt the password
        encrypted_data = await self.encryption.encrypt_for_tenant(
            self.tenant_id,
            password,
        )

        connection = Connection(
            id=str(uuid4()),
            tenant_id=self.tenant_id,
            name=name,
            description=description,
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            username=username,
            encrypted_password=encrypted_data["ciphertext"],
            encrypted_dek=encrypted_data["encrypted_dek"],
            key_version=encrypted_data.get("key_version", 1),
            encryption_salt=encrypted_data.get("salt"),
            password_encrypted_at=datetime.utcnow(),
            ssl_mode=ssl_mode,
            trust_server_certificate=trust_server_certificate,
            encrypt=encrypt,
            environment=environment,
            tags=tags or {},
            created_by=self.user_id,
            updated_by=self.user_id,
        )

        self.db.add(connection)
        await self.db.flush()
        await self.db.refresh(connection)

        return connection

    async def update_connection(
        self,
        connection_id: str,
        **updates,
    ) -> Optional[Connection]:
        """Update a connection."""
        connection = await self.get_connection(connection_id)
        if not connection:
            return None

        # Handle password update separately
        if "password" in updates:
            password = updates.pop("password")
            encrypted_data = await self.encryption.encrypt_for_tenant(
                self.tenant_id,
                password,
            )
            connection.encrypted_password = encrypted_data["ciphertext"]
            connection.encrypted_dek = encrypted_data["encrypted_dek"]
            connection.key_version = encrypted_data.get("key_version", 1)
            connection.encryption_salt = encrypted_data.get("salt")
            connection.password_encrypted_at = datetime.utcnow()

        # Update other fields
        for field, value in updates.items():
            if hasattr(connection, field) and value is not None:
                setattr(connection, field, value)

        connection.updated_by = self.user_id
        await self.db.flush()
        await self.db.refresh(connection)

        return connection

    async def delete_connection(self, connection_id: str) -> bool:
        """Soft delete a connection."""
        connection = await self.get_connection(connection_id)
        if not connection:
            return False

        connection.deleted_at = datetime.utcnow()
        connection.updated_by = self.user_id
        await self.db.flush()

        return True

    async def get_decrypted_password(self, connection: Connection) -> Optional[str]:
        """Get decrypted password for a connection."""
        if not connection.encrypted_password or not connection.encrypted_dek:
            return None

        try:
            return await self.encryption.decrypt_for_tenant(
                self.tenant_id,
                connection.encrypted_password,
                connection.encrypted_dek,
            )
        except Exception:
            return None

    async def test_connection(self, connection: Connection) -> dict:
        """Test a database connection."""
        import time

        password = await self.get_decrypted_password(connection)
        if not password:
            return {
                "success": False,
                "message": "Could not decrypt connection credentials",
            }

        start_time = time.time()

        try:
            if connection.db_type == DatabaseType.POSTGRESQL:
                import psycopg2

                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    user=connection.username,
                    password=password,
                    connect_timeout=10,
                )
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                conn.close()

                latency_ms = (time.time() - start_time) * 1000

                # Update last connected
                connection.last_connected_at = datetime.utcnow()
                connection.last_error = None
                await self.db.flush()

                return {
                    "success": True,
                    "message": "Connection successful",
                    "server_version": version.split(",")[0] if version else None,
                    "latency_ms": round(latency_ms, 2),
                }

            elif connection.db_type == DatabaseType.SQLSERVER:
                import pyodbc

                conn_str = (
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={connection.host},{connection.port};"
                    f"DATABASE={connection.database};"
                    f"UID={connection.username};"
                    f"PWD={password};"
                    f"TrustServerCertificate={'Yes' if connection.trust_server_certificate else 'No'};"
                    f"Encrypt={'Yes' if connection.encrypt else 'No'};"
                )

                with pyodbc.connect(conn_str, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT @@VERSION")
                    version = cursor.fetchone()[0]

                latency_ms = (time.time() - start_time) * 1000

                connection.last_connected_at = datetime.utcnow()
                connection.last_error = None
                await self.db.flush()

                return {
                    "success": True,
                    "message": "Connection successful",
                    "server_version": version.split("\n")[0] if version else None,
                    "latency_ms": round(latency_ms, 2),
                }

            else:
                return {
                    "success": False,
                    "message": f"Database type {connection.db_type.value} not yet supported",
                }

        except Exception as e:
            connection.last_error = str(e)
            await self.db.flush()

            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
            }

    async def count_by_status(self) -> dict:
        """Count connections by status."""
        total_query = select(func.count()).where(
            Connection.tenant_id == self.tenant_id,
            Connection.deleted_at.is_(None),
        )
        total = await self.db.scalar(total_query) or 0

        active_query = select(func.count()).where(
            Connection.tenant_id == self.tenant_id,
            Connection.deleted_at.is_(None),
            Connection.is_active == True,
            Connection.last_error.is_(None),
        )
        active = await self.db.scalar(active_query) or 0

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
        }
