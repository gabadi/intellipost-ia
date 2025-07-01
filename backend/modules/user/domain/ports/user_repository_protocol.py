"""
User data persistence protocol for hexagonal architecture.

This module defines Protocol interface for user data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Any, Protocol
from uuid import UUID


class UserRepositoryProtocol(Protocol):
    """Protocol for user data persistence operations."""

    async def create(self, user: Any) -> Any:
        """Create a new user."""
        ...

    async def get_by_id(self, user_id: UUID) -> Any | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> Any | None:
        """Get user by email address."""
        ...

    async def update(self, user: Any) -> Any:
        """Update an existing user."""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        ...
