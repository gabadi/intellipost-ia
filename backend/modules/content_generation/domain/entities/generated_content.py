"""
Generated Content domain entity.

This module defines the GeneratedContent entity which represents
AI-generated content for product listings on MercadoLibre.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from modules.content_generation.domain.entities.confidence_score import ConfidenceScore


@dataclass(frozen=True)
class GeneratedContent:
    """
    Domain entity representing AI-generated content for product listings.

    This entity encapsulates all the generated content components including
    titles, descriptions, categories, and MercadoLibre-specific attributes.
    """

    id: UUID
    product_id: UUID

    # Basic generated content
    title: str
    description: str

    # MercadoLibre specific fields
    ml_category_id: str
    ml_category_name: str
    ml_title: str
    ml_price: Decimal
    ml_currency_id: str
    ml_available_quantity: int
    ml_buying_mode: str
    ml_condition: str
    ml_listing_type_id: str

    # MercadoLibre flexible attributes and terms
    ml_attributes: dict[str, Any]
    ml_sale_terms: dict[str, Any]
    ml_shipping: dict[str, Any]

    # Confidence scoring
    confidence_overall: float
    confidence_breakdown: dict[str, float]

    # AI provider metadata
    ai_provider: str
    ai_model_version: str
    generation_time_ms: int

    # Version control
    version: int

    # Timestamps
    generated_at: datetime
    updated_at: datetime | None = None

    def __post_init__(self):
        """Validate the generated content entity."""
        self._validate_title()
        self._validate_description()
        self._validate_price()
        self._validate_confidence_scores()
        self._validate_ml_attributes()

    def _validate_title(self):
        """Validate title constraints."""
        if not self.title or len(self.title.strip()) < 10:
            raise ValueError("Title must be at least 10 characters long")

        if len(self.ml_title) > 60:
            raise ValueError("MercadoLibre title cannot exceed 60 characters")

    def _validate_description(self):
        """Validate description constraints."""
        if not self.description or len(self.description.strip()) < 50:
            raise ValueError("Description must be at least 50 characters long")

    def _validate_price(self):
        """Validate price constraints."""
        if self.ml_price <= 0:
            raise ValueError("Price must be greater than 0")

    def _validate_confidence_scores(self):
        """Validate confidence score constraints."""
        if not (0.0 <= self.confidence_overall <= 1.0):
            raise ValueError("Overall confidence must be between 0.0 and 1.0")

        for component, score in self.confidence_breakdown.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(
                    f"Confidence score for {component} must be between 0.0 and 1.0"
                )

    def _validate_ml_attributes(self):
        """Validate MercadoLibre attributes."""
        if not self.ml_category_id:
            raise ValueError("MercadoLibre category ID is required")

        if not self.ml_category_name:
            raise ValueError("MercadoLibre category name is required")

    def get_confidence_score(self) -> ConfidenceScore:
        """Get the confidence score as a domain entity."""
        return ConfidenceScore(
            overall=self.confidence_overall, breakdown=self.confidence_breakdown
        )

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the generated content has high confidence."""
        return self.confidence_overall >= threshold

    def get_quality_indicators(self) -> dict[str, bool]:
        """Get quality indicators for the generated content."""
        return {
            "title_length_optimal": 40 <= len(self.ml_title) <= 60,
            "description_comprehensive": len(self.description) >= 100,
            "has_required_attributes": len(self.ml_attributes) > 0,
            "price_reasonable": self.ml_price > 0,
            "high_confidence": self.is_high_confidence(),
            "category_detected": bool(self.ml_category_id),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary representation."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "title": self.title,
            "description": self.description,
            "ml_category_id": self.ml_category_id,
            "ml_category_name": self.ml_category_name,
            "ml_title": self.ml_title,
            "ml_price": float(self.ml_price),
            "ml_currency_id": self.ml_currency_id,
            "ml_available_quantity": self.ml_available_quantity,
            "ml_buying_mode": self.ml_buying_mode,
            "ml_condition": self.ml_condition,
            "ml_listing_type_id": self.ml_listing_type_id,
            "ml_attributes": self.ml_attributes,
            "ml_sale_terms": self.ml_sale_terms,
            "ml_shipping": self.ml_shipping,
            "confidence_overall": self.confidence_overall,
            "confidence_breakdown": self.confidence_breakdown,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "generation_time_ms": self.generation_time_ms,
            "version": self.version,
            "generated_at": self.generated_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
