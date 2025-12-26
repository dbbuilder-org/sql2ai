"""Database connection model."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql2ai_api.db.base import AuditedTenantModel

if TYPE_CHECKING:
    from sql2ai_api.models.tenant import Tenant


class DatabaseType(str, Enum):
    """Supported database types."""

    SQLSERVER = "sqlserver"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"


class Connection(AuditedTenantModel):
    """Database connection configuration."""

    __tablename__ = "connections"

    # Display name
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Connection details
    db_type: Mapped[DatabaseType] = mapped_column(
        SQLEnum(DatabaseType),
        nullable=False,
    )
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database: Mapped[str] = mapped_column(String(255), nullable=False)

    # Authentication
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    # Legacy: Password stored in Vault, reference stored here
    password_secret_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Envelope encryption for credentials (preferred)
    encrypted_password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_dek: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    encryption_salt: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    password_encrypted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    kms_key_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # SQL Server specific
    trust_server_certificate: Mapped[bool] = mapped_column(Boolean, default=False)
    encrypt: Mapped[bool] = mapped_column(Boolean, default=True)
    application_name: Mapped[str] = mapped_column(String(255), default="SQL2.AI")

    # SSL/TLS
    ssl_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ssl_ca_cert_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Connection pooling
    pool_size: Mapped[int] = mapped_column(Integer, default=5)
    max_overflow: Mapped[int] = mapped_column(Integer, default=10)

    # Metadata
    environment: Mapped[str] = mapped_column(String(50), default="development")
    tags: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_connected_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="connections")

    def __repr__(self) -> str:
        return f"<Connection {self.name} ({self.db_type.value})>"

    @property
    def connection_string_masked(self) -> str:
        """Get masked connection string for display."""
        if self.db_type == DatabaseType.SQLSERVER:
            return f"Server={self.host},{self.port};Database={self.database};User Id={self.username};Password=****"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:****@{self.host}:{self.port}/{self.database}"
        elif self.db_type in (DatabaseType.MYSQL, DatabaseType.MARIADB):
            return f"mysql://{self.username}:****@{self.host}:{self.port}/{self.database}"
        return f"{self.db_type.value}://{self.host}:{self.port}/{self.database}"

    def get_default_port(self) -> int:
        """Get default port for database type."""
        defaults = {
            DatabaseType.SQLSERVER: 1433,
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.MYSQL: 3306,
            DatabaseType.MARIADB: 3306,
        }
        return defaults.get(self.db_type, 0)
