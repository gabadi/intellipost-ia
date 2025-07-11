"""
ProductImage domain entity for product management.

This module contains the ProductImage domain entity that represents
a product image with all business rules and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from modules.product_management.domain.exceptions import InvalidProductImageError
from modules.product_management.domain.value_objects.product_image_metadata import (
    ProductImageMetadata,
)
from modules.product_management.domain.value_objects.product_image_resolution import (
    ProductImageResolution,
)


@dataclass
class ProductImage:
    """
    Domain entity representing a product image.

    Encapsulates all business rules and validation for product images,
    including file management, processing state, and metadata.
    """

    # Core identity
    id: UUID
    product_id: UUID

    # File information
    original_filename: str
    s3_key: str
    s3_url: str
    original_s3_url: str
    processed_s3_url: str | None
    file_size_bytes: int
    file_format: str
    resolution: ProductImageResolution
    is_primary: bool

    # Processing metadata
    metadata: ProductImageMetadata

    # Timestamps
    created_at: datetime
    updated_at: datetime
    uploaded_at: datetime
    processed_at: datetime | None

    # Business rule constants
    ALLOWED_FORMATS = {"jpg", "jpeg", "png", "webp", "avif"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_FILE_SIZE = 1024  # 1KB
    MAX_FILENAME_LENGTH = 255

    def __post_init__(self) -> None:
        """Validate the product image after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate the product image according to business rules.

        Raises:
            InvalidProductImageError: If validation fails.
        """
        # Validate file format
        if self.file_format.lower() not in self.ALLOWED_FORMATS:
            raise InvalidProductImageError(
                f"Unsupported file format: {self.file_format}. "
                f"Allowed formats: {', '.join(self.ALLOWED_FORMATS)}",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="file_format",
                field_value=self.file_format,
            )

        # Validate file size
        if self.file_size_bytes < self.MIN_FILE_SIZE:
            raise InvalidProductImageError(
                f"File size {self.file_size_bytes} bytes is below minimum {self.MIN_FILE_SIZE} bytes",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="file_size_bytes",
                field_value=str(self.file_size_bytes),
            )

        if self.file_size_bytes > self.MAX_FILE_SIZE:
            raise InvalidProductImageError(
                f"File size {self.file_size_bytes} bytes exceeds maximum {self.MAX_FILE_SIZE} bytes",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="file_size_bytes",
                field_value=str(self.file_size_bytes),
            )

        # Validate filename
        if not self.original_filename:
            raise InvalidProductImageError(
                "Original filename cannot be empty",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="original_filename",
                field_value=self.original_filename,
            )

        if len(self.original_filename) > self.MAX_FILENAME_LENGTH:
            raise InvalidProductImageError(
                f"Filename length {len(self.original_filename)} exceeds maximum {self.MAX_FILENAME_LENGTH}",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="original_filename",
                field_value=self.original_filename,
            )

        # Validate S3 URLs
        if not self.s3_key:
            raise InvalidProductImageError(
                "S3 key cannot be empty",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="s3_key",
                field_value=self.s3_key,
            )

        if not self.s3_url:
            raise InvalidProductImageError(
                "S3 URL cannot be empty",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="s3_url",
                field_value=self.s3_url,
            )

        if not self.original_s3_url:
            raise InvalidProductImageError(
                "Original S3 URL cannot be empty",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="original_s3_url",
                field_value=self.original_s3_url,
            )

        # Validate timestamps
        if self.created_at > self.updated_at:
            raise InvalidProductImageError(
                "Created timestamp cannot be after updated timestamp",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="created_at",
                field_value=self.created_at.isoformat(),
            )

        if self.uploaded_at > self.updated_at:
            raise InvalidProductImageError(
                "Uploaded timestamp cannot be after updated timestamp",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="uploaded_at",
                field_value=self.uploaded_at.isoformat(),
            )

        if self.processed_at and self.processed_at < self.uploaded_at:
            raise InvalidProductImageError(
                "Processed timestamp cannot be before uploaded timestamp",
                product_id=str(self.product_id),
                image_id=str(self.id),
                field_name="processed_at",
                field_value=self.processed_at.isoformat(),
            )

    @classmethod
    def create_from_upload(
        cls,
        id: UUID,
        product_id: UUID,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        file_size_bytes: int,
        file_format: str,
        resolution: ProductImageResolution,
        is_primary: bool = False,
        metadata: ProductImageMetadata | None = None,
        uploaded_at: datetime | None = None,
    ) -> "ProductImage":
        """
        Factory method to create ProductImage from upload data.

        Args:
            id: Unique identifier for the image.
            product_id: ID of the product this image belongs to.
            original_filename: Original filename of the uploaded file.
            s3_key: S3 key for the stored file.
            s3_url: S3 URL for accessing the file.
            file_size_bytes: Size of the file in bytes.
            file_format: Format of the file (jpg, png, etc.).
            resolution: Image resolution.
            is_primary: Whether this is the primary image.
            metadata: Processing metadata (optional).
            uploaded_at: Upload timestamp (defaults to now).

        Returns:
            New ProductImage instance.

        Raises:
            InvalidProductImageError: If validation fails.
        """
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        uploaded_at = uploaded_at or now

        return cls(
            id=id,
            product_id=product_id,
            original_filename=original_filename,
            s3_key=s3_key,
            s3_url=s3_url,
            original_s3_url=s3_url,  # Initially same as s3_url
            processed_s3_url=None,  # Set when processing is complete
            file_size_bytes=file_size_bytes,
            file_format=file_format.lower(),
            resolution=resolution,
            is_primary=is_primary,
            metadata=metadata or ProductImageMetadata(),
            created_at=now,
            updated_at=now,
            uploaded_at=uploaded_at,
            processed_at=None,
        )

    @property
    def is_processed(self) -> bool:
        """Check if the image has been processed."""
        return self.processed_at is not None and self.processed_s3_url is not None

    @property
    def is_processing_failed(self) -> bool:
        """Check if processing has failed."""
        return len(self.metadata.processing_errors) > 0

    @property
    def processing_status(self) -> str:
        """Get the current processing status."""
        if self.is_processing_failed:
            return "failed"
        elif self.is_processed:
            return "processed"
        elif self.metadata.processing_steps:
            return "processing"
        else:
            return "pending"

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size_bytes / (1024 * 1024)

    @property
    def is_high_quality(self) -> bool:
        """Check if the image is considered high quality."""
        avg_quality = self.metadata.average_quality_score
        return avg_quality is not None and avg_quality >= 0.7

    def set_as_primary(self) -> "ProductImage":
        """
        Create a new instance with this image set as primary.

        Returns:
            New ProductImage instance with is_primary=True.
        """
        from datetime import UTC, datetime

        return self.__class__(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=self.processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=self.resolution,
            is_primary=True,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            uploaded_at=self.uploaded_at,
            processed_at=self.processed_at,
        )

    def set_as_secondary(self) -> "ProductImage":
        """
        Create a new instance with this image set as secondary.

        Returns:
            New ProductImage instance with is_primary=False.
        """
        from datetime import UTC, datetime

        return self.__class__(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=self.processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=self.resolution,
            is_primary=False,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            uploaded_at=self.uploaded_at,
            processed_at=self.processed_at,
        )

    def mark_as_processed(
        self,
        processed_s3_url: str,
        updated_metadata: ProductImageMetadata | None = None,
    ) -> "ProductImage":
        """
        Mark the image as processed with updated URL and metadata.

        Args:
            processed_s3_url: URL of the processed image.
            updated_metadata: Updated metadata (optional).

        Returns:
            New ProductImage instance marked as processed.
        """
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        final_metadata = updated_metadata or self.metadata.add_processing_step(
            "completed"
        )

        return self.__class__(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=self.resolution,
            is_primary=self.is_primary,
            metadata=final_metadata,
            created_at=self.created_at,
            updated_at=now,
            uploaded_at=self.uploaded_at,
            processed_at=now,
        )

    def mark_processing_failed(self, error_message: str) -> "ProductImage":
        """
        Mark the image processing as failed with error message.

        Args:
            error_message: Error message describing the failure.

        Returns:
            New ProductImage instance with processing error.
        """
        from datetime import UTC, datetime

        updated_metadata = self.metadata.add_processing_error(error_message)

        return self.__class__(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=self.processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=self.resolution,
            is_primary=self.is_primary,
            metadata=updated_metadata,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            uploaded_at=self.uploaded_at,
            processed_at=self.processed_at,
        )

    def update_metadata(self, new_metadata: ProductImageMetadata) -> "ProductImage":
        """
        Update the image metadata.

        Args:
            new_metadata: New metadata to apply.

        Returns:
            New ProductImage instance with updated metadata.
        """
        from datetime import UTC, datetime

        return self.__class__(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=self.processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=self.resolution,
            is_primary=self.is_primary,
            metadata=new_metadata,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            uploaded_at=self.uploaded_at,
            processed_at=self.processed_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for API serialization.

        Returns:
            Dictionary representation suitable for API responses.
        """
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "original_filename": self.original_filename,
            "s3_key": self.s3_key,
            "s3_url": self.s3_url,
            "original_s3_url": self.original_s3_url,
            "processed_s3_url": self.processed_s3_url,
            "file_size_bytes": self.file_size_bytes,
            "file_format": self.file_format,
            "resolution": {
                "width": self.resolution.width,
                "height": self.resolution.height,
            },
            "is_primary": self.is_primary,
            "metadata": self.metadata.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "uploaded_at": self.uploaded_at.isoformat(),
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
            "processing_status": self.processing_status,
            "is_processed": self.is_processed,
            "file_size_mb": round(self.file_size_mb, 2),
        }

    def __str__(self) -> str:
        """String representation of the product image."""
        return (
            f"ProductImage(id={self.id}, product_id={self.product_id}, "
            f"filename={self.original_filename}, size={self.file_size_mb:.1f}MB, "
            f"resolution={self.resolution}, primary={self.is_primary})"
        )

    def __repr__(self) -> str:
        """Developer-friendly representation of the product image."""
        return self.__str__()
