"""
Password service protocol for user management module.

This module defines the Protocol interface for password hashing and verification operations.
"""

from typing import Protocol


class PasswordServiceProtocol(Protocol):
    """Protocol for password hashing and verification operations."""

    async def hash_password(self, password: str) -> str:
        """Hash a password securely."""
        ...

    async def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        ...
