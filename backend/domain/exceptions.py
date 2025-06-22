"""
Domain exceptions for the IntelliPost AI backend.

This module contains all domain-specific exceptions that represent
business rule violations and domain errors.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


# User-related exceptions
class UserException(DomainException):
    """Base exception for user-related errors."""

    pass


class UserNotFound(UserException):
    """Raised when a user cannot be found."""

    pass


class UserAlreadyExists(UserException):
    """Raised when attempting to create a user that already exists."""

    pass


class UserNotActive(UserException):
    """Raised when attempting to perform actions on inactive user."""

    pass


class EmailNotVerified(UserException):
    """Raised when user's email is not verified."""

    pass


class InvalidCredentials(UserException):
    """Raised when user credentials are invalid."""

    pass


# Product-related exceptions
class ProductException(DomainException):
    """Base exception for product-related errors."""

    pass


class ProductNotFound(ProductException):
    """Raised when a product cannot be found."""

    pass


class ProductNotReady(ProductException):
    """Raised when product is not ready for processing."""

    pass


class ProductAlreadyPublished(ProductException):
    """Raised when attempting to republish a product."""

    pass


class InvalidProductStatus(ProductException):
    """Raised when product is in invalid status for operation."""

    pass


# AI service exceptions
class AIServiceException(DomainException):
    """Base exception for AI service errors."""

    pass


class AIContentGenerationFailed(AIServiceException):
    """Raised when AI content generation fails."""

    pass


class LowConfidenceContent(AIServiceException):
    """Raised when AI-generated content has low confidence."""

    pass


# MercadoLibre integration exceptions
class MercadoLibreException(DomainException):
    """Base exception for MercadoLibre integration errors."""

    pass


class MercadoLibreAuthenticationFailed(MercadoLibreException):
    """Raised when MercadoLibre authentication fails."""

    pass


class MercadoLibreTokenExpired(MercadoLibreException):
    """Raised when MercadoLibre access token is expired."""

    pass


class MercadoLibreAPIError(MercadoLibreException):
    """Raised when MercadoLibre API returns an error."""

    pass


class ListingCreationFailed(MercadoLibreException):
    """Raised when product listing creation fails."""

    pass


# Authorization and permission exceptions
class AuthorizationException(DomainException):
    """Base exception for authorization errors."""

    pass


class UnauthorizedAccess(AuthorizationException):
    """Raised when user lacks permission for operation."""

    pass


class ForbiddenOperation(AuthorizationException):
    """Raised when operation is forbidden."""

    pass


# Validation exceptions
class ValidationException(DomainException):
    """Base exception for validation errors."""

    pass


class InvalidEmailFormat(ValidationException):
    """Raised when email format is invalid."""

    pass


class InvalidProductData(ValidationException):
    """Raised when product data is invalid."""

    pass


class RequiredFieldMissing(ValidationException):
    """Raised when required field is missing."""

    pass


# External service exceptions
class ExternalServiceException(DomainException):
    """Base exception for external service errors."""

    pass


class EmailServiceException(ExternalServiceException):
    """Raised when email service operations fail."""

    pass


class DatabaseException(ExternalServiceException):
    """Raised when database operations fail."""

    pass


class NetworkException(ExternalServiceException):
    """Raised when network operations fail."""

    pass
