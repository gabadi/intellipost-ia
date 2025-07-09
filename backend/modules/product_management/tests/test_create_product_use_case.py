"""
Unit tests for CreateProductUseCase.

This module tests the business logic for creating products with images.
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import UploadFile

from modules.product_management.application.use_cases.create_product import (
    CreateProductUseCase,
    GetProductsUseCase,
)
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_status import ProductStatus

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


@pytest.fixture
def mock_product_repository():
    """Create mock product repository."""
    repository = Mock()
    repository.create = AsyncMock()
    repository.delete = AsyncMock()
    repository.create_product_image = AsyncMock()
    repository.get_by_user_id = AsyncMock()
    repository.get_product_images = AsyncMock()
    return repository


@pytest.fixture
def mock_file_storage_service():
    """Create mock file storage service."""
    service = Mock()
    service.validate_image_file = Mock()
    service.upload_product_image = AsyncMock()
    return service


@pytest.fixture
def create_product_use_case(mock_product_repository, mock_file_storage_service):
    """Create CreateProductUseCase with mocked dependencies."""
    return CreateProductUseCase(mock_product_repository, mock_file_storage_service)


@pytest.fixture
def get_products_use_case(mock_product_repository):
    """Create GetProductsUseCase with mocked dependencies."""
    return GetProductsUseCase(mock_product_repository)


@pytest.fixture
def mock_upload_file():
    """Create mock UploadFile."""
    file_content = b"fake image content"
    upload_file = Mock(spec=UploadFile)
    upload_file.filename = "test.jpg"
    upload_file.content_type = "image/jpeg"
    upload_file.read = AsyncMock(return_value=file_content)
    return upload_file


class TestCreateProductUseCase:
    """Test cases for CreateProductUseCase."""

    @pytest.mark.asyncio
    async def test_create_product_success(
        self,
        create_product_use_case,
        mock_product_repository,
        mock_file_storage_service,
        mock_upload_file,
    ):
        """Test successful product creation with images."""
        user_id = uuid4()
        prompt_text = "iPhone 13 Pro usado, excelente estado, 128GB"

        # Setup mocks
        created_product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text,
        )
        mock_product_repository.create.return_value = created_product

        mock_file_storage_service.validate_image_file.return_value = {
            "is_valid": True,
            "error_message": None,
            "file_info": {
                "file_size_bytes": 1024,
                "file_format": "jpg",
                "resolution_width": 1920,
                "resolution_height": 1080,
            },
        }

        mock_file_storage_service.upload_product_image.return_value = {
            "s3_key": "products/user/product/test.jpg",
            "s3_url": "https://bucket.s3.amazonaws.com/products/user/product/test.jpg",
            "file_size_bytes": 1024,
            "file_format": "jpg",
            "resolution_width": 1920,
            "resolution_height": 1080,
        }

        mock_image_record = {
            "id": uuid4(),
            "product_id": uuid4(),
            "original_filename": "test.jpg",
            "s3_key": "products/user/product/test.jpg",
            "s3_url": "https://bucket.s3.amazonaws.com/products/user/product/test.jpg",
            "file_size_bytes": 1024,
            "file_format": "jpg",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "is_primary": True,
        }
        mock_product_repository.create_product_image.return_value = mock_image_record

        # Execute use case
        result = await create_product_use_case.execute(
            user_id=user_id,
            prompt_text=prompt_text,
            images=[mock_upload_file],
        )

        # Verify results
        assert result["product_id"] == str(created_product.id)
        assert result["user_id"] == str(user_id)
        assert result["status"] == "uploading"
        assert result["prompt_text"] == prompt_text
        assert result["images_uploaded"] == 1
        assert len(result["upload_results"]) == 1
        assert len(result["upload_errors"]) == 0

        # Verify repository calls
        mock_product_repository.create.assert_called_once()
        mock_product_repository.create_product_image.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_empty_prompt_text(self, create_product_use_case):
        """Test product creation with empty prompt text fails."""
        user_id = uuid4()

        with pytest.raises(ValueError, match="Product description cannot be empty"):
            await create_product_use_case.execute(
                user_id=user_id,
                prompt_text="   ",  # Empty/whitespace only
                images=[Mock()],
            )

    @pytest.mark.asyncio
    async def test_create_product_no_images(self, create_product_use_case):
        """Test product creation without images fails."""
        user_id = uuid4()
        prompt_text = "Valid prompt text"

        with pytest.raises(ValueError, match="At least one image is required"):
            await create_product_use_case.execute(
                user_id=user_id,
                prompt_text=prompt_text,
                images=[],
            )

    @pytest.mark.asyncio
    async def test_create_product_too_many_images(self, create_product_use_case):
        """Test product creation with too many images fails."""
        user_id = uuid4()
        prompt_text = "Valid prompt text"
        images = [Mock() for _ in range(9)]  # More than 8 allowed

        with pytest.raises(ValueError, match="Maximum 8 images allowed"):
            await create_product_use_case.execute(
                user_id=user_id,
                prompt_text=prompt_text,
                images=images,
            )

    @pytest.mark.asyncio
    async def test_create_product_with_invalid_image(
        self,
        create_product_use_case,
        mock_product_repository,
        mock_file_storage_service,
        mock_upload_file,
    ):
        """Test product creation with invalid image."""
        user_id = uuid4()
        prompt_text = "Valid prompt text"

        # Setup mocks
        created_product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text,
        )
        mock_product_repository.create.return_value = created_product

        # Mock invalid image validation
        mock_file_storage_service.validate_image_file.return_value = {
            "is_valid": False,
            "error_message": "Invalid image format",
            "file_info": None,
        }

        # Execute use case
        with pytest.raises(ValueError, match="Failed to upload any images"):
            await create_product_use_case.execute(
                user_id=user_id,
                prompt_text=prompt_text,
                images=[mock_upload_file],
            )

        # Verify product was cleaned up
        mock_product_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_partial_upload_success(
        self,
        create_product_use_case,
        mock_product_repository,
        mock_file_storage_service,
    ):
        """Test product creation with some images failing to upload."""
        user_id = uuid4()
        prompt_text = "Valid prompt text"

        # Create multiple upload files
        valid_file = Mock(spec=UploadFile)
        valid_file.filename = "valid.jpg"
        valid_file.content_type = "image/jpeg"
        valid_file.read = AsyncMock(return_value=b"valid content")

        invalid_file = Mock(spec=UploadFile)
        invalid_file.filename = "invalid.gif"
        invalid_file.content_type = "image/gif"
        invalid_file.read = AsyncMock(return_value=b"invalid content")

        # Setup mocks
        created_product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text,
        )
        mock_product_repository.create.return_value = created_product

        def validate_side_effect(_content, filename):
            if filename == "valid.jpg":
                return {
                    "is_valid": True,
                    "error_message": None,
                    "file_info": {"file_size_bytes": 1024, "file_format": "jpg"},
                }
            else:
                return {
                    "is_valid": False,
                    "error_message": "Invalid format",
                    "file_info": None,
                }

        mock_file_storage_service.validate_image_file.side_effect = validate_side_effect
        mock_file_storage_service.upload_product_image.return_value = {
            "s3_key": "test_key",
            "s3_url": "test_url",
            "file_size_bytes": 1024,
            "file_format": "jpg",
            "resolution_width": 1920,
            "resolution_height": 1080,
        }

        mock_image_record = {
            "id": uuid4(),
            "product_id": uuid4(),
            "original_filename": "valid.jpg",
            "s3_key": "test_key",
            "s3_url": "test_url",
            "file_size_bytes": 1024,
            "file_format": "jpg",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "is_primary": True,
        }
        mock_product_repository.create_product_image.return_value = mock_image_record

        # Execute use case
        result = await create_product_use_case.execute(
            user_id=user_id,
            prompt_text=prompt_text,
            images=[valid_file, invalid_file],
        )

        # Verify results
        assert result["images_uploaded"] == 1
        assert len(result["upload_results"]) == 1
        assert len(result["upload_errors"]) == 1
        assert result["upload_errors"][0]["filename"] == "invalid.gif"

    @pytest.mark.asyncio
    async def test_create_product_upload_exception(
        self,
        create_product_use_case,
        mock_product_repository,
        mock_file_storage_service,
        mock_upload_file,
    ):
        """Test product creation handles upload exceptions."""
        user_id = uuid4()
        prompt_text = "Valid prompt text"

        # Setup mocks
        created_product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text,
        )
        mock_product_repository.create.return_value = created_product

        mock_file_storage_service.validate_image_file.return_value = {
            "is_valid": True,
            "error_message": None,
            "file_info": {"file_size_bytes": 1024, "file_format": "jpg"},
        }

        # Mock upload failure
        mock_file_storage_service.upload_product_image.side_effect = Exception(
            "S3 connection failed"
        )

        # Execute use case - should fail and clean up
        with pytest.raises(ValueError, match="Failed to upload any images"):
            await create_product_use_case.execute(
                user_id=user_id,
                prompt_text=prompt_text,
                images=[mock_upload_file],
            )

        # Verify cleanup
        mock_product_repository.delete.assert_called_once()


class TestGetProductsUseCase:
    """Test cases for GetProductsUseCase."""

    @pytest.mark.asyncio
    async def test_get_products_success(
        self,
        get_products_use_case,
        mock_product_repository,
    ):
        """Test successful product retrieval."""
        user_id = uuid4()

        # Setup mock products
        products = [
            Product(
                id=uuid4(),
                user_id=user_id,
                status=ProductStatus.READY,
                prompt_text="Product 1 description",
                title="Product 1",
            ),
            Product(
                id=uuid4(),
                user_id=user_id,
                status=ProductStatus.PUBLISHED,
                prompt_text="Product 2 description",
                title="Product 2",
            ),
        ]

        mock_product_repository.get_by_user_id.return_value = products
        mock_product_repository.get_product_images.return_value = []

        # Execute use case
        result = await get_products_use_case.execute(user_id)

        # Verify results
        assert len(result) == 2
        assert result[0]["id"] == str(products[0].id)
        assert result[0]["title"] == "Product 1"
        assert result[0]["prompt_text"] == "Product 1 description"
        assert result[1]["id"] == str(products[1].id)
        assert result[1]["title"] == "Product 2"

        # Verify repository calls
        mock_product_repository.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_products_with_images(
        self,
        get_products_use_case,
        mock_product_repository,
    ):
        """Test product retrieval includes images."""
        user_id = uuid4()
        product_id = uuid4()

        # Setup mock product
        product = Product(
            id=product_id,
            user_id=user_id,
            status=ProductStatus.READY,
            prompt_text="Product with images",
            title="Product with Images",
        )

        # Setup mock images
        mock_image = Mock()
        mock_image.to_dict.return_value = {
            "id": str(uuid4()),
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

        mock_product_repository.get_by_user_id.return_value = [product]
        mock_product_repository.get_product_images.return_value = [mock_image]

        # Execute use case
        result = await get_products_use_case.execute(user_id)

        # Verify results
        assert len(result) == 1
        assert len(result[0]["images"]) == 1
        assert result[0]["images"][0]["original_filename"] == "test.jpg"
        assert result[0]["images"][0]["is_primary"] is True

    @pytest.mark.asyncio
    async def test_get_products_empty_result(
        self,
        get_products_use_case,
        mock_product_repository,
    ):
        """Test product retrieval with no products."""
        user_id = uuid4()

        mock_product_repository.get_by_user_id.return_value = []

        # Execute use case
        result = await get_products_use_case.execute(user_id)

        # Verify empty result
        assert result == []
        mock_product_repository.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_products_includes_all_fields(
        self,
        get_products_use_case,
        mock_product_repository,
    ):
        """Test that all product fields are included in response."""
        from datetime import UTC, datetime

        from modules.product_management.domain.entities.confidence_score import (
            ConfidenceScore,
        )

        user_id = uuid4()
        created_at = datetime.now(UTC)

        # Setup complete product
        product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.PUBLISHED,
            prompt_text="Complete product description",
            confidence=ConfidenceScore(0.85),
            title="Complete Product",
            description="Full description",
            price=99.99,
            category_id="TEST123",
            ai_title="AI Generated Title",
            ai_description="AI Generated Description",
            ai_tags=["tag1", "tag2"],
            ml_listing_id="ML123456",
            ml_category_id="MLCAT123",
            processing_started_at=created_at,
            processing_completed_at=created_at,
            created_at=created_at,
            updated_at=created_at,
            published_at=created_at,
        )

        mock_product_repository.get_by_user_id.return_value = [product]
        mock_product_repository.get_product_images.return_value = []

        # Execute use case
        result = await get_products_use_case.execute(user_id)

        # Verify all fields are present
        product_data = result[0]
        assert product_data["prompt_text"] == "Complete product description"
        assert product_data["confidence"] == "0.85"
        assert product_data["title"] == "Complete Product"
        assert product_data["description"] == "Full description"
        assert product_data["price"] == 99.99
        assert product_data["category_id"] == "TEST123"
        assert product_data["ai_title"] == "AI Generated Title"
        assert product_data["ai_description"] == "AI Generated Description"
        assert product_data["ai_tags"] == ["tag1", "tag2"]
        assert product_data["ml_listing_id"] == "ML123456"
        assert product_data["ml_category_id"] == "MLCAT123"
        assert product_data["processing_started_at"] is not None
        assert product_data["processing_completed_at"] is not None
        assert product_data["created_at"] is not None
        assert product_data["updated_at"] is not None
        assert product_data["published_at"] is not None
