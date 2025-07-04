"""
Refresh token domain entity for user management module.

This module contains the refresh token entity for JWT token management.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RefreshToken:
    """
    Refresh token domain entity for JWT token management.

    This entity represents a refresh token that can be used to
    generate new access tokens without requiring user re-authentication.
    """

    # Core identity
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime

    def is_expired(self) -> bool:
        """Check if the refresh token is expired."""
        from datetime import UTC, datetime

        return datetime.now(UTC) >= self.expires_at

    def is_valid(self) -> bool:
        """Check if the refresh token is valid (not expired)."""
        return not self.is_expired()
