"""Pytest configuration for user_management module tests."""
# pyright: reportMissingImports=false
# pyright: reportUnknownMemberType=false
# pyright: reportUntypedFunctionDecorator=false

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest  # type: ignore[import-untyped]

from modules.user_management.domain.entities.user import User, UserStatus


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password_123",
        created_at=datetime.now(UTC),
        first_name="John",
        last_name="Doe",
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )


@pytest.fixture
def pending_user():
    """Create a pending verification user for testing."""
    return User(
        id=uuid4(),
        email="pending@example.com",
        password_hash="hashed_password_456",
        created_at=datetime.now(UTC),
        status=UserStatus.PENDING_VERIFICATION,
        is_active=True,
        is_email_verified=False,
        email_verification_token="verification_token_123",
    )


@pytest.fixture
def ml_connected_user():
    """Create a user connected to MercadoLibre for testing."""
    return User(
        id=uuid4(),
        email="ml_user@example.com",
        password_hash="hashed_password_789",
        created_at=datetime.now(UTC),
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
        ml_user_id="ML123456",
        ml_access_token="ml_access_token_123",
        ml_refresh_token="ml_refresh_token_123",
        ml_token_expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
