"""
API tests for content generation endpoints.

This module tests the FastAPI endpoints for content generation including
request/response validation, WebSocket functionality, and error handling.
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from modules.content_generation.api.routers.content_generation_router import router
from modules.content_generation.api.schemas import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentValidationSchema,
    ErrorResponseSchema,
    GeneratedContentSchema,
    ProcessingStatusSchema,
)
from modules.content_generation.domain.entities.ai_generation import (
    AIGeneration,
    GenerationStatus,
    ProcessingStep,
)
from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    AIServiceError,
    CategoryDetectionError,
    EntityNotFoundError,
    QualityThresholdError,
)


@pytest.fixture
def app():
    """Create FastAPI app with content generation router."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_use_case():
    """Create mock use case for testing."""
    return Mock()


@pytest.fixture
def mock_ai_generation():
    """Create mock AI generation for testing."""
    return AIGeneration(
        id=uuid4(),
        product_id=uuid4(),
        status=GenerationStatus.PROCESSING,
        current_step=ProcessingStep.TITLE_GENERATION,
        progress_percentage=45.0,
        estimated_completion_seconds=15,
        error_message=None,
        error_code=None,
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture
def mock_generated_content():
    """Create mock generated content for testing."""
    return GeneratedContent(
        id=uuid4(),
        product_id=uuid4(),
        title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
        description="iPhone 13 Pro de 128GB en excelente estado...",
        ml_category_id="MLA1055",
        ml_category_name="Celulares y Smartphones",
        ml_title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
        ml_price=Decimal("450000"),
        ml_currency_id="ARS",
        ml_available_quantity=1,
        ml_buying_mode="buy_it_now",
        ml_condition="used",
        ml_listing_type_id="gold_special",
        ml_attributes={
            "BRAND": "Apple",
            "MODEL": "iPhone 13 Pro",
            "COLOR": "Negro",
            "STORAGE_CAPACITY": "128GB",
        },
        ml_sale_terms={},
        ml_shipping={},
        confidence_overall=0.89,
        confidence_breakdown={
            "title": 0.95,
            "description": 0.87,
            "category": 0.92,
            "price": 0.82,
            "attributes": 0.91,
        },
        ai_provider="gemini",
        ai_model_version="2.5-flash",
        generation_time_ms=2340,
        version=1,
        generated_at=datetime.now(UTC),
    )


class TestContentGenerationEndpoints:
    """Test cases for content generation API endpoints."""

    def test_generate_content_success(self, client, mock_use_case, mock_ai_generation):
        """Test successful content generation request."""
        product_id = uuid4()

        # Mock the use case dependency
        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.execute.return_value = mock_ai_generation

            # Mock authentication
            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {
                    "regenerate": False,
                    "category_hint": "celulares",
                    "price_range": {"min": 400000, "max": 500000},
                    "target_audience": "usuarios premium",
                }

                response = client.post(
                    f"/api/v1/content-generation/products/{product_id}/generate",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_202_ACCEPTED
                response_data = response.json()

                assert "processing_id" in response_data
                assert response_data["status"] == "processing"
                assert response_data["progress"]["current_step"] == "title_generation"
                assert response_data["progress"]["percentage"] == 45.0
                assert response_data["estimated_completion_seconds"] == 15

    def test_generate_content_invalid_request(self, client):
        """Test content generation with invalid request data."""
        product_id = uuid4()

        # Invalid request data (missing required fields, invalid types)
        request_data = {
            "regenerate": "invalid",  # Should be boolean
            "price_range": {"min": "invalid"},  # Should be number
        }

        response = client.post(
            f"/api/v1/content-generation/products/{product_id}/generate",
            json=request_data,
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_generate_content_unauthorized(self, client):
        """Test content generation without authentication."""
        product_id = uuid4()

        request_data = {"regenerate": False, "category_hint": "celulares"}

        response = client.post(
            f"/api/v1/content-generation/products/{product_id}/generate",
            json=request_data,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_generate_content_ai_service_error(self, client, mock_use_case):
        """Test content generation with AI service error."""
        product_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.execute.side_effect = AIServiceError("AI service unavailable")

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {"regenerate": False}

                response = client.post(
                    f"/api/v1/content-generation/products/{product_id}/generate",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
                assert "AI service error" in response.json()["detail"]

    def test_generate_content_category_detection_error(self, client, mock_use_case):
        """Test content generation with category detection error."""
        product_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.execute.side_effect = CategoryDetectionError(
                "Category detection failed"
            )

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {"regenerate": False}

                response = client.post(
                    f"/api/v1/content-generation/products/{product_id}/generate",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert "Category detection failed" in response.json()["detail"]

    def test_generate_content_quality_threshold_error(self, client, mock_use_case):
        """Test content generation with quality threshold error."""
        product_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.execute.side_effect = QualityThresholdError(
                "Content quality below threshold"
            )

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {"regenerate": False}

                response = client.post(
                    f"/api/v1/content-generation/products/{product_id}/generate",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert (
                    "Generated content quality below threshold"
                    in response.json()["detail"]
                )

    def test_get_processing_status_success(self, client, mock_use_case):
        """Test successful processing status retrieval."""
        processing_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                response = client.get(
                    f"/api/v1/content-generation/processing/{processing_id}/status",
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()

                assert "processing_id" in response_data
                assert "status" in response_data
                assert "progress_percentage" in response_data
                assert "estimated_completion_seconds" in response_data

    def test_get_processing_status_not_found(self, client, mock_use_case):
        """Test processing status retrieval for non-existent processing."""
        processing_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.get_processing_status.side_effect = EntityNotFoundError(
                f"Processing not found: {processing_id}"
            )

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                response = client.get(
                    f"/api/v1/content-generation/processing/{processing_id}/status",
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_404_NOT_FOUND
                assert "Processing not found" in response.json()["detail"]

    def test_get_generated_content_not_implemented(self, client):
        """Test get generated content endpoint (not yet implemented)."""
        content_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_current_user"
        ) as mock_get_user:
            mock_get_user.return_value = {
                "user_id": "test_user",
                "email": "test@example.com",
            }

            response = client.get(
                f"/api/v1/content-generation/content/{content_id}",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    def test_validate_generated_content_success(self, client, mock_use_case):
        """Test successful content validation."""
        content_id = uuid4()

        mock_validation_results = {
            "is_valid": True,
            "validation_errors": [],
            "validation_warnings": ["Minor formatting issue"],
            "is_compliant": True,
            "compliance_issues": [],
            "quality_score": 0.89,
            "meets_threshold": True,
            "improvement_suggestions": ["Consider adding more product details"],
            "quality_indicators": {
                "has_key_features": True,
                "appropriate_length": True,
                "ml_compliant": True,
                "seo_optimized": True,
            },
        }

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.validate_generated_content.return_value = (
                mock_validation_results
            )

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                response = client.post(
                    f"/api/v1/content-generation/content/{content_id}/validate",
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()

                assert response_data["content_id"] == str(content_id)
                assert response_data["is_valid"] is True
                assert response_data["is_compliant"] is True
                assert response_data["quality_score"] == 0.89
                assert response_data["meets_threshold"] is True
                assert len(response_data["improvement_suggestions"]) == 1

    def test_validate_generated_content_not_found(self, client, mock_use_case):
        """Test content validation for non-existent content."""
        content_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.validate_generated_content.side_effect = EntityNotFoundError(
                f"Generated content not found: {content_id}"
            )

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                response = client.post(
                    f"/api/v1/content-generation/content/{content_id}/validate",
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_404_NOT_FOUND
                assert "Generated content not found" in response.json()["detail"]

    def test_enhance_generated_content_success(
        self, client, mock_use_case, mock_generated_content
    ):
        """Test successful content enhancement."""
        content_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.enhance_content.return_value = mock_generated_content

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {
                    "enhancement_type": "description",
                    "additional_data": {"focus": "technical_specs"},
                }

                response = client.post(
                    f"/api/v1/content-generation/content/{content_id}/enhance",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()

                assert response_data["id"] == str(mock_generated_content.id)
                assert response_data["title"] == mock_generated_content.title
                assert (
                    response_data["description"] == mock_generated_content.description
                )
                assert (
                    response_data["confidence_overall"]
                    == mock_generated_content.confidence_overall
                )

    def test_get_content_versions_success(
        self, client, mock_use_case, mock_generated_content
    ):
        """Test successful content versions retrieval."""
        product_id = uuid4()

        mock_versions = [mock_generated_content]

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.get_content_versions.return_value = mock_versions

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                response = client.get(
                    f"/api/v1/content-generation/products/{product_id}/versions",
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()

                assert response_data["product_id"] == str(product_id)
                assert len(response_data["versions"]) == 1
                assert response_data["total_versions"] == 1
                assert response_data["latest_version"] == 1

    def test_regenerate_content_success(
        self, client, mock_use_case, mock_ai_generation
    ):
        """Test successful content regeneration."""
        product_id = uuid4()

        with patch(
            "modules.content_generation.api.routers.content_generation_router.get_generate_content_use_case"
        ) as mock_get_use_case:
            mock_get_use_case.return_value = mock_use_case
            mock_use_case.execute.return_value = mock_ai_generation

            with patch(
                "modules.content_generation.api.routers.content_generation_router.get_current_user"
            ) as mock_get_user:
                mock_get_user.return_value = {
                    "user_id": "test_user",
                    "email": "test@example.com",
                }

                request_data = {
                    "regenerate": False,  # Will be forced to True
                    "category_hint": "celulares",
                }

                response = client.post(
                    f"/api/v1/content-generation/products/{product_id}/regenerate",
                    json=request_data,
                    headers={"Authorization": "Bearer test_token"},
                )

                assert response.status_code == status.HTTP_202_ACCEPTED
                response_data = response.json()

                assert "processing_id" in response_data
                assert response_data["status"] == "processing"

                # Verify that regenerate was forced to True
                mock_use_case.execute.assert_called_once()
                args, kwargs = mock_use_case.execute.call_args
                assert kwargs["regenerate"] is True


class TestWebSocketFunctionality:
    """Test cases for WebSocket functionality."""

    @pytest.mark.asyncio
    async def test_websocket_connection_success(self, client):
        """Test successful WebSocket connection."""
        processing_id = uuid4()

        with client.websocket_connect(
            f"/api/v1/content-generation/ws/processing/{processing_id}"
        ) as websocket:
            # Should receive connection confirmation
            data = websocket.receive_json()

            assert data["type"] == "connect"
            assert data["processing_id"] == str(processing_id)
            assert data["message"] == "Connected to content generation updates"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_websocket_heartbeat(self, client):
        """Test WebSocket heartbeat functionality."""
        processing_id = uuid4()

        with client.websocket_connect(
            f"/api/v1/content-generation/ws/processing/{processing_id}"
        ) as websocket:
            # Skip connection message
            websocket.receive_json()

            # Send heartbeat
            websocket.send_json(
                {"type": "heartbeat", "timestamp": datetime.now(UTC).isoformat()}
            )

            # Should receive heartbeat response
            data = websocket.receive_json()

            assert data["type"] == "heartbeat"
            assert "timestamp" in data
            assert "server_time" in data

    @pytest.mark.asyncio
    async def test_websocket_progress_updates(self, client):
        """Test WebSocket progress updates."""
        processing_id = uuid4()

        with client.websocket_connect(
            f"/api/v1/content-generation/ws/processing/{processing_id}"
        ) as websocket:
            # Skip connection message
            websocket.receive_json()

            # Mock progress monitoring would send updates
            # In a real scenario, this would be triggered by the processing workflow

            # This test would verify the WebSocket message format
            # and ensure proper broadcasting to connected clients

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, client):
        """Test WebSocket error handling."""
        processing_id = uuid4()

        with client.websocket_connect(
            f"/api/v1/content-generation/ws/processing/{processing_id}"
        ) as websocket:
            # Skip connection message
            websocket.receive_json()

            # Send invalid message
            websocket.send_text("invalid json")

            # Connection should remain open despite invalid message
            # (Error handling should be logged but not close connection)

    @pytest.mark.asyncio
    async def test_websocket_disconnection_cleanup(self, client):
        """Test WebSocket disconnection cleanup."""
        processing_id = uuid4()

        with client.websocket_connect(
            f"/api/v1/content-generation/ws/processing/{processing_id}"
        ) as websocket:
            # Connection established
            websocket.receive_json()

            # Close connection
            websocket.close()

            # WebSocket manager should clean up the connection
            # This would be verified in integration tests with actual WebSocket manager


class TestRequestResponseValidation:
    """Test cases for request and response validation."""

    def test_content_generation_request_validation(self):
        """Test ContentGenerationRequest validation."""
        # Valid request
        valid_request = ContentGenerationRequest(
            regenerate=False,
            category_hint="celulares",
            price_range={"min": 10000, "max": 50000},
            target_audience="usuarios premium",
        )

        assert valid_request.regenerate is False
        assert valid_request.category_hint == "celulares"
        assert valid_request.price_range["min"] == 10000
        assert valid_request.target_audience == "usuarios premium"

    def test_content_generation_request_validation_invalid(self):
        """Test ContentGenerationRequest validation with invalid data."""
        # Test category hint too long
        with pytest.raises(ValueError):
            ContentGenerationRequest(
                regenerate=False,
                category_hint="a" * 101,  # Too long
            )

        # Test target audience too long
        with pytest.raises(ValueError):
            ContentGenerationRequest(
                regenerate=False,
                target_audience="a" * 101,  # Too long
            )

    def test_content_generation_response_validation(self):
        """Test ContentGenerationResponse validation."""
        processing_id = uuid4()

        response = ContentGenerationResponse(
            processing_id=processing_id,
            status="processing",
            estimated_completion_seconds=30,
            progress={
                "current_step": "title_generation",
                "total_steps": 9,
                "percentage": 45.0,
            },
        )

        assert response.processing_id == processing_id
        assert response.status == "processing"
        assert response.estimated_completion_seconds == 30
        assert response.progress["current_step"] == "title_generation"
        assert response.progress["percentage"] == 45.0

    def test_generated_content_schema_validation(self):
        """Test GeneratedContentSchema validation."""
        content_id = uuid4()
        product_id = uuid4()

        content = GeneratedContentSchema(
            id=content_id,
            product_id=product_id,
            title="iPhone 13 Pro 128GB Negro",
            description="iPhone description",
            ml_category_id="MLA1055",
            ml_category_name="Celulares y Smartphones",
            ml_title="iPhone 13 Pro 128GB Negro",
            ml_price=450000.0,
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition="used",
            ml_listing_type_id="gold_special",
            ml_attributes={"BRAND": "Apple", "MODEL": "iPhone 13 Pro"},
            ml_sale_terms={},
            ml_shipping={},
            confidence_overall=0.89,
            confidence_breakdown={"title": 0.95, "description": 0.87},
            ai_provider="gemini",
            ai_model_version="2.5-flash",
            generation_time_ms=2340,
            version=1,
            generated_at=datetime.now(UTC),
        )

        assert content.id == content_id
        assert content.product_id == product_id
        assert content.title == "iPhone 13 Pro 128GB Negro"
        assert content.ml_price == 450000.0
        assert content.confidence_overall == 0.89
        assert content.version == 1

    def test_processing_status_schema_validation(self):
        """Test ProcessingStatusSchema validation."""
        processing_id = uuid4()
        product_id = uuid4()

        status_schema = ProcessingStatusSchema(
            processing_id=processing_id,
            product_id=product_id,
            status="processing",
            current_step="title_generation",
            progress_percentage=45.0,
            estimated_completion_seconds=15,
            estimated_remaining_seconds=8,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        assert status_schema.processing_id == processing_id
        assert status_schema.product_id == product_id
        assert status_schema.status == "processing"
        assert status_schema.progress_percentage == 45.0
        assert status_schema.estimated_completion_seconds == 15

    def test_content_validation_schema_validation(self):
        """Test ContentValidationSchema validation."""
        content_id = uuid4()

        validation = ContentValidationSchema(
            content_id=content_id,
            is_valid=True,
            validation_errors=[],
            validation_warnings=["Minor formatting issue"],
            is_compliant=True,
            compliance_issues=[],
            quality_score=0.89,
            meets_threshold=True,
            improvement_suggestions=["Add more details"],
            quality_indicators={
                "has_key_features": True,
                "appropriate_length": True,
                "ml_compliant": True,
            },
        )

        assert validation.content_id == content_id
        assert validation.is_valid is True
        assert validation.is_compliant is True
        assert validation.quality_score == 0.89
        assert validation.meets_threshold is True
        assert len(validation.improvement_suggestions) == 1

    def test_error_response_schema_validation(self):
        """Test ErrorResponseSchema validation."""
        error_response = ErrorResponseSchema(
            error_type="AI_SERVICE_ERROR",
            message="AI service temporarily unavailable",
            error_code="AI_503",
            details={"retry_after": 60},
            timestamp=datetime.now(UTC),
        )

        assert error_response.error_type == "AI_SERVICE_ERROR"
        assert error_response.message == "AI service temporarily unavailable"
        assert error_response.error_code == "AI_503"
        assert error_response.details["retry_after"] == 60
