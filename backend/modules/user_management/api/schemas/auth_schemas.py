"""
Authentication API schemas for user management module.

This module contains Pydantic models for authentication request/response data.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    first_name: str | None = Field(max_length=100, default=None)
    last_name: str | None = Field(max_length=100, default=None)


class LoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Token refresh request schema."""

    refresh_token: str


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_email_verified: bool
    status: str
    created_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Authentication token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class LogoutResponse(BaseModel):
    """Logout response schema."""

    message: str = "Successfully logged out"


class ErrorResponse(BaseModel):
    """Error response schema."""

    error_code: str
    message: str
    details: dict[str, str] | None = None
