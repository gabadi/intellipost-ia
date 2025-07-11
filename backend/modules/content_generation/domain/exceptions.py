"""
Content Generation domain exceptions.

This module defines the exception hierarchy for the content generation domain,
providing specific error types for different failure scenarios.
"""

from typing import Any


class ContentGenerationError(Exception):
    """Base exception for content generation domain errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "error_code": self.error_code,
            "details": self.details,
        }


class AIServiceError(ContentGenerationError):
    """Raised when AI service fails to generate content."""

    def __init__(
        self,
        message: str,
        provider: str,
        model_version: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.model_version = model_version
        self.details.update(
            {
                "provider": provider,
                "model_version": model_version,
            }
        )


class AIServiceTimeoutError(AIServiceError):
    """Raised when AI service request times out."""

    def __init__(
        self, message: str, provider: str, timeout_seconds: int, **kwargs: Any
    ):
        super().__init__(message, provider, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.details.update(
            {
                "timeout_seconds": timeout_seconds,
            }
        )


class AIServiceRateLimitError(AIServiceError):
    """Raised when AI service rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        provider: str,
        retry_after_seconds: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, provider, **kwargs)
        self.retry_after_seconds = retry_after_seconds
        self.details.update(
            {
                "retry_after_seconds": retry_after_seconds,
            }
        )


class AIServiceQuotaExceededError(AIServiceError):
    """Raised when AI service quota is exceeded."""

    def __init__(self, message: str, provider: str, quota_type: str, **kwargs: Any):
        super().__init__(message, provider, **kwargs)
        self.quota_type = quota_type
        self.details.update(
            {
                "quota_type": quota_type,
            }
        )


