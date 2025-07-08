"""
Unit tests for FileStorageService.

This module tests the file storage functionality including S3 operations,
validation, and presigned URL generation.
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from infrastructure.config.settings import Settings
from modules.product_management.infrastructure.services.file_storage_service import (
    FileStorageService,
)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.s3_bucket_name = "test-bucket"
    settings.s3_endpoint_url = "http://localhost:9000"
    settings.s3_access_key = "test-key"
    settings.s3_secret_key = "test-secret"
    settings.s3_region = "us-east-1"
    settings.product_max_image_size_mb = 10
    return settings


@pytest.fixture
def mock_s3_client():
    """Create mock S3 client."""
    client = Mock()
    client.head_bucket = Mock()
    client.create_bucket = Mock()
    client.put_object = Mock()
    client.delete_object = Mock()
    client.head_object = Mock()
    client.list_objects_v2 = Mock()
    client.copy_object = Mock()
    client.generate_presigned_url = Mock()
    client.generate_presigned_post = Mock()
    return client


@pytest.fixture
def file_storage_service(mock_settings, mock_s3_client):
    """Create FileStorageService with mocked dependencies."""
    with patch(
        "modules.product_management.infrastructure.services.file_storage_service.boto3.client"
    ) as mock_boto3:
        mock_boto3.return_value = mock_s3_client
        service = FileStorageService(mock_settings)
        service.s3_client = mock_s3_client
        return service


class TestFileStorageService:
    """Test cases for FileStorageService."""

    @pytest.mark.asyncio
    async def test_upload_product_image_success(
        self, file_storage_service, mock_s3_client
    ):
        """Test successful image upload."""
        user_id = uuid4()
        product_id = uuid4()
        file_content = b"fake image content"
        filename = "test.jpg"
        content_type = "image/jpeg"

        # Mock PIL.Image.open to return dimensions
        with patch(
            "modules.product_management.infrastructure.services.file_storage_service.Image.open"
        ) as mock_image:
            mock_image.return_value.size = (1920, 1080)

            # Mock asyncio.get_event_loop().run_in_executor
            with patch("asyncio.get_event_loop") as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(return_value=None)

                result = await file_storage_service.upload_product_image(
                    user_id=user_id,
                    product_id=product_id,
                    file_content=file_content,
                    filename=filename,
                    content_type=content_type,
                )

        assert "s3_key" in result
        assert "s3_url" in result
        assert result["file_size_bytes"] == len(file_content)
        assert result["file_format"] == "jpg"
        assert result["resolution_width"] == 1920
        assert result["resolution_height"] == 1080

    @pytest.mark.asyncio
    async def test_validate_image_file_valid(self, file_storage_service):
        """Test image validation for valid image."""
        file_content = b"fake image content"
        filename = "test.jpg"

        with patch(
            "modules.product_management.infrastructure.services.file_storage_service.Image.open"
        ) as mock_image:
            mock_image.return_value.size = (1920, 1080)

            result = file_storage_service.validate_image_file(file_content, filename)

        assert result["is_valid"] is True
        assert result["error_message"] is None
        assert result["file_info"]["file_size_bytes"] == len(file_content)
        assert result["file_info"]["file_format"] == "jpg"
        assert result["file_info"]["resolution_width"] == 1920
        assert result["file_info"]["resolution_height"] == 1080

    def test_validate_image_file_too_large(self, file_storage_service):
        """Test image validation for oversized file."""
        # Create a file larger than 10MB
        file_content = b"x" * (11 * 1024 * 1024)
        filename = "test.jpg"

        result = file_storage_service.validate_image_file(file_content, filename)

        assert result["is_valid"] is False
        assert "too large" in result["error_message"].lower()

    def test_validate_image_file_too_small_resolution(self, file_storage_service):
        """Test image validation for small resolution."""
        file_content = b"fake image content"
        filename = "test.jpg"

        with patch(
            "modules.product_management.infrastructure.services.file_storage_service.Image.open"
        ) as mock_image:
            mock_image.return_value.size = (400, 300)  # Below 800x600 minimum

            result = file_storage_service.validate_image_file(file_content, filename)

        assert result["is_valid"] is False
        assert "resolution too small" in result["error_message"].lower()

    def test_validate_image_file_invalid_format(self, file_storage_service):
        """Test image validation for invalid format."""
        file_content = b"fake image content"
        filename = "test.gif"  # Unsupported format

        with patch(
            "modules.product_management.infrastructure.services.file_storage_service.Image.open"
        ) as mock_image:
            mock_image.return_value.size = (1920, 1080)

            result = file_storage_service.validate_image_file(file_content, filename)

        assert result["is_valid"] is False
        assert "invalid file format" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_generate_presigned_url(self, file_storage_service, mock_s3_client):
        """Test presigned URL generation."""
        s3_key = "test/key.jpg"
        expected_url = "https://test-bucket.s3.amazonaws.com/test/key.jpg?signature=abc"

        mock_s3_client.generate_presigned_url.return_value = expected_url

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value=expected_url
            )

            result = await file_storage_service.generate_presigned_url(s3_key)

        assert result == expected_url

    @pytest.mark.asyncio
    async def test_generate_presigned_upload_url(
        self, file_storage_service, mock_s3_client
    ):
        """Test presigned upload URL generation."""
        s3_key = "test/key.jpg"
        expected_response = {
            "url": "https://test-bucket.s3.amazonaws.com/",
            "fields": {"key": s3_key, "policy": "encoded_policy"},
        }

        mock_s3_client.generate_presigned_post.return_value = expected_response

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value=expected_response
            )

            result = await file_storage_service.generate_presigned_upload_url(
                s3_key, content_type="image/jpeg"
            )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_delete_file_success(self, file_storage_service, mock_s3_client):
        """Test successful file deletion."""
        s3_key = "test/key.jpg"

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(return_value=None)

            result = await file_storage_service.delete_file(s3_key)

        assert result is True

    @pytest.mark.asyncio
    async def test_file_exists_true(self, file_storage_service, mock_s3_client):
        """Test file existence check when file exists."""
        s3_key = "test/key.jpg"

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value={"ContentLength": 1024}
            )

            result = await file_storage_service.file_exists(s3_key)

        assert result is True

    @pytest.mark.asyncio
    async def test_file_exists_false(self, file_storage_service, mock_s3_client):
        """Test file existence check when file doesn't exist."""
        s3_key = "test/nonexistent.jpg"

        from botocore.exceptions import ClientError

        client_error = ClientError({"Error": {"Code": "NoSuchKey"}}, "head_object")

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(side_effect=client_error)

            result = await file_storage_service.file_exists(s3_key)

        assert result is False

    @pytest.mark.asyncio
    async def test_list_files_by_prefix(self, file_storage_service, mock_s3_client):
        """Test listing files by prefix."""
        prefix = "products/user123/"
        mock_response = {
            "Contents": [
                {
                    "Key": "products/user123/image1.jpg",
                    "Size": 1024,
                    "LastModified": "2023-01-01T00:00:00Z",
                    "ETag": '"abc123"',
                },
                {
                    "Key": "products/user123/image2.jpg",
                    "Size": 2048,
                    "LastModified": "2023-01-02T00:00:00Z",
                    "ETag": '"def456"',
                },
            ]
        }

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value=mock_response
            )

            result = await file_storage_service.list_files_by_prefix(prefix)

        assert len(result) == 2
        assert result[0]["key"] == "products/user123/image1.jpg"
        assert result[0]["size"] == 1024
        assert result[1]["key"] == "products/user123/image2.jpg"
        assert result[1]["size"] == 2048

    @pytest.mark.asyncio
    async def test_get_file_metadata(self, file_storage_service, mock_s3_client):
        """Test getting file metadata."""
        s3_key = "test/key.jpg"
        mock_response = {
            "ContentLength": 1024,
            "LastModified": "2023-01-01T00:00:00Z",
            "ETag": '"abc123"',
            "ContentType": "image/jpeg",
            "Metadata": {"custom": "value"},
        }

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value=mock_response
            )

            result = await file_storage_service.get_file_metadata(s3_key)

        assert result["key"] == s3_key
        assert result["size"] == 1024
        assert result["content_type"] == "image/jpeg"
        assert result["metadata"] == {"custom": "value"}

    @pytest.mark.asyncio
    async def test_copy_file(self, file_storage_service, mock_s3_client):
        """Test file copying."""
        source_key = "source/key.jpg"
        destination_key = "destination/key.jpg"

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(return_value=None)

            result = await file_storage_service.copy_file(source_key, destination_key)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_bucket_usage(self, file_storage_service, mock_s3_client):
        """Test getting bucket usage statistics."""
        mock_response = {"Contents": [{"Size": 1024}, {"Size": 2048}, {"Size": 512}]}

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                return_value=mock_response
            )

            result = await file_storage_service.get_bucket_usage()

        assert result["bucket_name"] == "test-bucket"
        assert result["total_files"] == 3
        assert result["total_size_bytes"] == 3584  # 1024 + 2048 + 512
        assert result["total_size_mb"] == 3.5  # 3584 / 1024 / 1024

    def test_get_image_dimensions(self, file_storage_service):
        """Test image dimension extraction."""
        file_content = b"fake image content"

        with patch(
            "modules.product_management.infrastructure.services.file_storage_service.Image.open"
        ) as mock_image:
            mock_image.return_value.size = (1920, 1080)

            width, height = file_storage_service._get_image_dimensions(file_content)

        assert width == 1920
        assert height == 1080

    def test_get_file_format_from_content_type(self, file_storage_service):
        """Test file format detection from content type."""
        # Test JPEG
        format_result = file_storage_service._get_file_format("image.jpg", "image/jpeg")
        assert format_result == "jpg"

        # Test PNG
        format_result = file_storage_service._get_file_format("image.png", "image/png")
        assert format_result == "png"

        # Test WebP
        format_result = file_storage_service._get_file_format(
            "image.webp", "image/webp"
        )
        assert format_result == "webp"

    def test_get_file_format_from_filename(self, file_storage_service):
        """Test file format detection from filename."""
        # Test various extensions
        assert file_storage_service._get_file_format("image.jpg") == "jpg"
        assert file_storage_service._get_file_format("image.jpeg") == "jpg"
        assert file_storage_service._get_file_format("image.PNG") == "png"
        assert file_storage_service._get_file_format("image.webp") == "webp"
        assert (
            file_storage_service._get_file_format("image.unknown") == "jpg"
        )  # Default

    def test_generate_s3_key(self, file_storage_service):
        """Test S3 key generation."""
        user_id = uuid4()
        product_id = uuid4()
        filename = "test image.jpg"

        s3_key = file_storage_service._generate_s3_key(user_id, product_id, filename)

        assert s3_key.startswith(f"products/{user_id}/{product_id}/")
        assert s3_key.endswith("_test image.jpg")
        assert len(s3_key.split("/")) == 4  # products/user_id/product_id/filename

    def test_generate_public_url_minio(self, file_storage_service):
        """Test public URL generation for MinIO."""
        s3_key = "products/user123/product456/image.jpg"

        url = file_storage_service._generate_public_url(s3_key)

        expected = (
            "http://localhost:9000/test-bucket/products/user123/product456/image.jpg"
        )
        assert url == expected

    def test_generate_public_url_aws(self, file_storage_service):
        """Test public URL generation for AWS S3."""
        # Modify settings to simulate AWS S3
        file_storage_service.settings.s3_endpoint_url = None
        s3_key = "products/user123/product456/image.jpg"

        url = file_storage_service._generate_public_url(s3_key)

        expected = "https://test-bucket.s3.us-east-1.amazonaws.com/products/user123/product456/image.jpg"
        assert url == expected
