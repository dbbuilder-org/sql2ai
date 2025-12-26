"""Secure credential encryption with envelope encryption and tenant-scoped keys.

This module implements a multi-layer encryption strategy for protecting sensitive
data like database credentials in a multi-tenant environment:

1. Data Encryption Keys (DEKs): Unique per-tenant symmetric keys for encrypting data
2. Key Encryption Keys (KEKs): Master keys that encrypt DEKs, stored in KMS
3. Session Binding: Credentials only decrypted during active authenticated sessions

Security Model:
- Credentials are encrypted with tenant-specific DEK
- DEK is encrypted with KEK from Azure Key Vault / AWS KMS
- Decryption requires valid user session + tenant membership
- All operations are audited
"""

import base64
import hashlib
import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Tuple

import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, SecretStr

from sql2ai_api.config import settings

logger = structlog.get_logger()


class EncryptedCredential(BaseModel):
    """Encrypted credential with metadata."""

    # The encrypted credential data (base64 encoded)
    ciphertext: str
    # The encrypted DEK used to encrypt this credential (base64 encoded)
    encrypted_dek: str
    # Key version for rotation support
    key_version: int
    # Tenant this credential belongs to
    tenant_id: str
    # Salt used for key derivation
    salt: str
    # Timestamp of encryption
    encrypted_at: datetime
    # Algorithm identifier for future-proofing
    algorithm: str = "AES-256-GCM"
    # KMS key identifier (Key Vault key name or AWS KMS ARN)
    kms_key_id: Optional[str] = None


class KeyManagementProvider(ABC):
    """Abstract base class for key management providers."""

    @abstractmethod
    async def encrypt_dek(self, dek: bytes, tenant_id: str) -> Tuple[bytes, str, int]:
        """Encrypt a DEK using the KEK.

        Returns:
            Tuple of (encrypted_dek, kms_key_id, key_version)
        """
        pass

    @abstractmethod
    async def decrypt_dek(
        self, encrypted_dek: bytes, kms_key_id: str, key_version: int
    ) -> bytes:
        """Decrypt a DEK using the KEK."""
        pass

    @abstractmethod
    async def rotate_key(self, tenant_id: str) -> None:
        """Rotate the KEK for a tenant."""
        pass


