"""
Authentication API schemas.

This module contains Pydantic models for authentication API requests and responses.
These schemas are owned by the API layer and used for request/response validation.
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str


class UserResponse(BaseModel):
    """Response model for user information."""

    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: str
    last_login_at: str | None


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class LogoutResponse(BaseModel):
    """Response model for logout."""

    message: str


class AuthErrorResponse(BaseModel):
    """Response model for authentication errors."""

    detail: str
