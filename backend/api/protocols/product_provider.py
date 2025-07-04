"""
Product provider protocol for API layer.

This protocol defines what the API needs for product management functionality.
"""

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel


class ProductData(BaseModel):
    """Product data for API operations."""

    id: UUID
    name: str
    description: str | None
    price: float | None
    status: str
    user_id: UUID
    created_at: str  # ISO format
    updated_at: str  # ISO format


class ProductCreationRequest(BaseModel):
    """Request for creating a new product."""

    name: str
    description: str | None = None
    price: float | None = None
    user_id: UUID


class ProductUpdateRequest(BaseModel):
    """Request for updating a product."""

    name: str | None = None
    description: str | None = None
    price: float | None = None
    status: str | None = None


class ProductProviderProtocol(Protocol):
    """
    Protocol defining product management capabilities that the API requires.

    This protocol is owned by the API layer and defines what product management
    functionality the API needs from modules.
    """

    async def create_product(self, request: ProductCreationRequest) -> ProductData:
        """
        Create a new product.

        Args:
            request: Product creation request

        Returns:
            Created product data

        Raises:
            ProductCreationError: If creation fails
        """
        ...

    async def get_product(self, product_id: UUID) -> ProductData | None:
        """
        Get product by ID.

        Args:
            product_id: Product identifier

        Returns:
            Product data if found, None otherwise
        """
        ...

    async def update_product(
        self, product_id: UUID, request: ProductUpdateRequest
    ) -> ProductData | None:
        """
        Update an existing product.

        Args:
            product_id: Product identifier
            request: Product update request

        Returns:
            Updated product data if successful, None if not found
        """
        ...

    async def delete_product(self, product_id: UUID) -> bool:
        """
        Delete a product.

        Args:
            product_id: Product identifier

        Returns:
            True if deletion successful, False if not found
        """
        ...

    async def list_user_products(self, user_id: UUID) -> list[ProductData]:
        """
        List all products for a user.

        Args:
            user_id: User identifier

        Returns:
            List of user's products
        """
        ...
