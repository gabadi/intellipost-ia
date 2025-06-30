"""
Authentication API schemas.

This module contains Pydantic schemas for authentication endpoints.
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")


class TokenResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")


class SessionResponse(BaseModel):
    """Response schema for session status."""

    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    created_at: str = Field(..., description="Session creation timestamp")


class ChangePasswordRequest(BaseModel):
    """Request schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str = Field(..., description="Error message")
