"""
Authentication API schemas using Pydantic.

This module contains request and response schemas for authentication endpoints.
"""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.auth.domain.protocols import AuthUserProtocol
from modules.auth.domain.value_objects import CreatedAuthUser


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration."""

    email: str = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password (8-128 characters, mixed case, numbers)",
        examples=["SecurePass123"],
    )
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's first name",
        examples=["John"],
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's last name",
        examples=["Doe"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one number"
            )

        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_fields(cls, v: str | None) -> str | None:
        """Validate and clean name fields."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    email: str = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=1,
        description="User's password",
        examples=["SecurePass123"],
    )


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(
        description="Valid refresh token",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."],
    )


class LogoutRequest(BaseModel):
    """Request schema for user logout."""

    refresh_token: str = Field(
        description="Refresh token to invalidate",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."],
    )


class PasswordChangeRequest(BaseModel):
    """Request schema for password change."""

    current_password: str = Field(
        min_length=1,
        description="Current password for verification",
        examples=["CurrentPassword123"],
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password (8-128 characters, mixed case, numbers)",
        examples=["NewSecurePass456"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        """Validate new password strength requirements."""
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "New password must contain at least one uppercase letter, "
                "one lowercase letter, and one number"
            )

        return v


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    status: str | None = Field(None, description="User's account status")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: str = Field(..., description="Account creation timestamp")
    last_login_at: str | None = Field(None, description="Last login timestamp")
    email_verified_at: str | None = Field(
        None, description="Email verification timestamp"
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."],
    )
    refresh_token: str = Field(
        description="JWT refresh token",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[900],
    )


class AuthenticationResponse(BaseModel):
    """Response schema for authentication operations."""

    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    message: str = Field(..., description="Success message")


class AccessTokenResponse(BaseModel):
    """Response schema for access token refresh."""

    access_token: str = Field(
        description="New JWT access token",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Access token expiration time in seconds",
        examples=[900],
    )


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(None, description="Error code")


# Helper function to convert User domain entity to UserResponse
def user_to_response(user: AuthUserProtocol | CreatedAuthUser) -> UserResponse:
    """Convert User domain entity to UserResponse schema."""
    # Handle both AuthUserProtocol (with id) and CreatedAuthUser (with user_id)
    if isinstance(user, CreatedAuthUser):
        user_id = user.user_id
        status = None  # CreatedAuthUser doesn't have status
        last_login_at = None
        email_verified_at = None
    else:
        user_id = user.id
        status = user.status.value if hasattr(user, "status") and user.status else None
        last_login_at = user.last_login_at.isoformat() if user.last_login_at else None
        email_verified_at = (
            user.email_verified_at.isoformat() if user.email_verified_at else None
        )

    return UserResponse(
        id=user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status=status,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login_at=last_login_at,
        email_verified_at=email_verified_at,
    )
