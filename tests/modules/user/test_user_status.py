"""Tests for user status enumeration."""

from modules.user_management.domain.entities.user import UserStatus


class TestUserStatus:
    """Test the UserStatus enumeration."""

    def test_all_status_values(self):
        """Test that all expected status values exist."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.PENDING_VERIFICATION.value == "pending_verification"

    def test_status_enum_members(self):
        """Test that all expected enum members exist."""
        expected_statuses = {
            "ACTIVE", "INACTIVE", "SUSPENDED", "PENDING_VERIFICATION"
        }
        actual_statuses = {status.name for status in UserStatus}
        assert actual_statuses == expected_statuses

    def test_status_enum_count(self):
        """Test that we have the expected number of statuses."""
        assert len(UserStatus) == 4
