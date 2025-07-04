"""
JWT service protocol for user management module.

This module defines the Protocol interface for JWT token operations.
"""

from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID


class JWTServiceProtocol(Protocol):
    """Protocol for JWT token operations."""

    def create_access_token(
        self, user_id: UUID, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token for user."""
        ...

    def create_refresh_token(
        self, user_id: UUID, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT refresh token for user."""
        ...

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a JWT token."""
        ...

    def extract_user_id(self, token: str) -> UUID | None:
        """Extract user ID from a valid JWT token."""
        ...

    def is_token_expired(self, token: str) -> bool:
        """Check if a token is expired."""
        ...

    def get_token_expiry(self, token: str) -> datetime | None:
        """Get the expiry time of a token."""
        ...
