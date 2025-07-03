"""
Product status management operations.

This module contains methods for managing product status changes.
"""

from datetime import UTC, datetime

from .entities.confidence_score import ConfidenceScore
from .entities.product_status import ProductStatus
from .product_core import ProductCore


class ProductStatusManager:
    """Status management operations for product entities."""

    @staticmethod
    def mark_as_processed(product: ProductCore, confidence: ConfidenceScore) -> None:
        """Mark product as processed with confidence score."""
        product.status = ProductStatus.PROCESSED
        product.confidence = confidence
        product.updated_at = datetime.now(UTC)

    @staticmethod
    def mark_as_published(product: ProductCore, ml_listing_id: str) -> None:
        """Mark product as published to MercadoLibre."""
        product.status = ProductStatus.PUBLISHED
        product.ml_listing_id = ml_listing_id
        product.published_at = datetime.now(UTC)
        product.updated_at = datetime.now(UTC)

    @staticmethod
    def mark_as_failed(product: ProductCore) -> None:
        """Mark product processing as failed."""
        product.status = ProductStatus.FAILED
        product.updated_at = datetime.now(UTC)
