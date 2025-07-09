"""
Content Generation API schemas.

This module defines the request/response schemas for content generation endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContentGenerationRequest(BaseModel):
    """Request schema for content generation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    regenerate: bool = Field(
        default=False, description="Whether to regenerate existing content"
    )

    category_hint: str | None = Field(
        default=None, description="Optional hint for category detection", max_length=100
    )

    price_range: dict[str, float] | None = Field(
        default=None,
        description="Optional price range guidance",
        example={"min": 10000, "max": 50000},
    )

    target_audience: str | None = Field(
        default=None,
        description="Optional target audience specification",
        max_length=100,
    )


class ContentGenerationResponse(BaseModel):
    """Response schema for content generation."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        },
    )

    processing_id: UUID = Field(description="Unique processing identifier")

    status: str = Field(description="Current processing status")

    estimated_completion_seconds: int | None = Field(
        default=None, description="Estimated time to completion in seconds"
    )

    progress: dict[str, Any] = Field(
        description="Progress information",
        example={"current_step": "image_analysis", "total_steps": 5, "percentage": 20},
    )


class ProgressUpdateSchema(BaseModel):
    """Schema for progress updates."""

    model_config = ConfigDict(use_enum_values=True)

    processing_id: UUID = Field(description="Processing identifier")

    status: str = Field(description="Current processing status")

    current_step: str | None = Field(
        default=None, description="Current processing step"
    )

    progress_percentage: float = Field(description="Progress percentage (0-100)")

    estimated_remaining_seconds: int | None = Field(
        default=None, description="Estimated remaining time in seconds"
    )


class ConfidenceScoreSchema(BaseModel):
    """Schema for confidence scores."""

    overall: float = Field(
        description="Overall confidence score (0.0-1.0)", ge=0.0, le=1.0
    )

    breakdown: dict[str, float] = Field(
        description="Confidence breakdown by component",
        example={
            "title": 0.92,
            "description": 0.85,
            "category": 0.88,
            "price": 0.75,
            "attributes": 0.90,
        },
    )


class GeneratedContentSchema(BaseModel):
    """Schema for generated content."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        },
    )

    id: UUID = Field(description="Content identifier")

    product_id: UUID = Field(description="Product identifier")

    title: str = Field(description="Generated title")

    description: str = Field(description="Generated description")

    ml_category_id: str = Field(description="MercadoLibre category ID")

    ml_category_name: str = Field(description="MercadoLibre category name")

    ml_title: str = Field(description="MercadoLibre optimized title (max 60 chars)")

    ml_price: float = Field(description="Estimated price in ARS")

    ml_currency_id: str = Field(description="Currency identifier", default="ARS")

    ml_available_quantity: int = Field(description="Available quantity", default=1)

    ml_buying_mode: str = Field(description="Buying mode", default="buy_it_now")

    ml_condition: str = Field(description="Product condition", default="new")

    ml_listing_type_id: str = Field(
        description="Listing type identifier", default="gold_special"
    )

    ml_attributes: dict[str, Any] = Field(
        description="MercadoLibre attributes", default={}
    )

    ml_sale_terms: dict[str, Any] = Field(
        description="MercadoLibre sale terms", default={}
    )

    ml_shipping: dict[str, Any] = Field(
        description="MercadoLibre shipping configuration", default={}
    )

    confidence_overall: float = Field(
        description="Overall confidence score (0.0-1.0)", ge=0.0, le=1.0
    )

    confidence_breakdown: dict[str, float] = Field(
        description="Confidence breakdown by component"
    )

    ai_provider: str = Field(description="AI provider used for generation")

    ai_model_version: str = Field(description="AI model version")

    generation_time_ms: int | None = Field(
        default=None, description="Generation time in milliseconds"
    )

    version: int = Field(description="Content version number")

    generated_at: datetime = Field(description="Generation timestamp")

    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )


class ContentGenerationCompletionSchema(BaseModel):
    """Schema for content generation completion."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    processing_id: UUID = Field(description="Processing identifier")

    status: str = Field(description="Final processing status")

    generated_content: GeneratedContentSchema | None = Field(
        default=None, description="Generated content (if successful)"
    )

    error_message: str | None = Field(
        default=None, description="Error message (if failed)"
    )

    error_code: str | None = Field(default=None, description="Error code (if failed)")

    processing_time_ms: int | None = Field(
        default=None, description="Total processing time in milliseconds"
    )


class ContentValidationSchema(BaseModel):
    """Schema for content validation results."""

    content_id: UUID = Field(description="Content identifier")

    is_valid: bool = Field(description="Whether content is valid")

    validation_errors: list[str] = Field(description="List of validation errors")

    validation_warnings: list[str] = Field(description="List of validation warnings")

    is_compliant: bool = Field(description="Whether content is MercadoLibre compliant")

    compliance_issues: list[str] = Field(description="List of compliance issues")

    quality_score: float = Field(
        description="Content quality score (0.0-1.0)", ge=0.0, le=1.0
    )

    meets_threshold: bool = Field(description="Whether content meets quality threshold")

    improvement_suggestions: list[str] = Field(
        description="List of improvement suggestions"
    )

    quality_indicators: dict[str, bool] = Field(description="Quality indicators")


class ContentEnhancementRequest(BaseModel):
    """Request schema for content enhancement."""

    model_config = ConfigDict(str_strip_whitespace=True)

    enhancement_type: str = Field(
        description="Type of enhancement (title, description, attributes)"
    )

    additional_data: dict[str, Any] | None = Field(
        default=None, description="Additional data for enhancement"
    )


class ContentVersionsSchema(BaseModel):
    """Schema for content versions."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    product_id: UUID = Field(description="Product identifier")

    versions: list[GeneratedContentSchema] = Field(
        description="List of content versions"
    )

    total_versions: int = Field(description="Total number of versions")

    latest_version: int = Field(description="Latest version number")


class ProcessingStatusSchema(BaseModel):
    """Schema for processing status."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    processing_id: UUID = Field(description="Processing identifier")

    product_id: UUID = Field(description="Product identifier")

    status: str = Field(description="Current processing status")

    current_step: str | None = Field(
        default=None, description="Current processing step"
    )

    progress_percentage: float = Field(description="Progress percentage (0-100)")

    estimated_completion_seconds: int | None = Field(
        default=None, description="Estimated time to completion"
    )

    estimated_remaining_seconds: int | None = Field(
        default=None, description="Estimated remaining time"
    )

    error_message: str | None = Field(
        default=None, description="Error message (if failed)"
    )

    error_code: str | None = Field(default=None, description="Error code (if failed)")

    created_at: datetime = Field(description="Processing start timestamp")

    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""

    error_type: str = Field(description="Type of error")

    message: str = Field(description="Error message")

    error_code: str | None = Field(default=None, description="Error code")

    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )

    timestamp: datetime = Field(description="Error timestamp")


class WebSocketMessageSchema(BaseModel):
    """Schema for WebSocket messages."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    type: str = Field(description="Message type (progress_update, completion, error)")

    data: dict[str, Any] = Field(description="Message data")

    timestamp: datetime = Field(description="Message timestamp")
