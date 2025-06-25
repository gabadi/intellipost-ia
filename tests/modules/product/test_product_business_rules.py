"""Unit tests for Product business rules."""

from uuid import uuid4

import pytest

from backend.modules.product_core import ProductCore
from backend.modules.product_business_rules import ProductBusinessRules
from backend.modules.product_status import ProductStatus
from backend.modules.confidence_score import ConfidenceScore


class TestProductBusinessRules:
    """Test cases for Product business rules."""

    def test_is_ready_for_processing_true(self):
        """Test product is ready for processing when conditions are met."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            title="Test Product"
        )

        assert ProductBusinessRules.is_ready_for_processing(product) is True

    def test_is_ready_for_processing_false_no_title(self):
        """Test product is not ready when title is missing."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING
        )

        assert ProductBusinessRules.is_ready_for_processing(product) is False

    def test_is_ready_for_processing_false_empty_title(self):
        """Test product is not ready when title is empty."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            title="   "
        )

        assert ProductBusinessRules.is_ready_for_processing(product) is False

    def test_is_ready_for_processing_false_wrong_status(self):
        """Test product is not ready when status is not UPLOADING."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING,
            title="Test Product"
        )

        assert ProductBusinessRules.is_ready_for_processing(product) is False

    def test_is_published_true(self):
        """Test product is published when status and listing ID are set."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PUBLISHED,
            ml_listing_id="ML123456"
        )

        assert ProductBusinessRules.is_published(product) is True

    def test_is_published_false_no_listing_id(self):
        """Test product is not published without listing ID."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PUBLISHED
        )

        assert ProductBusinessRules.is_published(product) is False

    def test_is_published_false_wrong_status(self):
        """Test product is not published with wrong status."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            ml_listing_id="ML123456"
        )

        assert ProductBusinessRules.is_published(product) is False

    def test_has_high_confidence_true(self):
        """Test high confidence detection."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            confidence=ConfidenceScore.high()
        )

        assert ProductBusinessRules.has_high_confidence(product) is True

    def test_has_high_confidence_false(self):
        """Test low confidence detection."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED,
            confidence=ConfidenceScore.medium()
        )

        assert ProductBusinessRules.has_high_confidence(product) is False

    def test_has_high_confidence_false_no_confidence(self):
        """Test confidence detection when confidence is None."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED
        )

        assert ProductBusinessRules.has_high_confidence(product) is False
