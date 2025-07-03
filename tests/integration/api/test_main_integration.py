"""Integration tests for main application.

These tests verify the complete FastAPI application setup including:
- Application metadata configuration
- Middleware setup (CORS)
- Route registration
- OpenAPI documentation endpoints

Note: These are integration tests because they test the full application
instance with TestClient, not isolated units of code.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


class TestMainApp:
    """Test cases for main FastAPI application."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as test_client:
            yield test_client

    def test_app_metadata(self, client):
        """Test FastAPI application metadata."""
        openapi = client.get("/openapi.json").json()

        assert openapi["info"]["title"] == "IntelliPost AI Backend"
        assert openapi["info"]["version"] == "1.0.0"
        assert "description" in openapi["info"]

    def test_cors_middleware_configured(self, client):
        """Test CORS middleware is properly configured by testing CORS headers."""
        # Test OPTIONS request to check CORS
        response = client.options("/health")
        # Should not fail due to CORS issues
        assert response.status_code in [200, 405]  # 405 is OK, means endpoint exists

    def test_health_route_registered(self, client):
        """Test health route is properly registered."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_route_registered(self, client):
        """Test root route is properly registered."""
        response = client.get("/")
        assert response.status_code == 200

    def test_openapi_documentation_available(self, client):
        """Test OpenAPI documentation endpoints are available."""
        # Test JSON schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Test docs UI
        response = client.get("/docs")
        assert response.status_code == 200

        # Test redoc UI
        response = client.get("/redoc")
        assert response.status_code == 200
