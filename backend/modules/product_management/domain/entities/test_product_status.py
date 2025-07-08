"""Tests for product status enumeration."""

import pytest

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit

from .product_status import ProductStatus


class TestProductStatus:
    """Test the ProductStatus enumeration."""

    def test_all_status_values(self):
        """Test that all expected status values exist."""
        assert ProductStatus.DRAFT.value == "draft"
        assert ProductStatus.PENDING.value == "pending"
        assert ProductStatus.UPLOADING.value == "uploading"
        assert ProductStatus.PROCESSING.value == "processing"
        assert ProductStatus.PROCESSED.value == "processed"
        assert ProductStatus.READY.value == "ready"
        assert ProductStatus.PUBLISHING.value == "publishing"
        assert ProductStatus.PUBLISHED.value == "published"
        assert ProductStatus.FAILED.value == "failed"

    def test_status_enum_members(self):
        """Test that all expected enum members exist."""
        expected_statuses = {
            "DRAFT",
            "PENDING",
            "UPLOADING",
            "PROCESSING",
            "PROCESSED",
            "READY",
            "PUBLISHING",
            "PUBLISHED",
            "FAILED",
        }
        actual_statuses = {status.name for status in ProductStatus}
        assert actual_statuses == expected_statuses

    def test_status_enum_count(self):
        """Test that we have the expected number of statuses."""
        assert len(ProductStatus) == 9
