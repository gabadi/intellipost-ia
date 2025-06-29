"""
Standardized error handling for authentication API endpoints.

This module provides consistent error responses across all authentication endpoints.
"""

import logging
from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AuthenticationError(HTTPException):
    """Base exception for authentication-related errors."""

    def __init__(
        self,
        detail: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            detail=detail,
            error_code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class EmailAlreadyExistsError(AuthenticationError):
    """Raised when trying to register with an existing email."""

    def __init__(self, detail: str = "Email already registered"):
        super().__init__(
            detail=detail,
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class WeakPasswordError(AuthenticationError):
    """Raised when password doesn't meet strength requirements."""

    def __init__(self, detail: str = "Password doesn't meet security requirements"):
        super().__init__(
            detail=detail,
            error_code="WEAK_PASSWORD",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidEmailFormatError(AuthenticationError):
    """Raised when email format is invalid."""

    def __init__(self, detail: str = "Invalid email format"):
        super().__init__(
            detail=detail,
            error_code="INVALID_EMAIL_FORMAT",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or expired."""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            detail=detail,
            error_code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidRefreshTokenError(AuthenticationError):
    """Raised when refresh token is invalid or expired."""

    def __init__(self, detail: str = "Invalid or expired refresh token"):
        super().__init__(
            detail=detail,
            error_code="INVALID_REFRESH_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserInactiveError(AuthenticationError):
    """Raised when user account is inactive or suspended."""

    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(
            detail=detail,
            error_code="USER_INACTIVE",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class RateLimitExceededError(AuthenticationError):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later"):
        super().__init__(
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class MissingAuthorizationError(AuthenticationError):
    """Raised when Authorization header is missing."""

    def __init__(self, detail: str = "Missing Authorization header"):
        super().__init__(
            detail=detail,
            error_code="MISSING_AUTHORIZATION",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


def create_error_response(
    error: AuthenticationError, request_id: str | None = None
) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        error: Authentication error instance
        request_id: Optional request ID for tracking

    Returns:
        JSONResponse with standardized error format
    """
    error_data = {
        "error": error.detail,
        "error_code": error.error_code,
        "status_code": error.status_code,
    }

    if request_id:
        error_data["request_id"] = request_id

    # Log error for monitoring
    logger.warning(
        f"Authentication error: {error.error_code} - {error.detail}",
        extra={
            "error_code": error.error_code,
            "status_code": error.status_code,
            "request_id": request_id,
        },
    )

    return JSONResponse(status_code=error.status_code, content=error_data)


def handle_validation_errors(errors: list[dict[str, Any]]) -> AuthenticationError:
    """
    Convert Pydantic validation errors to authentication errors.

    Args:
        errors: List of Pydantic validation errors

    Returns:
        AuthenticationError with appropriate error code
    """
    # Check for specific error types
    for error in errors:
        field = error.get("loc", [""])[0] if error.get("loc") else ""
        error_type = error.get("type", "")
        message = error.get("msg", "")

        # Email validation errors
        if field == "email" or "email" in error_type:
            return InvalidEmailFormatError(detail=f"Invalid email format: {message}")

        # Password validation errors
        if field == "password" or "password" in message.lower():
            return WeakPasswordError(detail=f"Password validation failed: {message}")

    # Generic validation error
    first_error = errors[0] if errors else {}
    detail = first_error.get("msg", "Validation failed")

    return AuthenticationError(
        detail=f"Validation error: {detail}",
        error_code="VALIDATION_ERROR",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def map_domain_exceptions(exception: Exception) -> AuthenticationError:
    """
    Map domain-layer exceptions to API-layer authentication errors.

    Args:
        exception: Domain exception

    Returns:
        AuthenticationError with appropriate status code and message
    """
    exception_name = type(exception).__name__
    exception_message = str(exception)

    # Map common domain exceptions
    exception_mapping = {
        "UserAlreadyExistsError": EmailAlreadyExistsError,
        "InvalidCredentialsError": InvalidCredentialsError,
        "WeakPasswordError": WeakPasswordError,
        "InvalidEmailError": InvalidEmailFormatError,
        "TokenExpiredError": InvalidTokenError,
        "InvalidTokenError": InvalidTokenError,
        "UserNotFoundError": InvalidCredentialsError,  # Don't reveal user existence
        "UserInactiveError": UserInactiveError,
    }

    error_class = exception_mapping.get(exception_name)
    if error_class:
        return error_class(detail=exception_message)

    # Log unknown exceptions for debugging
    logger.error(
        f"Unmapped domain exception: {exception_name} - {exception_message}",
        extra={"exception_type": exception_name},
    )

    # Default to generic authentication error
    return AuthenticationError(
        detail="Authentication failed",
        error_code="AUTHENTICATION_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def create_mobile_friendly_error(error: AuthenticationError) -> dict[str, Any]:
    """
    Create mobile-friendly error response with action-oriented messages.

    Args:
        error: Authentication error

    Returns:
        Dictionary with mobile-optimized error information
    """
    # Mobile-friendly error messages with suggested actions
    mobile_messages = {
        "INVALID_CREDENTIALS": {
            "title": "Login Failed",
            "message": "Check your email and password, then try again.",
            "action": "Try Again",
            "recoverable": True,
        },
        "EMAIL_ALREADY_EXISTS": {
            "title": "Account Exists",
            "message": "An account with this email already exists. Try logging in instead.",
            "action": "Go to Login",
            "recoverable": True,
        },
        "WEAK_PASSWORD": {
            "title": "Password Too Weak",
            "message": "Use at least 8 characters with uppercase, lowercase, and numbers.",
            "action": "Try Another Password",
            "recoverable": True,
        },
        "INVALID_EMAIL_FORMAT": {
            "title": "Invalid Email",
            "message": "Please enter a valid email address.",
            "action": "Check Email",
            "recoverable": True,
        },
        "INVALID_TOKEN": {
            "title": "Session Expired",
            "message": "Your session has expired. Please log in again.",
            "action": "Log In",
            "recoverable": True,
        },
        "RATE_LIMIT_EXCEEDED": {
            "title": "Too Many Attempts",
            "message": "Please wait a moment before trying again.",
            "action": "Wait",
            "recoverable": True,
        },
        "USER_INACTIVE": {
            "title": "Account Suspended",
            "message": "Your account is temporarily suspended. Contact support for help.",
            "action": "Contact Support",
            "recoverable": False,
        },
    }

    mobile_error = mobile_messages.get(
        error.error_code,
        {
            "title": "Error",
            "message": error.detail,
            "action": "Try Again",
            "recoverable": True,
        },
    )

    return {
        "error": {
            "code": error.error_code,
            "title": mobile_error["title"],
            "message": mobile_error["message"],
            "suggested_action": mobile_error["action"],
            "recoverable": mobile_error["recoverable"],
            "status_code": error.status_code,
        }
    }


def log_authentication_event(
    event_type: str,
    user_id: str | None = None,
    email: str | None = None,
    success: bool = True,
    error_code: str | None = None,
    request_id: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Log authentication events for security monitoring.

    Args:
        event_type: Type of authentication event (login, register, logout, etc.)
        user_id: User ID if available
        email: User email if available
        success: Whether the event was successful
        error_code: Error code if event failed
        request_id: Request ID for tracking
        user_agent: User agent string
        ip_address: Client IP address
    """
    event_data = {
        "event_type": event_type,
        "success": success,
        "timestamp": "auto",  # Will be added by logging system
        "request_id": request_id,
        "user_agent": user_agent,
        "ip_address": ip_address,
    }

    if user_id:
        event_data["user_id"] = user_id
    if email:
        event_data["email"] = email
    if error_code:
        event_data["error_code"] = error_code

    if success:
        logger.info(f"Authentication event: {event_type} successful", extra=event_data)
    else:
        logger.warning(
            f"Authentication event: {event_type} failed - {error_code}",
            extra=event_data,
        )
