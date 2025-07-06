"""Unit tests for authentication service."""
# pyright: reportMissingImports=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUntypedFunctionDecorator=false

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest  # type: ignore[import-untyped]

from modules.user_management.domain.entities.user import User, UserStatus
from modules.user_management.domain.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from modules.user_management.domain.services.authentication import AuthenticationService


class TestAuthenticationService:
    """Test cases for AuthenticationService."""

    @pytest.fixture  # type: ignore[misc]
    def mock_user_repository(self) -> AsyncMock:
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture  # type: ignore[misc]
    def mock_password_service(self) -> AsyncMock:
        """Mock password service."""
        return AsyncMock()

    @pytest.fixture  # type: ignore[misc]
    def auth_service(
        self, mock_user_repository: AsyncMock, mock_password_service: AsyncMock
    ) -> Any:
        """Create authentication service with mocked dependencies."""
        return AuthenticationService(
            user_repository=mock_user_repository,
            password_service=mock_password_service,
            max_login_attempts=5,
            token_expiry_hours=24,
        )

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test successful user registration."""
        # Setup
        email = "test@example.com"
        password = "SecureP@ss123"
        first_name = "John"
        last_name = "Doe"

        mock_user_repository.get_by_email.return_value = None  # User doesn't exist
        mock_password_service.hash_password.return_value = "hashed_password"

        created_user = User(
            id=uuid4(),
            email=email,
            password_hash="hashed_password",
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(UTC),
        )
        mock_user_repository.create.return_value = created_user

        # Execute
        result = await auth_service.register_user(
            email, password, first_name, last_name
        )

        # Verify
        assert result == created_user
        mock_user_repository.get_by_email.assert_called_once_with(email)
        mock_password_service.hash_password.assert_called_once_with(password)
        mock_user_repository.create.assert_called_once()

        # Verify user data passed to repository
        user_arg = mock_user_repository.create.call_args[0][0]
        assert user_arg.email == email
        assert user_arg.password_hash == "hashed_password"
        assert user_arg.first_name == first_name
        assert user_arg.last_name == last_name
        assert user_arg.status == UserStatus.PENDING_VERIFICATION

    @pytest.mark.asyncio
    async def test_register_user_already_exists(
        self, auth_service, mock_user_repository
    ):
        """Test registration fails when user already exists."""
        # Setup
        email = "existing@example.com"
        existing_user = User(
            id=uuid4(),
            email=email,
            password_hash="existing_hash",
            created_at=datetime.now(UTC),
        )
        mock_user_repository.get_by_email.return_value = existing_user

        # Execute & Verify
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await auth_service.register_user(email, "password")

        assert exc_info.value.email == email
        mock_user_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self, auth_service, mock_user_repository
    ):
        """Test registration fails with weak password."""
        # Setup
        mock_user_repository.get_by_email.return_value = None

        # Execute & Verify
        with pytest.raises(WeakPasswordError):
            await auth_service.register_user("test@example.com", "weak")

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test successful user authentication."""
        # Setup
        email = "test@example.com"
        password = "correct_password"

        user = User(
            id=uuid4(),
            email=email,
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
            is_active=True,
        )

        mock_user_repository.get_by_email.return_value = user
        mock_password_service.verify_password.return_value = True
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.authenticate_user(email, password)

        # Verify
        assert result == user
        mock_user_repository.get_by_email.assert_called_once_with(email)
        mock_password_service.verify_password.assert_called_once_with(
            password, "hashed_password"
        )
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self, auth_service, mock_user_repository
    ):
        """Test authentication fails when user not found."""
        # Setup
        mock_user_repository.get_by_email.return_value = None

        # Execute
        result = await auth_service.authenticate_user(
            "nonexistent@example.com", "password"
        )

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(
        self, auth_service, mock_user_repository
    ):
        """Test authentication fails when account is locked."""
        # Setup
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            failed_login_attempts=5,  # Max attempts reached
        )

        mock_user_repository.get_by_email.return_value = user

        # Execute & Verify
        with pytest.raises(AccountLockedError) as exc_info:
            await auth_service.authenticate_user("test@example.com", "password")

        assert exc_info.value.failed_attempts == 5
        assert exc_info.value.max_attempts == 5

    @pytest.mark.asyncio
    async def test_authenticate_user_account_inactive(
        self, auth_service, mock_user_repository
    ):
        """Test authentication fails when account is inactive."""
        # Setup
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.SUSPENDED,
        )

        mock_user_repository.get_by_email.return_value = user

        # Execute & Verify
        with pytest.raises(AccountInactiveError):
            await auth_service.authenticate_user("test@example.com", "password")

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test authentication fails with wrong password."""
        # Setup
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
            is_active=True,
        )

        mock_user_repository.get_by_email.return_value = user
        mock_password_service.verify_password.return_value = False
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.authenticate_user(
            "test@example.com", "wrong_password"
        )

        # Verify
        assert result is None
        mock_user_repository.update.assert_called_once()  # Failed attempt recorded

    @pytest.mark.asyncio
    async def test_verify_email_success(self, auth_service, mock_user_repository):
        """Test successful email verification."""
        # Setup
        user_id = uuid4()
        verification_token = "valid_token"

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            email_verification_token=verification_token,
            is_email_verified=False,
        )

        mock_user_repository.get_by_id.return_value = user
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.verify_email(user_id, verification_token)

        # Verify
        assert result is True
        assert user.is_email_verified is True
        assert user.email_verification_token is None
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, auth_service, mock_user_repository):
        """Test email verification with invalid token."""
        # Setup
        user_id = uuid4()

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            email_verification_token="correct_token",
            is_email_verified=False,
        )

        mock_user_repository.get_by_id.return_value = user

        # Execute
        result = await auth_service.verify_email(user_id, "wrong_token")

        # Verify
        assert result is False
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_initiate_password_reset_success(
        self, auth_service, mock_user_repository
    ):
        """Test successful password reset initiation."""
        # Setup
        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
        )

        mock_user_repository.get_by_email.return_value = user
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.initiate_password_reset("test@example.com")

        # Verify
        assert result is not None
        assert len(result) > 20  # Should be a secure token
        assert user.password_reset_token == result
        assert user.password_reset_expires_at is not None
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_initiate_password_reset_user_not_found(
        self, auth_service, mock_user_repository
    ):
        """Test password reset initiation for non-existent user."""
        # Setup
        mock_user_repository.get_by_email.return_value = None

        # Execute
        result = await auth_service.initiate_password_reset("nonexistent@example.com")

        # Verify
        assert result is None
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test successful password reset."""
        # Setup
        user_id = uuid4()
        reset_token = "valid_reset_token"
        new_password = "NewSecureP@ss123"

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="old_hashed_password",
            created_at=datetime.now(UTC),
            password_reset_token=reset_token,
            password_reset_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        mock_user_repository.get_by_id.return_value = user
        mock_password_service.hash_password.return_value = "new_hashed_password"
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.reset_password(user_id, reset_token, new_password)

        # Verify
        assert result is True
        assert user.password_hash == "new_hashed_password"
        assert user.password_reset_token is None
        assert user.password_reset_expires_at is None
        mock_password_service.hash_password.assert_called_once_with(new_password)
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(
        self, auth_service, mock_user_repository
    ):
        """Test password reset with expired token."""
        # Setup
        user_id = uuid4()
        reset_token = "expired_token"

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(UTC),
            password_reset_token=reset_token,
            password_reset_expires_at=datetime.now(UTC) - timedelta(hours=1),  # Expired
        )

        mock_user_repository.get_by_id.return_value = user

        # Execute
        result = await auth_service.reset_password(
            user_id, reset_token, "NewPassword123!"
        )

        # Verify
        assert result is False
        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test successful password change."""
        # Setup
        user_id = uuid4()
        current_password = "current_password"
        new_password = "NewSecureP@ss123"

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="current_hashed_password",
            created_at=datetime.now(UTC),
        )

        mock_user_repository.get_by_id.return_value = user
        mock_password_service.verify_password.return_value = True
        mock_password_service.hash_password.return_value = "new_hashed_password"
        mock_user_repository.update.return_value = user

        # Execute
        result = await auth_service.change_password(
            user_id, current_password, new_password
        )

        # Verify
        assert result is True
        assert user.password_hash == "new_hashed_password"
        mock_password_service.verify_password.assert_called_once_with(
            current_password, "current_hashed_password"
        )
        mock_password_service.hash_password.assert_called_once_with(new_password)
        mock_user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(
        self, auth_service, mock_user_repository, mock_password_service
    ):
        """Test password change with wrong current password."""
        # Setup
        user_id = uuid4()

        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="current_hashed_password",
            created_at=datetime.now(UTC),
        )

        mock_user_repository.get_by_id.return_value = user
        mock_password_service.verify_password.return_value = False

        # Execute
        result = await auth_service.change_password(
            user_id, "wrong_password", "NewPassword123!"
        )

        # Verify
        assert result is False
        mock_password_service.hash_password.assert_not_called()
        mock_user_repository.update.assert_not_called()

    def test_is_password_strong_valid_passwords(self, auth_service):
        """Test password strength validation with valid passwords."""
        valid_passwords = [
            "SecureP@ss123",
            "MyStr0ng!Password",
            "C0mpl3x$P@ssw0rd",
            "Test123!@#",
        ]

        for password in valid_passwords:
            assert auth_service._is_password_strong(password) is True

    def test_is_password_strong_invalid_passwords(self, auth_service):
        """Test password strength validation with invalid passwords."""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!@#",  # No numbers
            "NoSpecialChars123",  # No special characters
            "password",  # Too weak overall
            "",  # Empty
        ]

        for password in invalid_passwords:
            assert auth_service._is_password_strong(password) is False

    def test_generate_secure_token(self, auth_service):
        """Test secure token generation."""
        token1 = auth_service._generate_secure_token()
        token2 = auth_service._generate_secure_token()

        # Tokens should be different
        assert token1 != token2

        # Tokens should be reasonably long
        assert len(token1) > 20
        assert len(token2) > 20
