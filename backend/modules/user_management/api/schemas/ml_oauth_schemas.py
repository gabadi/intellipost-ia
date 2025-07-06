"""
MercadoLibre OAuth API schemas for user management module.

This module contains Pydantic schemas for ML OAuth API requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field, validator


class MLOAuthInitiateRequest(BaseModel):
    """Request schema for initiating ML OAuth flow."""

    redirect_uri: str = Field(
        ...,
        description="OAuth redirect URI",
        pattern=r"^https?://.+",
        min_length=10,
        max_length=500,
    )
    site_id: str = Field(
        default="MLA",
        description="MercadoLibre site ID",
        pattern=r"^(MLA|MLM|MBL|MLC|MCO)$",
    )

    @validator("redirect_uri")
    def validate_redirect_uri(cls, v):
        """Validate redirect URI format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("redirect_uri must start with http:// or https://")
        return v


class MLOAuthInitiateResponse(BaseModel):
    """Response schema for OAuth flow initiation."""

    authorization_url: str = Field(
        ..., description="MercadoLibre authorization URL to redirect user to"
    )
    state: str = Field(..., description="CSRF state parameter for validation")
    code_verifier: str = Field(
        ..., description="PKCE code verifier for client-side storage"
    )
    expires_in: int = Field(
        default=300, description="Seconds until authorization expires"
    )


class MLOAuthCallbackRequest(BaseModel):
    """Request schema for handling OAuth callback."""

    code: str = Field(
        ...,
        description="Authorization code from callback",
        min_length=10,
        max_length=500,
    )
    state: str = Field(
        ...,
        description="CSRF state parameter",
        min_length=10,
        max_length=100,
    )
    code_verifier: str = Field(
        ...,
        description="PKCE code verifier",
        min_length=43,
        max_length=128,
    )


class MLOAuthCallbackResponse(BaseModel):
    """Response schema for OAuth callback completion."""

    success: bool = Field(..., description="Whether OAuth was successful")
    message: str = Field(..., description="Success or error message")
    ml_nickname: str | None = Field(None, description="MercadoLibre user nickname")
    ml_email: str | None = Field(None, description="MercadoLibre user email")
    ml_site_id: str = Field(..., description="MercadoLibre site ID")
    connection_health: str = Field(..., description="Connection health status")


class MLConnectionStatusResponse(BaseModel):
    """Response schema for connection status."""

    is_connected: bool = Field(
        ..., description="Whether user is connected to MercadoLibre"
    )
    connection_health: str = Field(
        ...,
        description="Connection health status",
        pattern=r"^(healthy|expired|invalid|disconnected)$",
    )
    ml_nickname: str | None = Field(None, description="MercadoLibre user nickname")
    ml_email: str | None = Field(None, description="MercadoLibre user email")
    ml_site_id: str | None = Field(None, description="MercadoLibre site ID")
    expires_at: datetime | None = Field(None, description="Token expiration time")
    last_validated_at: datetime | None = Field(None, description="Last validation time")
    error_message: str | None = Field(None, description="Error message if any")
    should_refresh: bool = Field(
        default=False, description="Whether token should be refreshed soon"
    )
    time_until_refresh: int | None = Field(
        None, description="Seconds until token refresh is needed"
    )


class MLDisconnectRequest(BaseModel):
    """Request schema for disconnecting ML account."""

    confirm: bool = Field(default=True, description="Confirmation of disconnect action")


class MLDisconnectResponse(BaseModel):
    """Response schema for disconnect operation."""

    success: bool = Field(..., description="Whether disconnect was successful")
    message: str = Field(..., description="Success or error message")


class MLTokenRefreshResponse(BaseModel):
    """Response schema for token refresh operation."""

    success: bool = Field(..., description="Whether refresh was successful")
    message: str = Field(..., description="Success or error message")
    expires_at: datetime | None = Field(None, description="New token expiration time")
    connection_health: str = Field(..., description="Updated connection health")


class MLValidationResponse(BaseModel):
    """Response schema for connection validation."""

    is_valid: bool = Field(..., description="Whether connection is valid")
    connection_health: str = Field(..., description="Connection health status")
    last_validated_at: datetime = Field(..., description="Validation timestamp")
    error_message: str | None = Field(None, description="Error message if invalid")


class MLErrorResponse(BaseModel):
    """Response schema for ML OAuth errors."""

    error: str = Field(..., description="Error code")
    error_description: str = Field(..., description="Human-readable error description")
    error_uri: str | None = Field(None, description="URI with error information")
    status_code: int = Field(..., description="HTTP status code")
    request_id: str | None = Field(None, description="Request ID for tracking")

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "error": "invalid_grant",
                "error_description": "The authorization code is invalid or has expired",
                "status_code": 400,
                "request_id": "req_123456789",
            }
        }


class MLManagerAccountError(BaseModel):
    """Response schema for manager account requirement errors."""

    error: str = Field(default="manager_account_required")
    error_description: str = Field(
        default="Only manager accounts can authorize applications. "
        "Collaborator accounts cannot connect to IntelliPost AI."
    )
    guidance: str = Field(
        default="Please use a MercadoLibre manager account to complete the connection."
    )
    status_code: int = Field(default=403)

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "error": "manager_account_required",
                "error_description": "Only manager accounts can authorize applications. "
                "Collaborator accounts cannot connect to IntelliPost AI.",
                "guidance": "Please use a MercadoLibre manager account to complete the connection.",
                "status_code": 403,
            }
        }


class MLRateLimitResponse(BaseModel):
    """Response schema for rate limit errors."""

    error: str = Field(default="rate_limited")
    error_description: str = Field(default="Too many requests. Please try again later.")
    retry_after: int = Field(..., description="Seconds to wait before retrying")
    status_code: int = Field(default=429)

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "error": "rate_limited",
                "error_description": "Too many requests. Please try again later.",
                "retry_after": 60,
                "status_code": 429,
            }
        }


class MLHealthCheckResponse(BaseModel):
    """Response schema for ML service health check."""

    service: str = Field(default="ml_oauth")
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    checks: dict = Field(..., description="Individual health checks")

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "service": "ml_oauth",
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-07-06T10:00:00Z",
                "checks": {
                    "database": "healthy",
                    "encryption": "healthy",
                    "ml_api": "healthy",
                },
            }
        }
