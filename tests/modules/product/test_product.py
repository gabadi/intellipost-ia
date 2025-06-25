"""Unit tests for Product domain entity."""

from datetime import datetime
from uuid import uuid4

import pytest

from backend.modules.product import Product, ProductStatus, ConfidenceScore


class TestProduct:
    """Test cases for Product domain entity."""

    def test_product_creation(self):
        """Test creating a product with required fields."""
        product_id = uuid4()
        user_id = uuid4()

        product = Product(
            id=product_id,
            user_id=user_id,
            status=ProductStatus.UPLOADING
        )

        assert product.id == product_id
        assert product.user_id == user_id
        assert product.status == ProductStatus.UPLOADING
        assert product.confidence is None
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_post_init(self):
        """Test product post-initialization logic."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING
        )

        # Should set created_at and updated_at
        assert isinstance(product.created_at, datetime)
        assert isinstance(product.updated_at, datetime)

    def test_is_ready_for_processing_true(self):
        """Test product is ready for processing when conditions are met."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            title="Test Product"
        )

        assert product.is_ready_for_processing() is True

    def test_is_ready_for_processing_false_no_title(self):
        """Test product is not ready when title is missing."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING
        )

        assert product.is_ready_for_processing() is False

    def test_is_ready_for_processing_false_empty_title(self):
        """Test product is not ready when title is empty."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            title="   "
        )

        assert product.is_ready_for_processing() is False

    def test_is_ready_for_processing_false_wrong_status(self):
        """Test product is not ready when status is not UPLOADING."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING,
            title="Test Product"
        )

        assert product.is_ready_for_processing() is False

    def test_is_published_true(self):
        """Test product is published when status and listing ID are set."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PUBLISHED,
            ml_listing_id="ML123456"
        )

        assert product.is_published() is True

    def test_is_published_false_no_listing_id(self):
        """Test product is not published without listing ID."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PUBLISHED
        )

        assert product.is_published() is False

    def test_is_published_false_wrong_status(self):
        """Test product is not published with wrong status."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            ml_listing_id="ML123456"
        )

        assert product.is_published() is False

    def test_has_high_confidence_true(self):
        """Test high confidence detection."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            confidence=ConfidenceScore.high()
        )

        assert product.has_high_confidence() is True

    def test_has_high_confidence_false(self):
        """Test low confidence detection."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            confidence=ConfidenceScore.medium()
        )

        assert product.has_high_confidence() is False

    def test_mark_as_processed(self):
        """Test marking product as processed."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING
        )
        initial_updated_at = product.updated_at

        product.mark_as_processed(ConfidenceScore.high())

        assert product.status == ProductStatus.PROCESSED
        assert product.confidence == ConfidenceScore.high()
        assert product.updated_at > initial_updated_at

    def test_mark_as_published(self):
        """Test marking product as published."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED
        )
        initial_updated_at = product.updated_at
        listing_id = "ML123456"

        product.mark_as_published(listing_id)

        assert product.status == ProductStatus.PUBLISHED
        assert product.ml_listing_id == listing_id
        assert product.published_at is not None
        assert product.updated_at > initial_updated_at

    def test_mark_as_failed(self):
        """Test marking product processing as failed."""
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING
        )
        initial_updated_at = product.updated_at

        product.mark_as_failed()

        assert product.status == ProductStatus.FAILED
        assert product.updated_at > initial_updated_at
