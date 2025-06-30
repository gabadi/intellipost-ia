"""
Unit tests for authentication service.

Tests the authentication service implementation with mocked dependencies.
"""

import pytest
from datetime import UTC, datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from modules.auth.application.authentication_service import AuthenticationServiceImpl
from modules.auth.domain.models import AuthResult, AuthenticatedUser, TokenPair
from modules.user.infrastructure.models import UserModel
from infrastructure.config.settings import settings


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def auth_service(mock_db_session):
    """Create authentication service with mocked dependencies."""
    return AuthenticationServiceImpl(mock_db_session)


@pytest.fixture
def sample_user():
    """Create a sample user model."""
    return UserModel(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        status="pending_verification",
        failed_login_attempts=0
    )


class TestAuthenticationService:
    """Test suite for authentication service."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_db_session):
        """Test successful user registration."""
        # Setup
        email = "newuser@example.com"
        password = "StrongPass123!"

        # Mock database queries
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None  # User doesn't exist
        mock_db_session.execute.return_value = mock_result

        # Execute
        result = await auth_service.register_user(email, password)

        # Assert
        assert isinstance(result, AuthResult)
        assert result.email == email
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "Bearer"

        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, auth_service, mock_db_session, sample_user):
        """Test registration with existing email."""
        # Setup
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_user  # User exists
        mock_db_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(sample_user.email, "password123")

    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, auth_service):
        """Test registration with weak password."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            await auth_service.register_user("test@example.com", "weak")

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_db_session, sample_user):
        """Test successful user authentication."""
        # Setup
        email = sample_user.email
        password = "correct_password"

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        # Mock password verification
        with patch.object(auth_service.password_manager, 'verify_password', return_value=True):
            result = await auth_service.authenticate_user(email, password)

        # Assert
        assert isinstance(result, AuthResult)
        assert result.email == email
        assert result.access_token is not None
        assert result.refresh_token is not None

        # Verify login was recorded
        assert sample_user.failed_login_attempts == 0
        assert sample_user.last_login_at is not None

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, mock_db_session, sample_user):
        """Test authentication with wrong password."""
        # Setup
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        # Mock password verification to fail
        with patch.object(auth_service.password_manager, 'verify_password', return_value=False):
            with pytest.raises(ValueError, match="Invalid credentials"):
                await auth_service.authenticate_user(sample_user.email, "wrong_password")

        # Verify failed attempt was recorded
        assert sample_user.failed_login_attempts == 1

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, auth_service, mock_db_session, sample_user):
        """Test authentication with locked account."""
        # Setup locked account
        sample_user.failed_login_attempts = 5
        sample_user.last_failed_login_at = datetime.now(UTC)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValueError, match="Account temporarily locked"):
            await auth_service.authenticate_user(sample_user.email, "any_password")

    @pytest.mark.asyncio
    async def test_validate_token_success(self, auth_service, mock_db_session, sample_user):
        """Test successful token validation."""
        # Create valid token
        user_id = sample_user.id
        email = sample_user.email
        token = auth_service.jwt_manager.create_access_token(user_id, email)

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        # Execute
        result = await auth_service.validate_token(token)

        # Assert
        assert isinstance(result, AuthenticatedUser)
        assert result.user_id == user_id
        assert result.email == email

    @pytest.mark.asyncio
    async def test_validate_token_expired(self, auth_service):
        """Test validation of expired token."""
        # Create expired token
        expire = datetime.now(UTC) - timedelta(minutes=1)
        data = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "exp": expire,
            "type": "access"
        }
        token = jwt.encode(data, settings.secret_key, algorithm=settings.jwt_algorithm)

        # Execute and assert
        with pytest.raises(ValueError, match="Invalid token"):
            await auth_service.validate_token(token)

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, mock_db_session, sample_user):
        """Test successful token refresh."""
        # Create valid refresh token
        refresh_token, expires_at = auth_service.jwt_manager.create_refresh_token(sample_user.id)
        token_hash = auth_service._hash_token(refresh_token)

        # Mock refresh token model
        refresh_token_model = Mock()
        refresh_token_model.token_hash = token_hash
        refresh_token_model.user_id = sample_user.id
        refresh_token_model.expires_at = expires_at

        # Mock database queries
        mock_result1 = AsyncMock()
        mock_result1.scalar_one_or_none.return_value = refresh_token_model

        mock_result2 = AsyncMock()
        mock_result2.scalar_one_or_none.return_value = sample_user

        mock_db_session.execute.side_effect = [mock_result1, mock_result2]

        # Execute
        result = await auth_service.refresh_token(refresh_token)

        # Assert
        assert isinstance(result, TokenPair)
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "Bearer"

        # Verify old token was deleted
        mock_db_session.delete.assert_called_once_with(refresh_token_model)

    @pytest.mark.asyncio
    async def test_logout_user(self, auth_service, mock_db_session):
        """Test user logout."""
        user_id = uuid4()

        # Execute
        await auth_service.logout_user(user_id)

        # Verify refresh tokens were deleted
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
