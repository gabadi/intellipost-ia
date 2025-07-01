"""
Product data persistence protocol for hexagonal architecture.

This module defines Protocol interface for product data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Any, Protocol
from uuid import UUID


class ProductRepositoryProtocol(Protocol):
    """Protocol for product data persistence operations."""

    async def create(self, product: Any) -> Any:
        """Create a new product."""
        ...

    async def get_by_id(self, product_id: UUID) -> Any | None:
        """Get product by ID."""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[Any]:
        """Get all products for a user."""
        ...

    async def update(self, product: Any) -> Any:
        """Update an existing product."""
        ...

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""
        ...
