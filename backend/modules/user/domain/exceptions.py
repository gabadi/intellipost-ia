"""
User domain exceptions.

This module contains exceptions specific to user domain business rules.
Following YAGNI principle - only exceptions with clear use cases are defined.
"""


class UserDomainError(Exception):
    """Base exception for user domain errors."""

    def __init__(self, message: str, user_id: str | None = None) -> None:
        super().__init__(message)
        self.user_id = user_id


class InvalidUserStatusError(UserDomainError):
    """Raised when user status is invalid or transition is not allowed."""

    def __init__(
        self, current_status: str, target_status: str, user_id: str | None = None
    ) -> None:
        message = f"Invalid user status transition from '{current_status}' to '{target_status}'"
        super().__init__(message, user_id)
        self.current_status = current_status
        self.target_status = target_status


class AuthenticationError(UserDomainError):
    """Raised when user authentication fails."""

    def __init__(
        self, message: str = "Authentication failed", user_id: str | None = None
    ) -> None:
        super().__init__(message, user_id)


class UserAlreadyExistsError(UserDomainError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists")
        self.email = email


class UserNotFoundError(UserDomainError):
    """Raised when a user cannot be found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"User not found: {identifier}")
        self.identifier = identifier


class InvalidCredentialsError(UserDomainError):
    """Raised when authentication credentials are invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class UserNotActiveError(UserDomainError):
    """Raised when attempting to authenticate inactive user."""

    def __init__(self) -> None:
        super().__init__("User account is not active")


class RepositoryError(UserDomainError):
    """Raised when repository operations fail."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.original_error = original_error