class CategoryDetectionError(ContentGenerationError):
    """Raised when category detection fails."""

    def __init__(
        self,
        message: str,
        product_features: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.product_features = product_features or {}
        self.details.update(
            {
                "product_features": product_features,
            }
        )


class CategoryValidationError(CategoryDetectionError):
    """Raised when category validation fails."""

    def __init__(
        self,
        message: str,
        category_id: str,
        validation_errors: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.category_id = category_id
        self.validation_errors = validation_errors or {}
        self.details.update(
            {
                "category_id": category_id,
                "validation_errors": validation_errors,
            }
        )


class InvalidContentError(ContentGenerationError):
    """Raised when generated content doesn't meet quality standards."""

    def __init__(
        self,
        message: str,
        content_type: str,
        validation_errors: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.content_type = content_type
        self.validation_errors = validation_errors or {}
        self.details.update(
            {
                "content_type": content_type,
                "validation_errors": validation_errors,
            }
        )


class TitleGenerationError(InvalidContentError):
    """Raised when title generation fails quality checks."""

    def __init__(self, message: str, generated_title: str | None = None, **kwargs: Any):
        super().__init__(message, "title", **kwargs)
        self.generated_title = generated_title
        self.details.update(
            {
                "generated_title": generated_title,
            }
        )


class DescriptionGenerationError(InvalidContentError):
    """Raised when description generation fails quality checks."""

    def __init__(
        self, message: str, generated_description: str | None = None, **kwargs: Any
    ):
        super().__init__(message, "description", **kwargs)
        self.generated_description = generated_description
        self.details.update(
            {
                "generated_description": generated_description,
            }
        )


class AttributeMappingError(ContentGenerationError):
    """Raised when attribute mapping fails."""

    def __init__(
        self,
        message: str,
        category_id: str,
        attribute_errors: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.category_id = category_id
        self.attribute_errors = attribute_errors or {}
        self.details.update(
            {
                "category_id": category_id,
                "attribute_errors": attribute_errors,
            }
        )


class AttributeValidationError(AttributeMappingError):
    """Raised when attribute validation fails."""

    def __init__(
        self,
        message: str,
        category_id: str,
        attribute_name: str,
        attribute_value: Any,
        **kwargs: Any,
    ):
        super().__init__(message, category_id, **kwargs)
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.details.update(
            {
                "attribute_name": attribute_name,
                "attribute_value": attribute_value,
            }
        )


class PriceEstimationError(ContentGenerationError):
    """Raised when price estimation fails."""

    def __init__(
        self, message: str, estimated_price: float | None = None, **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.estimated_price = estimated_price
        self.details.update(
            {
                "estimated_price": estimated_price,
            }
        )


class ImageProcessingError(ContentGenerationError):
    """Raised when image processing fails."""

    def __init__(
        self,
        message: str,
        image_path: str,
        processing_step: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.image_path = image_path
        self.processing_step = processing_step
        self.details.update(
            {
                "image_path": image_path,
                "processing_step": processing_step,
            }
        )


class ContentValidationError(ContentGenerationError):
    """Raised when content validation fails."""

    def __init__(
        self,
        message: str,
        validation_rules: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.validation_rules = validation_rules or {}
        self.details.update(
            {
                "validation_rules": validation_rules,
            }
        )


class ProcessingTimeoutError(ContentGenerationError):
    """Raised when content generation processing times out."""

    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        current_step: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.current_step = current_step
        self.details.update(
            {
                "timeout_seconds": timeout_seconds,
                "current_step": current_step,
            }
        )


class ConfigurationError(ContentGenerationError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.details.update(
            {
                "config_key": config_key,
            }
        )


class ExternalServiceError(ContentGenerationError):
    """Raised when external service integration fails."""

    def __init__(
        self,
        message: str,
        service_name: str,
        service_url: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.service_url = service_url
        self.details.update(
            {
                "service_name": service_name,
                "service_url": service_url,
            }
        )


class MercadoLibreAPIError(ExternalServiceError):
    """Raised when MercadoLibre API integration fails."""

    def __init__(
        self,
        message: str,
        api_endpoint: str,
        status_code: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, "MercadoLibre API", **kwargs)
        self.api_endpoint = api_endpoint
        self.status_code = status_code
        self.details.update(
            {
                "api_endpoint": api_endpoint,
                "status_code": status_code,
            }
        )


class ContentGenerationCancelledError(ContentGenerationError):
    """Raised when content generation is cancelled."""

    def __init__(self, message: str, reason: str | None = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.reason = reason
        self.details.update(
            {
                "reason": reason,
            }
        )


class MaxRetriesExceededError(ContentGenerationError):
    """Raised when maximum retry attempts are exceeded."""

    def __init__(
        self,
        message: str,
        max_retries: int,
        last_error: Exception | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.last_error = last_error
        self.details.update(
            {
                "max_retries": max_retries,
                "last_error": str(last_error) if last_error else None,
            }
        )


class InsufficientDataError(ContentGenerationError):
    """Raised when insufficient data is provided for content generation."""

    def __init__(
        self, message: str, required_fields: list[str] | None = None, **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.required_fields = required_fields or []
        self.details.update(
            {
                "required_fields": required_fields,
            }
        )


class QualityThresholdError(ContentGenerationError):
    """Raised when generated content doesn't meet quality thresholds."""

    def __init__(
        self, message: str, quality_score: float, threshold: float, **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.quality_score = quality_score
        self.threshold = threshold
        self.details.update(
            {
                "quality_score": quality_score,
                "threshold": threshold,
            }
        )


class RepositoryError(ContentGenerationError):
    """Raised when repository operations fail."""

    def __init__(
        self,
        message: str,
        operation: str,
        entity_type: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.entity_type = entity_type
        self.details.update(
            {
                "operation": operation,
                "entity_type": entity_type,
            }
        )


class EntityNotFoundError(RepositoryError):
    """Raised when requested entity is not found."""

    def __init__(self, message: str, entity_type: str, entity_id: str, **kwargs: Any):
        super().__init__(message, "find", entity_type, **kwargs)
        self.entity_id = entity_id
        self.details.update(
            {
                "entity_id": entity_id,
            }
        )


class EntityAlreadyExistsError(RepositoryError):
    """Raised when entity already exists."""

    def __init__(self, message: str, entity_type: str, entity_id: str, **kwargs: Any):
        super().__init__(message, "create", entity_type, **kwargs)
        self.entity_id = entity_id
        self.details.update(
            {
                "entity_id": entity_id,
            }
        )


class TypeSafetyViolationError(ContentGenerationError):
    """Raised when type safety is violated in service layer."""

    def __init__(
        self,
        message: str,
        service_name: str,
        method_name: str,
        expected_type: str,
        actual_type: str,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.method_name = method_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.details.update(
            {
                "service_name": service_name,
                "method_name": method_name,
                "expected_type": expected_type,
                "actual_type": actual_type,
            }
        )
