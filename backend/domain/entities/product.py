"""
Product domain entity.

This module contains the Product entity representing a MercadoLibre product
listing with AI-generated content capabilities.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class ProductStatus(Enum):
    """Product processing status enumeration."""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PUBLISHED = "published"
    FAILED = "failed"
    DRAFT = "draft"


class ConfidenceScore(Enum):
    """AI confidence score for generated content."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Product:
    """
    Product domain entity representing a MercadoLibre listing.

    This entity encapsulates all the business logic and rules related to
    product listings, including AI-generated content and processing status.
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
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_ready_for_processing(self) -> bool:
        """Check if product is ready for AI processing."""
        return (
            self.status == ProductStatus.UPLOADING
            and self.title is not None
            and len(self.title.strip()) > 0
        )

    def is_published(self) -> bool:
        """Check if product is published to MercadoLibre."""
        return self.status == ProductStatus.PUBLISHED and self.ml_listing_id is not None

    def has_high_confidence(self) -> bool:
        """Check if AI-generated content has high confidence."""
        return self.confidence == ConfidenceScore.HIGH

    def mark_as_processed(self, confidence: ConfidenceScore) -> None:
        """Mark product as processed with confidence score."""
        self.status = ProductStatus.PROCESSED
        self.confidence = confidence
        self.updated_at = datetime.utcnow()

    def mark_as_published(self, ml_listing_id: str) -> None:
        """Mark product as published to MercadoLibre."""
        self.status = ProductStatus.PUBLISHED
        self.ml_listing_id = ml_listing_id
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self) -> None:
        """Mark product processing as failed."""
        self.status = ProductStatus.FAILED
        self.updated_at = datetime.utcnow()
