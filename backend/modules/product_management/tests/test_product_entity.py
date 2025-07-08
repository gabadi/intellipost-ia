"""
Unit tests for Product domain entity.

This module tests the Product entity and its business logic.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from modules.product_management.domain.entities.confidence_score import ConfidenceScore
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_status import ProductStatus
from modules.product_management.domain.exceptions import InvalidConfidenceScoreError


class TestProduct:
    """Test cases for Product entity."""

    def test_product_creation(self):
        """Test creating a product with required fields."""
        product_id = uuid4()
        user_id = uuid4()
        prompt_text = "iPhone 13 Pro usado, excelente estado, 128GB"

        product = Product(
            id=product_id,
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text,
        )

        assert product.id == product_id
        assert product.user_id == user_id
        assert product.status == ProductStatus.UPLOADING
        assert product.prompt_text == prompt_text
        assert product.confidence is None
        assert product.title is None
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_creation_with_all_fields(self):
        """Test creating a product with all fields."""
        product_id = uuid4()
        user_id = uuid4()
        prompt_text = "iPhone 13 Pro usado, excelente estado, 128GB"
        confidence = ConfidenceScore(0.85)
        title = "iPhone 13 Pro 128GB"
        description = "Excellent condition iPhone 13 Pro"
        price = 799.99
        created_at = datetime.now(UTC)

        product = Product(
            id=product_id,
            user_id=user_id,
            status=ProductStatus.READY,
            prompt_text=prompt_text,
            confidence=confidence,
            title=title,
            description=description,
            price=price,
            category_id="MLU1055",
            ai_title="AI Generated Title",
            ai_description="AI Generated Description",
            ai_tags=["iPhone", "Apple", "Smartphone"],
            ml_listing_id="MLU123456789",
            ml_category_id="MLU1055",
            created_at=created_at,
        )

        assert product.id == product_id
        assert product.user_id == user_id
        assert product.status == ProductStatus.READY
        assert product.prompt_text == prompt_text
        assert product.confidence == confidence
        assert product.title == title
        assert product.description == description
        assert product.price == price
        assert product.category_id == "MLU1055"
        assert product.ai_title == "AI Generated Title"
        assert product.ai_description == "AI Generated Description"
        assert product.ai_tags == ["iPhone", "Apple", "Smartphone"]
        assert product.ml_listing_id == "MLU123456789"
        assert product.ml_category_id == "MLU1055"
        assert product.created_at == created_at

    def test_is_ready_for_processing(self):
        """Test business logic for processing readiness."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Test product description",
        )

        # Initially not ready (status is uploading)
        assert not product.is_ready_for_processing()

        # Set status to ready for processing
        product.status = ProductStatus.READY
        assert product.is_ready_for_processing()

    def test_is_published(self):
        """Test business logic for published status."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Test product description",
        )

        # Initially not published
        assert not product.is_published()

        # Set as published
        product.status = ProductStatus.PUBLISHED
        product.ml_listing_id = "MLU123456789"
        assert product.is_published()

    def test_has_high_confidence(self):
        """Test business logic for high confidence."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.READY,
            prompt_text="Test product description",
        )

        # No confidence score
        assert not product.has_high_confidence()

        # Low confidence
        product.confidence = ConfidenceScore(0.6)
        assert not product.has_high_confidence()

        # High confidence
        product.confidence = ConfidenceScore(0.85)
        assert product.has_high_confidence()

    def test_mark_as_processed(self):
        """Test marking product as processed."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING,
            prompt_text="Test product description",
        )

        confidence = ConfidenceScore(0.85)
        product.mark_as_processed(confidence)

        assert product.status == ProductStatus.READY
        assert product.confidence == confidence

    def test_mark_as_published(self):
        """Test marking product as published."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PUBLISHING,
            prompt_text="Test product description",
        )

        ml_listing_id = "MLU123456789"
        product.mark_as_published(ml_listing_id)

        assert product.status == ProductStatus.PUBLISHED
        assert product.ml_listing_id == ml_listing_id

    def test_mark_as_failed(self):
        """Test marking product as failed."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING,
            prompt_text="Test product description",
        )

        product.mark_as_failed()

        assert product.status == ProductStatus.FAILED


class TestProductStatus:
    """Test cases for ProductStatus enum."""

    def test_all_statuses_defined(self):
        """Test that all required statuses are defined."""
        expected_statuses = {
            "uploading",
            "processing",
            "ready",
            "publishing",
            "published",
            "failed",
        }

        actual_statuses = {status.value for status in ProductStatus}
        assert actual_statuses == expected_statuses

    def test_status_values(self):
        """Test specific status values."""
        assert ProductStatus.UPLOADING.value == "uploading"
        assert ProductStatus.PROCESSING.value == "processing"
        assert ProductStatus.READY.value == "ready"
        assert ProductStatus.PUBLISHING.value == "publishing"
        assert ProductStatus.PUBLISHED.value == "published"
        assert ProductStatus.FAILED.value == "failed"


class TestConfidenceScore:
    """Test cases for ConfidenceScore value object."""

    def test_valid_confidence_scores(self):
        """Test creating valid confidence scores."""
        scores = [0.0, 0.5, 0.75, 1.0]

        for score in scores:
            confidence = ConfidenceScore(score)
            assert confidence.score == score

    def test_invalid_confidence_scores(self):
        """Test invalid confidence scores raise InvalidConfidenceScoreError."""
        invalid_scores = [-0.1, 1.1, 2.0, -1.0]

        for score in invalid_scores:
            with pytest.raises(InvalidConfidenceScoreError):
                ConfidenceScore(score)

    def test_confidence_score_comparison(self):
        """Test confidence score comparison."""
        low = ConfidenceScore(0.3)
        medium = ConfidenceScore(0.6)
        high = ConfidenceScore(0.9)

        assert low < medium < high
        assert high > medium > low
        assert low == ConfidenceScore(0.3)

    def test_confidence_score_string_representation(self):
        """Test string representation of confidence score."""
        confidence = ConfidenceScore(0.85)
        assert str(confidence) == "0.85"
        assert repr(confidence) == "ConfidenceScore(0.85)"
