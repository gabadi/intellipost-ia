"""
Password hashing and verification utilities.

This module provides secure password hashing using bcrypt with timing attack prevention.
"""

import secrets

from passlib.context import CryptContext

# Configure bcrypt with sensible defaults
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    """Manages password hashing and verification with security best practices."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash with timing attack prevention.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str | None]:
        """
        Validate password meets minimum strength requirements.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        # Additional checks can be added here
        # e.g., uppercase, lowercase, numbers, special characters

        return True, None

    @staticmethod
    def generate_secure_token() -> str:
        """
        Generate a cryptographically secure random token.

        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(32)
