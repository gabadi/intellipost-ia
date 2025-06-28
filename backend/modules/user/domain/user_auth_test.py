"""Unit tests for User authentication."""

from datetime import UTC, datetime
from uuid import uuid4

from backend.modules.user.domain.user_auth import UserAuth
from backend.modules.user.domain.user_core import UserCore
from backend.modules.user.domain.user_status import UserStatus


class TestUserAuth:
    """Test cases for User authentication methods."""

    def test_is_active_true(self):
        """Test active status detection."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )

        assert UserAuth.is_active(user) is True

    def test_is_active_false(self):
        """Test inactive status detection."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.INACTIVE,
        )

        assert UserAuth.is_active(user) is False

    def test_is_email_verified_true(self):
        """Test email verification detection when verified."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            email_verified_at=datetime.now(UTC),
        )

        assert UserAuth.is_email_verified(user) is True

    def test_is_email_verified_false(self):
        """Test email verification detection when not verified."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )

        assert UserAuth.is_email_verified(user) is False

    def test_verify_email(self):
        """Test email verification."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        UserAuth.verify_email(user)

        assert user.email_verified_at is not None
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_record_login(self):
        """Test recording user login."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        UserAuth.record_login(user)

        assert user.last_login_at is not None
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_activate(self):
        """Test user activation."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
        )
        initial_updated_at = user.updated_at

        UserAuth.activate(user)

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_deactivate(self):
        """Test user deactivation."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        UserAuth.deactivate(user)

        assert user.status == UserStatus.INACTIVE
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_suspend(self):
        """Test user suspension."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        # Add small delay to ensure timestamp difference
        import time

        time.sleep(0.001)

        UserAuth.suspend(user)

        assert user.status == UserStatus.SUSPENDED
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at
