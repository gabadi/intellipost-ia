"""
Domain exceptions for the IntelliPost AI backend.

This module contains essential domain-specific exceptions following YAGNI principles.
Only exceptions with immediate, clear use cases are included.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class ValidationException(DomainException):
    """Exception for domain validation errors."""

    pass


class NotFoundError(DomainException):
    """Exception for when a requested resource cannot be found."""

    pass
