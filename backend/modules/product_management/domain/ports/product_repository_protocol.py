"""
Product data persistence protocol for hexagonal architecture.

This module defines Protocol interface for product data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Any, Protocol
from uuid import UUID

from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_image import ProductImage
from modules.product_management.domain.value_objects.product_image_metadata import (
    ProductImageMetadata,
)
from modules.product_management.domain.value_objects.product_image_resolution import (
    ProductImageResolution,
)


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

    async def create_product_image(
        self,
        product_id: UUID,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        file_size_bytes: int,
        file_format: str,
        resolution: ProductImageResolution,
        is_primary: bool = False,
        metadata: ProductImageMetadata | None = None,
    ) -> ProductImage:
        """Create a new product image."""
        ...

    async def get_product_images(self, product_id: UUID) -> list[ProductImage]:
        """Get all images for a product."""
        ...

    async def get_product_image_by_id(self, image_id: UUID) -> ProductImage | None:
        """Get a specific product image by ID."""
        ...

    async def update_product_image(self, image: ProductImage) -> ProductImage:
        """Update an existing product image."""
        ...

    async def delete_product_image(self, image_id: UUID) -> bool:
        """Delete a product image by ID."""
        ...

    async def set_primary_image(self, product_id: UUID, image_id: UUID) -> bool:
        """Set a specific image as primary for a product."""
        ...
