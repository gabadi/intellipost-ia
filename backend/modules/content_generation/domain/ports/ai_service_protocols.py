"""
AI service protocols for hexagonal architecture.

This module defines Protocol interfaces for AI-related services,
ensuring loose coupling between domain logic and AI service implementations.
"""

from typing import Any, Protocol
from uuid import UUID

from modules.content_generation.domain.entities.confidence_score import ConfidenceScore
from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)
from modules.content_generation.domain.entities.product_features import ProductFeatures
from shared.value_objects import PriceRange


class ImageData(Protocol):
    """Protocol for image data representation."""

    s3_key: str
    s3_url: str
    file_format: str
    resolution_width: int
    resolution_height: int


class AIContentGeneratorProtocol(Protocol):
    """Protocol for AI content generation services."""

    async def generate_listing(
        self,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: PriceRange | None = None,
        target_audience: str | None = None,
    ) -> GeneratedContent:
        """Generate complete MercadoLibre listing content."""
        ...

    async def calculate_confidence(self, content: GeneratedContent) -> ConfidenceScore:
        """Calculate confidence scores for generated content."""
        ...

    async def validate_content(self, content: GeneratedContent) -> dict[str, Any]:
        """Validate generated content against quality standards."""
        ...

    async def generate_title_variations(
        self, base_title: str, product_info: str, count: int = 3
    ) -> list[str]:
        """Generate multiple title variations for A/B testing."""
        ...

    async def enhance_description(
        self,
        base_description: str,
        product_features: ProductFeatures,
        target_length: int | None = None,
    ) -> str:
        """Enhance an existing description with additional features."""
        ...

    async def extract_product_features(
        self, images: list[ImageData], prompt: str
    ) -> ProductFeatures:
        """Extract product features from images and prompt."""
        ...

    async def estimate_price(
        self,
        product_features: ProductFeatures,
        category_id: str,
        condition: str = "new",
    ) -> dict[str, Any]:
        """Estimate product price based on features and category."""
        ...

    async def check_content_quality(
        self, content: GeneratedContent, quality_threshold: float = 0.7
    ) -> bool:
        """Check if content meets quality standards."""
        ...


class MLCategoryServiceProtocol(Protocol):
    """Protocol for MercadoLibre category detection services."""

    async def predict_category(
        self, product_features: ProductFeatures, category_hint: str | None = None
    ) -> dict[str, Any]:
        """Predict MercadoLibre category from product features."""
        ...

    async def validate_category(
        self, category_id: str, product_features: ProductFeatures
    ) -> dict[str, Any]:
        """Validate if category is appropriate for product."""
        ...

    async def get_category_attributes(self, category_id: str) -> dict[str, Any]:
        """Get required and optional attributes for a category."""
        ...

    async def get_category_info(self, category_id: str) -> dict[str, Any]:
        """Get detailed information about a category."""
        ...


class ContentRepositoryProtocol(Protocol):
    """Protocol for content repository operations."""

    async def save_generated_content(
        self, content: GeneratedContent
    ) -> GeneratedContent:
        """Save generated content to the repository."""
        ...

    async def get_generated_content(self, content_id: UUID) -> GeneratedContent | None:
        """Get generated content by ID."""
        ...

    async def get_content_by_product_id(
        self, product_id: UUID
    ) -> GeneratedContent | None:
        """Get generated content by product ID."""
        ...

    async def update_generated_content(
        self, content: GeneratedContent
    ) -> GeneratedContent:
        """Update existing generated content."""
        ...

    async def delete_generated_content(self, content_id: UUID) -> bool:
        """Delete generated content by ID."""
        ...

    async def get_content_versions(self, product_id: UUID) -> list[GeneratedContent]:
        """Get all versions of content for a product."""
        ...


class TitleGenerationServiceProtocol(Protocol):
    """Protocol for title generation services."""

    async def generate_optimized_title(
        self, product_features: ProductFeatures, category_id: str, max_length: int = 60
    ) -> str:
        """Generate MercadoLibre-optimized title."""
        ...

    async def validate_title(self, title: str, category_id: str) -> dict[str, Any]:
        """Validate title against MercadoLibre requirements."""
        ...

    async def generate_title_variations(
        self, base_title: str, product_features: ProductFeatures, count: int = 3
    ) -> list[str]:
        """Generate multiple title variations."""
        ...

    async def calculate_title_confidence(
        self, title: str, product_features: ProductFeatures
    ) -> float:
        """Calculate confidence score for generated title."""
        ...


class DescriptionGenerationServiceProtocol(Protocol):
    """Protocol for description generation services."""

    async def generate_description(
        self,
        product_features: ProductFeatures,
        category_id: str,
        target_length: int | None = None,
    ) -> str:
        """Generate comprehensive product description."""
        ...

    async def validate_description(
        self, description: str, category_id: str
    ) -> dict[str, Any]:
        """Validate description against quality standards."""
        ...

    async def enhance_description(
        self, base_description: str, additional_features: ProductFeatures
    ) -> str:
        """Enhance existing description with additional features."""
        ...

    async def calculate_description_confidence(
        self, description: str, product_features: ProductFeatures
    ) -> float:
        """Calculate confidence score for generated description."""
        ...


class AttributeMappingServiceProtocol(Protocol):
    """Protocol for attribute mapping services."""

    async def map_attributes(
        self, product_features: ProductFeatures, category_id: str
    ) -> dict[str, Any]:
        """Map product features to MercadoLibre attributes."""
        ...

    async def validate_attributes(
        self, attributes: dict[str, Any], category_id: str
    ) -> dict[str, Any]:
        """Validate attributes against MercadoLibre requirements."""
        ...

    async def get_required_attributes(self, category_id: str) -> list[str]:
        """Get required attributes for a category."""
        ...

    async def get_optional_attributes(self, category_id: str) -> list[str]:
        """Get optional attributes for a category."""
        ...

    async def calculate_attribute_confidence(
        self, attributes: dict[str, Any], product_features: ProductFeatures
    ) -> float:
        """Calculate confidence score for mapped attributes."""
        ...


class ContentValidationServiceProtocol(Protocol):
    """Protocol for content validation services."""

    async def validate_content(self, content: GeneratedContent) -> dict[str, Any]:
        """Validate generated content comprehensively."""
        ...

    async def check_ml_compliance(self, content: GeneratedContent) -> dict[str, Any]:
        """Check if content complies with MercadoLibre policies."""
        ...

    async def calculate_quality_score(self, content: GeneratedContent) -> float:
        """Calculate overall quality score for content."""
        ...

    async def get_improvement_suggestions(self, content: GeneratedContent) -> list[str]:
        """Get suggestions for improving content quality."""
        ...
