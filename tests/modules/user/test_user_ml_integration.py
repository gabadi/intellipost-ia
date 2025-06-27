"""Unit tests for User MercadoLibre integration."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from backend.modules.user.domain.user_core import UserCore
from backend.modules.user.domain.user_ml_integration import UserMLIntegration


class TestUserMLIntegration:
    """Test cases for User MercadoLibre integration methods."""

    def test_is_ml_connected_true(self):
        """Test MercadoLibre connection detection when valid."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1)
        )

        assert UserMLIntegration.is_ml_connected(user) is True

    def test_is_ml_connected_false_no_user_id(self):
        """Test MercadoLibre connection when user ID is missing."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1)
        )

        assert UserMLIntegration.is_ml_connected(user) is False

    def test_is_ml_connected_false_no_access_token(self):
        """Test MercadoLibre connection when access token is missing."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_token_expires_at=datetime.now(UTC) + timedelta(hours=1)
        )

        assert UserMLIntegration.is_ml_connected(user) is False

    def test_is_ml_connected_false_token_expired(self):
        """Test MercadoLibre connection when token is expired."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123",
            ml_token_expires_at=datetime.now(UTC) - timedelta(hours=1)
        )

        assert UserMLIntegration.is_ml_connected(user) is False

    def test_is_ml_connected_false_no_expires_at(self):
        """Test MercadoLibre connection when expires_at is missing."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC),
            ml_user_id="ML123",
            ml_access_token="token123"
        )

        assert UserMLIntegration.is_ml_connected(user) is False

    def test_update_ml_tokens(self):
        """Test updating MercadoLibre tokens."""
        user = UserCore(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/kNdRHxLIcgdRLMzGu",
            created_at=datetime.now(UTC)
        )
        initial_updated_at = user.updated_at

        access_token = "new_access_token"
        refresh_token = "new_refresh_token"
        expires_at = datetime.now(UTC) + timedelta(hours=2)

        UserMLIntegration.update_ml_tokens(user, access_token, refresh_token, expires_at)

        assert user.ml_access_token == access_token
        assert user.ml_refresh_token == refresh_token
        assert user.ml_token_expires_at == expires_at
        assert user.updated_at > initial_updated_at
