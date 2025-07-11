"""
Product API schemas for request and response models.

This module contains Pydantic models for product API endpoints.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProductImageResponse(BaseModel):
    """Response model for product image."""

    id: str
    product_id: str
    original_filename: str
    s3_url: str
    original_s3_url: str
    processed_s3_url: str | None = None
    file_size_bytes: int
    file_format: str
    resolution_width: int
    resolution_height: int
    is_primary: bool
    processing_metadata: dict[str, Any] | None = None
    created_at: str
    updated_at: str
    uploaded_at: str
    processed_at: str | None = None


class ProductResponse(BaseModel):
    """Response model for product."""

    id: str
    user_id: str
    status: str
    confidence: str | None = None

    # Required user input
    prompt_text: str

    # Product information
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: str | None = None

    # AI-generated content
    ai_title: str | None = None
    ai_description: str | None = None
    ai_tags: list[str] | None = None

    # MercadoLibre integration
    ml_listing_id: str | None = None
    ml_category_id: str | None = None

    # Processing tracking
    processing_started_at: str | None = None
    processing_completed_at: str | None = None
    processing_error: str | None = None

    # Timestamps
    created_at: str
    updated_at: str
    published_at: str | None = None

    # Related data
    images: list[ProductImageResponse] = Field(default_factory=list)


class CreateProductRequest(BaseModel):
    """Request model for creating a product."""

    prompt_text: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Product description prompt for AI generation (10-500 characters)",
    )

    @field_validator("prompt_text")
    @classmethod
    def validate_prompt_text(cls, v: str) -> str:
        """Validate prompt text."""
        if not v or not v.strip():
            raise ValueError("Prompt text cannot be empty")
        return v.strip()


class CreateProductResponse(BaseModel):
    """Response model for product creation."""

    id: str
    user_id: str
    status: str
    prompt_text: str
    images_uploaded: int
    created_at: str
    message: str = "Product created successfully"


class ProductListResponse(BaseModel):
    """Response model for product list."""

    products: list[ProductResponse]
    total: int
    page: int = 1
    page_size: int = 20


class ErrorResponse(BaseModel):
    """Error response model."""

    error_code: str
    message: str
    details: dict[str, Any] | None = None


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error_code: str = "VALIDATION_ERROR"
    message: str = "Request validation failed"
    field_errors: list[dict[str, Any]]


class FileUploadError(BaseModel):
    """File upload error model."""

    filename: str
    error_message: str
