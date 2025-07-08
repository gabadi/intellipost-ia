"""Unit tests for unified User domain entity."""

import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from modules.user_management.domain.entities.user import User, UserStatus


class TestUser:
    """Test cases for unified User domain entity."""

    def test_user_creation(self):
        """Test creating a user with required fields."""
        user_id = uuid4()
        email = "test@example.com"
        password_hash = "hashed_password"
        created_at = datetime.now(UTC)

        user = User(
            id=user_id, email=email, password_hash=password_hash, created_at=created_at
        )

        assert user.id == user_id
        assert user.email == email
        assert user.password_hash == password_hash
        assert user.created_at == created_at
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.is_active is True
        assert user.is_email_verified is False
        assert user.updated_at is not None

    def test_user_post_init(self):
        """Test user post-initialization logic."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        # Should set updated_at
        assert isinstance(user.updated_at, datetime)

    def test_full_name_with_both_names(self):
        """Test full name when both first and last names are provided."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
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
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            first_name="John",
        )

        assert user.full_name == "John"

    def test_full_name_with_last_name_only(self):
        """Test full name when only last name is provided."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            last_name="Doe",
        )

        assert user.full_name == "Doe"

    def test_full_name_with_no_names(self):
        """Test full name when no names are provided."""
        user = User(
            id=uuid4(),
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        assert user.full_name == "john.doe"

    def test_is_ml_connected_true(self):
        """Test MercadoLibre connection detection when valid."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
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
            password_hash="hashed_password",
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
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) - timedelta(hours=1),
        )

        assert user.is_ml_connected is False

    def test_activate(self):
        """Test user activation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
        )
        initial_updated_at = user.updated_at

        user.activate()

        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
        assert user.updated_at > initial_updated_at

    def test_deactivate(self):
        """Test user deactivation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        user.deactivate()

        assert user.status == UserStatus.INACTIVE
        assert user.is_active is False
        assert user.updated_at > initial_updated_at

    def test_suspend(self):
        """Test user suspension."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
        initial_updated_at = user.updated_at

        # Add small delay to ensure updated_at timestamp is different
        time.sleep(0.001)
        user.suspend()

        assert user.status == UserStatus.SUSPENDED
        assert user.is_active is False
        assert user.updated_at > initial_updated_at

    def test_verify_email(self):
        """Test email verification."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
        )
        initial_updated_at = user.updated_at

        user.verify_email()

        assert user.is_email_verified is True
        assert user.email_verified_at is not None
        assert user.status == UserStatus.ACTIVE
        assert user.email_verification_token is None
        assert user.updated_at > initial_updated_at

    def test_record_login(self):
        """Test recording successful login."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=3,
        )
        initial_updated_at = user.updated_at

        user.record_login()

        assert user.last_login_at is not None
        assert user.failed_login_attempts == 0
        assert user.last_failed_login_at is None
        assert user.updated_at > initial_updated_at

    def test_record_failed_login(self):
        """Test recording failed login attempt."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        user.record_failed_login()

        assert user.failed_login_attempts == 1
        assert user.last_failed_login_at is not None
        assert user.updated_at > initial_updated_at

    def test_is_account_locked(self):
        """Test account locking detection."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=5,
        )

        assert user.is_account_locked() is True
        assert user.is_account_locked(max_attempts=10) is False

    def test_reset_failed_logins(self):
        """Test resetting failed login attempts."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=3,
            last_failed_login_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        user.reset_failed_logins()

        assert user.failed_login_attempts == 0
        assert user.last_failed_login_at is None
        assert user.updated_at > initial_updated_at

    def test_update_ml_tokens(self):
        """Test updating MercadoLibre tokens."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
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
        assert user.updated_at > initial_updated_at

    def test_disconnect_ml(self):
        """Test disconnecting MercadoLibre integration."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_refresh_token="refresh123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        initial_updated_at = user.updated_at

        user.disconnect_ml()

        assert user.ml_user_id is None
        assert user.ml_access_token is None
        assert user.ml_refresh_token is None
        assert user.ml_token_expires_at is None
        assert user.updated_at > initial_updated_at

    def test_update_profile(self):
        """Test updating user profile."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )
        initial_updated_at = user.updated_at

        user.update_profile(
            first_name="John",
            last_name="Doe",
            auto_publish=True,
            ai_confidence_threshold="high",
            default_ml_site="MLB",
        )

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.auto_publish is True
        assert user.ai_confidence_threshold == "high"
        assert user.default_ml_site == "MLB"
        assert user.updated_at > initial_updated_at

    # Additional Authentication Tests
    def test_verify_email_from_pending_status(self):
        """Test email verification activates user from pending status."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
            is_email_verified=False,
        )

        user.verify_email()

        assert user.is_email_verified is True
        assert user.status == UserStatus.ACTIVE
        assert user.email_verified_at is not None
        assert user.email_verification_token is None

    def test_verify_email_from_active_status(self):
        """Test email verification doesn't change status if already active."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
            is_email_verified=False,
        )

        user.verify_email()

        assert user.is_email_verified is True
        assert user.status == UserStatus.ACTIVE  # Should remain active
        assert user.email_verified_at is not None

    # Additional MercadoLibre Integration Tests
    def test_is_ml_connected_false_no_access_token(self):
        """Test MercadoLibre connection when access token is missing."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        assert user.is_ml_connected is False

    def test_is_ml_connected_false_no_expires_at(self):
        """Test MercadoLibre connection when expires_at is missing."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
        )

        assert user.is_ml_connected is False

    def test_update_ml_tokens_with_user_id(self):
        """Test updating ML tokens behavior with user ID."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        access_token = "new_access_token"
        refresh_token = "new_refresh_token"
        expires_at = datetime.now(UTC) + timedelta(hours=2)

        # Note: The current implementation doesn't set ml_user_id
        # This test validates the current behavior
        user.update_ml_tokens(access_token, refresh_token, expires_at)

        assert user.ml_access_token == access_token
        assert user.ml_refresh_token == refresh_token
        assert user.ml_token_expires_at == expires_at
        # ml_user_id should remain None as the method doesn't set it
        assert user.ml_user_id is None

    # Additional Profile Tests
    def test_update_profile_partial_update(self):
        """Test updating only some profile fields."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            first_name="Original",
            last_name="Name",
            auto_publish=False,
            ai_confidence_threshold="low",
            default_ml_site="MLA",
        )
        initial_updated_at = user.updated_at

        # Update only first name and auto_publish
        user.update_profile(first_name="Updated", auto_publish=True)

        assert user.first_name == "Updated"
        assert user.last_name == "Name"  # Unchanged
        assert user.auto_publish is True
        assert user.ai_confidence_threshold == "low"  # Unchanged
        assert user.default_ml_site == "MLA"  # Unchanged
        assert user.updated_at > initial_updated_at

    def test_update_profile_no_changes(self):
        """Test update_profile with no parameters doesn't change anything."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            first_name="John",
            last_name="Doe",
        )
        initial_updated_at = user.updated_at

        # Add small delay to ensure timestamp difference
        time.sleep(0.001)
        user.update_profile()

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        # Note: updated_at is still updated even with no changes due to implementation
        assert user.updated_at > initial_updated_at

    def test_update_profile_with_none_values(self):
        """Test update_profile with explicit None values doesn't update fields."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            first_name="John",
            last_name="Doe",
        )

        # Passing None explicitly should NOT update the fields (design choice)
        user.update_profile(first_name=None, last_name=None)

        # Fields should remain unchanged when None is passed
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    # Additional Failed Login Tests
    def test_multiple_failed_logins(self):
        """Test multiple failed login attempts increment counter."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        # Record multiple failed logins
        user.record_failed_login()
        assert user.failed_login_attempts == 1

        user.record_failed_login()
        assert user.failed_login_attempts == 2

        user.record_failed_login()
        assert user.failed_login_attempts == 3

    def test_successful_login_resets_failed_attempts(self):
        """Test successful login resets failed login attempts."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=3,
            last_failed_login_at=datetime.now(UTC),
        )

        user.record_login()

        assert user.failed_login_attempts == 0
        assert user.last_failed_login_at is None
        assert user.last_login_at is not None

    def test_account_locking_edge_cases(self):
        """Test account locking with different max attempt values."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=3,
        )

        # Should not be locked with default (5 attempts)
        assert user.is_account_locked() is False

        # Should be locked with lower threshold
        assert user.is_account_locked(max_attempts=3) is True
        assert user.is_account_locked(max_attempts=2) is True

        # Should not be locked with higher threshold
        assert user.is_account_locked(max_attempts=10) is False

    # Edge Cases and Validation Tests
    def test_user_defaults(self):
        """Test user creation with minimum required fields has correct defaults."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        # Verify all default values
        assert user.first_name is None
        assert user.last_name is None
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.is_active is True
        assert user.is_email_verified is False
        assert user.failed_login_attempts == 0
        assert user.last_failed_login_at is None
        assert user.password_reset_token is None
        assert user.password_reset_expires_at is None
        assert user.email_verification_token is None
        assert user.ml_user_id is None
        assert user.ml_access_token is None
        assert user.ml_refresh_token is None
        assert user.ml_token_expires_at is None
        assert user.default_ml_site == "MLA"
        assert user.auto_publish is False
        assert user.ai_confidence_threshold == "medium"
        assert user.last_login_at is None
        assert user.email_verified_at is None

    def test_full_name_edge_cases(self):
        """Test full name property with various edge cases."""
        # Test with complex email
        user = User(
            id=uuid4(),
            email="user.name+tag@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )
        assert user.full_name == "user.name+tag"

        # Test with empty string names (treated as None)
        user.first_name = ""
        user.last_name = ""
        # Empty strings should still use email fallback
        assert user.full_name == "user.name+tag"

    def test_status_transitions(self):
        """Test valid status transitions."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.PENDING_VERIFICATION,
        )

        # Pending -> Active (via activation)
        user.activate()
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True

        # Active -> Suspended
        user.suspend()
        assert user.status == UserStatus.SUSPENDED
        assert user.is_active is False

        # Suspended -> Active (via activation)
        user.activate()
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True

        # Active -> Inactive
        user.deactivate()
        assert user.status == UserStatus.INACTIVE
        assert user.is_active is False
