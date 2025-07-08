"""
File storage service for product images using MinIO/S3.

This module provides file upload and management capabilities for product images.
"""

import asyncio
import functools
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import (  # type: ignore[import-untyped]
    ClientError,
    NoCredentialsError,
)
from PIL import Image

from infrastructure.config.logging import get_logger
from infrastructure.config.settings import Settings

logger = get_logger(__name__)


class FileStorageService:
    """Service for handling file uploads to MinIO/S3."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.bucket_name = settings.s3_bucket_name

        # Initialize S3 client
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

        # Bucket existence will be checked on first use
        self._bucket_checked = False

    async def _ensure_bucket_exists(self) -> None:
        """Ensure the S3 bucket exists."""
        try:
            # Run in executor to avoid blocking
            head_bucket_func = functools.partial(
                self.s3_client.head_bucket, Bucket=self.bucket_name
            )
            await asyncio.get_event_loop().run_in_executor(None, head_bucket_func)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Bucket doesn't exist, create it
                try:
                    create_bucket_func = functools.partial(
                        self.s3_client.create_bucket, Bucket=self.bucket_name
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        None, create_bucket_func
                    )
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error accessing S3 bucket: {e}")
                raise

    def _get_image_dimensions(self, file_content: bytes) -> tuple[int, int]:
        """Get image dimensions from file content."""
        try:
            from io import BytesIO

            image = Image.open(BytesIO(file_content))
            return image.size
        except Exception as e:
            logger.warning(f"Could not determine image dimensions: {e}")
            return (0, 0)

    def _get_file_format(self, filename: str, content_type: str | None = None) -> str:
        """Determine file format from filename or content type."""
        if content_type:
            # Extract format from content type (e.g., 'image/jpeg' -> 'jpeg')
            if content_type.startswith("image/"):
                format_part = content_type.split("/")[1].lower()
                # Normalize common variations
                if format_part == "jpeg":
                    return "jpg"
                return format_part

        # Fall back to file extension
        suffix = Path(filename).suffix.lower()
        if suffix in [".jpg", ".jpeg"]:
            return "jpg"
        elif suffix in [".png"]:
            return "png"
        elif suffix in [".webp"]:
            return "webp"
        else:
            return "jpg"  # Default fallback

    def _generate_s3_key(self, user_id: UUID, product_id: UUID, filename: str) -> str:
        """Generate S3 key for the file."""
        # Create a unique key: products/{user_id}/{product_id}/{timestamp}_{uuid4}_{filename}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        safe_filename = Path(filename).name  # Remove any path components

        return (
            f"products/{user_id}/{product_id}/{timestamp}_{unique_id}_{safe_filename}"
        )

    async def upload_product_image(
        self,
        user_id: UUID,
        product_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> dict:
        """
        Upload product image to S3 and return metadata.

        Returns:
            dict: Contains s3_key, s3_url, file_size_bytes, file_format,
                  resolution_width, resolution_height
        """
        try:
            # Ensure bucket exists on first use
            if not self._bucket_checked:
                await self._ensure_bucket_exists()
                self._bucket_checked = True
            # Generate S3 key
            s3_key = self._generate_s3_key(user_id, product_id, filename)

            # Get image dimensions
            width, height = self._get_image_dimensions(file_content)

            # Determine file format
            file_format = self._get_file_format(filename, content_type)

            # Prepare upload parameters
            upload_params = {
                "Bucket": self.bucket_name,
                "Key": s3_key,
                "Body": file_content,
                "ContentType": content_type or f"image/{file_format}",
                "ContentDisposition": f'inline; filename="{filename}"',
            }

            # Upload to S3
            put_object_func = functools.partial(
                self.s3_client.put_object, **upload_params
            )
            await asyncio.get_event_loop().run_in_executor(None, put_object_func)

            # Generate public URL
            s3_url = self._generate_public_url(s3_key)

            logger.info(f"Successfully uploaded image: {s3_key}")

            return {
                "s3_key": s3_key,
                "s3_url": s3_url,
                "file_size_bytes": len(file_content),
                "file_format": file_format,
                "resolution_width": width,
                "resolution_height": height,
            }

        except NoCredentialsError as e:
            logger.error("AWS credentials not found")
            raise ValueError("File storage service not properly configured") from e
        except ClientError as e:
            logger.error(f"S3 client error: {e}")
            raise ValueError(f"Failed to upload file: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise ValueError(f"File upload failed: {e}") from e

    def _generate_public_url(self, s3_key: str) -> str:
        """Generate public URL for the uploaded file."""
        if self.settings.s3_endpoint_url:
            # MinIO or custom S3 endpoint
            base_url = self.settings.s3_endpoint_url.rstrip("/")
            return f"{base_url}/{self.bucket_name}/{s3_key}"
        else:
            # AWS S3
            return f"https://{self.bucket_name}.s3.{self.settings.s3_region}.amazonaws.com/{s3_key}"

    async def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3."""
        try:
            delete_object_func = functools.partial(
                self.s3_client.delete_object, Bucket=self.bucket_name, Key=s3_key
            )
            await asyncio.get_event_loop().run_in_executor(None, delete_object_func)
            logger.info(f"Successfully deleted file: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {s3_key}: {e}")
            return False

    async def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            head_object_func = functools.partial(
                self.s3_client.head_object, Bucket=self.bucket_name, Key=s3_key
            )
            await asyncio.get_event_loop().run_in_executor(None, head_object_func)
            return True
        except ClientError:
            return False

    def validate_image_file(self, file_content: bytes, filename: str) -> dict:
        """
        Validate image file and return validation results.

        Returns:
            dict: Contains is_valid, error_message, file_info
        """
        try:
            # Check file size
            max_size = self.settings.product_max_image_size_mb * 1024 * 1024
            if len(file_content) > max_size:
                return {
                    "is_valid": False,
                    "error_message": f"File too large. Maximum size is {self.settings.product_max_image_size_mb}MB",
                    "file_info": None,
                }

            # Check if it's a valid image
            width, height = self._get_image_dimensions(file_content)
            if width == 0 or height == 0:
                return {
                    "is_valid": False,
                    "error_message": "Invalid image file or corrupted image",
                    "file_info": None,
                }

            # Check minimum resolution (from frontend validation rules)
            min_width, min_height = 800, 600
            if width < min_width or height < min_height:
                return {
                    "is_valid": False,
                    "error_message": f"Image resolution too small. Minimum is {min_width}x{min_height}",
                    "file_info": None,
                }

            # Check file format
            file_format = self._get_file_format(filename)
            allowed_formats = ["jpg", "jpeg", "png", "webp"]
            if file_format not in allowed_formats:
                return {
                    "is_valid": False,
                    "error_message": f"Invalid file format. Allowed formats: {', '.join(allowed_formats)}",
                    "file_info": None,
                }

            return {
                "is_valid": True,
                "error_message": None,
                "file_info": {
                    "file_size_bytes": len(file_content),
                    "file_format": file_format,
                    "resolution_width": width,
                    "resolution_height": height,
                },
            }

        except Exception as e:
            logger.error(f"Error validating image file: {e}")
            return {
                "is_valid": False,
                "error_message": f"Error validating image: {e}",
                "file_info": None,
            }
