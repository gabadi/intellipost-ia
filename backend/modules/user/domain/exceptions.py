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
