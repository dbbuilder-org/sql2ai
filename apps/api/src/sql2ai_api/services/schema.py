"""Schema service for database metadata extraction with secure credentials."""

from typing import Optional
from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.models.connection import Connection, DatabaseType
from sql2ai_api.security.encryption import (
    EncryptionService,
    EncryptedCredential,
    create_encryption_service,
)

logger = structlog.get_logger()


class SchemaService:
    """Service for schema extraction and analysis with secure credential handling."""

    def __init__(self, encryption_service: Optional[EncryptionService] = None):
        """Initialize schema service.

        Args:
            encryption_service: Optional encryption service, creates default if not provided
        """
        self._encryption = encryption_service or create_encryption_service()

    async def extract_schema(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
        db: AsyncSession,
        include_definitions: bool = True,
        include_row_counts: bool = False,
        schemas: Optional[list[str]] = None,
    ) -> dict:
        """Extract schema from a database connection.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID (for credential access)
            db: Database session
            include_definitions: Include procedure/view definitions
            include_row_counts: Include table row counts
            schemas: Specific schemas to extract

        Returns:
            DatabaseSchema as dictionary
        """
        # Build connection string with decrypted credentials
        conn_str = await self._build_connection_string(
            connection, user_id, tenant_id
        )

        # Import schema engine
        from schema_engine.extractors import SQLServerExtractor, PostgreSQLExtractor

        # Select appropriate extractor
        if connection.db_type == DatabaseType.SQLSERVER:
            extractor = SQLServerExtractor(conn_str)
        elif connection.db_type == DatabaseType.POSTGRESQL:
            extractor = PostgreSQLExtractor(conn_str)
        else:
            raise ValueError(f"Unsupported database type: {connection.db_type}")

        logger.info(
            "extracting_schema",
            connection_id=str(connection.id),
            db_type=connection.db_type.value,
            user_id=user_id,
        )

        # Extract schema
        schema = await extractor.extract(
            include_definitions=include_definitions,
            include_row_counts=include_row_counts,
            schemas=schemas,
        )

        logger.info(
            "schema_extracted",
            connection_id=str(connection.id),
            tables=schema.table_count,
            views=schema.view_count,
            procedures=schema.procedure_count,
        )

        return schema.to_dict()

    async def analyze_schema(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> dict:
        """Analyze a database schema for documentation and optimization.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID
            db: Database session

        Returns:
            AnalysisResult as dictionary
        """
        # First extract the schema
        conn_str = await self._build_connection_string(
            connection, user_id, tenant_id
        )

        from schema_engine.extractors import SQLServerExtractor, PostgreSQLExtractor
        from schema_engine.analyzer import SchemaAnalyzer

        if connection.db_type == DatabaseType.SQLSERVER:
            extractor = SQLServerExtractor(conn_str)
        elif connection.db_type == DatabaseType.POSTGRESQL:
            extractor = PostgreSQLExtractor(conn_str)
        else:
            raise ValueError(f"Unsupported database type: {connection.db_type}")

        schema = await extractor.extract()

        # Analyze the schema
        analyzer = SchemaAnalyzer()
        analysis = analyzer.analyze(schema)

        logger.info(
            "schema_analyzed",
            connection_id=str(connection.id),
            pii_columns=len(analysis.pii_columns),
            issues_found=len(analysis.missing_primary_keys) + len(analysis.naming_violations),
        )

        return analysis.to_dict()

    async def create_snapshot(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
        db: AsyncSession,
        label: Optional[str] = None,
        is_baseline: bool = False,
    ) -> dict:
        """Create a schema snapshot for versioning.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID
            db: Database session
            label: Optional label for the snapshot
            is_baseline: Whether this is a baseline snapshot

        Returns:
            SchemaSnapshot as dictionary
        """
        conn_str = await self._build_connection_string(
            connection, user_id, tenant_id
        )

        from schema_engine.extractors import SQLServerExtractor, PostgreSQLExtractor

        if connection.db_type == DatabaseType.SQLSERVER:
            extractor = SQLServerExtractor(conn_str)
        elif connection.db_type == DatabaseType.POSTGRESQL:
            extractor = PostgreSQLExtractor(conn_str)
        else:
            raise ValueError(f"Unsupported database type: {connection.db_type}")

        snapshot = await extractor.create_snapshot(
            connection_id=str(connection.id),
            tenant_id=tenant_id,
            user_id=user_id,
            label=label,
            is_baseline=is_baseline,
        )

        logger.info(
            "snapshot_created",
            snapshot_id=snapshot.id,
            connection_id=str(connection.id),
            is_baseline=is_baseline,
        )

        return snapshot.to_dict()

    async def compare_schemas(
        self,
        source_snapshot: dict,
        target_snapshot: dict,
    ) -> dict:
        """Compare two schema snapshots.

        Args:
            source_snapshot: Source snapshot dictionary
            target_snapshot: Target snapshot dictionary

        Returns:
            SchemaDiff as dictionary
        """
        from schema_engine.differ import SchemaDiffer
        from schema_engine.models import DatabaseSchema, SchemaSnapshot

        # Reconstruct snapshots from dictionaries
        # This is a simplified version - in production you'd deserialize properly

        differ = SchemaDiffer()

        # For now, just compare the raw schemas
        source_schema_data = source_snapshot.get("schema", {})
        target_schema_data = target_snapshot.get("schema", {})

        # Create minimal DatabaseSchema objects for comparison
        source_schema = DatabaseSchema(
            database_name=source_schema_data.get("database_name", "source"),
        )
        target_schema = DatabaseSchema(
            database_name=target_schema_data.get("database_name", "target"),
        )

        diff = differ.compare(
            source_schema,
            target_schema,
            source_snapshot.get("id", "source"),
            target_snapshot.get("id", "target"),
        )

        return diff.to_dict()

    async def test_connection(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
    ) -> dict:
        """Test a database connection.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID

        Returns:
            Connection test result
        """
        conn_str = await self._build_connection_string(
            connection, user_id, tenant_id
        )

        from schema_engine.extractors import SQLServerExtractor, PostgreSQLExtractor

        if connection.db_type == DatabaseType.SQLSERVER:
            extractor = SQLServerExtractor(conn_str)
        elif connection.db_type == DatabaseType.POSTGRESQL:
            extractor = PostgreSQLExtractor(conn_str)
        else:
            return {
                "success": False,
                "message": f"Unsupported database type: {connection.db_type}",
            }

        success, message, version = await extractor.test_connection()

        return {
            "success": success,
            "message": message,
            "server_version": version,
        }

    async def _build_connection_string(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
    ) -> str:
        """Build connection string with decrypted credentials.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID for credential access

        Returns:
            Database connection string
        """
        # Get decrypted password
        password = await self._get_decrypted_password(
            connection, user_id, tenant_id
        )

        if connection.db_type == DatabaseType.SQLSERVER:
            # SQL Server connection string
            parts = [
                "DRIVER={ODBC Driver 18 for SQL Server}",
                f"SERVER={connection.host},{connection.port}",
                f"DATABASE={connection.database}",
                f"UID={connection.username}",
                f"PWD={password}",
            ]

            if connection.trust_server_certificate:
                parts.append("TrustServerCertificate=Yes")
            if connection.encrypt:
                parts.append("Encrypt=Yes")

            return ";".join(parts)

        elif connection.db_type == DatabaseType.POSTGRESQL:
            # PostgreSQL connection string
            ssl_mode = connection.ssl_mode or "prefer"
            return (
                f"postgresql://{connection.username}:{password}"
                f"@{connection.host}:{connection.port}/{connection.database}"
                f"?sslmode={ssl_mode}"
            )

        else:
            raise ValueError(f"Unsupported database type: {connection.db_type}")

    async def _get_decrypted_password(
        self,
        connection: Connection,
        user_id: str,
        tenant_id: str,
    ) -> str:
        """Get decrypted password for a connection.

        Args:
            connection: Database connection model
            user_id: ID of user making the request
            tenant_id: Tenant ID for credential access

        Returns:
            Decrypted password string
        """
        # Check tenant access
        if str(connection.tenant_id) != tenant_id:
            logger.warning(
                "credential_access_denied",
                user_id=user_id,
                user_tenant_id=tenant_id,
                connection_tenant_id=str(connection.tenant_id),
            )
            raise PermissionError("Access denied: tenant mismatch")

        # If we have an encrypted password stored
        if connection.encrypted_password:
            # Reconstruct EncryptedCredential from stored data
            credential = EncryptedCredential(
                ciphertext=connection.encrypted_password,
                encrypted_dek=connection.encrypted_dek,
                key_version=connection.key_version or 1,
                tenant_id=tenant_id,
                salt=connection.encryption_salt or "",
                encrypted_at=connection.password_encrypted_at or datetime.utcnow(),
                kms_key_id=connection.kms_key_id,
            )

            password = await self._encryption.decrypt(credential)

            logger.info(
                "credential_decrypted",
                connection_id=str(connection.id),
                user_id=user_id,
            )

            return password

        # Fallback: If we have a password_secret_id, fetch from vault
        # This is for legacy connections before encryption migration
        if connection.password_secret_id:
            # TODO: Implement vault integration
            logger.warning(
                "vault_password_not_implemented",
                connection_id=str(connection.id),
            )
            raise NotImplementedError("Vault password retrieval not yet implemented")

        raise ValueError("No password available for connection")

    async def store_encrypted_password(
        self,
        connection: Connection,
        password: str,
        user_id: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> None:
        """Store an encrypted password for a connection.

        Args:
            connection: Database connection model
            password: Plain text password to encrypt
            user_id: ID of user making the request
            tenant_id: Tenant ID
            db: Database session
        """
        # Check tenant access
        if str(connection.tenant_id) != tenant_id:
            raise PermissionError("Access denied: tenant mismatch")

        # Encrypt the password
        encrypted = await self._encryption.encrypt(password, tenant_id)

        # Update connection with encrypted data
        connection.encrypted_password = encrypted.ciphertext
        connection.encrypted_dek = encrypted.encrypted_dek
        connection.key_version = encrypted.key_version
        connection.encryption_salt = encrypted.salt
        connection.password_encrypted_at = encrypted.encrypted_at
        connection.kms_key_id = encrypted.kms_key_id

        await db.commit()

        logger.info(
            "password_encrypted_and_stored",
            connection_id=str(connection.id),
            user_id=user_id,
            key_version=encrypted.key_version,
        )
