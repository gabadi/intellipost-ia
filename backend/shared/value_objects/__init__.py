"""
Shared value objects for domain modeling.

This module provides base classes and utilities for creating immutable
value objects that can be shared across different domain modules.
"""

from .base import BaseValueObject, ValueObjectError
from .exceptions import (
    InvalidFieldFormatError,
    InvalidFieldLengthError,
    InvalidFieldRangeError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectDeserializationError,
    ValueObjectSerializationError,
    ValueObjectValidationError,
)
from .price_range import PriceRange
from .protocols import (
    MercadoLibreValueObjectProtocol,
    SerializableValueObjectProtocol,
    ValidatedValueObjectProtocol,
    ValueObjectProtocol,
)

__all__ = [
    "BaseValueObject",
    "ValueObjectError",
    "ValueObjectProtocol",
    "SerializableValueObjectProtocol",
    "ValidatedValueObjectProtocol",
    "MercadoLibreValueObjectProtocol",
    "ValueObjectValidationError",
    "ValueObjectSerializationError",
    "ValueObjectDeserializationError",
    "RequiredFieldError",
    "InvalidFieldTypeError",
    "InvalidFieldValueError",
    "InvalidFieldLengthError",
    "InvalidFieldRangeError",
    "InvalidFieldFormatError",
    "MultipleValidationError",
    "PriceRange",
]
