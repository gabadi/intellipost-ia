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
from modules.content_generation.domain.exceptions import InvalidContentError
from shared.migration.value_object_migration import (
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
)
from shared.value_objects.mercadolibre import MLAttributes, MLSaleTerms, MLShipping


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
    ml_attributes: MLAttributes
    ml_sale_terms: MLSaleTerms
    ml_shipping: MLShipping

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
        if not self.title or len(self.title.strip()) == 0:
            raise InvalidContentError("Title cannot be empty", "title")

        if len(self.title.strip()) < 10:
            raise InvalidContentError(
                "Title must be at least 10 characters long", "title"
            )

        if len(self.ml_title) > 60:
            raise InvalidContentError("Title must be 60 characters or less", "title")

    def _validate_description(self):
        """Validate description constraints."""
        if not self.description or len(self.description.strip()) < 50:
            raise InvalidContentError(
                "Description must be at least 50 characters long", "description"
            )

    def _validate_price(self):
        """Validate price constraints."""
        if self.ml_price <= 0:
            raise InvalidContentError("Price must be positive", "price")

    def _validate_confidence_scores(self):
        """Validate confidence score constraints."""
        if not (0.0 <= self.confidence_overall <= 1.0):
            raise InvalidContentError(
                "Overall confidence must be between 0.0 and 1.0", "confidence"
            )

        for component, score in self.confidence_breakdown.items():
            if not (0.0 <= score <= 1.0):
                raise InvalidContentError(
                    f"Confidence score for {component} must be between 0.0 and 1.0",
                    "confidence",
                )

    def _validate_ml_attributes(self):
        """Validate MercadoLibre attributes."""
        if not self.ml_category_id:
            raise InvalidContentError(
                "MercadoLibre category ID is required", "category"
            )

        if not self.ml_category_name:
            raise InvalidContentError(
                "MercadoLibre category name is required", "category"
            )

        if self.ml_available_quantity <= 0:
            raise InvalidContentError("Available quantity must be positive", "quantity")

        # Validate ML value objects
        try:
            self.ml_attributes.validate()
        except Exception as e:
            raise InvalidContentError(
                f"Invalid ML attributes: {str(e)}", "ml_attributes"
            ) from e

        try:
            self.ml_sale_terms.validate()
        except Exception as e:
            raise InvalidContentError(
                f"Invalid ML sale terms: {str(e)}", "ml_sale_terms"
            ) from e

        try:
            self.ml_shipping.validate()
        except Exception as e:
            raise InvalidContentError(
                f"Invalid ML shipping: {str(e)}", "ml_shipping"
            ) from e

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
            "has_required_attributes": not self.ml_attributes.is_empty(),
            "price_reasonable": self.ml_price > 0,
            "high_confidence": self.is_high_confidence(),
            "category_detected": bool(self.ml_category_id),
            "has_shipping_info": self.ml_shipping.mode != "not_specified",
            "has_sale_terms": not self.ml_sale_terms.is_empty(),
        }

    def meets_quality_threshold(self, threshold: float = 0.7) -> bool:
        """Check if the generated content meets the quality threshold."""
        return self.confidence_overall >= threshold

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
            "ml_attributes": self.ml_attributes.to_dict(),
            "ml_sale_terms": self.ml_sale_terms.to_dict(),
            "ml_shipping": self.ml_shipping.to_dict(),
            "confidence_overall": self.confidence_overall,
            "confidence_breakdown": self.confidence_breakdown,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "generation_time_ms": self.generation_time_ms,
            "version": self.version,
            "generated_at": self.generated_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_legacy_dict(cls, data: dict[str, Any]) -> "GeneratedContent":
        """
        Create GeneratedContent from legacy dictionary format.

        This method handles migration from the old dict[str, Any] format
        to the new typed value objects format.

        Args:
            data: Legacy dictionary containing generated content data

        Returns:
            GeneratedContent instance with migrated value objects

        Raises:
            InvalidContentError: If required fields are missing
        """
        try:
            # Extract required fields
            required_fields = [
                "id",
                "product_id",
                "title",
                "description",
                "ml_category_id",
                "ml_category_name",
                "ml_title",
                "ml_price",
                "ml_currency_id",
                "ml_available_quantity",
                "ml_buying_mode",
                "ml_condition",
                "ml_listing_type_id",
                "confidence_overall",
                "confidence_breakdown",
                "ai_provider",
                "ai_model_version",
                "generation_time_ms",
                "version",
                "generated_at",
            ]

            for field in required_fields:
                if field not in data:
                    raise InvalidContentError(f"Missing required field: {field}", field)

            # Migrate ML value objects
            ml_attributes = safe_migrate_ml_attributes(data.get("ml_attributes"))
            ml_sale_terms = safe_migrate_ml_sale_terms(data.get("ml_sale_terms"))
            ml_shipping = safe_migrate_ml_shipping(data.get("ml_shipping"))

            # Handle datetime fields
            generated_at = data["generated_at"]
            if isinstance(generated_at, str):
                from datetime import datetime

                generated_at = datetime.fromisoformat(
                    generated_at.replace("Z", "+00:00")
                )

            updated_at = data.get("updated_at")
            if updated_at and isinstance(updated_at, str):
                from datetime import datetime

                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            # Handle price conversion
            ml_price = data["ml_price"]
            if not isinstance(ml_price, Decimal):
                ml_price = Decimal(str(ml_price))

            return cls(
                id=UUID(data["id"]) if isinstance(data["id"], str) else data["id"],
                product_id=UUID(data["product_id"])
                if isinstance(data["product_id"], str)
                else data["product_id"],
                title=data["title"],
                description=data["description"],
                ml_category_id=data["ml_category_id"],
                ml_category_name=data["ml_category_name"],
                ml_title=data["ml_title"],
                ml_price=ml_price,
                ml_currency_id=data["ml_currency_id"],
                ml_available_quantity=data["ml_available_quantity"],
                ml_buying_mode=data["ml_buying_mode"],
                ml_condition=data["ml_condition"],
                ml_listing_type_id=data["ml_listing_type_id"],
                ml_attributes=ml_attributes,
                ml_sale_terms=ml_sale_terms,
                ml_shipping=ml_shipping,
                confidence_overall=data["confidence_overall"],
                confidence_breakdown=data["confidence_breakdown"],
                ai_provider=data["ai_provider"],
                ai_model_version=data["ai_model_version"],
                generation_time_ms=data["generation_time_ms"],
                version=data["version"],
                generated_at=generated_at,
                updated_at=updated_at,
            )

        except Exception as e:
            if isinstance(e, InvalidContentError):
                raise
            raise InvalidContentError(
                f"Failed to create GeneratedContent from legacy data: {str(e)}",
                "migration",
            ) from e
