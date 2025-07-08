"""
Product domain entity.

This module contains the Product entity representing a MercadoLibre product
listing with AI-generated content capabilities.
"""

from ..product_business_rules import (
    ProductBusinessRules,
)
from ..product_core import ProductCore
from ..product_status_manager import (
    ProductStatusManager,
)
from .confidence_score import ConfidenceScore


class Product(ProductCore):
    """
    Product domain entity representing a MercadoLibre listing.

    This entity encapsulates all the business logic and rules related to
    product listings, including AI-generated content and processing status.

    Uses composition pattern to separate concerns:
    - ProductCore: Data structure and basic properties
    - ProductBusinessRules: Business validation logic
    - ProductStatusManager: Status change operations
    """

    def is_ready_for_processing(self) -> bool:
        """Check if product is ready for AI processing."""
        return ProductBusinessRules.is_ready_for_processing(self)

    def is_published(self) -> bool:
        """Check if product is published to MercadoLibre."""
        return ProductBusinessRules.is_published(self)

    def has_high_confidence(self) -> bool:
        """Check if AI-generated content has high confidence."""
        return ProductBusinessRules.has_high_confidence(self)

    def mark_as_processed(self, confidence: ConfidenceScore) -> None:
        """Mark product as processed with confidence score."""
        ProductStatusManager.mark_as_processed(self, confidence)

    def mark_as_published(self, ml_listing_id: str) -> None:
        """Mark product as published to MercadoLibre."""
        ProductStatusManager.mark_as_published(self, ml_listing_id)

    def mark_as_failed(self) -> None:
        """Mark product processing as failed."""
        ProductStatusManager.mark_as_failed(self)
