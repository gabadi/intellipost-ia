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
from modules.product_management.domain.entities.product_status import ProductStatus


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
            title=self.title,
            description=self.description,
            price=float(self.price) if self.price else None,
            category_id=self.category_id,
            ai_title=self.ai_title,
            ai_description=self.ai_description,
            ai_tags=self.ai_tags,
            ml_listing_id=self.ml_listing_id,
            ml_category_id=self.ml_category_id,
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
            title=product.title,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            ai_title=product.ai_title,
            ai_description=product.ai_description,
            ai_tags=product.ai_tags,
            ml_listing_id=product.ml_listing_id,
            ml_category_id=product.ml_category_id,
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
        self.title = product.title
        self.description = product.description
        self.price = product.price
        self.category_id = product.category_id
        self.ai_title = product.ai_title
        self.ai_description = product.ai_description
        self.ai_tags = product.ai_tags
        self.ml_listing_id = product.ml_listing_id
        self.ml_category_id = product.ml_category_id
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
            "file_size_bytes": self.file_size_bytes,
            "file_format": self.file_format,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "is_primary": self.is_primary,
            "processing_metadata": self.processing_metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

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
            file_size_bytes=file_size_bytes,
            file_format=file_format,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            is_primary=is_primary,
            processing_metadata=processing_metadata,
        )
