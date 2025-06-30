"""
Integration tests for authentication API endpoints.

Tests the complete authentication flow with real database interactions.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from modules.user.infrastructure.models import UserModel, RefreshTokenModel


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthenticationAPI:
    """Integration tests for authentication endpoints."""

    async def test_register_flow(self, async_client: AsyncClient, test_db):
        """Test complete registration flow."""
        # Register new user
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "StrongPass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["email"] == "newuser@example.com"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

        # Verify user in database
        async with test_db() as session:
            stmt = select(UserModel).where(UserModel.email == "newuser@example.com")
            result = await session.execute(stmt)
            user = result.scalar_one()
            assert user is not None
            assert user.is_active is True

    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user):
        """Test registration with existing email."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "AnotherPass123!"
            }
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    async def test_login_flow(self, async_client: AsyncClient, test_user):
        """Test complete login flow."""
        # Login with valid credentials
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"  # This is the password used in conftest.py
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid_credentials(self, async_client: AsyncClient, test_user):
        """Test login with wrong password."""
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    async def test_session_endpoint(self, async_client: AsyncClient, test_user):
        """Test session status endpoint."""
        # First login to get token
        login_response = await async_client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        token = login_response.json()["access_token"]

        # Check session
        response = await async_client.get(
            "/api/auth/session",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert "created_at" in data

    async def test_refresh_token_flow(self, async_client: AsyncClient, test_user):
        """Test token refresh flow."""
        # Login to get initial tokens
        login_response = await async_client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh tokens
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token  # Should be different

    async def test_logout_flow(self, async_client: AsyncClient, test_user, test_db):
        """Test logout flow."""
        # Login first
        login_response = await async_client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Logout
        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 204

        # Verify refresh tokens are deleted
        async with test_db() as session:
            stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id == test_user.id)
            result = await session.execute(stmt)
            tokens = result.scalars().all()
            assert len(tokens) == 0

    async def test_protected_endpoint_without_auth(self, async_client: AsyncClient):
        """Test accessing protected endpoint without authentication."""
        response = await async_client.get("/api/auth/session")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    async def test_rate_limiting(self, async_client: AsyncClient, test_user):
        """Test rate limiting for failed login attempts."""
        # Make 5 failed login attempts
        for _ in range(5):
            response = await async_client.post(
                "/api/auth/login",
                json={
                    "email": test_user.email,
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == 401

        # 6th attempt should be locked
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 423
        assert "locked" in response.json()["detail"]

    async def test_password_validation(self, async_client: AsyncClient):
        """Test password strength validation."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "weak@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422  # Pydantic validation error
