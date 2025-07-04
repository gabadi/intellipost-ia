"""
Password service implementation for user management module.

This module provides password hashing and verification using bcrypt.
"""

import asyncio
from functools import partial

from passlib.context import CryptContext


class PasswordService:
    """Password service implementation using bcrypt."""

    def __init__(self) -> None:
        """Initialize password service with bcrypt configuration."""
        # Use bcrypt with 12 salt rounds as specified in story requirements
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12,  # Security requirement from story
        )

    async def hash_password(self, password: str) -> str:
        """
        Hash a password securely using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Bcrypt password hash
        """
        # Run password hashing in thread pool to avoid blocking the event loop
        # since bcrypt is CPU intensive
        loop = asyncio.get_event_loop()
        hash_func = partial(self._pwd_context.hash, password)
        return await loop.run_in_executor(None, hash_func)

    async def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Stored bcrypt hash to verify against

        Returns:
            True if password matches hash, False otherwise
        """
        # Run password verification in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        verify_func = partial(self._pwd_context.verify, password, password_hash)
        return await loop.run_in_executor(None, verify_func)

    def is_hash_valid(self, password_hash: str) -> bool:
        """
        Check if a password hash is valid bcrypt format.

        Args:
            password_hash: Hash string to validate

        Returns:
            True if hash is valid bcrypt format, False otherwise
        """
        try:
            # Try to identify the hash scheme
            return self._pwd_context.identify(password_hash) == "bcrypt"
        except Exception:
            return False

    def needs_update(self, password_hash: str) -> bool:
        """
        Check if a password hash needs to be updated.

        This can happen if the bcrypt rounds have been increased
        or if using deprecated hash schemes.

        Args:
            password_hash: Hash string to check

        Returns:
            True if hash needs updating, False otherwise
        """
        try:
            return self._pwd_context.needs_update(password_hash)
        except Exception:
            return True  # If we can't check, assume it needs updating
