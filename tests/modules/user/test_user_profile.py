"""Unit tests for User profile management."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.modules.user.domain.user_core import UserCore
from backend.modules.user.domain.user_profile import UserProfile


class TestUserProfile:
    """Test cases for User profile management."""

    def test_get_full_name_with_both_names(self):
        """Test full name when both first and last names are provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            created_at=datetime.now(timezone.utc),
            first_name="John",
            last_name="Doe"
        )

        assert UserProfile.get_full_name(user) == "John Doe"

    def test_get_full_name_with_first_name_only(self):
        """Test full name when only first name is provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            created_at=datetime.now(timezone.utc),
            first_name="John"
        )

        assert UserProfile.get_full_name(user) == "John"

    def test_get_full_name_with_last_name_only(self):
        """Test full name when only last name is provided."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            created_at=datetime.now(timezone.utc),
            last_name="Doe"
        )

        assert UserProfile.get_full_name(user) == "Doe"

    def test_get_full_name_with_no_names(self):
        """Test full name when no names are provided."""
        user = UserCore(
            id=uuid4(),
            email="john.doe@example.com",
            created_at=datetime.utcnow()
        )

        assert UserProfile.get_full_name(user) == "john.doe"