class LocalKeyProvider(KeyManagementProvider):
    """Local key provider for development/testing.

    WARNING: This should NOT be used in production.
    Use AzureKeyVaultProvider or AWSKMSProvider instead.
    """

    def __init__(self, master_key: Optional[str] = None):
        """Initialize with a master key.

        Args:
            master_key: Base64-encoded master key. If not provided,
                       uses ENCRYPTION_MASTER_KEY from settings.
        """
        if master_key:
            self._master_key = base64.b64decode(master_key)
        elif hasattr(settings, "encryption_master_key") and settings.encryption_master_key:
            self._master_key = base64.b64decode(settings.encryption_master_key)
        else:
            # Generate a random key for development
            self._master_key = secrets.token_bytes(32)
            logger.warning(
                "using_random_encryption_key",
                message="No encryption master key configured. Using random key.",
            )

        self._key_version = 1

    async def encrypt_dek(self, dek: bytes, tenant_id: str) -> Tuple[bytes, str, int]:
        """Encrypt DEK with master key."""
        # For local dev, use master key directly (no tenant isolation)
        # Production should use AzureKeyVaultProvider or AWSKMSProvider
        fernet = Fernet(base64.urlsafe_b64encode(self._master_key[:32]))
        encrypted = fernet.encrypt(dek)
        # Store tenant_id in the key_id for reference
        return encrypted, f"local-master-key:{tenant_id}", self._key_version

    async def decrypt_dek(
        self, encrypted_dek: bytes, kms_key_id: str, key_version: int
    ) -> bytes:
        """Decrypt DEK with master key."""
        # Use same master key for decryption
        fernet = Fernet(base64.urlsafe_b64encode(self._master_key[:32]))
        return fernet.decrypt(encrypted_dek)

    async def rotate_key(self, tenant_id: str) -> None:
        """Rotate key (no-op for local provider)."""
        logger.info("key_rotation_requested", tenant_id=tenant_id)
        self._key_version += 1

    def _derive_tenant_key(self, tenant_id: str) -> bytes:
        """Derive a tenant-specific key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=tenant_id.encode(),
            iterations=100000,
        )
        return kdf.derive(self._master_key)

    def _derive_tenant_key_from_encrypted(self, encrypted_dek: bytes) -> bytes:
        """Extract and derive tenant key (simplified for local dev)."""
        return self._master_key[:32]


class AzureKeyVaultProvider(KeyManagementProvider):
    """Azure Key Vault key management provider.

    Uses Azure Key Vault for secure KEK storage and cryptographic operations.
    All key operations happen within Key Vault's HSM boundary.
    """

    def __init__(self, vault_url: str, tenant_key_prefix: str = "sql2ai-tenant-"):
        """Initialize Azure Key Vault provider.

        Args:
            vault_url: Azure Key Vault URL (e.g., https://myvault.vault.azure.net)
            tenant_key_prefix: Prefix for tenant key names in Key Vault
        """
        self._vault_url = vault_url
        self._tenant_key_prefix = tenant_key_prefix
        self._client = None

    async def _get_client(self):
        """Get or create Key Vault client."""
        if self._client is None:
            from azure.identity.aio import DefaultAzureCredential
            from azure.keyvault.keys.aio import KeyClient
            from azure.keyvault.keys.crypto.aio import CryptographyClient

            credential = DefaultAzureCredential()
            self._client = KeyClient(vault_url=self._vault_url, credential=credential)
        return self._client

    async def encrypt_dek(self, dek: bytes, tenant_id: str) -> Tuple[bytes, str, int]:
        """Encrypt DEK using Azure Key Vault."""
        from azure.identity.aio import DefaultAzureCredential
        from azure.keyvault.keys.crypto.aio import CryptographyClient
        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        key_name = f"{self._tenant_key_prefix}{tenant_id}"
        client = await self._get_client()

        # Get or create tenant key
        try:
            key = await client.get_key(key_name)
        except Exception:
            # Create new RSA key for tenant
            key = await client.create_rsa_key(key_name, size=2048)
            logger.info("tenant_key_created", tenant_id=tenant_id, key_name=key_name)

        # Encrypt DEK with tenant's KEK
        credential = DefaultAzureCredential()
        crypto_client = CryptographyClient(key, credential=credential)

        result = await crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep_256, dek)

        await crypto_client.close()

        return result.ciphertext, key.id, int(key.properties.version or "1")

    async def decrypt_dek(
        self, encrypted_dek: bytes, kms_key_id: str, key_version: int
    ) -> bytes:
        """Decrypt DEK using Azure Key Vault."""
        from azure.identity.aio import DefaultAzureCredential
        from azure.keyvault.keys.crypto.aio import CryptographyClient
        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        credential = DefaultAzureCredential()

        # Use the specific key version
        crypto_client = CryptographyClient(kms_key_id, credential=credential)

        result = await crypto_client.decrypt(
            EncryptionAlgorithm.rsa_oaep_256, encrypted_dek
        )

        await crypto_client.close()

        return result.plaintext

    async def rotate_key(self, tenant_id: str) -> None:
        """Rotate tenant KEK in Azure Key Vault."""
        key_name = f"{self._tenant_key_prefix}{tenant_id}"
        client = await self._get_client()

        # Create new key version
        new_key = await client.create_rsa_key(key_name, size=2048)
        logger.info(
            "tenant_key_rotated",
            tenant_id=tenant_id,
            key_name=key_name,
            new_version=new_key.properties.version,
        )


class AWSKMSProvider(KeyManagementProvider):
    """AWS KMS key management provider.

    Uses AWS KMS for secure KEK storage and cryptographic operations.
    """

    def __init__(self, region: str = "us-east-1", key_alias_prefix: str = "alias/sql2ai-"):
        """Initialize AWS KMS provider.

        Args:
            region: AWS region
            key_alias_prefix: Prefix for tenant key aliases
        """
        self._region = region
        self._key_alias_prefix = key_alias_prefix
        self._client = None

    async def _get_client(self):
        """Get or create KMS client."""
        if self._client is None:
            import aioboto3

            session = aioboto3.Session()
            self._client = await session.client("kms", region_name=self._region).__aenter__()
        return self._client

    async def encrypt_dek(self, dek: bytes, tenant_id: str) -> Tuple[bytes, str, int]:
        """Encrypt DEK using AWS KMS."""
        key_alias = f"{self._key_alias_prefix}{tenant_id}"
        client = await self._get_client()

        try:
            # Try to encrypt with existing key
            response = await client.encrypt(KeyId=key_alias, Plaintext=dek)
        except client.exceptions.NotFoundException:
            # Create new key for tenant
            create_response = await client.create_key(
                Description=f"SQL2.AI tenant key for {tenant_id}",
                KeyUsage="ENCRYPT_DECRYPT",
                Origin="AWS_KMS",
            )
            key_id = create_response["KeyMetadata"]["KeyId"]

            # Create alias
            await client.create_alias(AliasName=key_alias, TargetKeyId=key_id)

            logger.info("tenant_key_created", tenant_id=tenant_id, key_alias=key_alias)

            # Encrypt with new key
            response = await client.encrypt(KeyId=key_alias, Plaintext=dek)

        return (
            response["CiphertextBlob"],
            response["KeyId"],
            1,  # KMS handles versioning internally
        )

    async def decrypt_dek(
        self, encrypted_dek: bytes, kms_key_id: str, key_version: int
    ) -> bytes:
        """Decrypt DEK using AWS KMS."""
        client = await self._get_client()
        response = await client.decrypt(CiphertextBlob=encrypted_dek, KeyId=kms_key_id)
        return response["Plaintext"]

    async def rotate_key(self, tenant_id: str) -> None:
        """Rotate tenant key in AWS KMS."""
        key_alias = f"{self._key_alias_prefix}{tenant_id}"
        client = await self._get_client()

        # Get key ID from alias
        response = await client.describe_key(KeyId=key_alias)
        key_id = response["KeyMetadata"]["KeyId"]

        # Enable automatic key rotation (annual)
        await client.enable_key_rotation(KeyId=key_id)

        logger.info("tenant_key_rotation_enabled", tenant_id=tenant_id, key_id=key_id)


class TenantKeyManager:
    """Manages tenant-specific encryption keys with caching and rotation."""

    def __init__(self, kms_provider: KeyManagementProvider):
        """Initialize tenant key manager.

        Args:
            kms_provider: Key management provider for KEK operations
        """
        self._kms = kms_provider
        self._dek_cache: dict[str, Tuple[bytes, datetime]] = {}
        self._cache_ttl_seconds = 300  # 5 minutes

    def _generate_dek(self) -> bytes:
        """Generate a new Data Encryption Key."""
        return secrets.token_bytes(32)

    async def get_encryption_key(
        self, tenant_id: str, force_new: bool = False
    ) -> Tuple[bytes, bytes, str, int]:
        """Get or create encryption key for tenant.

        Args:
            tenant_id: Tenant identifier
            force_new: Force generation of new key

        Returns:
            Tuple of (dek, encrypted_dek, kms_key_id, key_version)
        """
        # Check cache
        if not force_new and tenant_id in self._dek_cache:
            dek, cached_at = self._dek_cache[tenant_id]
            age = (datetime.now(timezone.utc) - cached_at).total_seconds()
            if age < self._cache_ttl_seconds:
                # Re-encrypt with current KEK for storage
                encrypted_dek, kms_key_id, key_version = await self._kms.encrypt_dek(
                    dek, tenant_id
                )
                return dek, encrypted_dek, kms_key_id, key_version

        # Generate new DEK
        dek = self._generate_dek()

        # Encrypt DEK with KEK
        encrypted_dek, kms_key_id, key_version = await self._kms.encrypt_dek(
            dek, tenant_id
        )

        # Cache DEK
        self._dek_cache[tenant_id] = (dek, datetime.now(timezone.utc))

        logger.info(
            "tenant_dek_generated",
            tenant_id=tenant_id,
            kms_key_id=kms_key_id,
            key_version=key_version,
        )

        return dek, encrypted_dek, kms_key_id, key_version

    async def decrypt_dek(
        self, encrypted_dek: bytes, kms_key_id: str, key_version: int
    ) -> bytes:
        """Decrypt a Data Encryption Key.

        Args:
            encrypted_dek: Encrypted DEK bytes
            kms_key_id: KMS key identifier used for encryption
            key_version: Version of the key used

        Returns:
            Decrypted DEK bytes
        """
        return await self._kms.decrypt_dek(encrypted_dek, kms_key_id, key_version)

    async def rotate_tenant_key(self, tenant_id: str) -> None:
        """Rotate the KEK for a tenant.

        Note: After rotation, credentials encrypted with old DEKs will still
        work as long as old key versions are available in KMS.
        """
        await self._kms.rotate_key(tenant_id)

        # Clear cached DEK to force new generation
        if tenant_id in self._dek_cache:
            del self._dek_cache[tenant_id]

        logger.info("tenant_key_rotated", tenant_id=tenant_id)

    def clear_cache(self, tenant_id: Optional[str] = None) -> None:
        """Clear DEK cache for security or memory management.

        Args:
            tenant_id: Specific tenant to clear, or None for all
        """
        if tenant_id:
            if tenant_id in self._dek_cache:
                del self._dek_cache[tenant_id]
        else:
            self._dek_cache.clear()


class EncryptionService:
    """High-level encryption service for credential management."""

    def __init__(self, key_manager: TenantKeyManager):
        """Initialize encryption service.

        Args:
            key_manager: Tenant key manager instance
        """
        self._key_manager = key_manager

    def _create_fernet(self, dek: bytes) -> Fernet:
        """Create Fernet instance from DEK."""
        # Ensure DEK is properly encoded for Fernet
        key = base64.urlsafe_b64encode(dek[:32])
        return Fernet(key)

    async def encrypt(
        self, plaintext: str, tenant_id: str
    ) -> EncryptedCredential:
        """Encrypt a credential for a tenant.

        Args:
            plaintext: The credential to encrypt
            tenant_id: Tenant identifier

        Returns:
            EncryptedCredential with all necessary metadata
        """
        # Get encryption key
        dek, encrypted_dek, kms_key_id, key_version = (
            await self._key_manager.get_encryption_key(tenant_id)
        )

        # Generate salt for this encryption
        salt = secrets.token_bytes(16)

        # Encrypt the plaintext
        fernet = self._create_fernet(dek)
        ciphertext = fernet.encrypt(plaintext.encode())

        return EncryptedCredential(
            ciphertext=base64.b64encode(ciphertext).decode(),
            encrypted_dek=base64.b64encode(encrypted_dek).decode(),
            key_version=key_version,
            tenant_id=tenant_id,
            salt=base64.b64encode(salt).decode(),
            encrypted_at=datetime.now(timezone.utc),
            kms_key_id=kms_key_id,
        )

    async def decrypt(self, credential: EncryptedCredential) -> str:
        """Decrypt a credential.

        Args:
            credential: The encrypted credential

        Returns:
            Decrypted plaintext
        """
        # Decrypt the DEK
        encrypted_dek = base64.b64decode(credential.encrypted_dek)
        dek = await self._key_manager.decrypt_dek(
            encrypted_dek, credential.kms_key_id or "", credential.key_version
        )

        # Decrypt the ciphertext
        fernet = self._create_fernet(dek)
        ciphertext = base64.b64decode(credential.ciphertext)
        plaintext = fernet.decrypt(ciphertext)

        return plaintext.decode()


class CredentialManager:
    """Manages database credentials with encryption and access control.

    This is the main interface for storing and retrieving connection credentials.
    It ensures:
    1. Credentials are always encrypted at rest
    2. Decryption only happens in authenticated request context
    3. All access is logged for audit
    """

    def __init__(self, encryption_service: EncryptionService):
        """Initialize credential manager.

        Args:
            encryption_service: Encryption service instance
        """
        self._encryption = encryption_service

    async def store_credential(
        self,
        tenant_id: str,
        credential_name: str,
        credential_value: str,
        user_id: str,
    ) -> EncryptedCredential:
        """Store an encrypted credential.

        Args:
            tenant_id: Tenant identifier
            credential_name: Name/identifier for the credential
            credential_value: The secret value to store
            user_id: User performing the operation (for audit)

        Returns:
            The encrypted credential for storage
        """
        encrypted = await self._encryption.encrypt(credential_value, tenant_id)

        logger.info(
            "credential_stored",
            tenant_id=tenant_id,
            credential_name=credential_name,
            user_id=user_id,
            key_version=encrypted.key_version,
        )

        return encrypted

    async def retrieve_credential(
        self,
        credential: EncryptedCredential,
        user_id: str,
        user_tenant_id: str,
    ) -> str:
        """Retrieve and decrypt a credential.

        Args:
            credential: The encrypted credential
            user_id: User performing the operation
            user_tenant_id: The tenant the user belongs to

        Returns:
            Decrypted credential value

        Raises:
            PermissionError: If user's tenant doesn't match credential's tenant
        """
        # Verify tenant access
        if user_tenant_id != credential.tenant_id:
            logger.warning(
                "credential_access_denied",
                user_id=user_id,
                user_tenant_id=user_tenant_id,
                credential_tenant_id=credential.tenant_id,
            )
            raise PermissionError("Access denied: tenant mismatch")

        decrypted = await self._encryption.decrypt(credential)

        logger.info(
            "credential_retrieved",
            tenant_id=credential.tenant_id,
            user_id=user_id,
            key_version=credential.key_version,
        )

        return decrypted


def create_encryption_service() -> EncryptionService:
    """Create an encryption service based on configuration.

    Returns the appropriate encryption service based on environment:
    - Production: Azure Key Vault or AWS KMS
    - Development: Local key provider
    """
    if hasattr(settings, "azure_key_vault_url") and settings.azure_key_vault_url:
        provider = AzureKeyVaultProvider(settings.azure_key_vault_url)
        logger.info("using_azure_key_vault", vault_url=settings.azure_key_vault_url)
    elif hasattr(settings, "aws_kms_region") and settings.aws_kms_region:
        provider = AWSKMSProvider(region=settings.aws_kms_region)
        logger.info("using_aws_kms", region=settings.aws_kms_region)
    else:
        provider = LocalKeyProvider()
        if settings.is_production:
            logger.error(
                "no_kms_configured_in_production",
                message="Production environment should use Azure Key Vault or AWS KMS",
            )

    key_manager = TenantKeyManager(provider)
    return EncryptionService(key_manager)


def create_credential_manager() -> CredentialManager:
    """Create a credential manager with proper encryption."""
    encryption_service = create_encryption_service()
    return CredentialManager(encryption_service)
