"""Unit tests for User profile management."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from backend.modules.user.domain.user_core import UserCore
from backend.modules.user.domain.user_profile import UserProfile

pytestmark = pytest.mark.unit


class TestUserProfile:
    """Test cases for User profile management."""

    def test_get_full_name_with_both_names(self):
        """Test full name when both first and last names are provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            first_name="John",
            last_name="Doe",
        )

        assert UserProfile.get_full_name(user) == "John Doe"

    def test_get_full_name_with_first_name_only(self):
        """Test full name when only first name is provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            first_name="John",
        )

        assert UserProfile.get_full_name(user) == "John"

    def test_get_full_name_with_last_name_only(self):
        """Test full name when only last name is provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            last_name="Doe",
        )

        assert UserProfile.get_full_name(user) == "Doe"

    def test_get_full_name_with_no_names(self):
        """Test full name when no names are provided."""
        user = UserCore(
            id=uuid4(),
            email="john.doe@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )

        assert UserProfile.get_full_name(user) == "john.doe"
