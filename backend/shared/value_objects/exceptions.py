"""
Value object validation exceptions.

This module defines exception classes for value object validation errors
and provides specific error types for different validation scenarios.
"""

from typing import Any


class ValueObjectError(Exception):
    """Base exception for value object errors."""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_value: Any = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.field_name = field_name
        self.field_value = field_value
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "field_name": self.field_name,
            "field_value": self.field_value,
            "details": self.details,
        }


class ValueObjectValidationError(ValueObjectError):
    """Raised when value object validation fails."""

    def __init__(
        self,
        message: str,
        field_name: str,
        field_value: Any = None,
        validation_rule: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, field_name, field_value, **kwargs)
        self.validation_rule = validation_rule
        if validation_rule:
            self.details.update({"validation_rule": validation_rule})


class ValueObjectSerializationError(ValueObjectError):
    """Raised when value object serialization fails."""

    def __init__(
        self,
        message: str,
        serialization_format: str,
        original_error: Exception | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.serialization_format = serialization_format
        self.original_error = original_error
        self.details.update(
            {
                "serialization_format": serialization_format,
                "original_error": str(original_error) if original_error else None,
            }
        )


class ValueObjectDeserializationError(ValueObjectError):
    """Raised when value object deserialization fails."""

    def __init__(
        self,
        message: str,
        input_data: Any,
        expected_type: str | None = None,
        original_error: Exception | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, **kwargs)
        self.input_data = input_data
        self.expected_type = expected_type
        self.original_error = original_error
        self.details.update(
            {
                "input_data": input_data,
                "expected_type": expected_type,
                "original_error": str(original_error) if original_error else None,
            }
        )


class RequiredFieldError(ValueObjectValidationError):
    """Raised when a required field is missing or empty."""

    def __init__(self, field_name: str, **kwargs: Any):
        super().__init__(
            f"Required field '{field_name}' is missing or empty",
            field_name,
            validation_rule="required",
            **kwargs,
        )


class InvalidFieldTypeError(ValueObjectValidationError):
    """Raised when a field has an invalid type."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        expected_type: str,
        **kwargs: Any,
    ):
        super().__init__(
            f"Field '{field_name}' must be of type {expected_type}, got {type(field_value).__name__}",
            field_name,
            field_value,
            validation_rule="type_check",
            **kwargs,
        )
        self.expected_type = expected_type
        self.details.update({"expected_type": expected_type})


class InvalidFieldValueError(ValueObjectValidationError):
    """Raised when a field has an invalid value."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        constraint_description: str,
        **kwargs: Any,
    ):
        super().__init__(
            f"Field '{field_name}' has invalid value: {constraint_description}",
            field_name,
            field_value,
            validation_rule="value_constraint",
            **kwargs,
        )
        self.constraint_description = constraint_description
        self.details.update({"constraint_description": constraint_description})


class InvalidFieldLengthError(ValueObjectValidationError):
    """Raised when a field has an invalid length."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        min_length: int | None = None,
        max_length: int | None = None,
        **kwargs: Any,
    ):
        actual_length = len(field_value) if hasattr(field_value, "__len__") else None
        constraint_parts = []

        if min_length is not None:
            constraint_parts.append(f"minimum {min_length}")
        if max_length is not None:
            constraint_parts.append(f"maximum {max_length}")

        constraint_description = " and ".join(constraint_parts)

        super().__init__(
            f"Field '{field_name}' length ({actual_length}) does not meet {constraint_description} constraint",
            field_name,
            field_value,
            validation_rule="length_constraint",
            **kwargs,
        )
        self.min_length = min_length
        self.max_length = max_length
        self.actual_length = actual_length
        self.details.update(
            {
                "min_length": min_length,
                "max_length": max_length,
                "actual_length": actual_length,
            }
        )


class InvalidFieldRangeError(ValueObjectValidationError):
    """Raised when a numeric field is outside valid range."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        min_value: float | int | None = None,
        max_value: float | int | None = None,
        **kwargs: Any,
    ):
        constraint_parts = []

        if min_value is not None:
            constraint_parts.append(f"minimum {min_value}")
        if max_value is not None:
            constraint_parts.append(f"maximum {max_value}")

        constraint_description = " and ".join(constraint_parts)

        super().__init__(
            f"Field '{field_name}' value ({field_value}) does not meet {constraint_description} constraint",
            field_name,
            field_value,
            validation_rule="range_constraint",
            **kwargs,
        )
        self.min_value = min_value
        self.max_value = max_value
        self.details.update(
            {
                "min_value": min_value,
                "max_value": max_value,
            }
        )


class InvalidFieldFormatError(ValueObjectValidationError):
    """Raised when a field doesn't match expected format."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        expected_format: str,
        **kwargs: Any,
    ):
        super().__init__(
            f"Field '{field_name}' does not match expected format: {expected_format}",
            field_name,
            field_value,
            validation_rule="format_constraint",
            **kwargs,
        )
        self.expected_format = expected_format
        self.details.update({"expected_format": expected_format})


class MultipleValidationError(ValueObjectError):
    """Raised when multiple validation errors occur."""

    def __init__(self, errors: list[ValueObjectValidationError]):
        self.errors = errors
        error_messages = [str(error) for error in errors]
        super().__init__(
            f"Multiple validation errors occurred: {'; '.join(error_messages)}"
        )
        self.details.update(
            {
                "error_count": len(errors),
                "individual_errors": [error.to_dict() for error in errors],
            }
        )
