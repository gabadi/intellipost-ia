"""
Content Generation domain service.

This module provides the core business logic for content generation,
orchestrating the various components needed to create MercadoLibre-optimized listings.
"""

from typing import Any
from uuid import UUID

from modules.content_generation.domain.entities import (
    ConfidenceScore,
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    ContentGenerationError,
    InvalidContentError,
    QualityThresholdError,
)
from modules.content_generation.domain.ports.ai_service_protocols import (
    AIContentGeneratorProtocol,
    AttributeMappingServiceProtocol,
    ContentRepositoryProtocol,
    ContentValidationServiceProtocol,
    DescriptionGenerationServiceProtocol,
    ImageData,
    MLCategoryServiceProtocol,
    TitleGenerationServiceProtocol,
)


class ContentGenerationService:
    """
    Domain service for content generation operations.

    This service orchestrates the entire content generation process,
    coordinating between different AI services and validation components.
    """

    def __init__(
        self,
        ai_content_generator: AIContentGeneratorProtocol,
        ml_category_service: MLCategoryServiceProtocol,
        content_repository: ContentRepositoryProtocol,
        title_generation_service: TitleGenerationServiceProtocol,
        description_generation_service: DescriptionGenerationServiceProtocol,
        attribute_mapping_service: AttributeMappingServiceProtocol,
        content_validation_service: ContentValidationServiceProtocol,
        quality_threshold: float = 0.7,
    ):
        self._ai_content_generator = ai_content_generator
        self._ml_category_service = ml_category_service
        self._content_repository = content_repository
        self._title_generation_service = title_generation_service
        self._description_generation_service = description_generation_service
        self._attribute_mapping_service = attribute_mapping_service
        self._content_validation_service = content_validation_service
        self._quality_threshold = quality_threshold

    async def generate_content(
        self,
        product_id: UUID,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: dict[str, float] | None = None,
        target_audience: str | None = None,
        regenerate: bool = False,
    ) -> GeneratedContent:
        """
        Generate complete MercadoLibre listing content.

        Args:
            product_id: ID of the product to generate content for
            images: List of product images
            prompt: User prompt describing the product
            category_hint: Optional hint for category detection
            price_range: Optional price range for estimation
            target_audience: Optional target audience specification
            regenerate: Whether to regenerate existing content

        Returns:
            GeneratedContent: The generated content entity

        Raises:
            ContentGenerationError: If content generation fails
            QualityThresholdError: If generated content doesn't meet quality standards
        """
        # Check if content already exists
        if not regenerate:
            existing_content = await self._content_repository.get_content_by_product_id(
                product_id
            )
            if existing_content:
                return existing_content

        # Generate content using AI service
        generated_content = await self._ai_content_generator.generate_listing(
            images=images,
            prompt=prompt,
            category_hint=category_hint,
            price_range=price_range,
            target_audience=target_audience,
        )

        # Validate the generated content
        validation_result = await self._content_validation_service.validate_content(
            generated_content
        )

        if not validation_result.get("is_valid", False):
            raise InvalidContentError(
                f"Generated content failed validation: {validation_result.get('errors', [])}",
                content_type="complete_listing",
                validation_errors=validation_result.get("errors", {}),
            )

        # Check quality threshold
        if generated_content.confidence_overall < self._quality_threshold:
            raise QualityThresholdError(
                f"Generated content quality ({generated_content.confidence_overall:.2f}) below threshold ({self._quality_threshold:.2f})",
                quality_score=generated_content.confidence_overall,
                threshold=self._quality_threshold,
            )

        # Save the generated content
        saved_content = await self._content_repository.save_generated_content(
            generated_content
        )

        return saved_content

    async def enhance_content(
        self,
        content_id: UUID,
        enhancement_type: str,
        additional_data: dict[str, Any] | None = None,
    ) -> GeneratedContent:
        """
        Enhance existing generated content.

        Args:
            content_id: ID of the content to enhance
            enhancement_type: Type of enhancement (title, description, attributes)
            additional_data: Additional data for enhancement

        Returns:
            GeneratedContent: Enhanced content entity

        Raises:
            ContentGenerationError: If enhancement fails
        """
        # Get existing content
        existing_content = await self._content_repository.get_generated_content(
            content_id
        )
        if not existing_content:
            raise ContentGenerationError(f"Content not found: {content_id}")

        # Perform enhancement based on type
        if enhancement_type == "title":
            await self._enhance_title(existing_content, additional_data)
            # Create new content with enhanced title
            # Implementation details for creating updated content entity
            pass
        elif enhancement_type == "description":
            await self._enhance_description(existing_content, additional_data)
            # Create new content with enhanced description
            # Implementation details for creating updated content entity
            pass
        elif enhancement_type == "attributes":
            await self._enhance_attributes(existing_content, additional_data)
            # Create new content with enhanced attributes
            # Implementation details for creating updated content entity
            pass
        else:
            raise ContentGenerationError(
                f"Unknown enhancement type: {enhancement_type}"
            )

        # For now, return the existing content
        # This would be replaced with actual enhancement logic
        return existing_content

    async def validate_content_quality(
        self,
        content: GeneratedContent,
    ) -> dict[str, Any]:
        """
        Validate content quality and provide improvement suggestions.

        Args:
            content: Generated content to validate

        Returns:
            Dict containing validation results and suggestions
        """
        # Perform comprehensive validation
        validation_result = await self._content_validation_service.validate_content(
            content
        )

        # Check MercadoLibre compliance
        compliance_result = await self._content_validation_service.check_ml_compliance(
            content
        )

        # Calculate quality score
        quality_score = await self._content_validation_service.calculate_quality_score(
            content
        )

        # Get improvement suggestions
        suggestions = (
            await self._content_validation_service.get_improvement_suggestions(content)
        )

        return {
            "is_valid": validation_result.get("is_valid", False),
            "validation_errors": validation_result.get("errors", []),
            "compliance_issues": compliance_result.get("issues", []),
            "quality_score": quality_score,
            "meets_threshold": quality_score >= self._quality_threshold,
            "improvement_suggestions": suggestions,
            "quality_indicators": content.get_quality_indicators(),
        }

    async def regenerate_content(
        self,
        product_id: UUID,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: dict[str, float] | None = None,
        target_audience: str | None = None,
    ) -> GeneratedContent:
        """
        Regenerate content for a product.

        This method will create a new version of the content,
        incrementing the version number.

        Args:
            product_id: ID of the product to regenerate content for
            images: List of product images
            prompt: User prompt describing the product
            category_hint: Optional hint for category detection
            price_range: Optional price range for estimation
            target_audience: Optional target audience specification

        Returns:
            GeneratedContent: The newly generated content entity
        """
        return await self.generate_content(
            product_id=product_id,
            images=images,
            prompt=prompt,
            category_hint=category_hint,
            price_range=price_range,
            target_audience=target_audience,
            regenerate=True,
        )

    async def get_content_versions(
        self,
        product_id: UUID,
    ) -> list[GeneratedContent]:
        """
        Get all versions of content for a product.

        Args:
            product_id: ID of the product

        Returns:
            List of GeneratedContent entities, ordered by version
        """
        return await self._content_repository.get_content_versions(product_id)

    async def calculate_confidence_score(
        self,
        content: GeneratedContent,
    ) -> ConfidenceScore:
        """
        Calculate confidence score for generated content.

        Args:
            content: Generated content to analyze

        Returns:
            ConfidenceScore: Confidence score entity
        """
        return await self._ai_content_generator.calculate_confidence(content)

    async def _enhance_title(
        self,
        content: GeneratedContent,
        additional_data: dict[str, Any] | None = None,
    ) -> str:
        """Enhance the title of existing content."""
        # Extract product features from additional data or existing content
        product_features = additional_data or {}

        # Generate enhanced title
        enhanced_title = await self._title_generation_service.generate_optimized_title(
            product_features=product_features,
            category_id=content.ml_category_id,
            max_length=60,
        )

        return enhanced_title

    async def _enhance_description(
        self,
        content: GeneratedContent,
        additional_data: dict[str, Any] | None = None,
    ) -> str:
        """Enhance the description of existing content."""
        # Extract additional features
        additional_features = additional_data or {}

        # Enhance description
        enhanced_description = (
            await self._description_generation_service.enhance_description(
                base_description=content.description,
                additional_features=additional_features,
            )
        )

        return enhanced_description

    async def _enhance_attributes(
        self,
        content: GeneratedContent,
        additional_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Enhance the attributes of existing content."""
        # Extract product features from additional data
        product_features = additional_data or {}

        # Map additional attributes
        enhanced_attributes = await self._attribute_mapping_service.map_attributes(
            product_features=product_features,
            category_id=content.ml_category_id,
        )

        # Merge with existing attributes
        if hasattr(content.ml_attributes, "to_dict"):
            current_attributes = content.ml_attributes.to_dict()
        else:
            current_attributes = (
                content.ml_attributes if isinstance(content.ml_attributes, dict) else {}
            )
        merged_attributes = {**current_attributes, **enhanced_attributes}

        return merged_attributes

    def _increment_version(self, content: GeneratedContent) -> int:
        """Increment the version number for regenerated content."""
        return content.version + 1

    async def validate_category_compatibility(
        self,
        category_id: str,
        product_features: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate if a category is compatible with product features.

        Args:
            category_id: MercadoLibre category ID
            product_features: Extracted product features

        Returns:
            Dict containing validation results
        """
        return await self._ml_category_service.validate_category(
            category_id=category_id,
            product_features=product_features,
        )

    async def get_category_requirements(
        self,
        category_id: str,
    ) -> dict[str, Any]:
        """
        Get requirements for a specific category.

        Args:
            category_id: MercadoLibre category ID

        Returns:
            Dict containing category requirements
        """
        return await self._ml_category_service.get_category_attributes(category_id)

    async def estimate_content_quality(
        self,
        content: GeneratedContent,
    ) -> float:
        """
        Estimate the quality of generated content.

        Args:
            content: Generated content to evaluate

        Returns:
            Quality score between 0.0 and 1.0
        """
        return await self._content_validation_service.calculate_quality_score(content)
