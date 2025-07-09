"""
WebSocket schemas for content generation.

This module defines the WebSocket message schemas for real-time updates.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WebSocketMessage(BaseModel):
    """Base WebSocket message schema."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    type: str = Field(description="Message type")

    processing_id: UUID = Field(description="Processing identifier")

    timestamp: datetime = Field(description="Message timestamp")


class ProgressUpdateMessage(WebSocketMessage):
    """WebSocket message for progress updates."""

    type: str = Field(default="progress_update", description="Message type")

    data: dict[str, Any] = Field(
        description="Progress data",
        example={
            "processing_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "processing",
            "current_step": "category_detection",
            "progress_percentage": 60,
            "estimated_remaining_seconds": 4,
        },
    )


class CompletionMessage(WebSocketMessage):
    """WebSocket message for processing completion."""

    type: str = Field(default="completion", description="Message type")

    data: dict[str, Any] = Field(
        description="Completion data",
        example={
            "processing_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "completed",
            "generated_content": {
                "id": "content_123",
                "title": "iPhone 13 Pro 128GB Usado Excelente Estado",
                "description": "...",
                "confidence_overall": 0.87,
                "confidence_breakdown": {
                    "title": 0.92,
                    "description": 0.85,
                    "category": 0.88,
                    "price": 0.75,
                    "attributes": 0.90,
                },
            },
        },
    )


class ErrorMessage(WebSocketMessage):
    """WebSocket message for processing errors."""

    type: str = Field(default="error", description="Message type")

    data: dict[str, Any] = Field(
        description="Error data",
        example={
            "processing_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "failed",
            "error_message": "AI service temporarily unavailable",
            "error_code": "AI_SERVICE_ERROR",
            "retry_after_seconds": 60,
        },
    )


class ConnectionMessage(BaseModel):
    """WebSocket connection message."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat(),
        },
    )

    type: str = Field(
        description="Message type (connect, disconnect, subscribe, unsubscribe)"
    )

    processing_id: UUID | None = Field(
        default=None, description="Processing identifier to subscribe to"
    )

    message: str | None = Field(default=None, description="Connection message")

    timestamp: datetime = Field(description="Message timestamp")


class HeartbeatMessage(BaseModel):
    """WebSocket heartbeat message."""

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
    )

    type: str = Field(default="heartbeat", description="Message type")

    timestamp: datetime = Field(description="Heartbeat timestamp")

    server_time: datetime = Field(description="Server timestamp")


class StatusMessage(WebSocketMessage):
    """WebSocket status message."""

    type: str = Field(default="status", description="Message type")

    data: dict[str, Any] = Field(
        description="Status data",
        example={
            "processing_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "processing",
            "current_step": "title_generation",
            "progress_percentage": 35,
            "estimated_completion_seconds": 8,
            "completed_steps": ["image_analysis", "content_extraction"],
            "total_steps": 9,
        },
    )
