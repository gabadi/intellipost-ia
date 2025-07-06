"""
Domain-specific exceptions for user management module.

This module contains custom exceptions that represent specific business rule
violations and error conditions within the user management domain.
"""


class UserManagementError(Exception):
    """Base exception for all user management domain errors."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class UserAlreadyExistsError(UserManagementError):
    """Raised when attempting to register a user with an email that already exists."""

    def __init__(self, email: str):
        super().__init__(
            f"User with email '{email}' already exists",
            error_code="USER_ALREADY_EXISTS",
        )
        self.email = email


class AccountLockedError(UserManagementError):
    """Raised when attempting to authenticate with a locked account."""

    def __init__(self, failed_attempts: int, max_attempts: int):
        super().__init__(
            f"Account locked due to {failed_attempts} failed login attempts. "
            f"Maximum allowed attempts: {max_attempts}",
            error_code="ACCOUNT_LOCKED",
        )
        self.failed_attempts = failed_attempts
        self.max_attempts = max_attempts


class WeakPasswordError(UserManagementError):
    """Raised when a password does not meet strength requirements."""

    def __init__(self, requirements: str | None = None):
        message = (
            requirements
            or "Password must be at least 8 characters long and contain "
            "uppercase, lowercase, number and special character"
        )
        super().__init__(message, error_code="WEAK_PASSWORD")


class AccountInactiveError(UserManagementError):
    """Raised when attempting to authenticate with an inactive account."""

    def __init__(self, reason: str | None = None):
        message = reason or "Account is not active"
        super().__init__(message, error_code="ACCOUNT_INACTIVE")


class UserNotFoundError(UserManagementError):
    """Raised when a requested user cannot be found."""

    def __init__(self, identifier: str):
        super().__init__(f"User not found: {identifier}", error_code="USER_NOT_FOUND")
        self.identifier = identifier


class InvalidTokenError(UserManagementError):
    """Raised when a token (verification, reset, etc.) is invalid or expired."""

    def __init__(self, token_type: str):
        super().__init__(
            f"Invalid or expired {token_type} token", error_code="INVALID_TOKEN"
        )
        self.token_type = token_type


class InvalidCredentialsError(UserManagementError):
    """Raised when login credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid email or password", error_code="INVALID_CREDENTIALS")


class OperationNotAllowedError(UserManagementError):
    """Raised when an operation is not allowed due to business rules."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Operation '{operation}' not allowed: {reason}",
            error_code="OPERATION_NOT_ALLOWED",
        )
        self.operation = operation
        self.reason = reason


class AuthenticationError(UserManagementError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code="AUTHENTICATION_ERROR")


class ValidationError(UserManagementError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, error_code="VALIDATION_ERROR")
