"""
File storage service for product images using MinIO/S3.

This module provides file upload and management capabilities for product images.
"""
# type: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType]

import asyncio
import functools
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID, uuid4

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import (  # type: ignore[import-untyped]
    ClientError,
    NoCredentialsError,
)

if TYPE_CHECKING:
    from botocore.client import BaseClient  # type: ignore[import-untyped]
from PIL import Image

from infrastructure.config.logging import get_logger
from infrastructure.config.settings import Settings

logger = get_logger(__name__)


class FileStorageService:
    """Service for handling file uploads to MinIO/S3."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.bucket_name: str = settings.s3_bucket_name

        # Initialize S3 client
        self.s3_client: BaseClient = boto3.client(  # type: ignore[reportUnknownMemberType]
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

        # Bucket existence will be checked on first use
        self._bucket_checked: bool = False

    async def _ensure_bucket_exists(self) -> None:
        """Ensure the S3 bucket exists."""
        try:
            # Run in executor to avoid blocking
            head_bucket_func = functools.partial(  # type: ignore[reportUnknownMemberType]
                self.s3_client.head_bucket,
                Bucket=self.bucket_name,  # type: ignore[reportUnknownMemberType]
            )
            await asyncio.get_event_loop().run_in_executor(None, head_bucket_func)  # type: ignore[reportUnknownArgumentType]
        except ClientError as e:
            error_code = cast("str", e.response["Error"]["Code"])
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
            return "unknown"  # Unknown format - will fail validation

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
    ) -> dict[str, Any]:
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

    async def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = "GET",
    ) -> str:
        """
        Generate a presigned URL for secure access to the file.

        Args:
            s3_key: The S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the presigned URL (GET, PUT, POST, etc.)

        Returns:
            str: Presigned URL for the file

        Raises:
            ValueError: If URL generation fails
        """
        try:
            # Generate presigned URL
            generate_url_func = functools.partial(
                self.s3_client.generate_presigned_url,
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
                HttpMethod=http_method,
            )

            presigned_url = await asyncio.get_event_loop().run_in_executor(
                None, generate_url_func
            )

            logger.info(
                f"Generated presigned URL for {s3_key}, expires in {expiration}s"
            )
            return presigned_url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            raise ValueError(f"Failed to generate presigned URL: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL for {s3_key}: {e}")
            raise ValueError(f"Presigned URL generation failed: {e}") from e

    async def generate_presigned_upload_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        content_type: str | None = None,
        max_content_length: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate a presigned URL for direct file upload.

        Args:
            s3_key: The S3 object key for the upload
            expiration: URL expiration time in seconds (default: 1 hour)
            content_type: Expected content type for the upload
            max_content_length: Maximum file size in bytes

        Returns:
            dict: Contains 'url' and 'fields' for the presigned POST

        Raises:
            ValueError: If URL generation fails
        """
        try:
            conditions: list[dict[str, Any] | list[Any]] = []
            if content_type:
                conditions.append({"Content-Type": content_type})
            if max_content_length:
                conditions.append(["content-length-range", 1, max_content_length])

            # Generate presigned POST URL
            generate_post_func = functools.partial(
                self.s3_client.generate_presigned_post,
                Bucket=self.bucket_name,
                Key=s3_key,
                ExpiresIn=expiration,
                Conditions=conditions if conditions else None,
            )

            presigned_post = await asyncio.get_event_loop().run_in_executor(
                None, generate_post_func
            )

            logger.info(
                f"Generated presigned upload URL for {s3_key}, expires in {expiration}s"
            )
            return presigned_post

        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL for {s3_key}: {e}")
            raise ValueError(f"Failed to generate presigned upload URL: {e}") from e
        except Exception as e:
            logger.error(
                f"Unexpected error generating presigned upload URL for {s3_key}: {e}"
            )
            raise ValueError(f"Presigned upload URL generation failed: {e}") from e

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

    def validate_image_file(self, file_content: bytes, filename: str) -> dict[str, Any]:
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

    async def list_files_by_prefix(self, prefix: str) -> list[dict[str, Any]]:
        """
        List files in the bucket with a specific prefix.

        Args:
            prefix: S3 key prefix to filter files

        Returns:
            list[dict]: List of file metadata
        """
        try:
            list_objects_func = functools.partial(
                self.s3_client.list_objects_v2,
                Bucket=self.bucket_name,
                Prefix=prefix,
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None, list_objects_func
            )

            files: list[dict[str, Any]] = []
            for obj in response.get("Contents", []):
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "etag": obj["ETag"].strip('"'),
                    }
                )

            logger.info(f"Found {len(files)} files with prefix {prefix}")
            return files

        except ClientError as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise ValueError(f"Failed to list files: {e}") from e

    async def get_file_metadata(self, s3_key: str) -> dict[str, Any] | None:
        """
        Get metadata for a specific file.

        Args:
            s3_key: S3 object key

        Returns:
            dict | None: File metadata or None if not found
        """
        try:
            head_object_func = functools.partial(
                self.s3_client.head_object,
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None, head_object_func
            )

            return {
                "key": s3_key,
                "size": response["ContentLength"],
                "last_modified": response["LastModified"].isoformat(),
                "etag": response["ETag"].strip('"'),
                "content_type": response.get("ContentType", ""),
                "metadata": response.get("Metadata", {}),
            }

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            logger.error(f"Failed to get metadata for {s3_key}: {e}")
            raise ValueError(f"Failed to get file metadata: {e}") from e

    async def copy_file(self, source_key: str, destination_key: str) -> bool:
        """
        Copy a file within the bucket.

        Args:
            source_key: Source S3 object key
            destination_key: Destination S3 object key

        Returns:
            bool: True if successful
        """
        try:
            copy_source = {"Bucket": self.bucket_name, "Key": source_key}
            copy_object_func = functools.partial(
                self.s3_client.copy_object,
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key,
            )

            await asyncio.get_event_loop().run_in_executor(None, copy_object_func)
            logger.info(f"Successfully copied {source_key} to {destination_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to copy {source_key} to {destination_key}: {e}")
            raise ValueError(f"Failed to copy file: {e}") from e

    async def get_bucket_usage(self) -> dict[str, Any]:
        """
        Get bucket usage statistics.

        Returns:
            dict: Bucket usage information
        """
        try:
            list_objects_func = functools.partial(
                self.s3_client.list_objects_v2,
                Bucket=self.bucket_name,
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None, list_objects_func
            )

            total_size = 0
            file_count = 0

            for obj in response.get("Contents", []):
                total_size += obj["Size"]
                file_count += 1

            return {
                "bucket_name": self.bucket_name,
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            }

        except ClientError as e:
            logger.error(f"Failed to get bucket usage: {e}")
            raise ValueError(f"Failed to get bucket usage: {e}") from e
