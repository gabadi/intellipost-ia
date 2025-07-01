"""Unit tests for Product status manager."""

from uuid import uuid4

import pytest

from modules.product_management.domain.product_core import ProductCore
from modules.product_management.domain.product_status_manager import ProductStatusManager
from modules.product_management.domain.product_status import ProductStatus
from modules.product_management.domain.confidence_score import ConfidenceScore


class TestProductStatusManager:
    """Test cases for Product status manager."""

    def test_mark_as_processed(self):
        """Test marking product as processed."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING
        )
        initial_updated_at = product.updated_at

        ProductStatusManager.mark_as_processed(product, ConfidenceScore.high())

        assert product.status == ProductStatus.PROCESSED
        assert product.confidence == ConfidenceScore.high()
        assert product.updated_at > initial_updated_at

    def test_mark_as_published(self):
        """Test marking product as published."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSED
        )
        initial_updated_at = product.updated_at
        listing_id = "ML123456"

        ProductStatusManager.mark_as_published(product, listing_id)

        assert product.status == ProductStatus.PUBLISHED
        assert product.ml_listing_id == listing_id
        assert product.published_at is not None
        assert product.updated_at > initial_updated_at

    def test_mark_as_failed(self):
        """Test marking product processing as failed."""
        product = ProductCore(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.PROCESSING
        )
        initial_updated_at = product.updated_at

        # Add small delay to ensure timestamp difference
        import time
        time.sleep(0.001)

        ProductStatusManager.mark_as_failed(product)

        assert product.status == ProductStatus.FAILED
        assert product.updated_at > initial_updated_at
