"""
SQLAlchemy Product model for product management module.

This module contains the SQLAlchemy models for Product and ProductImage entities.
"""

from datetime import UTC, datetime
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base
from modules.product_management.domain.entities.confidence_score import ConfidenceScore
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_image import ProductImage
from modules.product_management.domain.entities.product_status import ProductStatus
from modules.product_management.domain.value_objects.product_image_metadata import (
    ProductImageMetadata,
)
from modules.product_management.domain.value_objects.product_image_resolution import (
    ProductImageResolution,
)


class ProductModel(Base):
    """SQLAlchemy model for Product entity."""

    __tablename__ = "products"

    # Core identity
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Required user input
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Product information
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    category_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # AI-generated content
    ai_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # MercadoLibre integration
    ml_listing_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ml_category_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Processing tracking
    processing_started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Relationships
    images: Mapped[list["ProductImageModel"]] = relationship(
        "ProductImageModel", back_populates="product", cascade="all, delete-orphan"
    )

    def to_domain(self) -> Product:
        """Convert SQLAlchemy model to domain entity."""
        confidence_score = None
        if self.confidence:
            confidence_score = ConfidenceScore(float(self.confidence))

        return Product(
            id=self.id,
            user_id=self.user_id,
            status=ProductStatus(self.status),
            confidence=confidence_score,
            prompt_text=self.prompt_text,
            title=self.title,
            description=self.description,
            price=float(self.price) if self.price else None,
            category_id=self.category_id,
            ai_title=self.ai_title,
            ai_description=self.ai_description,
            ai_tags=self.ai_tags,
            ml_listing_id=self.ml_listing_id,
            ml_category_id=self.ml_category_id,
            processing_started_at=self.processing_started_at,
            processing_completed_at=self.processing_completed_at,
            processing_error=self.processing_error,
            created_at=self.created_at,
            updated_at=self.updated_at,
            published_at=self.published_at,
        )

    @classmethod
    def from_domain(cls, product: Product) -> "ProductModel":
        """Create SQLAlchemy model from domain entity."""
        confidence_value = str(product.confidence.score) if product.confidence else None

        return cls(
            id=product.id,
            user_id=product.user_id,
            status=product.status.value,
            confidence=confidence_value,
            prompt_text=product.prompt_text,
            title=product.title,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            ai_title=product.ai_title,
            ai_description=product.ai_description,
            ai_tags=product.ai_tags,
            ml_listing_id=product.ml_listing_id,
            ml_category_id=product.ml_category_id,
            processing_started_at=product.processing_started_at,
            processing_completed_at=product.processing_completed_at,
            processing_error=product.processing_error,
            created_at=product.created_at,
            updated_at=product.updated_at,
            published_at=product.published_at,
        )

    def update_from_domain(self, product: Product) -> None:
        """Update SQLAlchemy model from domain entity."""
        confidence_value = str(product.confidence.score) if product.confidence else None

        self.user_id = product.user_id
        self.status = product.status.value
        self.confidence = confidence_value
        self.prompt_text = product.prompt_text
        self.title = product.title
        self.description = product.description
        self.price = product.price
        self.category_id = product.category_id
        self.ai_title = product.ai_title
        self.ai_description = product.ai_description
        self.ai_tags = product.ai_tags
        self.ml_listing_id = product.ml_listing_id
        self.ml_category_id = product.ml_category_id
        self.processing_started_at = product.processing_started_at
        self.processing_completed_at = product.processing_completed_at
        self.processing_error = product.processing_error
        self.updated_at = product.updated_at or datetime.now(UTC)
        self.published_at = product.published_at


