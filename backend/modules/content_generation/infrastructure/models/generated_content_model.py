"""
Generated Content database model.

This module defines the SQLAlchemy models for the generated content tables.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.database import Base


class GeneratedContentModel(Base):
    """SQLAlchemy model for generated content."""

    __tablename__ = "generated_content"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # Foreign keys
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # AI Generated content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # MercadoLibre specific fields
    ml_category_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ml_category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    ml_title: Mapped[str] = mapped_column(String(60), nullable=False)
    ml_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ml_currency_id: Mapped[str] = mapped_column(
        String(3), nullable=False, default="ARS"
    )
    ml_available_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    ml_buying_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="buy_it_now"
    )
    ml_condition: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    ml_listing_type_id: Mapped[str] = mapped_column(
        String(50), nullable=False, default="gold_special"
    )

    # MercadoLibre flexible attributes and terms
    ml_attributes: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default={}
    )
    ml_sale_terms: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default={}
    )
    ml_shipping: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default={}
    )

    # AI confidence scoring
    confidence_overall: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, index=True
    )
    confidence_breakdown: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default={}
    )

    # AI provider metadata
    ai_provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="gemini", index=True
    )
    ai_model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    generation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Version control for regeneration
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, index=True)

    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "char_length(trim(title)) >= 10",
            name="ck_generated_content_title_min_length",
        ),
        CheckConstraint(
            "char_length(trim(description)) >= 50",
            name="ck_generated_content_description_min_length",
        ),
        CheckConstraint(
            "ml_price > 0",
            name="ck_generated_content_price_positive",
        ),
        CheckConstraint(
            "confidence_overall BETWEEN 0.00 AND 1.00",
            name="ck_generated_content_confidence_range",
        ),
        CheckConstraint(
            "generation_time_ms > 0 OR generation_time_ms IS NULL",
            name="ck_generated_content_generation_time_positive",
        ),
        CheckConstraint(
            "version > 0",
            name="ck_generated_content_version_positive",
        ),
    )

    # Relationship to products (if products table exists)
    # product = relationship("ProductModel", back_populates="generated_content")

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "title": self.title,
            "description": self.description,
            "ml_category_id": self.ml_category_id,
            "ml_category_name": self.ml_category_name,
            "ml_title": self.ml_title,
            "ml_price": float(self.ml_price),
            "ml_currency_id": self.ml_currency_id,
            "ml_available_quantity": self.ml_available_quantity,
            "ml_buying_mode": self.ml_buying_mode,
            "ml_condition": self.ml_condition,
            "ml_listing_type_id": self.ml_listing_type_id,
            "ml_attributes": self.ml_attributes,
            "ml_sale_terms": self.ml_sale_terms,
            "ml_shipping": self.ml_shipping,
            "confidence_overall": float(self.confidence_overall),
            "confidence_breakdown": self.confidence_breakdown,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "generation_time_ms": self.generation_time_ms,
            "version": self.version,
            "generated_at": self.generated_at.isoformat()
            if self.generated_at
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIGenerationModel(Base):
    """SQLAlchemy model for AI generation tracking."""

    __tablename__ = "ai_generation"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # Foreign keys
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_content_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("generated_content.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Processing status
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Processing metadata
    current_step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    progress_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0.0
    )
    estimated_completion_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Input data
    input_images: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=[])
    input_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_hint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_range: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default={}
    )
    target_audience: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Processing results
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # AI provider metadata
    ai_provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="gemini", index=True
    )
    ai_model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Processing steps tracking
    completed_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=[])
    failed_step: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=func.now(),
        index=True,
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "progress_percentage BETWEEN 0.0 AND 100.0",
            name="ck_ai_generation_progress_range",
        ),
        CheckConstraint(
            "processing_time_ms > 0 OR processing_time_ms IS NULL",
            name="ck_ai_generation_processing_time_positive",
        ),
        CheckConstraint(
            "estimated_completion_seconds > 0 OR estimated_completion_seconds IS NULL",
            name="ck_ai_generation_estimated_completion_positive",
        ),
    )

    # Relationships
    # product = relationship("ProductModel", back_populates="ai_generations")
    # generated_content = relationship("GeneratedContentModel", back_populates="ai_generation")

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "generated_content_id": self.generated_content_id,
            "status": self.status,
            "current_step": self.current_step,
            "progress_percentage": float(self.progress_percentage),
            "estimated_completion_seconds": self.estimated_completion_seconds,
            "input_images": self.input_images,
            "input_prompt": self.input_prompt,
            "category_hint": self.category_hint,
            "price_range": self.price_range,
            "target_audience": self.target_audience,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "processing_time_ms": self.processing_time_ms,
            "completed_steps": self.completed_steps,
            "failed_step": self.failed_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
