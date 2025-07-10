"""
File storage protocol for hexagonal architecture.

This module defines the protocol interface for file storage operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Any, Protocol
from uuid import UUID


class FileStorageProtocol(Protocol):
    """Protocol for file storage operations."""

    def validate_image_file(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Validate an image file.

        Args:
            file_content: The file content bytes
            filename: The original filename

        Returns:
            Dict with validation result containing is_valid boolean and error_message if invalid
        """
        ...

    async def upload_product_image(
        self,
        user_id: UUID,
        product_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Upload a product image to storage.

        Args:
            user_id: ID of the user uploading the image
            product_id: ID of the product the image belongs to
            file_content: The image file content
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            Dict with upload metadata including s3_key, s3_url, file_size_bytes, etc.
        """
        ...
