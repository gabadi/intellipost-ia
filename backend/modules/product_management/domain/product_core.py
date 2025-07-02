"""
Product domain entity core.

This module contains the core Product entity dataclass and basic properties.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from .entities.confidence_score import ConfidenceScore
from .entities.product_status import ProductStatus


@dataclass
class ProductCore:
    """
    Core Product domain entity representing a MercadoLibre listing.

    This entity contains the essential data structure and basic properties
    for product listings.
    """

    id: UUID
    user_id: UUID
    status: ProductStatus
    confidence: ConfidenceScore | None = None

    # Product information
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: str | None = None

    # AI-generated content
    ai_title: str | None = None
    ai_description: str | None = None
    ai_tags: list[str] | None = None

    # MercadoLibre integration
    ml_listing_id: str | None = None
    ml_category_id: str | None = None

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
