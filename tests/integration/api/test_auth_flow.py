"""Integration tests for authentication API endpoints."""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from datetime import datetime, timezone
import json

from backend.main import app

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestAuthenticationFlow:
    """Integration tests for complete authentication flow."""

    @pytest_asyncio.fixture
    async def client(self):
        """Async HTTP client for testing."""
        from httpx import AsyncClient
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def test_user_data(self):
        """Test user registration data."""
        return {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }

    @pytest.fixture
    def login_data(self):
        """Test user login data."""
        return {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }

    async def test_user_registration_flow(self, client: AsyncClient, test_user_data):
        """Test complete user registration flow."""
        # Test successful registration
        response = await client.post("/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "tokens" in data
        assert "message" in data

        # Verify user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["first_name"] == test_user_data["first_name"]
        assert user["last_name"] == test_user_data["last_name"]
        assert "password_hash" not in user  # Should not expose password hash

        # Verify tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert "expires_in" in tokens

    async def test_duplicate_email_registration(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email fails."""
        # First registration should succeed
        response = await client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201

        # Second registration with same email should fail
        response = await client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data
        assert "email" in data["error"].lower()

    async def test_user_login_flow(self, client: AsyncClient, test_user_data, login_data):
        """Test complete user login flow."""
        # First register a user
        await client.post("/auth/register", json=test_user_data)

        # Test successful login
        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "tokens" in data
        assert "message" in data

        # Verify user data
        user = data["user"]
        assert user["email"] == login_data["email"]

        # Verify tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    async def test_invalid_login_credentials(self, client: AsyncClient, test_user_data):
        """Test login with invalid credentials fails."""
        # Register a user first
        await client.post("/auth/register", json=test_user_data)

        # Test with wrong password
        invalid_login = {
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = await client.post("/auth/login", json=invalid_login)
        assert response.status_code == 401

        # Test with non-existent email
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!"
        }
        response = await client.post("/auth/login", json=invalid_login)
        assert response.status_code == 401

    async def test_token_refresh_flow(self, client: AsyncClient, test_user_data):
        """Test JWT token refresh flow."""
        # Register and login to get tokens
        await client.post("/auth/register", json=test_user_data)
        login_response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        tokens = login_response.json()["tokens"]
        refresh_token = tokens["refresh_token"]

        # Test token refresh
        response = await client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "expires_in" in data
        # New access token should be different
        assert data["access_token"] != tokens["access_token"]

    async def test_protected_endpoint_access(self, client: AsyncClient, test_user_data):
        """Test accessing protected endpoints with JWT."""
        # Register and login to get tokens
        await client.post("/auth/register", json=test_user_data)
        login_response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        access_token = login_response.json()["tokens"]["access_token"]

        # Test accessing protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert "user" in data
        user = data["user"]
        assert user["email"] == test_user_data["email"]

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoints without JWT fails."""
        response = await client.get("/auth/me")
        assert response.status_code == 401

    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoints with invalid JWT fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401

    async def test_logout_flow(self, client: AsyncClient, test_user_data):
        """Test user logout flow."""
        # Register and login to get tokens
        await client.post("/auth/register", json=test_user_data)
        login_response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        tokens = login_response.json()["tokens"]
        refresh_token = tokens["refresh_token"]

        # Test logout
        response = await client.post("/auth/logout", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # After logout, refresh token should be invalid
        refresh_response = await client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 401

    async def test_password_validation_requirements(self, client: AsyncClient):
        """Test password validation requirements."""
        # Test weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        }

        response = await client.post("/auth/register", json=weak_password_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data
        assert "password" in data["error"].lower()

    async def test_email_validation_requirements(self, client: AsyncClient):
        """Test email validation requirements."""
        # Test invalid email format
        invalid_email_data = {
            "email": "invalid-email",
            "password": "ValidPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }

        response = await client.post("/auth/register", json=invalid_email_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data
        assert "email" in data["error"].lower()

    # NOTE: Performance testing moved to tests/performance/test_auth_timing.py
    # Integration tests focus on functionality, not response times
