"""
Refresh token repository protocol for user management module.

This module defines the Protocol interface for refresh token persistence operations.
"""

from typing import Protocol
from uuid import UUID

from modules.user_management.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepositoryProtocol(Protocol):
    """Protocol for refresh token data persistence operations."""

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token."""
        ...

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Get refresh token by token hash."""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """Get all refresh tokens for a user."""
        ...

    async def delete_by_token_hash(self, token_hash: str) -> bool:
        """Delete refresh token by token hash."""
        ...

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """Delete all refresh tokens for a user. Returns count of deleted tokens."""
        ...

    async def delete_expired(self) -> int:
        """Delete all expired refresh tokens. Returns count of deleted tokens."""
        ...
