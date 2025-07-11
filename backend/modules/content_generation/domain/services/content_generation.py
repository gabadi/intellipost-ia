"""
Content Generation domain service.

This module provides the core business logic for content generation,
orchestrating the various components needed to create MercadoLibre-optimized listings.
"""

from typing import Any
from uuid import UUID

from modules.content_generation.domain.entities import (
    ConfidenceScore,
    EnhancementData,
    GeneratedContent,
    ProductFeatures,
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
from modules.content_generation.domain.value_objects.category_results import (
    CategoryAttributes,
)
from modules.content_generation.domain.value_objects.ml_attributes import MLAttributes
from modules.content_generation.domain.value_objects.validation_results import (
    ContentValidationResult,
)
from shared.value_objects import PriceRange


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
        price_range: PriceRange | None = None,
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
        enhancement_data: EnhancementData,
    ) -> GeneratedContent:
        """
        Enhance existing generated content.

        Args:
            content_id: ID of the content to enhance
            enhancement_data: Enhancement data containing type and parameters

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

        # Validate enhancement data
        if not enhancement_data.is_valid_for_type():
            raise ContentGenerationError(
                f"Invalid enhancement data for type: {enhancement_data.enhancement_type}"
            )

        # Perform enhancement based on type
        if enhancement_data.enhancement_type == "title":
            await self._enhance_title(existing_content, enhancement_data)
            # Create new content with enhanced title
            # Implementation details for creating updated content entity
            pass
        elif enhancement_data.enhancement_type == "description":
            await self._enhance_description(existing_content, enhancement_data)
            # Create new content with enhanced description
            # Implementation details for creating updated content entity
            pass
        elif enhancement_data.enhancement_type == "attributes":
            await self._enhance_attributes(existing_content, enhancement_data)
            # Create new content with enhanced attributes
            # Implementation details for creating updated content entity
            pass
        else:
            raise ContentGenerationError(
                f"Unknown enhancement type: {enhancement_data.enhancement_type}"
            )

        # For now, return the existing content
        # This would be replaced with actual enhancement logic
        return existing_content

    async def enhance_content_legacy(
        self,
        content_id: UUID,
        enhancement_type: str,
        additional_data: dict[str, Any] | None = None,
    ) -> GeneratedContent:
        """
        Legacy method for enhancing content using old dict format.

        This method provides backward compatibility for existing code
        that still uses the old additional_data dict format.

        Args:
            content_id: ID of the content to enhance
            enhancement_type: Type of enhancement (title, description, attributes)
            additional_data: Additional data for enhancement (legacy format)

        Returns:
            GeneratedContent: Enhanced content entity

        Raises:
            ContentGenerationError: If enhancement fails
        """
        # Convert legacy format to EnhancementData
        if additional_data is None:
            additional_data = {}

        # Ensure enhancement_type is included
        additional_data["enhancement_type"] = enhancement_type

        enhancement_data = EnhancementData.from_dict_legacy(additional_data)

        return await self.enhance_content(content_id, enhancement_data)

    async def validate_content_quality(
        self,
        content: GeneratedContent,
    ) -> ContentValidationResult:
        """
        Validate content quality and provide improvement suggestions.

        Args:
            content: Generated content to validate

        Returns:
            ContentValidationResult containing validation results and suggestions
        """
        # Perform comprehensive validation
        validation_result = await self._content_validation_service.validate_content(
            content
        )

        # Get improvement suggestions
        suggestions = (
            await self._content_validation_service.get_improvement_suggestions(content)
        )

        # Enhance with improvement suggestions if not already present
        if suggestions and not validation_result.has_suggestions:
            validation_result = validation_result.__class__(
                valid=validation_result.valid,
                validation_score=validation_result.validation_score,
                content_quality_score=validation_result.content_quality_score,
                readability_score=validation_result.readability_score,
                grammar_score=validation_result.grammar_score,
                validation_errors=validation_result.validation_errors,
                validation_warnings=validation_result.validation_warnings,
                validation_suggestions=suggestions,
                word_count=validation_result.word_count,
                character_count=validation_result.character_count,
                sentence_count=validation_result.sentence_count,
                seo_score=validation_result.seo_score,
                keyword_density=validation_result.keyword_density,
                title_optimization=validation_result.title_optimization,
                validation_timestamp=validation_result.validation_timestamp,
                validation_engine=validation_result.validation_engine,
                validation_version=validation_result.validation_version,
            )

        return validation_result

    async def regenerate_content(
        self,
        product_id: UUID,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: PriceRange | None = None,
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
        enhancement_data: EnhancementData,
    ) -> str:
        """Enhance the title of existing content."""
        # Convert enhancement data to ProductFeatures for compatibility
        if enhancement_data.custom_attributes:
            product_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            product_features = ProductFeatures.create_minimal()

        # Generate enhanced title with constraints from enhancement data
        max_length = enhancement_data.target_length or 60
        enhanced_title = await self._title_generation_service.generate_optimized_title(
            product_features=product_features,
            category_id=content.ml_category_id,
            max_length=max_length,
        )

        return enhanced_title

    async def _enhance_description(
        self,
        content: GeneratedContent,
        enhancement_data: EnhancementData,
    ) -> str:
        """Enhance the description of existing content."""
        # Convert enhancement data to ProductFeatures for compatibility
        if enhancement_data.custom_attributes:
            additional_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            additional_features = ProductFeatures.create_minimal()

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
        enhancement_data: EnhancementData,
    ) -> MLAttributes:
        """Enhance the attributes of existing content."""
        # Convert enhancement data to ProductFeatures for compatibility
        if enhancement_data.custom_attributes:
            product_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            product_features = ProductFeatures.create_minimal()

        # Map additional attributes
        enhanced_attributes = await self._attribute_mapping_service.map_attributes(
            product_features=product_features,
            category_id=content.ml_category_id,
        )

        # Merge with existing attributes if needed
        if hasattr(content.ml_attributes, "to_dict"):
            current_attributes = content.ml_attributes.to_dict()
            merged_dict = {
                **current_attributes,
                **enhanced_attributes.mapped_attributes,
            }

            # Create new MLAttributes with merged data
            enhanced_attributes = MLAttributes(
                category_id=enhanced_attributes.category_id,
                mapped_attributes=merged_dict,
                confidence_score=enhanced_attributes.confidence_score,
                required_attributes=enhanced_attributes.required_attributes,
                optional_attributes=enhanced_attributes.optional_attributes,
                mapped_count=len(merged_dict),
                missing_required=enhanced_attributes.missing_required,
                completeness_score=enhanced_attributes.completeness_score,
                accuracy_score=enhanced_attributes.accuracy_score,
                relevance_score=enhanced_attributes.relevance_score,
                mapping_warnings=enhanced_attributes.mapping_warnings,
                mapping_suggestions=enhanced_attributes.mapping_suggestions,
                mapping_timestamp=enhanced_attributes.mapping_timestamp,
                mapping_engine=enhanced_attributes.mapping_engine,
                mapping_version=enhanced_attributes.mapping_version,
            )

        return enhanced_attributes

    def _increment_version(self, content: GeneratedContent) -> int:
        """Increment the version number for regenerated content."""
        return content.version + 1

    async def validate_category_compatibility(
        self,
        category_id: str,
        product_features: ProductFeatures,
    ) -> ContentValidationResult:
        """
        Validate if a category is compatible with product features.

        Args:
            category_id: MercadoLibre category ID
            product_features: Extracted product features

        Returns:
            ContentValidationResult containing validation results
        """
        return await self._ml_category_service.validate_category(
            category_id=category_id,
            product_features=product_features,
        )

    async def get_category_requirements(
        self,
        category_id: str,
    ) -> CategoryAttributes:
        """
        Get requirements for a specific category.

        Args:
            category_id: MercadoLibre category ID

        Returns:
            CategoryAttributes containing category requirements
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
