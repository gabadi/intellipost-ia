"""Unit tests for User domain entity."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from backend.modules.user.domain.user import User
from backend.modules.user.domain.user_status import UserStatus

pytestmark = pytest.mark.unit


class TestUser:
    """Test cases for User domain entity."""

    def test_user_creation(self):
        """Test creating a user with required fields."""
        user_id = uuid4()
        email = "test@example.com"
        password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu"  # bcrypt hash for 'testpass123'
        created_at = datetime.now(UTC)

        user = User(
            id=user_id, email=email, password_hash=password_hash, created_at=created_at
        )

        assert user.id == user_id
        assert user.email == email
        assert user.created_at == created_at
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.updated_at is not None

    def test_user_post_init(self):
        """Test user post-initialization logic."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )

        # Should set updated_at
        assert isinstance(user.updated_at, datetime)

    def test_full_name_with_both_names(self):
        """Test full name when both first and last names are provided."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            first_name="John",
            last_name="Doe",
        )

        assert user.full_name == "John Doe"

    def test_full_name_with_first_name_only(self):
        """Test full name when only first name is provided."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            first_name="John",
        )

        assert user.full_name == "John"

    def test_full_name_with_last_name_only(self):
        """Test full name when only last name is provided."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            last_name="Doe",
        )

        assert user.full_name == "Doe"

    def test_full_name_with_no_names(self):
        """Test full name when no names are provided."""
        user = User(
            id=uuid4(),
            email="john.doe@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )

        assert user.full_name == "john.doe"

    def test_is_active_true(self):
        """Test active status detection."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )

        assert user.is_active is True

    def test_is_active_false(self):
        """Test inactive status detection."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.INACTIVE,
        )

        assert user.is_active is False

    def test_is_ml_connected_true(self):
        """Test MercadoLibre connection detection when valid."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        assert user.is_ml_connected is True

    def test_is_ml_connected_false_no_user_id(self):
        """Test MercadoLibre connection when user ID is missing."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        assert user.is_ml_connected is False

    def test_is_ml_connected_false_token_expired(self):
        """Test MercadoLibre connection when token is expired."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) - timedelta(hours=1),
        )

        assert user.is_ml_connected is False

    def test_is_email_verified_true(self):
        """Test email verification detection when verified."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            email_verified_at=datetime.now(UTC),
        )

        assert user.is_email_verified is True

    def test_is_email_verified_false(self):
        """Test email verification detection when not verified."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )

        assert user.is_email_verified is False

    def test_activate(self):
        """Test user activation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
        )
        initial_updated_at = user.updated_at

        user.activate()

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at >= initial_updated_at

    def test_deactivate(self):
        """Test user deactivation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        user.deactivate()

        assert user.status == UserStatus.INACTIVE
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_suspend(self):
        """Test user suspension."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        user.suspend()

        assert user.status == UserStatus.SUSPENDED
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_verify_email(self):
        """Test email verification."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        user.verify_email()

        assert user.email_verified_at is not None
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_update_ml_tokens(self):
        """Test updating MercadoLibre tokens."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        access_token = "new_access_token"
        refresh_token = "new_refresh_token"
        expires_at = datetime.now(UTC) + timedelta(hours=2)

        user.update_ml_tokens(access_token, refresh_token, expires_at)

        assert user.ml_access_token == access_token
        assert user.ml_refresh_token == refresh_token
        assert user.ml_token_expires_at == expires_at
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at

    def test_record_login(self):
        """Test recording user login."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        user.record_login()

        assert user.last_login_at is not None
        assert user.updated_at is not None
        assert initial_updated_at is not None
        assert user.updated_at > initial_updated_at
