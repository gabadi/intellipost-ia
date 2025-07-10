"""
Unit tests for content generation domain entities.

This module tests the domain entities including GeneratedContent, ConfidenceScore, and AIGeneration.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.content_generation.domain.entities.ai_generation import (
    AIGeneration,
    GenerationStatus,
    ProcessingStep,
)
from modules.content_generation.domain.entities.confidence_score import ConfidenceScore
from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    InvalidContentError,
)
from shared.migration.value_object_migration import (
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
)

pytestmark = pytest.mark.unit


class TestGeneratedContent:
    """Test cases for GeneratedContent entity."""

    def test_create_generated_content_success(self):
        """Test creating a valid GeneratedContent instance."""
        content_id = uuid4()
        product_id = uuid4()

        content = GeneratedContent(
            id=content_id,
            product_id=product_id,
            title="iPhone 13 Pro 128GB Usado Excelente Estado",
            description="iPhone 13 Pro de 128GB en excelente estado con caja original...",
            ml_category_id="MLA1055",
            ml_category_name="Celulares y Smartphones",
            ml_title="iPhone 13 Pro 128GB Usado Excelente Estado",
            ml_price=Decimal("450000.00"),
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition="used",
            ml_listing_type_id="gold_special",
            ml_attributes=safe_migrate_ml_attributes(
                {
                    "COLOR": "Negro",
                    "BRAND": "Apple",
                    "LINE": "iPhone",
                    "MODEL": "iPhone 13 Pro",
                }
            ),
            ml_sale_terms=safe_migrate_ml_sale_terms(
                {
                    "WARRANTY_TYPE": {
                        "id": "WARRANTY_TYPE",
                        "name": "Tipo de garantía",
                        "value_id": "WARRANTY_TYPE_DEALER",
                        "value_name": "Garantía del vendedor",
                    }
                }
            ),
            ml_shipping=safe_migrate_ml_shipping(
                {"mode": "me2", "local_pick_up": True, "free_shipping": False}
            ),
            confidence_overall=0.87,
            confidence_breakdown={
                "title": 0.92,
                "description": 0.85,
                "category": 0.88,
                "price": 0.75,
                "attributes": 0.90,
            },
            ai_provider="gemini",
            ai_model_version="2.5-flash",
            generation_time_ms=2340,
            version=1,
            generated_at=datetime.now(UTC),
            updated_at=None,
        )

        assert content.id == content_id
        assert content.product_id == product_id
        assert content.title == "iPhone 13 Pro 128GB Usado Excelente Estado"
        assert content.ml_price == Decimal("450000.00")
        assert content.confidence_overall == 0.87
        assert content.version == 1
        assert content.ai_provider == "gemini"

    def test_title_too_long_raises_error(self):
        """Test that creating content with title > 60 characters raises an error."""
        with pytest.raises(
            InvalidContentError, match="Title must be 60 characters or less"
        ):
            GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="This is a very long title that exceeds the maximum allowed length of 60 characters for MercadoLibre",
                description="Valid description that is long enough to meet the minimum length requirement for the description field in this test case",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="This is a very long title that exceeds the maximum allowed length of 60 characters for MercadoLibre",
                ml_price=Decimal("100.00"),
                ml_currency_id="ARS",
                ml_available_quantity=1,
                ml_buying_mode="buy_it_now",
                ml_condition="new",
                ml_listing_type_id="gold_special",
                ml_attributes=safe_migrate_ml_attributes({}),
                ml_sale_terms=safe_migrate_ml_sale_terms({}),
                ml_shipping=safe_migrate_ml_shipping({}),
                confidence_overall=0.8,
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1000,
                version=1,
                generated_at=datetime.now(UTC),
            )

    def test_invalid_confidence_score_raises_error(self):
        """Test that invalid confidence scores raise errors."""
        with pytest.raises(
            InvalidContentError, match="Overall confidence must be between 0.0 and 1.0"
        ):
            GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="Valid title that is at least 10 characters long",
                description="Valid description that is at least 50 characters long to pass validation",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="Valid title for ML",
                ml_price=Decimal("100.00"),
                ml_currency_id="ARS",
                ml_available_quantity=1,
                ml_buying_mode="buy_it_now",
                ml_condition="new",
                ml_listing_type_id="gold_special",
                ml_attributes=safe_migrate_ml_attributes({}),
                ml_sale_terms=safe_migrate_ml_sale_terms({}),
                ml_shipping=safe_migrate_ml_shipping({}),
                confidence_overall=1.5,  # Invalid confidence score
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1000,
                version=1,
                generated_at=datetime.now(UTC),
            )

    def test_empty_title_raises_error(self):
        """Test that empty title raises an error."""
        with pytest.raises(InvalidContentError, match="Title cannot be empty"):
            GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="",  # Empty title
                description="Valid description that is at least 50 characters long to pass validation",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="Valid title for ML",
                ml_price=Decimal("100.00"),
                ml_currency_id="ARS",
                ml_available_quantity=1,
                ml_buying_mode="buy_it_now",
                ml_condition="new",
                ml_listing_type_id="gold_special",
                ml_attributes=safe_migrate_ml_attributes({}),
                ml_sale_terms=safe_migrate_ml_sale_terms({}),
                ml_shipping=safe_migrate_ml_shipping({}),
                confidence_overall=0.8,
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1000,
                version=1,
                generated_at=datetime.now(UTC),
            )

    def test_negative_price_raises_error(self):
        """Test that negative price raises an error."""
        with pytest.raises(InvalidContentError, match="Price must be positive"):
            GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="Valid title that is at least 10 characters long",
                description="Valid description that is at least 50 characters long to pass validation",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="Valid title for ML",
                ml_price=Decimal("-100.00"),  # Negative price
                ml_currency_id="ARS",
                ml_available_quantity=1,
                ml_buying_mode="buy_it_now",
                ml_condition="new",
                ml_listing_type_id="gold_special",
                ml_attributes=safe_migrate_ml_attributes({}),
                ml_sale_terms=safe_migrate_ml_sale_terms({}),
                ml_shipping=safe_migrate_ml_shipping({}),
                confidence_overall=0.8,
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1000,
                version=1,
                generated_at=datetime.now(UTC),
            )

    def test_invalid_quantity_raises_error(self):
        """Test that invalid quantity raises an error."""
        with pytest.raises(
            InvalidContentError, match="Available quantity must be positive"
        ):
            GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="Valid title that is at least 10 characters long",
                description="Valid description that is at least 50 characters long to pass validation",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="Valid title for ML",
                ml_price=Decimal("100.00"),
                ml_currency_id="ARS",
                ml_available_quantity=0,  # Invalid quantity
                ml_buying_mode="buy_it_now",
                ml_condition="new",
                ml_listing_type_id="gold_special",
                ml_attributes=safe_migrate_ml_attributes({}),
                ml_sale_terms=safe_migrate_ml_sale_terms({}),
                ml_shipping=safe_migrate_ml_shipping({}),
                confidence_overall=0.8,
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1000,
                version=1,
                generated_at=datetime.now(UTC),
            )

    def test_content_meets_quality_threshold(self):
        """Test quality threshold validation."""
        content = GeneratedContent(
            id=uuid4(),
            product_id=uuid4(),
            title="Valid title that is at least 10 characters long",
            description="Valid description that is at least 50 characters long to pass validation",
            ml_category_id="MLA1055",
            ml_category_name="Celulares y Smartphones",
            ml_title="Valid title for ML",
            ml_price=Decimal("100.00"),
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition="new",
            ml_listing_type_id="gold_special",
            ml_attributes=safe_migrate_ml_attributes({}),
            ml_sale_terms=safe_migrate_ml_sale_terms({}),
            ml_shipping=safe_migrate_ml_shipping({}),
            confidence_overall=0.9,  # High confidence
            confidence_breakdown={},
            ai_provider="gemini",
            ai_model_version="2.5-flash",
            generation_time_ms=1000,
            version=1,
            generated_at=datetime.now(UTC),
        )

        assert content.meets_quality_threshold()

    def test_content_below_quality_threshold(self):
        """Test quality threshold validation for low confidence."""
        content = GeneratedContent(
            id=uuid4(),
            product_id=uuid4(),
            title="Valid title that is at least 10 characters long",
            description="Valid description that is at least 50 characters long to pass validation",
            ml_category_id="MLA1055",
            ml_category_name="Celulares y Smartphones",
            ml_title="Valid title for ML",
            ml_price=Decimal("100.00"),
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition="new",
            ml_listing_type_id="gold_special",
            ml_attributes=safe_migrate_ml_attributes({}),
            ml_sale_terms=safe_migrate_ml_sale_terms({}),
            ml_shipping=safe_migrate_ml_shipping({}),
            confidence_overall=0.3,  # Low confidence
            confidence_breakdown={},
            ai_provider="gemini",
            ai_model_version="2.5-flash",
            generation_time_ms=1000,
            version=1,
            generated_at=datetime.now(UTC),
        )

        assert not content.meets_quality_threshold()


class TestConfidenceScore:
    """Test cases for ConfidenceScore entity."""

    def test_create_confidence_score_success(self):
        """Test creating a valid ConfidenceScore instance."""
        score = ConfidenceScore(
            overall=0.87,
            breakdown={
                "title": 0.92,
                "description": 0.85,
                "category": 0.88,
                "price": 0.75,
                "attributes": 0.90,
            },
        )

        assert score.overall == 0.87
        assert score.breakdown["title"] == 0.92
        assert score.breakdown["description"] == 0.85

    def test_overall_confidence_out_of_range_raises_error(self):
        """Test that overall confidence outside 0-1 range raises an error."""
        with pytest.raises(
            InvalidContentError, match="Overall confidence must be between 0.0 and 1.0"
        ):
            ConfidenceScore(
                overall=1.5,  # Invalid confidence
                breakdown={},
            )

    def test_breakdown_confidence_out_of_range_raises_error(self):
        """Test that breakdown confidence outside 0-1 range raises an error."""
        with pytest.raises(
            InvalidContentError,
            match="Breakdown confidence scores must be between 0.0 and 1.0",
        ):
            ConfidenceScore(
                overall=0.8,
                breakdown={
                    "title": 1.2,  # Invalid confidence
                    "description": 0.85,
                },
            )

    def test_meets_threshold_success(self):
        """Test that high confidence meets threshold."""
        score = ConfidenceScore(
            overall=0.9, breakdown={"title": 0.95, "description": 0.85}
        )

        assert score.meets_threshold()

    def test_meets_threshold_failure(self):
        """Test that low confidence does not meet threshold."""
        score = ConfidenceScore(
            overall=0.4, breakdown={"title": 0.3, "description": 0.5}
        )

        assert not score.meets_threshold()

    def test_has_low_component_confidence_true(self):
        """Test detection of low component confidence."""
        score = ConfidenceScore(
            overall=0.8,
            breakdown={
                "title": 0.9,
                "description": 0.3,  # Low confidence component
                "category": 0.8,
            },
        )

        assert score.has_low_component_confidence()

    def test_has_low_component_confidence_false(self):
        """Test no low component confidence detected."""
        score = ConfidenceScore(
            overall=0.8, breakdown={"title": 0.9, "description": 0.85, "category": 0.8}
        )

        assert not score.has_low_component_confidence()


class TestAIGeneration:
    """Test cases for AIGeneration entity."""

    def test_create_ai_generation_success(self):
        """Test creating a valid AIGeneration instance."""
        generation_id = uuid4()
        product_id = uuid4()

        generation = AIGeneration(
            id=generation_id,
            product_id=product_id,
            status=GenerationStatus.PENDING,
            current_step=None,
            progress_percentage=0.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert generation.id == generation_id
        assert generation.product_id == product_id
        assert generation.status == GenerationStatus.PENDING
        assert generation.progress_percentage == 0.0
        assert generation.estimated_completion_seconds == 30

    def test_start_processing_success(self):
        """Test starting processing updates status correctly."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PENDING,
            current_step=None,
            progress_percentage=0.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        generation.start_processing("gemini-2.5-flash")

        assert generation.status == GenerationStatus.PROCESSING
        assert generation.current_step == ProcessingStep.IMAGE_ANALYSIS
        assert generation.progress_percentage == 0.0
        assert generation.updated_at is not None

    def test_update_progress_success(self):
        """Test updating progress."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.IMAGE_ANALYSIS,
            progress_percentage=10.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        generation.update_progress(ProcessingStep.CATEGORY_DETECTION, 40.0)

        assert generation.current_step == ProcessingStep.CATEGORY_DETECTION
        assert generation.progress_percentage == 40.0
        assert generation.updated_at is not None

    def test_complete_success(self):
        """Test completing generation."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.CONTENT_FINALIZATION,
            progress_percentage=95.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        generation.complete_processing(uuid4(), 2500)

        assert generation.status == GenerationStatus.COMPLETED
        assert generation.progress_percentage == 100.0
        assert generation.updated_at is not None

    def test_fail_with_error(self):
        """Test failing generation with error."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        generation.fail_processing("AI service unavailable", "AI_SERVICE_ERROR")

        assert generation.status == GenerationStatus.FAILED
        assert generation.error_message == "AI service unavailable"
        assert generation.error_code == "AI_SERVICE_ERROR"
        assert generation.updated_at is not None

    def test_is_processing_true(self):
        """Test is_processing returns True for processing status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert generation.is_processing()

    def test_is_processing_false(self):
        """Test is_processing returns False for non-processing status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.COMPLETED,
            current_step=ProcessingStep.CONTENT_FINALIZATION,
            progress_percentage=100.0,
            estimated_completion_seconds=30,
            generated_content_id=uuid4(),  # Required for COMPLETED status
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert not generation.is_processing()

    def test_is_completed_true(self):
        """Test is_completed returns True for completed status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.COMPLETED,
            current_step=ProcessingStep.CONTENT_FINALIZATION,
            progress_percentage=100.0,
            estimated_completion_seconds=30,
            generated_content_id=uuid4(),  # Required for COMPLETED status
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert generation.is_completed()

    def test_is_completed_false(self):
        """Test is_completed returns False for non-completed status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert not generation.is_completed()

    def test_is_failed_true(self):
        """Test is_failed returns True for failed status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.FAILED,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message="AI service error",
            error_code="AI_SERVICE_ERROR",
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert generation.is_failed()

    def test_is_failed_false(self):
        """Test is_failed returns False for non-failed status."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        assert not generation.is_failed()

    def test_get_estimated_remaining_time(self):
        """Test calculating estimated remaining time."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.PROCESSING,
            current_step=ProcessingStep.TITLE_GENERATION,
            progress_percentage=50.0,
            estimated_completion_seconds=30,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        remaining = generation.get_estimated_remaining_time()

        # Should be roughly half the estimated time since we're 50% done
        assert remaining is not None and 14 <= remaining <= 16

    def test_get_estimated_remaining_time_completed(self):
        """Test estimated remaining time for completed generation."""
        generation = AIGeneration(
            id=uuid4(),
            product_id=uuid4(),
            status=GenerationStatus.COMPLETED,
            current_step=ProcessingStep.CONTENT_FINALIZATION,
            progress_percentage=100.0,
            estimated_completion_seconds=30,
            generated_content_id=uuid4(),  # Required for COMPLETED status
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        remaining = generation.get_estimated_remaining_time()

        assert remaining == 0
