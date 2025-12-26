"""Tests for encryption service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from sql2ai_api.security.encryption import (
    EncryptedCredential,
    EncryptionService,
    CredentialManager,
    TenantKeyManager,
    LocalKeyProvider,
    create_encryption_service,
    create_credential_manager,
)


class TestEncryptedCredential:
    """Tests for EncryptedCredential model."""

    def test_encrypted_credential_creation(self):
        """Test EncryptedCredential model creation."""
        cred = EncryptedCredential(
            ciphertext="encrypted_data",
            encrypted_dek="encrypted_key",
            key_version=1,
            tenant_id="tenant_123",
            salt="random_salt",
            encrypted_at=datetime.now(timezone.utc),
            kms_key_id="key_id_456",
        )

        assert cred.ciphertext == "encrypted_data"
        assert cred.encrypted_dek == "encrypted_key"
        assert cred.key_version == 1
        assert cred.tenant_id == "tenant_123"
        assert cred.algorithm == "AES-256-GCM"

    def test_encrypted_credential_defaults(self):
        """Test EncryptedCredential default values."""
        cred = EncryptedCredential(
            ciphertext="data",
            encrypted_dek="key",
            key_version=1,
            tenant_id="tenant",
            salt="salt",
            encrypted_at=datetime.now(timezone.utc),
        )

        assert cred.algorithm == "AES-256-GCM"
        assert cred.kms_key_id is None


class TestLocalKeyProvider:
    """Tests for LocalKeyProvider."""

    @pytest.mark.asyncio
    async def test_encrypt_dek(self):
        """Test DEK encryption."""
        provider = LocalKeyProvider()
        dek = b"test_data_encryption_key_32bytes!"

        encrypted_dek, kms_key_id, key_version = await provider.encrypt_dek(
            dek, "tenant_123"
        )

        assert encrypted_dek is not None
        assert len(encrypted_dek) > 0
        assert kms_key_id == "local-master-key"
        assert key_version == 1

    @pytest.mark.asyncio
    async def test_key_rotation(self):
        """Test key rotation increments version."""
        provider = LocalKeyProvider()

        initial_version = provider._key_version
        await provider.rotate_key("tenant_123")

        assert provider._key_version == initial_version + 1


class TestTenantKeyManager:
    """Tests for TenantKeyManager."""

    @pytest.fixture
    def key_manager(self):
        """Create key manager with local provider."""
        provider = LocalKeyProvider()
        return TenantKeyManager(provider)

    @pytest.mark.asyncio
    async def test_get_encryption_key(self, key_manager):
        """Test getting encryption key for tenant."""
        dek, encrypted_dek, kms_key_id, key_version = (
            await key_manager.get_encryption_key("tenant_123")
        )

        assert dek is not None
        assert len(dek) == 32  # 256-bit key
        assert encrypted_dek is not None
        assert kms_key_id == "local-master-key"
        assert key_version >= 1

    @pytest.mark.asyncio
    async def test_key_caching(self, key_manager):
        """Test that DEKs are cached."""
        # First call
        dek1, _, _, _ = await key_manager.get_encryption_key("tenant_123")

        # Second call should return same DEK from cache
        dek2, _, _, _ = await key_manager.get_encryption_key("tenant_123")

        assert dek1 == dek2

    @pytest.mark.asyncio
    async def test_force_new_key(self, key_manager):
        """Test forcing new key generation."""
        # First call
        dek1, _, _, _ = await key_manager.get_encryption_key("tenant_123")

        # Force new key
        dek2, _, _, _ = await key_manager.get_encryption_key(
            "tenant_123", force_new=True
        )

        assert dek1 != dek2

    def test_clear_cache(self, key_manager):
        """Test clearing DEK cache."""
        # Manually add to cache
        key_manager._dek_cache["tenant_123"] = (
            b"cached_key",
            datetime.now(timezone.utc),
        )

        key_manager.clear_cache("tenant_123")

        assert "tenant_123" not in key_manager._dek_cache

    def test_clear_all_cache(self, key_manager):
        """Test clearing all DEK cache."""
        # Add multiple entries
        key_manager._dek_cache["tenant_1"] = (b"key1", datetime.now(timezone.utc))
        key_manager._dek_cache["tenant_2"] = (b"key2", datetime.now(timezone.utc))

        key_manager.clear_cache()

        assert len(key_manager._dek_cache) == 0


class TestEncryptionService:
    """Tests for EncryptionService."""

    @pytest.fixture
    def encryption_service(self):
        """Create encryption service."""
        provider = LocalKeyProvider()
        key_manager = TenantKeyManager(provider)
        return EncryptionService(key_manager)

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_roundtrip(self, encryption_service):
        """Test encrypting and decrypting returns original value."""
        plaintext = "my_secret_password_123!"
        tenant_id = "tenant_test"

        # Encrypt
        encrypted = await encryption_service.encrypt(plaintext, tenant_id)

        assert encrypted.ciphertext != plaintext
        assert encrypted.tenant_id == tenant_id
        assert encrypted.key_version >= 1

        # Decrypt
        decrypted = await encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    @pytest.mark.asyncio
    async def test_encrypt_different_tenants(self, encryption_service):
        """Test that different tenants get different ciphertexts."""
        plaintext = "same_password"

        encrypted1 = await encryption_service.encrypt(plaintext, "tenant_1")
        encrypted2 = await encryption_service.encrypt(plaintext, "tenant_2")

        # Same plaintext should produce different ciphertext for different tenants
        assert encrypted1.ciphertext != encrypted2.ciphertext
        assert encrypted1.tenant_id != encrypted2.tenant_id

    @pytest.mark.asyncio
    async def test_encrypt_includes_metadata(self, encryption_service):
        """Test that encryption includes all required metadata."""
        encrypted = await encryption_service.encrypt("password", "tenant_123")

        assert encrypted.ciphertext is not None
        assert encrypted.encrypted_dek is not None
        assert encrypted.key_version is not None
        assert encrypted.tenant_id == "tenant_123"
        assert encrypted.salt is not None
        assert encrypted.encrypted_at is not None


class TestCredentialManager:
    """Tests for CredentialManager."""

    @pytest.fixture
    def credential_manager(self):
        """Create credential manager."""
        provider = LocalKeyProvider()
        key_manager = TenantKeyManager(provider)
        encryption_service = EncryptionService(key_manager)
        return CredentialManager(encryption_service)

    @pytest.mark.asyncio
    async def test_store_credential(self, credential_manager):
        """Test storing a credential."""
        encrypted = await credential_manager.store_credential(
            tenant_id="tenant_123",
            credential_name="db_password",
            credential_value="super_secret",
            user_id="user_456",
        )

        assert encrypted.tenant_id == "tenant_123"
        assert encrypted.ciphertext is not None
        assert "super_secret" not in encrypted.ciphertext

    @pytest.mark.asyncio
    async def test_retrieve_credential(self, credential_manager):
        """Test retrieving a stored credential."""
        # Store
        encrypted = await credential_manager.store_credential(
            tenant_id="tenant_123",
            credential_name="db_password",
            credential_value="my_password",
            user_id="user_456",
        )

        # Retrieve
        decrypted = await credential_manager.retrieve_credential(
            credential=encrypted,
            user_id="user_456",
            user_tenant_id="tenant_123",
        )

        assert decrypted == "my_password"

    @pytest.mark.asyncio
    async def test_retrieve_credential_wrong_tenant(self, credential_manager):
        """Test retrieving credential with wrong tenant fails."""
        # Store for tenant_123
        encrypted = await credential_manager.store_credential(
            tenant_id="tenant_123",
            credential_name="db_password",
            credential_value="secret",
            user_id="user_456",
        )

        # Try to retrieve with different tenant
        with pytest.raises(PermissionError) as exc_info:
            await credential_manager.retrieve_credential(
                credential=encrypted,
                user_id="user_789",
                user_tenant_id="tenant_999",  # Wrong tenant
            )

        assert "tenant mismatch" in str(exc_info.value)


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_encryption_service(self):
        """Test creating encryption service via factory."""
        service = create_encryption_service()
        assert isinstance(service, EncryptionService)

    def test_create_credential_manager(self):
        """Test creating credential manager via factory."""
        manager = create_credential_manager()
        assert isinstance(manager, CredentialManager)
