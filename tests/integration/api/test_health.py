"""Integration tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient

from main import app

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Test cases for health endpoint."""

    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_structure(self, client):
        """Test that health endpoint returns expected JSON structure."""
        response = client.get("/health")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

        # Check field values
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert isinstance(data["timestamp"], str)

    def test_health_endpoint_timestamp_format(self, client):
        """Test that health endpoint returns valid ISO timestamp."""
        response = client.get("/health")
        data = response.json()

        # Should be able to parse as ISO format
        from datetime import datetime

        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)

    def test_health_endpoint_response_schema(self, client):
        """Test that health endpoint matches expected schema."""
        response = client.get("/health")
        data = response.json()

        # Validate data types
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)

        # Validate content
        assert len(data["status"]) > 0
        assert len(data["timestamp"]) > 0
        assert len(data["version"]) > 0

    def test_root_endpoint_returns_200(self, client):
        """Test that root endpoint returns 200 status code."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_returns_api_info(self, client):
        """Test that root endpoint returns API information."""
        response = client.get("/")
        data = response.json()

        # Check required fields
        assert "message" in data
        assert "version" in data
        assert "docs" in data

        # Check field values
        assert data["message"] == "IntelliPost AI Backend API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_docs_endpoint_accessible(self, client):
        """Test that OpenAPI docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # Should return valid JSON
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
