"""
Credential Encryption Service for user management module.

This module provides secure encryption and decryption of sensitive
MercadoLibre credentials using AES-256-GCM encryption.
"""

import base64
import hashlib
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from modules.user_management.domain.ports.settings_protocol import SettingsProtocol


class CredentialEncryptionService:
    """
    Service for encrypting and decrypting MercadoLibre credentials.

    Uses AES-256-GCM encryption with PBKDF2 key derivation for secure
    credential storage as required by the story specifications.
    """

    _encryption_key: str

    def __init__(
        self,
        encryption_key: str | None = None,
        settings: SettingsProtocol | None = None,
    ) -> None:
        """
        Initialize encryption service with key.

        Args:
            encryption_key: Base encryption key. If provided, uses this directly.
            settings: Settings provider for configuration. If None, uses environment variables.
        """
        if encryption_key:
            self._encryption_key = encryption_key
        else:
            # Get from settings provider or fallback to environment variable
            key_from_settings = None
            if settings:
                key_from_settings = settings.ml_encryption_key

            if not key_from_settings:
                key_from_settings = os.getenv("ML_ENCRYPTION_KEY")

            if key_from_settings:
                self._encryption_key = key_from_settings
            else:
                # Check if production environment
                is_production = False
                if settings:
                    is_production = settings.is_production
                else:
                    is_production = (
                        os.getenv("ENVIRONMENT", "development") == "production"
                    )

                if is_production:
                    raise ValueError(
                        "ML encryption key is required in production (set ML_ENCRYPTION_KEY or configure settings)"
                    )
                else:
                    # Use test/development default
                    self._encryption_key = (
                        "test-encryption-key-for-development-and-testing-only-32chars"
                    )

        # Validate key length (minimum 32 characters for security)
        if len(self._encryption_key) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from master key using PBKDF2.

        Args:
            salt: Salt bytes for key derivation

        Returns:
            Derived 32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return kdf.derive(self._encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: Text to encrypt

        Returns:
            Base64-encoded encrypted data with format: salt:nonce:ciphertext:tag

        Raises:
            ValueError: If encryption fails
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty plaintext")

        try:
            # Generate random salt and nonce
            salt = os.urandom(16)
            nonce = os.urandom(12)

            # Derive key from salt
            key = self._derive_key(salt)

            # Create cipher
            cipher = Cipher(
                algorithms.AES(key), modes.GCM(nonce), backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Encrypt data
            ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

            # Combine salt, nonce, ciphertext, and tag
            encrypted_data = salt + nonce + ciphertext + encryptor.tag

            # Return base64 encoded
            return base64.b64encode(encrypted_data).decode("utf-8")

        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}") from e

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data using AES-256-GCM.

        Args:
            encrypted_data: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_data:
            raise ValueError("Cannot decrypt empty data")

        try:
            # Decode base64
            data = base64.b64decode(encrypted_data.encode("utf-8"))

            # Extract components
            salt = data[:16]
            nonce = data[16:28]
            ciphertext = data[28:-16]
            tag = data[-16:]

            # Derive key from salt
            key = self._derive_key(salt)

            # Create cipher
            cipher = Cipher(
                algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return plaintext.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}") from e

    def encrypt_access_token(self, access_token: str) -> str:
        """
        Encrypt MercadoLibre access token.

        Args:
            access_token: ML access token to encrypt

        Returns:
            Encrypted token
        """
        return self.encrypt(access_token)

    def decrypt_access_token(self, encrypted_token: str) -> str:
        """
        Decrypt MercadoLibre access token.

        Args:
            encrypted_token: Encrypted ML access token

        Returns:
            Decrypted token
        """
        return self.decrypt(encrypted_token)

    def encrypt_refresh_token(self, refresh_token: str) -> str:
        """
        Encrypt MercadoLibre refresh token.

        Args:
            refresh_token: ML refresh token to encrypt

        Returns:
            Encrypted token
        """
        return self.encrypt(refresh_token)

    def decrypt_refresh_token(self, encrypted_token: str) -> str:
        """
        Decrypt MercadoLibre refresh token.

        Args:
            encrypted_token: Encrypted ML refresh token

        Returns:
            Decrypted token
        """
        return self.decrypt(encrypted_token)

    def encrypt_app_secret(self, app_secret: str) -> str:
        """
        Encrypt MercadoLibre app secret.

        Args:
            app_secret: ML app secret to encrypt

        Returns:
            Encrypted secret
        """
        return self.encrypt(app_secret)

    def decrypt_app_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt MercadoLibre app secret.

        Args:
            encrypted_secret: Encrypted ML app secret

        Returns:
            Decrypted secret
        """
        return self.decrypt(encrypted_secret)

    def is_encrypted(self, data: str) -> bool:
        """
        Check if data appears to be encrypted.

        Args:
            data: Data to check

        Returns:
            True if data appears encrypted, False otherwise
        """
        try:
            # Try to decode as base64
            decoded = base64.b64decode(data.encode("utf-8"))
            # Check if it has the expected minimum length (salt + nonce + tag = 44 bytes)
            return len(decoded) >= 44
        except Exception:
            return False

    def hash_for_comparison(self, data: str) -> str:
        """
        Create a hash for data comparison (not encryption).

        Used for comparing tokens without decryption.

        Args:
            data: Data to hash

        Returns:
            SHA-256 hash of the data
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def rotate_encryption(self, encrypted_data: str, new_key: str) -> str:
        """
        Rotate encryption key for existing encrypted data.

        Args:
            encrypted_data: Data encrypted with old key
            new_key: New encryption key

        Returns:
            Data encrypted with new key
        """
        # Decrypt with current key
        plaintext = self.decrypt(encrypted_data)

        # Create new service with new key
        new_service = CredentialEncryptionService(new_key)

        # Encrypt with new key
        return new_service.encrypt(plaintext)
