"""
Bcrypt implementation of PasswordServiceProtocol.

This module provides secure password hashing and verification using bcrypt.
"""

import bcrypt


class BcryptPasswordService:
    """Bcrypt implementation of PasswordServiceProtocol."""

    def __init__(self, rounds: int = 12):
        """Initialize with number of salt rounds."""
        self.rounds = rounds

    async def hash_password(self, password: str) -> str:
        """Hash a password securely."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    async def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
