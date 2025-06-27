"""
Password hashing service implementation.

This module provides password hashing and verification using bcrypt
following security best practices.
"""

from passlib.context import CryptContext


class PasswordService:
    """
    Password hashing and verification service.

    Uses bcrypt with 12 salt rounds for secure password storage.
    """

    def __init__(self) -> None:
        """Initialize password service with bcrypt context."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12,  # 12 rounds for security as per story requirements
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: Plain text password to hash

        Returns:
            str: Hashed password

        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty")

        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise

        Raises:
            ValueError: If either password is empty or None
        """
        if not plain_password or not hashed_password:
            raise ValueError("Passwords cannot be empty")

        return self.pwd_context.verify(plain_password, hashed_password)

    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be updated.

        This is useful for upgrading hashes when security requirements change.

        Args:
            hashed_password: Hashed password to check

        Returns:
            bool: True if password hash needs updating, False otherwise
        """
        if not hashed_password:
            return True

        return self.pwd_context.needs_update(hashed_password)
