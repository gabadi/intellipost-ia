"""
Product domain service protocol for product module.

This module defines abstract base class for product domain services.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from .entities.product import Product


class ProductDomainService(ABC):
    """Abstract base class for product domain services."""

    @abstractmethod
    async def create_product(
        self, user_id: UUID, product_data: dict[str, Any]
    ) -> Product:
        """Create a new product."""
        ...

    @abstractmethod
    async def process_product_content(self, product_id: UUID) -> Product:
        """Process product with AI content generation."""
        ...

    @abstractmethod
    async def publish_to_mercadolibre(self, product_id: UUID) -> Product:
        """Publish product to MercadoLibre."""
        ...
