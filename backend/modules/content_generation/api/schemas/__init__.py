"""
Content Generation API schemas.

This module exports all API schemas for the content generation module.
"""

from .content_generation_schemas import (
    ConfidenceScoreSchema,
    ContentEnhancementRequest,
    ContentGenerationCompletionSchema,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentValidationSchema,
    ContentVersionsSchema,
    ErrorResponseSchema,
    GeneratedContentSchema,
    ProcessingStatusSchema,
    ProgressUpdateSchema,
    WebSocketMessageSchema,
)
from .websocket_schemas import (
    CompletionMessage,
    ConnectionMessage,
    ErrorMessage,
    HeartbeatMessage,
    ProgressUpdateMessage,
    StatusMessage,
    WebSocketMessage,
)

__all__ = [
    # Content Generation Schemas
    "ContentGenerationRequest",
    "ContentGenerationResponse",
    "ContentGenerationCompletionSchema",
    "ContentValidationSchema",
    "ContentEnhancementRequest",
    "ContentVersionsSchema",
    "ProcessingStatusSchema",
    "ErrorResponseSchema",
    "GeneratedContentSchema",
    "ConfidenceScoreSchema",
    "ProgressUpdateSchema",
    "WebSocketMessageSchema",
    # WebSocket Schemas
    "WebSocketMessage",
    "ProgressUpdateMessage",
    "CompletionMessage",
    "ErrorMessage",
    "ConnectionMessage",
    "HeartbeatMessage",
    "StatusMessage",
]
