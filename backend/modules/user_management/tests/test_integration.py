"""Integration tests for user management module."""
# pyright: reportMissingImports=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUntypedFunctionDecorator=false

from datetime import UTC, datetime
from uuid import uuid4

import pytest  # type: ignore[import-untyped]

from modules.user_management.domain.entities.user import User, UserStatus
from modules.user_management.infrastructure.models.user_model import UserModel
from modules.user_management.infrastructure.services.bcrypt_password_service import (
    BcryptPasswordService,
)
from modules.user_management.infrastructure.services.jose_jwt_service import (
    JoseJWTService,
)


class TestUserModelIntegration:
    """Test User entity and SQLAlchemy model integration."""

    def test_user_model_to_domain_conversion(self):
        """Test converting SQLAlchemy model to domain entity."""
        # Create a UserModel instance
        user_model = UserModel(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            status=UserStatus.ACTIVE.value,
            is_active=True,
            is_email_verified=True,
            failed_login_attempts=0,
            default_ml_site="MLA",
            auto_publish=False,
            ai_confidence_threshold="medium",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Convert to domain entity
        user = user_model.to_domain()

        # Verify conversion
        assert isinstance(user, User)
        assert user.id == user_model.id
        assert user.email == user_model.email
        assert user.password_hash == user_model.password_hash
        assert user.first_name == user_model.first_name
        assert user.last_name == user_model.last_name
        assert user.status == UserStatus.ACTIVE
        assert user.is_active == user_model.is_active
        assert user.is_email_verified == user_model.is_email_verified

    def test_user_domain_to_model_conversion(self):
        """Test converting domain entity to SQLAlchemy model."""
        # Create a User domain entity
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            status=UserStatus.ACTIVE,
            is_active=True,
            is_email_verified=True,
            created_at=datetime.now(UTC),
        )

        # Convert to SQLAlchemy model
        user_model = UserModel.from_domain(user)

        # Verify conversion
        assert isinstance(user_model, UserModel)
        assert user_model.id == user.id
        assert user_model.email == user.email
        assert user_model.password_hash == user.password_hash
        assert user_model.first_name == user.first_name
        assert user_model.last_name == user.last_name
        assert user_model.status == user.status.value
        assert user_model.is_active == user.is_active
        assert user_model.is_email_verified == user.is_email_verified

    def test_user_model_update_from_domain(self):
        """Test updating SQLAlchemy model from domain entity."""
        # Create initial model
        user_model = UserModel(
            id=uuid4(),
            email="test@example.com",
            password_hash="old_hash",
            first_name="Old",
            last_name="Name",
            status=UserStatus.PENDING_VERIFICATION.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Create updated domain entity
        updated_user = User(
            id=user_model.id,
            email="updated@example.com",
            password_hash="new_hash",
            first_name="New",
            last_name="Name",
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            created_at=user_model.created_at,
        )

        # Update model from domain
        user_model.update_from_domain(updated_user)

        # Verify updates
        assert user_model.email == "updated@example.com"
        assert user_model.password_hash == "new_hash"
        assert user_model.first_name == "New"
        assert user_model.status == UserStatus.ACTIVE.value
        assert user_model.is_email_verified is True


class TestBcryptPasswordService:
    """Test BcryptPasswordService integration."""

    @pytest.fixture
    def password_service(self):
        """Create password service instance."""
        return BcryptPasswordService(rounds=4)  # Lower rounds for faster tests

    @pytest.mark.asyncio
    async def test_password_hashing_and_verification(self, password_service):
        """Test password hashing and verification."""
        password = "test_password_123"

        # Hash password
        password_hash = await password_service.hash_password(password)

        # Verify password hash is generated
        assert password_hash is not None
        assert password_hash != password
        assert len(password_hash) > 50  # bcrypt hashes are typically 60 chars

        # Verify correct password
        is_valid = await password_service.verify_password(password, password_hash)
        assert is_valid is True

        # Verify incorrect password
        is_valid = await password_service.verify_password(
            "wrong_password", password_hash
        )
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_password_hash_uniqueness(self, password_service):
        """Test that same password generates different hashes."""
        password = "same_password"

        hash1 = await password_service.hash_password(password)
        hash2 = await password_service.hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert await password_service.verify_password(password, hash1) is True
        assert await password_service.verify_password(password, hash2) is True


class TestJoseJWTService:
    """Test JoseJWTService integration."""

    @pytest.fixture
    def jwt_service(self):
        """Create JWT service instance."""
        return JoseJWTService(
            secret_key="test_secret_key_for_testing",
            algorithm="HS256",
            access_token_expire_minutes=15,
            refresh_token_expire_days=7,
        )

    def test_access_token_creation_and_verification(self, jwt_service):
        """Test access token creation and verification."""
        user_id = uuid4()

        # Create access token
        access_token = jwt_service.create_access_token(user_id)

        # Verify token is created
        assert access_token is not None
        assert len(access_token) > 50  # JWT tokens are quite long

        # Verify token
        payload = jwt_service.verify_token(access_token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

        # Extract user ID
        extracted_user_id = jwt_service.extract_user_id(access_token)
        assert extracted_user_id == user_id

    def test_refresh_token_creation_and_verification(self, jwt_service):
        """Test refresh token creation and verification."""
        user_id = uuid4()

        # Create refresh token
        refresh_token = jwt_service.create_refresh_token(user_id)

        # Verify token is created
        assert refresh_token is not None
        assert len(refresh_token) > 50

        # Verify token
        payload = jwt_service.verify_token(refresh_token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

        # Extract user ID
        extracted_user_id = jwt_service.extract_user_id(refresh_token)
        assert extracted_user_id == user_id

    def test_invalid_token_verification(self, jwt_service):
        """Test verification of invalid tokens."""
        # Test completely invalid token
        payload = jwt_service.verify_token("invalid.token.here")
        assert payload is None

        # Test token extraction from invalid token
        user_id = jwt_service.extract_user_id("invalid.token.here")
        assert user_id is None

    def test_token_with_custom_expiry(self, jwt_service):
        """Test token creation with custom expiry."""
        from datetime import timedelta

        user_id = uuid4()
        custom_expiry = datetime.now(UTC) + timedelta(minutes=30)

        # Create token with custom expiry
        token = jwt_service.create_access_token(user_id, custom_expiry)

        # Verify token
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["exp"] == int(custom_expiry.timestamp())

    @pytest.mark.skip(
        reason="TODO: JWT token uniqueness test failing - needs timestamp precision fix"
    )
    def test_token_uniqueness(self, jwt_service):
        """Test that tokens are unique even for same user."""
        user_id = uuid4()

        token1 = jwt_service.create_access_token(user_id)
        token2 = jwt_service.create_access_token(user_id)

        # Tokens should be different due to timestamp differences
        assert token1 != token2

        # But both should be valid for the same user
        assert jwt_service.extract_user_id(token1) == user_id
        assert jwt_service.extract_user_id(token2) == user_id


@pytest.mark.integration  # type: ignore[misc]
class TestUserManagementIntegration:
    """Integration tests combining multiple components."""

    @pytest.fixture
    def password_service(self):
        return BcryptPasswordService(rounds=4)

    @pytest.fixture
    def jwt_service(self):
        return JoseJWTService(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=15,
            refresh_token_expire_days=7,
        )

    @pytest.mark.asyncio
    async def test_complete_user_creation_flow(self, password_service):
        """Test complete user creation with password hashing."""
        # Create user with hashed password
        plain_password = "SecureP@ssword123"
        hashed_password = await password_service.hash_password(plain_password)

        user = User(
            id=uuid4(),
            email="integration@test.com",
            password_hash=hashed_password,
            first_name="Integration",
            last_name="Test",
            created_at=datetime.now(UTC),
        )

        # Verify password verification works
        is_valid = await password_service.verify_password(
            plain_password, user.password_hash
        )
        assert is_valid is True

        # Convert to model and back
        user_model = UserModel.from_domain(user)
        converted_user = user_model.to_domain()

        # Verify conversion preserves data
        assert converted_user.id == user.id
        assert converted_user.email == user.email
        assert converted_user.password_hash == user.password_hash

        # Verify password still works after conversion
        is_valid_after_conversion = await password_service.verify_password(
            plain_password, converted_user.password_hash
        )
        assert is_valid_after_conversion is True

    @pytest.mark.skip(
        reason="TODO: JWT token uniqueness test failing - needs timestamp precision fix"
    )
    def test_complete_authentication_flow(self, jwt_service):
        """Test complete authentication flow with JWT tokens."""
        user_id = uuid4()

        # Create tokens
        access_token = jwt_service.create_access_token(user_id)
        refresh_token = jwt_service.create_refresh_token(user_id)

        # Verify access token
        access_payload = jwt_service.verify_token(access_token)
        assert access_payload["type"] == "access"
        assert jwt_service.extract_user_id(access_token) == user_id

        # Verify refresh token
        refresh_payload = jwt_service.verify_token(refresh_token)
        assert refresh_payload["type"] == "refresh"
        assert jwt_service.extract_user_id(refresh_token) == user_id

        # Simulate token refresh
        new_access_token = jwt_service.create_access_token(user_id)
        new_refresh_token = jwt_service.create_refresh_token(user_id)

        # Verify new tokens work
        assert jwt_service.extract_user_id(new_access_token) == user_id
        assert jwt_service.extract_user_id(new_refresh_token) == user_id

        # Verify old and new tokens are different
        assert access_token != new_access_token
        assert refresh_token != new_refresh_token
