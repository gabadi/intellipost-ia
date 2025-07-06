"""
User API schemas for user management module.

This module contains Pydantic models for user-related request/response data.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserProfileUpdateRequest(BaseModel):
    """User profile update request schema."""

    first_name: str | None = Field(max_length=100, default=None)
    last_name: str | None = Field(max_length=100, default=None)
    auto_publish: bool | None = None
    ai_confidence_threshold: str | None = Field(max_length=20, default=None)
    default_ml_site: str | None = Field(max_length=10, default=None)


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=255)


class UserDetailResponse(BaseModel):
    """Detailed user response schema."""

    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_email_verified: bool
    status: str
    ml_user_id: str | None
    is_ml_connected: bool
    default_ml_site: str
    auto_publish: bool
    ai_confidence_threshold: str
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    email_verified_at: datetime | None

    class Config:
        from_attributes = True
