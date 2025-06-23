"""
Data persistence protocols for hexagonal architecture.

This module defines Protocol interfaces for data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Protocol
from uuid import UUID

from domain.entities.product import Product
from domain.entities.user import User


class UserRepositoryProtocol(Protocol):
    """Protocol for user data persistence operations."""

    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        ...

    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        ...


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
