"""
User API schemas.

This module contains Pydantic schemas for user endpoints.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserPreferences(BaseModel):
    """User preferences schema."""

    default_ml_site: str = Field(default="MLA", description="Default MercadoLibre site")
    auto_publish: bool = Field(default=False, description="Auto-publish products")
    ai_confidence_threshold: str = Field(
        default="medium", description="AI confidence threshold (low/medium/high)"
    )


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""

    user_id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    status: str = Field(..., description="User status")
    preferences: dict[str, Any] = Field(..., description="User preferences")


class UserProfileUpdateRequest(BaseModel):
    """Request schema for user profile update."""

    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    preferences: dict[str, Any] | None = Field(None, description="User preferences")
