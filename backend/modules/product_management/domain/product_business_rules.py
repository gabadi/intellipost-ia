"""
Product business rules and validation logic.

This module contains the business validation methods for product entities.
"""

from .entities.product_status import ProductStatus
from .product_core import ProductCore


class ProductBusinessRules:
    """Business validation methods for product entities."""

    @staticmethod
    def is_ready_for_processing(product: ProductCore) -> bool:
        """Check if product is ready for AI processing."""
        return (
            product.status == ProductStatus.UPLOADING
            and product.title is not None
            and len(product.title.strip()) > 0
        )

    @staticmethod
    def is_published(product: ProductCore) -> bool:
        """Check if product is published to MercadoLibre."""
        return (
            product.status == ProductStatus.PUBLISHED
            and product.ml_listing_id is not None
        )

    @staticmethod
    def has_high_confidence(product: ProductCore) -> bool:
        """Check if AI-generated content has high confidence."""
        return product.confidence is not None and product.confidence.is_high