class ProductImageModel(Base):
    """SQLAlchemy model for ProductImage entity."""

    __tablename__ = "product_images"

    # Core identity
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    product_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    original_s3_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    processed_s3_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    resolution_width: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_height: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    # Processing metadata
    processing_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Relationships
    product: Mapped[ProductModel] = relationship(
        "ProductModel", back_populates="images"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
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
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "is_primary": self.is_primary,
            "processing_metadata": self.processing_metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "uploaded_at": self.uploaded_at.isoformat(),
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
        }

    def to_domain(self) -> ProductImage:
        """Convert SQLAlchemy model to domain entity."""
        # Create resolution value object
        resolution = ProductImageResolution(
            width=self.resolution_width, height=self.resolution_height
        )

        # Create metadata value object
        metadata_dict = self.processing_metadata or {}
        metadata = ProductImageMetadata(
            ai_analysis=metadata_dict.get("ai_analysis", {}),
            quality_score=metadata_dict.get("quality_score"),
            sharpness_score=metadata_dict.get("sharpness_score"),
            brightness_score=metadata_dict.get("brightness_score"),
            contrast_score=metadata_dict.get("contrast_score"),
            detected_objects=metadata_dict.get("detected_objects", []),
            dominant_colors=metadata_dict.get("dominant_colors", []),
            color_palette=metadata_dict.get("color_palette", []),
            processing_steps=metadata_dict.get("processing_steps", []),
            processing_errors=metadata_dict.get("processing_errors", []),
            compression_ratio=metadata_dict.get("compression_ratio"),
            file_hash=metadata_dict.get("file_hash"),
        )

        return ProductImage(
            id=self.id,
            product_id=self.product_id,
            original_filename=self.original_filename,
            s3_key=self.s3_key,
            s3_url=self.s3_url,
            original_s3_url=self.original_s3_url,
            processed_s3_url=self.processed_s3_url,
            file_size_bytes=self.file_size_bytes,
            file_format=self.file_format,
            resolution=resolution,
            is_primary=self.is_primary,
            metadata=metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
            uploaded_at=self.uploaded_at,
            processed_at=self.processed_at,
        )

    @classmethod
    def from_domain(cls, image: ProductImage) -> "ProductImageModel":
        """Create SQLAlchemy model from domain entity."""
        # Convert metadata to dict for JSON storage
        metadata_dict = {
            "ai_analysis": image.metadata.ai_analysis,
            "quality_score": image.metadata.quality_score,
            "sharpness_score": image.metadata.sharpness_score,
            "brightness_score": image.metadata.brightness_score,
            "contrast_score": image.metadata.contrast_score,
            "detected_objects": image.metadata.detected_objects,
            "dominant_colors": image.metadata.dominant_colors,
            "color_palette": image.metadata.color_palette,
            "processing_steps": image.metadata.processing_steps,
            "processing_errors": image.metadata.processing_errors,
            "compression_ratio": image.metadata.compression_ratio,
            "file_hash": image.metadata.file_hash,
        }

        return cls(
            id=image.id,
            product_id=image.product_id,
            original_filename=image.original_filename,
            s3_key=image.s3_key,
            s3_url=image.s3_url,
            original_s3_url=image.original_s3_url,
            processed_s3_url=image.processed_s3_url,
            file_size_bytes=image.file_size_bytes,
            file_format=image.file_format,
            resolution_width=image.resolution.width,
            resolution_height=image.resolution.height,
            is_primary=image.is_primary,
            processing_metadata=metadata_dict,
            created_at=image.created_at,
            updated_at=image.updated_at,
            uploaded_at=image.uploaded_at,
            processed_at=image.processed_at,
        )

    @classmethod
    def from_upload_data(
        cls,
        product_id: UUIDType,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        file_size_bytes: int,
        file_format: str,
        resolution_width: int,
        resolution_height: int,
        is_primary: bool = False,
        processing_metadata: dict | None = None,
    ) -> "ProductImageModel":
        """Create ProductImageModel from upload data."""
        return cls(
            product_id=product_id,
            original_filename=original_filename,
            s3_key=s3_key,
            s3_url=s3_url,
            original_s3_url=s3_url,  # Use s3_url as original_s3_url initially
            file_size_bytes=file_size_bytes,
            file_format=file_format,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            is_primary=is_primary,
            processing_metadata=processing_metadata,
        )
