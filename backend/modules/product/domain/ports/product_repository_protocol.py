"""
Product data persistence protocol for hexagonal architecture.

This module defines Protocol interface for product data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Protocol
from uuid import UUID

from modules.product.domain.product import Product


class ProductRepositoryProtocol(Protocol):
    """Protocol for product data persistence operations."""

    async def create(self, product: Product) -> Product:
        """Create a new product."""
        ...

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[Product]:
        """Get all products for a user."""
        ...

    async def update(self, product: Product) -> Product:
        """Update an existing product."""
        ...

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""
        ...
