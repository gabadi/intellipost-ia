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

    async def create_product_image(
        self,
        product_id: UUID,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        file_size_bytes: int,
        file_format: str,
        resolution_width: int,
        resolution_height: int,
        is_primary: bool = False,
        processing_metadata: dict | None = None,
    ) -> Any:
        """Create a new product image."""
        ...

    async def get_product_images(self, product_id: UUID) -> list[Any]:
        """Get all images for a product."""
        ...
