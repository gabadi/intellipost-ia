"""
API integration tests for product management endpoints.

This module tests the FastAPI endpoints with real request/response cycles.
"""

from io import BytesIO
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient

from modules.product_management.api.routers.product_router import create_product_router
from modules.user_management.domain.entities.user import User


@pytest.fixture
def mock_create_product_use_case():
    """Mock CreateProductUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def mock_get_products_use_case():
    """Mock GetProductsUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def mock_current_user():
    """Mock current user."""
    from datetime import UTC, datetime

    return User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password",
        created_at=datetime.now(UTC),
        first_name="Test",
        last_name="User",
        is_active=True,
    )


@pytest.fixture
def test_app(
    mock_create_product_use_case,
    mock_get_products_use_case,
    mock_current_user,
):
    """Create test FastAPI app with mocked dependencies."""
    app = FastAPI()

    def create_use_case_factory():
        return mock_create_product_use_case

    def get_use_case_factory():
        return mock_get_products_use_case

    def current_user_provider():
        return mock_current_user

    router = create_product_router(
        create_product_use_case_factory=create_use_case_factory,
        get_products_use_case_factory=get_use_case_factory,
        current_user_provider=current_user_provider,
    )

    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestProductAPI:
    """Test cases for Product API endpoints."""

    def test_create_product_success(
        self,
        client,
        mock_create_product_use_case,
        mock_current_user,
        sample_image_bytes,
    ):
        """Test successful product creation via API."""
        # Setup mock response
        product_id = uuid4()
        mock_create_product_use_case.execute.return_value = {
            "product_id": str(product_id),
            "user_id": str(mock_current_user.id),
            "status": "uploading",
            "prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB",
            "images_uploaded": 1,
            "upload_results": [
                {
                    "filename": "test.jpg",
                    "image_id": str(uuid4()),
                    "s3_url": "https://bucket.s3.amazonaws.com/test.jpg",
                    "is_primary": True,
                }
            ],
            "upload_errors": [],
            "created_at": "2023-01-01T00:00:00Z",
        }

        # Prepare request data
        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {"prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB"}

        # Make request
        response = client.post("/products/", files=files, data=data)

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()
        assert response_data["id"] == str(product_id)
        assert response_data["status"] == "uploading"
        assert (
            response_data["prompt_text"]
            == "iPhone 13 Pro usado, excelente estado, 128GB"
        )
        assert response_data["images_uploaded"] == 1

        # Verify use case was called
        mock_create_product_use_case.execute.assert_called_once()
        call_args = mock_create_product_use_case.execute.call_args
        assert call_args[1]["user_id"] == mock_current_user.id
        assert (
            call_args[1]["prompt_text"]
            == "iPhone 13 Pro usado, excelente estado, 128GB"
        )
        assert len(call_args[1]["images"]) == 1

    def test_create_product_validation_error_short_prompt(
        self, client, sample_image_bytes
    ):
        """Test product creation with too short prompt text."""
        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {
            "prompt_text": "short"  # Less than 10 characters
        }

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_validation_error_long_prompt(
        self, client, sample_image_bytes
    ):
        """Test product creation with too long prompt text."""
        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {
            "prompt_text": "x" * 501  # More than 500 characters
        }

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_no_images(self, client):
        """Test product creation without images."""
        data = {"prompt_text": "Valid prompt text for testing"}

        response = client.post("/products/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"]["error_code"] == "NO_IMAGES"

    def test_create_product_empty_prompt(self, client, sample_image_bytes):
        """Test product creation with empty prompt text."""
        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {
            "prompt_text": "   "  # Only whitespace
        }

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"]["error_code"] == "INVALID_PROMPT"

    def test_create_product_too_many_images(self, client, sample_image_bytes):
        """Test product creation with too many images."""
        # Create 9 image files (more than 8 allowed)
        files = []
        for i in range(9):
            files.append(
                ("images", (f"test{i}.jpg", BytesIO(sample_image_bytes), "image/jpeg"))
            )

        data = {"prompt_text": "Valid prompt text for testing"}

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"]["error_code"] == "TOO_MANY_IMAGES"

    def test_create_product_invalid_file_type(self, client):
        """Test product creation with invalid file type."""
        files = [("images", ("test.txt", BytesIO(b"not an image"), "text/plain"))]
        data = {"prompt_text": "Valid prompt text for testing"}

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"]["error_code"] == "INVALID_FILE_TYPE"

    def test_create_product_use_case_error(
        self,
        client,
        mock_create_product_use_case,
        sample_image_bytes,
    ):
        """Test product creation with use case error."""
        # Setup mock to raise exception
        mock_create_product_use_case.execute.side_effect = ValueError(
            "Failed to upload any images"
        )

        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {"prompt_text": "Valid prompt text for testing"}

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"]["error_code"] == "VALIDATION_ERROR"

    def test_get_products_success(
        self,
        client,
        mock_get_products_use_case,
        mock_current_user,
    ):
        """Test successful product list retrieval."""
        # Setup mock response
        product_id = uuid4()
        image_id = uuid4()

        mock_get_products_use_case.execute.return_value = [
            {
                "id": str(product_id),
                "user_id": str(mock_current_user.id),
                "status": "ready",
                "confidence": "0.85",
                "prompt_text": "Test product description",
                "title": "Test Product",
                "description": "Product description",
                "price": 99.99,
                "category_id": "TEST123",
                "ai_title": "AI Title",
                "ai_description": "AI Description",
                "ai_tags": ["tag1", "tag2"],
                "ml_listing_id": "ML123456",
                "ml_category_id": "MLCAT123",
                "processing_started_at": "2023-01-01T00:00:00Z",
                "processing_completed_at": "2023-01-01T00:01:00Z",
                "processing_error": None,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:01:00Z",
                "published_at": None,
                "images": [
                    {
                        "id": str(image_id),
                        "product_id": str(product_id),
                        "original_filename": "test.jpg",
                        "s3_url": "https://bucket.s3.amazonaws.com/test.jpg",
                        "original_s3_url": "https://bucket.s3.amazonaws.com/test.jpg",
                        "processed_s3_url": None,
                        "file_size_bytes": 1024,
                        "file_format": "jpg",
                        "resolution_width": 1920,
                        "resolution_height": 1080,
                        "is_primary": True,
                        "processing_metadata": {},
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z",
                        "uploaded_at": "2023-01-01T00:00:00Z",
                        "processed_at": None,
                    }
                ],
            }
        ]

        # Make request
        response = client.get("/products/")

        # Verify response
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["total"] == 1
        assert len(response_data["products"]) == 1

        product = response_data["products"][0]
        assert product["id"] == str(product_id)
        assert product["prompt_text"] == "Test product description"
        assert product["status"] == "ready"
        assert len(product["images"]) == 1

        image = product["images"][0]
        assert image["id"] == str(image_id)
        assert image["is_primary"] is True

        # Verify use case was called
        mock_get_products_use_case.execute.assert_called_once_with(
            user_id=mock_current_user.id
        )

    def test_get_products_empty_list(
        self,
        client,
        mock_get_products_use_case,
    ):
        """Test product list retrieval with empty result."""
        mock_get_products_use_case.execute.return_value = []

        response = client.get("/products/")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["total"] == 0
        assert response_data["products"] == []

    def test_get_product_by_id_success(
        self,
        client,
        mock_get_products_use_case,
        mock_current_user,
    ):
        """Test successful individual product retrieval."""
        product_id = uuid4()

        # Setup mock response
        mock_get_products_use_case.execute.return_value = [
            {
                "id": str(product_id),
                "user_id": str(mock_current_user.id),
                "status": "published",
                "confidence": "0.90",
                "prompt_text": "Specific product description",
                "title": "Specific Product",
                "description": None,
                "price": None,
                "category_id": None,
                "ai_title": None,
                "ai_description": None,
                "ai_tags": None,
                "ml_listing_id": None,
                "ml_category_id": None,
                "processing_started_at": None,
                "processing_completed_at": None,
                "processing_error": None,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "published_at": "2023-01-01T00:02:00Z",
                "images": [],
            }
        ]

        response = client.get(f"/products/{product_id}")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["id"] == str(product_id)
        assert response_data["title"] == "Specific Product"
        assert response_data["status"] == "published"

    def test_get_product_by_id_not_found(
        self,
        client,
        mock_get_products_use_case,
    ):
        """Test individual product retrieval when product not found."""
        product_id = uuid4()

        # Setup mock to return empty list (product not found)
        mock_get_products_use_case.execute.return_value = []

        response = client.get(f"/products/{product_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        response_data = response.json()
        assert response_data["detail"]["error_code"] == "PRODUCT_NOT_FOUND"

    def test_get_products_use_case_error(
        self,
        client,
        mock_get_products_use_case,
    ):
        """Test product list retrieval with use case error."""
        mock_get_products_use_case.execute.side_effect = Exception(
            "Database connection failed"
        )

        response = client.get("/products/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        response_data = response.json()
        assert response_data["detail"]["error_code"] == "INTERNAL_ERROR"

    def test_create_product_with_upload_warnings(
        self,
        client,
        mock_create_product_use_case,
        mock_current_user,
        sample_image_bytes,
    ):
        """Test product creation with partial upload success."""
        product_id = uuid4()

        # Setup mock response with upload errors
        mock_create_product_use_case.execute.return_value = {
            "product_id": str(product_id),
            "user_id": str(mock_current_user.id),
            "status": "uploading",
            "prompt_text": "Product with some upload issues",
            "images_uploaded": 1,
            "upload_results": [
                {
                    "filename": "good.jpg",
                    "image_id": str(uuid4()),
                    "s3_url": "https://bucket.s3.amazonaws.com/good.jpg",
                    "is_primary": True,
                }
            ],
            "upload_errors": [
                {
                    "filename": "bad.jpg",
                    "error_message": "Invalid image format",
                }
            ],
            "created_at": "2023-01-01T00:00:00Z",
        }

        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {"prompt_text": "Product with some upload issues"}

        response = client.post("/products/", files=files, data=data)

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()
        assert response_data["images_uploaded"] == 1
        assert "(1 errors)" in response_data["message"]

    def test_api_response_schemas(
        self,
        client,
        mock_create_product_use_case,
        mock_get_products_use_case,
        mock_current_user,
        sample_image_bytes,
    ):
        """Test that API responses match expected schemas."""
        # Test CreateProductResponse schema
        product_id = uuid4()
        mock_create_product_use_case.execute.return_value = {
            "product_id": str(product_id),
            "user_id": str(mock_current_user.id),
            "status": "uploading",
            "prompt_text": "Schema validation test",
            "images_uploaded": 1,
            "upload_results": [],
            "upload_errors": [],
            "created_at": "2023-01-01T00:00:00Z",
        }

        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        data = {"prompt_text": "Schema validation test"}

        create_response = client.post("/products/", files=files, data=data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Validate CreateProductResponse fields
        create_data = create_response.json()
        required_fields = {
            "id",
            "user_id",
            "status",
            "prompt_text",
            "images_uploaded",
            "created_at",
            "message",
        }
        assert set(create_data.keys()) == required_fields

        # Test ProductListResponse schema
        mock_get_products_use_case.execute.return_value = []

        list_response = client.get("/products/")
        assert list_response.status_code == status.HTTP_200_OK

        # Validate ProductListResponse fields
        list_data = list_response.json()
        required_fields = {"products", "total", "page", "page_size"}
        assert set(list_data.keys()) == required_fields
        assert isinstance(list_data["products"], list)
        assert isinstance(list_data["total"], int)


class TestProductAPIErrorHandling:
    """Test error handling in Product API."""

    def test_missing_prompt_text(self, client, sample_image_bytes):
        """Test API with missing prompt_text field."""
        files = [("images", ("test.jpg", BytesIO(sample_image_bytes), "image/jpeg"))]
        # No prompt_text in data

        response = client.post("/products/", files=files)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_product_id_format(self, client):
        """Test API with invalid UUID format for product ID."""
        response = client.get("/products/invalid-uuid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_content_type_validation(self, client):
        """Test API content type validation."""
        # Test without multipart/form-data
        response = client.post(
            "/products/",
            json={"prompt_text": "This should be form data"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProductAPIIntegration:
    """Integration tests that test the full request/response cycle."""

    def test_full_product_creation_flow(
        self,
        client,
        mock_create_product_use_case,
        mock_get_products_use_case,
        mock_current_user,
        sample_image_bytes,
    ):
        """Test complete flow: create product then retrieve it."""
        product_id = uuid4()
        image_id = uuid4()

        # Setup create product mock
        mock_create_product_use_case.execute.return_value = {
            "product_id": str(product_id),
            "user_id": str(mock_current_user.id),
            "status": "uploading",
            "prompt_text": "Integration test product",
            "images_uploaded": 1,
            "upload_results": [
                {
                    "filename": "integration.jpg",
                    "image_id": str(image_id),
                    "s3_url": "https://bucket.s3.amazonaws.com/integration.jpg",
                    "is_primary": True,
                }
            ],
            "upload_errors": [],
            "created_at": "2023-01-01T00:00:00Z",
        }

        # Step 1: Create product
        files = [
            ("images", ("integration.jpg", BytesIO(sample_image_bytes), "image/jpeg"))
        ]
        data = {"prompt_text": "Integration test product"}

        create_response = client.post("/products/", files=files, data=data)
        assert create_response.status_code == status.HTTP_201_CREATED

        created_product = create_response.json()
        assert created_product["id"] == str(product_id)

        # Setup get products mock
        mock_get_products_use_case.execute.return_value = [
            {
                "id": str(product_id),
                "user_id": str(mock_current_user.id),
                "status": "ready",  # Status changed after processing
                "confidence": "0.88",
                "prompt_text": "Integration test product",
                "title": "Generated Title",
                "description": "Generated Description",
                "price": None,
                "category_id": None,
                "ai_title": "Generated Title",
                "ai_description": "Generated Description",
                "ai_tags": ["test", "integration"],
                "ml_listing_id": None,
                "ml_category_id": None,
                "processing_started_at": "2023-01-01T00:00:00Z",
                "processing_completed_at": "2023-01-01T00:01:00Z",
                "processing_error": None,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:01:00Z",
                "published_at": None,
                "images": [
                    {
                        "id": str(image_id),
                        "product_id": str(product_id),
                        "original_filename": "integration.jpg",
                        "s3_url": "https://bucket.s3.amazonaws.com/integration.jpg",
                        "original_s3_url": "https://bucket.s3.amazonaws.com/integration.jpg",
                        "processed_s3_url": "https://bucket.s3.amazonaws.com/processed/integration.jpg",
                        "file_size_bytes": len(sample_image_bytes),
                        "file_format": "jpg",
                        "resolution_width": 1920,
                        "resolution_height": 1080,
                        "is_primary": True,
                        "processing_metadata": {"ai_processed": True},
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:01:00Z",
                        "uploaded_at": "2023-01-01T00:00:00Z",
                        "processed_at": "2023-01-01T00:01:00Z",
                    }
                ],
            }
        ]

        # Step 2: Retrieve product
        get_response = client.get("/products/")
        assert get_response.status_code == status.HTTP_200_OK

        products_data = get_response.json()
        assert products_data["total"] == 1

        retrieved_product = products_data["products"][0]
        assert retrieved_product["id"] == str(product_id)
        assert retrieved_product["status"] == "ready"
        assert retrieved_product["ai_title"] == "Generated Title"
        assert len(retrieved_product["images"]) == 1

        # Step 3: Get specific product
        specific_response = client.get(f"/products/{product_id}")
        assert specific_response.status_code == status.HTTP_200_OK

        specific_product = specific_response.json()
        assert specific_product["id"] == str(product_id)
        assert specific_product["prompt_text"] == "Integration test product"
