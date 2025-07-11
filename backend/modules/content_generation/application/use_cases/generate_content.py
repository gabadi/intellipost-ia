"""
Generate Content Use Case implementation.

This module orchestrates the entire content generation process,
coordinating between different services to create optimized MercadoLibre listings.
"""

import time
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from modules.content_generation.domain.entities import (
    AIGeneration,
    EnhancementData,
    GeneratedContent,
    GenerationStatus,
    ProcessingStep,
    ProductFeatures,
)
from modules.content_generation.domain.exceptions import (
    CategoryDetectionError,
    ContentGenerationError,
    InvalidContentError,
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
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)
from modules.content_generation.domain.services.value_object_migration_service import (
    ValueObjectMigrationService,
)
from modules.content_generation.domain.value_objects.category_results import (
    CategoryPredictionResult,
)
from shared.value_objects import PriceRange


class GenerateContentUseCase:
    """
    Use case for generating MercadoLibre-optimized content.

    This use case orchestrates the entire content generation workflow,
    from image analysis to final content validation and storage.
    """

    def __init__(
        self,
        ai_service: AIContentGeneratorProtocol,
        content_repository: ContentRepositoryProtocol,
        title_service: TitleGenerationServiceProtocol,
        description_service: DescriptionGenerationServiceProtocol,
        validation_service: ContentValidationServiceProtocol,
        attribute_service: AttributeMappingServiceProtocol,
        category_service: MLCategoryServiceProtocol,
        migration_service: ValueObjectMigrationService,
        logger: ContentLoggerProtocol,
        quality_threshold: float = 0.7,
        max_retry_attempts: int = 3,
    ):
        """
        Initialize the generate content use case.

        Args:
            ai_service: AI content generation service protocol
            content_repository: Content repository protocol
            title_service: Title generation service protocol
            description_service: Description generation service protocol
            validation_service: Content validation service protocol
            attribute_service: Attribute mapping service protocol
            category_service: MercadoLibre category service protocol
            migration_service: Value object migration service
            logger: Content logger protocol for logging operations
            quality_threshold: Minimum quality threshold
            max_retry_attempts: Maximum retry attempts
        """
        self.ai_service = ai_service
        self.content_repository = content_repository
        self.title_service = title_service
        self.description_service = description_service
        self.validation_service = validation_service
        self.attribute_service = attribute_service
        self.category_service = category_service
        self.migration_service = migration_service
        self.logger = logger
        self.quality_threshold = quality_threshold
        self.max_retry_attempts = max_retry_attempts

        # Processing step weights for progress calculation
        self.step_weights = {
            ProcessingStep.IMAGE_ANALYSIS: 0.15,
            ProcessingStep.CONTENT_EXTRACTION: 0.10,
            ProcessingStep.CATEGORY_DETECTION: 0.15,
            ProcessingStep.TITLE_GENERATION: 0.15,
            ProcessingStep.DESCRIPTION_GENERATION: 0.15,
            ProcessingStep.ATTRIBUTE_MAPPING: 0.10,
            ProcessingStep.PRICE_ESTIMATION: 0.05,
            ProcessingStep.QUALITY_VALIDATION: 0.10,
            ProcessingStep.CONTENT_FINALIZATION: 0.05,
        }

        self.logger.info("Initialized Generate Content Use Case")

    async def execute(
        self,
        product_id: UUID,
        images: Sequence[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: PriceRange | None = None,
        target_audience: str | None = None,
        regenerate: bool = False,
    ) -> AIGeneration:
        """
        Execute the content generation process.

        Args:
            product_id: ID of the product to generate content for
            images: List of product images
            prompt: User prompt describing the product
            category_hint: Optional hint for category detection
            price_range: Optional price range for estimation
            target_audience: Optional target audience specification
            regenerate: Whether to regenerate existing content

        Returns:
            AIGeneration: Processing status and results

        Raises:
            ContentGenerationError: If content generation fails
        """
        # Create AI generation tracking entity
        generation_id = uuid4()
        ai_generation = AIGeneration(
            id=generation_id,
            product_id=product_id,
            status=GenerationStatus.PENDING,
            input_images=[img.s3_key for img in images],
            input_prompt=prompt,
            category_hint=category_hint,
            price_range=price_range,
            target_audience=target_audience,
            estimated_completion_seconds=30,
            created_at=datetime.now(UTC),
        )

        try:
            # Check if content already exists and not regenerating
            if not regenerate:
                existing_content = (
                    await self.content_repository.get_content_by_product_id(product_id)
                )
                if existing_content:
                    ai_generation.status = GenerationStatus.COMPLETED
                    ai_generation.generated_content_id = existing_content.id
                    ai_generation.completed_at = datetime.now(UTC)
                    return ai_generation

            # Start processing
            ai_generation.start_processing("gemini-2.5-flash")

            # Execute processing steps
            generated_content = await self._execute_processing_steps(
                ai_generation,
                images,
                prompt,
                category_hint,
                price_range,
                target_audience,
            )

            # Complete processing
            processing_time_ms = (
                int((time.time() - ai_generation.created_at.timestamp()) * 1000)
                if ai_generation.created_at
                else 0
            )
            ai_generation.complete_processing(generated_content.id, processing_time_ms)

            self.logger.info(
                f"Content generation completed successfully for product {product_id}"
            )

            return ai_generation

        except Exception as e:
            # Handle failure
            ai_generation.fail_processing(str(e), type(e).__name__)
            self.logger.error(
                f"Content generation failed for product {product_id}: {e}"
            )
            raise

    async def regenerate_content(
        self,
        product_id: UUID,
        images: Sequence[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: PriceRange | None = None,
        target_audience: str | None = None,
    ) -> AIGeneration:
        """
        Regenerate content for a product.

        Args:
            product_id: ID of the product to regenerate content for
            images: List of product images
            prompt: User prompt describing the product
            category_hint: Optional hint for category detection
            price_range: Optional price range for estimation
            target_audience: Optional target audience specification

        Returns:
            AIGeneration: Processing status and results
        """
        return await self.execute(
            product_id=product_id,
            images=images,
            prompt=prompt,
            category_hint=category_hint,
            price_range=price_range,
            target_audience=target_audience,
            regenerate=True,
        )

    async def validate_generated_content(
        self,
        content_id: UUID,
    ) -> dict[str, Any]:
        """
        Validate generated content.

        Args:
            content_id: ID of the content to validate

        Returns:
            Dict containing validation results
        """
        content = await self.content_repository.get_generated_content(content_id)
        if not content:
            raise ContentGenerationError(f"Content not found: {content_id}")

        # Perform comprehensive validation
        validation_results = await self.validation_service.validate_content(content)

        # Check MercadoLibre compliance
        compliance_results = await self.validation_service.check_ml_compliance(content)

        # Calculate quality score
        quality_score = await self.validation_service.calculate_quality_score(content)

        # Get improvement suggestions
        suggestions = await self.validation_service.get_improvement_suggestions(content)

        return {
            "content_id": str(content_id),
            "is_valid": validation_results.valid,
            "validation_errors": validation_results.validation_errors,
            "validation_warnings": validation_results.validation_warnings,
            "is_compliant": compliance_results.compliant,
            "compliance_issues": compliance_results.policy_violations,
            "quality_score": quality_score,
            "meets_threshold": quality_score >= self.quality_threshold,
            "improvement_suggestions": suggestions,
            "quality_indicators": content.get_quality_indicators(),
        }

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
        """
        content = await self.content_repository.get_generated_content(content_id)
        if not content:
            raise ContentGenerationError(f"Content not found: {content_id}")

        # Validate enhancement data
        if not enhancement_data.is_valid_for_type():
            raise ContentGenerationError(
                f"Invalid enhancement data for type: {enhancement_data.enhancement_type}"
            )

        enhanced_content = None

        if enhancement_data.enhancement_type == "title":
            enhanced_content = await self._enhance_title(content, enhancement_data)
        elif enhancement_data.enhancement_type == "description":
            enhanced_content = await self._enhance_description(
                content, enhancement_data
            )
        elif enhancement_data.enhancement_type == "attributes":
            enhanced_content = await self._enhance_attributes(content, enhancement_data)
        else:
            raise ContentGenerationError(
                f"Unknown enhancement type: {enhancement_data.enhancement_type}"
            )

        # Save enhanced content
        saved_content = await self.content_repository.update_generated_content(
            enhanced_content
        )

        return saved_content

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
        """
        # Convert legacy format to EnhancementData
        if additional_data is None:
            additional_data = {}

        # Ensure enhancement_type is included
        additional_data["enhancement_type"] = enhancement_type

        enhancement_data = EnhancementData.from_dict_legacy(additional_data)

        return await self.enhance_content(content_id, enhancement_data)

    async def get_generated_content(
        self,
        content_id: UUID,
    ) -> GeneratedContent | None:
        """
        Get generated content by ID.

        Args:
            content_id: Content ID to retrieve

        Returns:
            GeneratedContent or None if not found

        Raises:
            EntityNotFoundError: If content is not found
        """
        try:
            content = await self.content_repository.get_generated_content(content_id)
            if content is None:
                from modules.content_generation.domain.exceptions import (
                    EntityNotFoundError,
                )

                raise EntityNotFoundError(
                    f"Generated content not found: {content_id}",
                    "GeneratedContent",
                    str(content_id),
                )
            return content
        except Exception as e:
            self.logger.error(f"Error getting generated content {content_id}: {e}")
            raise

    async def get_content_versions(
        self,
        product_id: UUID,
    ) -> list[GeneratedContent]:
        """
        Get all versions of content for a product.

        Args:
            product_id: ID of the product

        Returns:
            List of GeneratedContent entities
        """
        return await self.content_repository.get_content_versions(product_id)

    async def _execute_processing_steps(
        self,
        ai_generation: AIGeneration,
        images: Sequence[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: PriceRange | None = None,
        target_audience: str | None = None,
    ) -> GeneratedContent:
        """Execute all processing steps in sequence."""

        # Step 1: Image Analysis
        ai_generation.update_progress(ProcessingStep.IMAGE_ANALYSIS, 10.0)
        image_features = await self._analyze_images(images)

        # Step 2: Content Extraction
        ai_generation.update_progress(ProcessingStep.CONTENT_EXTRACTION, 20.0)
        product_features = await self._extract_product_features(
            images, prompt, image_features
        )

        # Step 3: Category Detection
        ai_generation.update_progress(ProcessingStep.CATEGORY_DETECTION, 35.0)
        category_info = await self._detect_category(product_features, category_hint)

        # Step 4: Title Generation
        ai_generation.update_progress(ProcessingStep.TITLE_GENERATION, 50.0)
        title_info = await self._generate_title(
            product_features, category_info.predicted_category.category_id
        )

        # Step 5: Description Generation
        ai_generation.update_progress(ProcessingStep.DESCRIPTION_GENERATION, 65.0)
        description_info = await self._generate_description(
            product_features, category_info.predicted_category.category_id
        )

        # Step 6: Attribute Mapping
        ai_generation.update_progress(ProcessingStep.ATTRIBUTE_MAPPING, 75.0)
        attribute_info = await self._map_attributes(
            product_features, category_info.predicted_category.category_id
        )

        # Step 7: Price Estimation
        ai_generation.update_progress(ProcessingStep.PRICE_ESTIMATION, 80.0)
        price_info = await self._estimate_price(
            product_features, category_info.predicted_category.category_id, price_range
        )

        # Step 8: Quality Validation
        ai_generation.update_progress(ProcessingStep.QUALITY_VALIDATION, 90.0)
        generated_content = await self._create_generated_content(
            ai_generation.product_id,
            title_info,
            description_info,
            category_info,
            attribute_info,
            price_info,
            product_features,
        )

        # Validate content
        validation_results = await self.validation_service.validate_content(
            generated_content
        )

        if not validation_results.valid:
            raise InvalidContentError(
                f"Generated content failed validation: {validation_results.validation_errors}",
                content_type="complete_listing",
                validation_errors={
                    f"error_{i}": err
                    for i, err in enumerate(validation_results.validation_errors)
                },
            )

        # Step 9: Content Finalization
        ai_generation.update_progress(ProcessingStep.CONTENT_FINALIZATION, 95.0)

        # Save generated content
        saved_content = await self.content_repository.save_generated_content(
            generated_content
        )

        ai_generation.update_progress(ProcessingStep.CONTENT_FINALIZATION, 100.0)

        return saved_content

    async def _analyze_images(self, images: Sequence[ImageData]) -> dict[str, Any]:
        """Analyze images to extract visual features."""
        # This would typically use computer vision services
        # For now, return basic image metadata
        return {
            "image_count": len(images),
            "formats": [img.file_format for img in images],
            "resolutions": [
                (img.resolution_width, img.resolution_height) for img in images
            ],
            "has_multiple_angles": len(images) > 1,
        }

    async def _extract_product_features(
        self,
        images: Sequence[ImageData],
        prompt: str,
        image_features: dict[str, Any],
    ) -> ProductFeatures:
        """Extract product features from images and prompt."""
        try:
            # Use AI service to extract features
            features = await self.ai_service.extract_product_features(
                list(images), prompt
            )

            # Enhance with image analysis
            enhanced_data = features.to_dict_legacy()
            enhanced_data.update(image_features)

            return ProductFeatures.from_dict_legacy(enhanced_data)

        except Exception as e:
            self.logger.error(f"Error extracting product features: {e}")
            # Return basic features from prompt
            fallback_data = {
                "description": prompt,
                "category": "general",
                "condition": "new",
            }
            return ProductFeatures.from_dict_legacy(fallback_data)

    async def _detect_category(
        self,
        product_features: ProductFeatures,
        category_hint: str | None = None,
    ) -> CategoryPredictionResult:
        """Detect MercadoLibre category."""
        try:
            category_prediction = await self.category_service.predict_category(
                product_features, category_hint
            )

            # Validate category
            validation_results = await self.category_service.validate_category(
                category_prediction.predicted_category.category_id, product_features
            )

            if not validation_results.valid:
                self.logger.warning(
                    f"Category validation failed: {validation_results.validation_errors}"
                )
                # Use fallback category
                from modules.content_generation.domain.value_objects.category_results import (
                    CategoryInfo,
                    CategoryPredictionResult,
                )

                fallback_category = CategoryInfo(
                    category_id="MLA1144", category_name="Electrónicos, Audio y Video"
                )
                category_prediction = CategoryPredictionResult(
                    predicted_category=fallback_category,
                    confidence_score=0.5,
                    prediction_quality="low",
                    needs_human_review=True,
                )

            return category_prediction

        except CategoryDetectionError as e:
            self.logger.error(f"Category detection failed: {e}")
            # Return default category
            from modules.content_generation.domain.value_objects.category_results import (
                CategoryInfo,
                CategoryPredictionResult,
            )

            fallback_category = CategoryInfo(
                category_id="MLA1144", category_name="Electrónicos, Audio y Video"
            )
            return CategoryPredictionResult(
                predicted_category=fallback_category,
                confidence_score=0.3,
                prediction_quality="low",
                needs_human_review=True,
            )

    async def _generate_title(
        self,
        product_features: ProductFeatures,
        category_id: str,
    ) -> dict[str, Any]:
        """Generate optimized title."""
        try:
            title = await self.title_service.generate_optimized_title(
                product_features, category_id
            )

            # Validate title
            validation_results = await self.title_service.validate_title(
                title, category_id
            )

            # Calculate confidence
            confidence = await self.title_service.calculate_title_confidence(
                title, product_features
            )

            return {
                "title": title,
                "confidence": confidence,
                "validation": validation_results,
            }

        except Exception as e:
            self.logger.error(f"Title generation failed: {e}")
            # Return fallback title
            brand = product_features.brand or ""
            model = product_features.model or ""
            fallback_title = f"{brand} {model}".strip() or "Producto"

            return {
                "title": fallback_title,
                "confidence": 0.3,
                "validation": {"is_valid": True, "warnings": ["Fallback title used"]},
            }

    async def _generate_description(
        self,
        product_features: ProductFeatures,
        category_id: str,
    ) -> dict[str, Any]:
        """Generate comprehensive description."""
        try:
            description = await self.description_service.generate_description(
                product_features, category_id
            )

            # Validate description
            validation_results = await self.description_service.validate_description(
                description, category_id
            )

            # Calculate confidence
            confidence = (
                await self.description_service.calculate_description_confidence(
                    description, product_features
                )
            )

            return {
                "description": description,
                "confidence": confidence,
                "validation": validation_results,
            }

        except Exception as e:
            self.logger.error(f"Description generation failed: {e}")
            # Return fallback description
            fallback_description = product_features.description or "Producto de calidad"

            return {
                "description": fallback_description,
                "confidence": 0.3,
                "validation": {
                    "is_valid": True,
                    "warnings": ["Fallback description used"],
                },
            }

    async def _map_attributes(
        self,
        product_features: ProductFeatures,
        category_id: str,
    ) -> dict[str, Any]:
        """Map product attributes."""
        try:
            attributes = await self.attribute_service.map_attributes(
                product_features, category_id
            )

            # Validate attributes
            validation_results = await self.attribute_service.validate_attributes(
                attributes, category_id
            )

            # Calculate confidence
            confidence = await self.attribute_service.calculate_attribute_confidence(
                attributes, product_features
            )

            return {
                "attributes": attributes,
                "confidence": confidence,
                "validation": validation_results,
            }

        except Exception as e:
            self.logger.error(f"Attribute mapping failed: {e}")
            # Return basic attributes
            fallback_attributes = {}
            if product_features.brand:
                fallback_attributes["BRAND"] = product_features.brand
            if product_features.model:
                fallback_attributes["MODEL"] = product_features.model

            return {
                "attributes": fallback_attributes,
                "confidence": 0.3,
                "validation": {
                    "is_valid": True,
                    "warnings": ["Fallback attributes used"],
                },
            }

    async def _estimate_price(
        self,
        product_features: ProductFeatures,
        category_id: str,
        price_range: PriceRange | None = None,
    ) -> dict[str, Any]:
        """Estimate product price."""
        try:
            price_estimation = await self.ai_service.estimate_price(
                product_features, category_id
            )

            # Apply price range constraints if provided
            estimated_price = float(price_estimation.estimated_price)
            if price_range:
                min_price = float(price_range.min_price)
                max_price = float(price_range.max_price)

                if estimated_price < min_price:
                    estimated_price = min_price
                elif estimated_price > max_price:
                    estimated_price = max_price

            return {
                "estimated_price": estimated_price,
                "confidence": price_estimation.confidence_score,
                "reasoning": f"ML estimation with {price_estimation.model_version}",
            }

        except Exception as e:
            self.logger.error(f"Price estimation failed: {e}")
            # Return fallback price
            fallback_price = 10000.0  # Default price in ARS
            if price_range:
                fallback_price = float(price_range.min_price)

            return {
                "estimated_price": fallback_price,
                "confidence": 0.3,
                "reasoning": "Fallback price used due to estimation failure",
            }

    async def _create_generated_content(
        self,
        product_id: UUID,
        title_info: dict[str, Any],
        description_info: dict[str, Any],
        category_info: CategoryPredictionResult,
        attribute_info: dict[str, Any],
        price_info: dict[str, Any],
        product_features: ProductFeatures,
    ) -> GeneratedContent:
        """Create the final generated content entity."""

        # Calculate overall confidence
        confidence_scores = {
            "title": title_info["confidence"],
            "description": description_info["confidence"],
            "category": category_info.confidence_score,
            "attributes": attribute_info["confidence"],
            "price": price_info["confidence"],
        }

        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)

        # Create content entity
        content = GeneratedContent(
            id=uuid4(),
            product_id=product_id,
            title=title_info["title"],
            description=description_info["description"],
            ml_category_id=category_info.predicted_category.category_id,
            ml_category_name=category_info.predicted_category.category_name,
            ml_title=title_info["title"][:60],  # Ensure ML title fits limit
            ml_price=price_info["estimated_price"],
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition=product_features.condition or "new",
            ml_listing_type_id="gold_special",
            ml_attributes=self.migration_service.migrate_ml_attributes(
                attribute_info["attributes"]
            ),
            ml_sale_terms=self.migration_service.migrate_ml_sale_terms(
                {"warranty": "Garantía del vendedor"}
            ),
            ml_shipping=self.migration_service.migrate_ml_shipping(
                {"mode": "me2", "free_shipping": True}
            ),
            confidence_overall=overall_confidence,
            confidence_breakdown=confidence_scores,
            ai_provider="gemini",
            ai_model_version="gemini-2.5-flash",
            generation_time_ms=0,  # Will be set by caller
            version=1,
            generated_at=datetime.now(UTC),
        )

        return content

    async def _enhance_title(
        self,
        content: GeneratedContent,
        enhancement_data: EnhancementData,
    ) -> GeneratedContent:
        """Enhance content title."""
        # Convert enhancement data to ProductFeatures for compatibility
        # Use custom_attributes as the product features data
        if enhancement_data.custom_attributes:
            product_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            product_features = ProductFeatures.create_minimal()

        # Generate enhanced title
        enhanced_title = await self.title_service.generate_optimized_title(
            product_features, content.ml_category_id
        )

        # Calculate new confidence
        title_confidence = await self.title_service.calculate_title_confidence(
            enhanced_title, product_features
        )

        # Update content
        enhanced_content = GeneratedContent(
            id=content.id,
            product_id=content.product_id,
            title=enhanced_title,
            description=content.description,
            ml_category_id=content.ml_category_id,
            ml_category_name=content.ml_category_name,
            ml_title=enhanced_title[:60],
            ml_price=content.ml_price,
            ml_currency_id=content.ml_currency_id,
            ml_available_quantity=content.ml_available_quantity,
            ml_buying_mode=content.ml_buying_mode,
            ml_condition=content.ml_condition,
            ml_listing_type_id=content.ml_listing_type_id,
            ml_attributes=content.ml_attributes,
            ml_sale_terms=content.ml_sale_terms,
            ml_shipping=content.ml_shipping,
            confidence_overall=self._recalculate_overall_confidence(
                content.confidence_breakdown, "title", title_confidence
            ),
            confidence_breakdown={
                **content.confidence_breakdown,
                "title": title_confidence,
            },
            ai_provider=content.ai_provider,
            ai_model_version=content.ai_model_version,
            generation_time_ms=content.generation_time_ms,
            version=content.version + 1,
            generated_at=content.generated_at,
            updated_at=datetime.now(UTC),
        )

        return enhanced_content

    async def _enhance_description(
        self,
        content: GeneratedContent,
        enhancement_data: EnhancementData,
    ) -> GeneratedContent:
        """Enhance content description."""
        # Convert enhancement data to ProductFeatures for compatibility
        if enhancement_data.custom_attributes:
            additional_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            additional_features = ProductFeatures.create_minimal()

        # Enhance description
        enhanced_description = await self.description_service.enhance_description(
            content.description, additional_features
        )

        # Calculate new confidence
        description_confidence = (
            await self.description_service.calculate_description_confidence(
                enhanced_description, additional_features
            )
        )

        # Update content
        enhanced_content = GeneratedContent(
            id=content.id,
            product_id=content.product_id,
            title=content.title,
            description=enhanced_description,
            ml_category_id=content.ml_category_id,
            ml_category_name=content.ml_category_name,
            ml_title=content.ml_title,
            ml_price=content.ml_price,
            ml_currency_id=content.ml_currency_id,
            ml_available_quantity=content.ml_available_quantity,
            ml_buying_mode=content.ml_buying_mode,
            ml_condition=content.ml_condition,
            ml_listing_type_id=content.ml_listing_type_id,
            ml_attributes=content.ml_attributes,
            ml_sale_terms=content.ml_sale_terms,
            ml_shipping=content.ml_shipping,
            confidence_overall=self._recalculate_overall_confidence(
                content.confidence_breakdown, "description", description_confidence
            ),
            confidence_breakdown={
                **content.confidence_breakdown,
                "description": description_confidence,
            },
            ai_provider=content.ai_provider,
            ai_model_version=content.ai_model_version,
            generation_time_ms=content.generation_time_ms,
            version=content.version + 1,
            generated_at=content.generated_at,
            updated_at=datetime.now(UTC),
        )

        return enhanced_content

    async def _enhance_attributes(
        self,
        content: GeneratedContent,
        enhancement_data: EnhancementData,
    ) -> GeneratedContent:
        """Enhance content attributes."""
        # Convert enhancement data to ProductFeatures for compatibility
        if enhancement_data.custom_attributes:
            product_features = ProductFeatures.from_dict_legacy(
                enhancement_data.custom_attributes
            )
        else:
            product_features = ProductFeatures.create_minimal()

        # Map additional attributes
        enhanced_attributes = await self.attribute_service.map_attributes(
            product_features, content.ml_category_id
        )

        # Merge with existing attributes
        if hasattr(content.ml_attributes, "to_dict"):
            current_attributes_dict = content.ml_attributes.to_dict()
        else:
            current_attributes_dict = (
                content.ml_attributes if isinstance(content.ml_attributes, dict) else {}
            )

        # enhanced_attributes is already MLAttributes, get its dict representation
        enhanced_attributes_dict = enhanced_attributes.to_dict()

        # Merge attributes dictionaries
        merged_attributes_dict = {**current_attributes_dict, **enhanced_attributes_dict}

        # Convert to MLAttributes for the service call
        from modules.content_generation.domain.value_objects.ml_attributes import (
            MLAttributes,
        )

        merged_attributes = MLAttributes(
            category_id=content.ml_category_id,
            mapped_attributes=merged_attributes_dict,
            confidence_score=0.8,  # Default confidence for merged attributes
        )

        # Calculate new confidence
        attribute_confidence = (
            await self.attribute_service.calculate_attribute_confidence(
                merged_attributes, product_features
            )
        )

        # Update content
        enhanced_content = GeneratedContent(
            id=content.id,
            product_id=content.product_id,
            title=content.title,
            description=content.description,
            ml_category_id=content.ml_category_id,
            ml_category_name=content.ml_category_name,
            ml_title=content.ml_title,
            ml_price=content.ml_price,
            ml_currency_id=content.ml_currency_id,
            ml_available_quantity=content.ml_available_quantity,
            ml_buying_mode=content.ml_buying_mode,
            ml_condition=content.ml_condition,
            ml_listing_type_id=content.ml_listing_type_id,
            ml_attributes=self.migration_service.migrate_ml_attributes(
                merged_attributes.mapped_attributes
            ),
            ml_sale_terms=content.ml_sale_terms,
            ml_shipping=content.ml_shipping,
            confidence_overall=self._recalculate_overall_confidence(
                content.confidence_breakdown, "attributes", attribute_confidence
            ),
            confidence_breakdown={
                **content.confidence_breakdown,
                "attributes": attribute_confidence,
            },
            ai_provider=content.ai_provider,
            ai_model_version=content.ai_model_version,
            generation_time_ms=content.generation_time_ms,
            version=content.version + 1,
            generated_at=content.generated_at,
            updated_at=datetime.now(UTC),
        )

        return enhanced_content

    def _recalculate_overall_confidence(
        self,
        current_breakdown: dict[str, float],
        updated_component: str,
        new_confidence: float,
    ) -> float:
        """Recalculate overall confidence after updating a component."""
        updated_breakdown = {**current_breakdown, updated_component: new_confidence}
        return sum(updated_breakdown.values()) / len(updated_breakdown)
