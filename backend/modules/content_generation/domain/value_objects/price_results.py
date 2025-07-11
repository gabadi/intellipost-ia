"""
Price estimation and validation result value objects for content generation.

This module contains value objects for price estimation and title validation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class ValidationError(BaseValueObject):
    """
    Value object for a single validation error.

    Represents an individual validation error with details
    about the error type, severity, and suggested fixes.
    """

    # Error identification
    error_code: str
    error_message: str
    error_type: str  # critical, warning, suggestion

    # Error context
    field_name: str | None = None
    field_value: str | None = None
    suggested_fix: str | None = None

    # Error metadata
    rule_id: str | None = None
    source: str = "validation_engine"

    # Business rule constants
    VALID_ERROR_TYPES = {"critical", "warning", "suggestion"}
    MAX_MESSAGE_LENGTH = 500
    MAX_FIELD_NAME_LENGTH = 100

    def validate(self) -> None:
        """
        Validate validation error according to business rules.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []

        # Validate error code
        if not isinstance(self.error_code, str) or not self.error_code.strip():
            errors.append("error_code must be a non-empty string")

        # Validate error message
        if not isinstance(self.error_message, str) or not self.error_message.strip():
            errors.append("error_message must be a non-empty string")
        elif len(self.error_message) > self.MAX_MESSAGE_LENGTH:
            errors.append(
                f"error_message length {len(self.error_message)} exceeds "
                f"maximum {self.MAX_MESSAGE_LENGTH}"
            )

        # Validate error type
        if self.error_type not in self.VALID_ERROR_TYPES:
            errors.append(
                f"error_type must be one of {self.VALID_ERROR_TYPES}, got {self.error_type}"
            )

        # Validate field name if provided
        if self.field_name is not None:
            if not isinstance(self.field_name, str):
                errors.append(
                    f"field_name must be a string, got {type(self.field_name).__name__}"
                )
            elif len(self.field_name) > self.MAX_FIELD_NAME_LENGTH:
                errors.append(
                    f"field_name length {len(self.field_name)} exceeds "
                    f"maximum {self.MAX_FIELD_NAME_LENGTH}"
                )

        # Validate source
        if not isinstance(self.source, str) or not self.source.strip():
            errors.append("source must be a non-empty string")

        if errors:
            from shared.value_objects.exceptions import MultipleValidationError

            raise MultipleValidationError(
                "Validation error validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors],
            )

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.

        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.

        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        if field_name == "error_type":
            if field_value not in self.VALID_ERROR_TYPES:
                raise ValueObjectValidationError(
                    f"error_type must be one of {self.VALID_ERROR_TYPES}, got {field_value}"
                )

        elif field_name in ("error_code", "error_message", "source"):
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueObjectValidationError(
                    f"{field_name} must be a non-empty string"
                )

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical error."""
        return self.error_type == "critical"

    @property
    def is_warning(self) -> bool:
        """Check if this is a warning."""
        return self.error_type == "warning"

    @property
    def is_suggestion(self) -> bool:
        """Check if this is a suggestion."""
        return self.error_type == "suggestion"

    @property
    def has_suggested_fix(self) -> bool:
        """Check if error has a suggested fix."""
        return self.suggested_fix is not None and self.suggested_fix.strip()


@dataclass(frozen=True)
class TitleValidationResult(BaseValueObject):
    """
    Value object for title validation results.

    Encapsulates validation results for product titles including
    SEO scoring, compliance checks, and optimization suggestions.
    """

    # Validation status
    valid: bool
    validation_score: float
    seo_score: float
    keyword_optimization: float
    length_score: float
    readability_score: float
    character_count: int
    word_count: int

    # Validation errors and suggestions
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    suggestions: list[ValidationError] = field(default_factory=list)

    # SEO analysis
    detected_keywords: list[str] = field(default_factory=list)
    keyword_density: float = 0.0
    title_uniqueness: float = 1.0

    # Validation metadata
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now())
    validation_engine: str = "title_validator"

    # Business rule constants
    MIN_SCORE = 0.0
    MAX_SCORE = 1.0
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 100
    MAX_ERRORS = 20
    MAX_KEYWORDS = 10

    def validate(self) -> None:
        """
        Validate title validation result according to business rules.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []

        # Validate scores
        score_fields = [
            ("validation_score", self.validation_score),
            ("seo_score", self.seo_score),
            ("keyword_optimization", self.keyword_optimization),
            ("length_score", self.length_score),
            ("readability_score", self.readability_score),
            ("keyword_density", self.keyword_density),
            ("title_uniqueness", self.title_uniqueness),
        ]

        for field_name, score in score_fields:
            if not isinstance(score, int | float):
                errors.append(
                    f"{field_name} must be a number, got {type(score).__name__}"
                )
            elif not (self.MIN_SCORE <= score <= self.MAX_SCORE):
                errors.append(
                    f"{field_name} {score} must be between "
                    f"{self.MIN_SCORE} and {self.MAX_SCORE}"
                )

        # Validate counts
        if not isinstance(self.character_count, int):
            errors.append(
                f"character_count must be an integer, got {type(self.character_count).__name__}"
            )
        elif self.character_count < 0:
            errors.append(
                f"character_count must be non-negative, got {self.character_count}"
            )

        if not isinstance(self.word_count, int):
            errors.append(
                f"word_count must be an integer, got {type(self.word_count).__name__}"
            )
        elif self.word_count < 0:
            errors.append(f"word_count must be non-negative, got {self.word_count}")

        # Validate error lists
        error_lists = [
            ("errors", self.errors),
            ("warnings", self.warnings),
            ("suggestions", self.suggestions),
        ]

        for list_name, error_list in error_lists:
            if len(error_list) > self.MAX_ERRORS:
                errors.append(
                    f"Too many {list_name}: {len(error_list)} (max: {self.MAX_ERRORS})"
                )

            for i, error in enumerate(error_list):
                if not isinstance(error, ValidationError):
                    errors.append(f"{list_name}[{i}] must be a ValidationError")

        # Validate keywords
        if len(self.detected_keywords) > self.MAX_KEYWORDS:
            errors.append(
                f"Too many detected keywords: {len(self.detected_keywords)} (max: {self.MAX_KEYWORDS})"
            )

        for i, keyword in enumerate(self.detected_keywords):
            if not isinstance(keyword, str):
                errors.append(
                    f"detected_keywords[{i}] must be a string, got {type(keyword).__name__}"
                )

        # Validate engine
        if (
            not isinstance(self.validation_engine, str)
            or not self.validation_engine.strip()
        ):
            errors.append("validation_engine must be a non-empty string")

        # Business logic validation
        if not self.valid and len(self.errors) == 0:
            errors.append("Invalid title must have validation errors")

        if self.character_count < self.MIN_TITLE_LENGTH and self.valid:
            errors.append(
                f"Valid title should be at least {self.MIN_TITLE_LENGTH} characters"
            )

        if self.character_count > self.MAX_TITLE_LENGTH:
            errors.append(
                f"Title exceeds maximum length of {self.MAX_TITLE_LENGTH} characters"
            )

        if errors:
            from shared.value_objects.exceptions import MultipleValidationError

            raise MultipleValidationError(
                "Title validation result validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors],
            )

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.

        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.

        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        if field_name in ("validation_score", "seo_score", "keyword_optimization"):
            if not isinstance(field_value, int | float):
                raise ValueObjectValidationError(
                    f"{field_name} must be a number, got {type(field_value).__name__}"
                )
            if not (self.MIN_SCORE <= field_value <= self.MAX_SCORE):
                raise ValueObjectValidationError(
                    f"{field_name} {field_value} must be between "
                    f"{self.MIN_SCORE} and {self.MAX_SCORE}"
                )

        elif field_name in ("character_count", "word_count"):
            if not isinstance(field_value, int):
                raise ValueObjectValidationError(
                    f"{field_name} must be an integer, got {type(field_value).__name__}"
                )
            if field_value < 0:
                raise ValueObjectValidationError(
                    f"{field_name} must be non-negative, got {field_value}"
                )

        elif field_name == "valid":
            if not isinstance(field_value, bool):
                raise ValueObjectValidationError(
                    f"valid must be a boolean, got {type(field_value).__name__}"
                )

    @property
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.warnings) > 0

    @property
    def has_suggestions(self) -> bool:
        """Check if there are validation suggestions."""
        return len(self.suggestions) > 0

    @property
    def overall_quality(self) -> str:
        """Get overall title quality assessment."""
        if self.validation_score >= 0.9:
            return "excellent"
        elif self.validation_score >= 0.7:
            return "good"
        elif self.validation_score >= 0.5:
            return "fair"
        else:
            return "poor"

    @property
    def seo_optimization_level(self) -> str:
        """Get SEO optimization level."""
        if self.seo_score >= 0.8:
            return "highly_optimized"
        elif self.seo_score >= 0.6:
            return "well_optimized"
        elif self.seo_score >= 0.4:
            return "moderately_optimized"
        else:
            return "needs_optimization"

    @property
    def is_valid(self) -> bool:
        """Check if title is valid (backwards compatibility property)."""
        return self.valid

    @property
    def is_production_ready(self) -> bool:
        """Check if title is ready for production."""
        return (
            self.valid
            and self.validation_score >= 0.7
            and not self.has_errors
            and self.character_count >= self.MIN_TITLE_LENGTH
        )


@dataclass(frozen=True)
class PriceEstimationResult(BaseValueObject):
    """
    Value object for price estimation results.

    Encapsulates ML-based price estimation results including
    market analysis, confidence intervals, and pricing recommendations.
    """

    # Primary price estimation
    estimated_price: Decimal
    currency: str
    confidence_score: float
    min_price: Decimal
    max_price: Decimal

    # Market analysis
    market_average: Decimal | None = None

    # Market analysis
    competitor_count: int = 0
    similar_products_analyzed: int = 0
    market_trend: str = "stable"  # rising, falling, stable, volatile

    # Price factors
    pricing_factors: dict[str, float] = field(default_factory=dict)
    quality_multiplier: float = 1.0
    brand_premium: float = 0.0

    # Validation and quality
    title_validation: TitleValidationResult | None = None
    price_validation_errors: list[ValidationError] = field(default_factory=list)

    # Estimation metadata
    estimation_timestamp: datetime = field(default_factory=lambda: datetime.now())
    estimation_engine: str = "price_estimator"
    model_version: str = "1.0"
    data_sources: list[str] = field(default_factory=list)

    # Confidence intervals
    confidence_interval_95: tuple[Decimal, Decimal] | None = None
    confidence_interval_68: tuple[Decimal, Decimal] | None = None

    # Business rule constants
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0
    MIN_PRICE = Decimal("0.01")
    MAX_PRICE = Decimal("1000000.00")
    VALID_CURRENCIES = {"USD", "EUR", "ARS", "BRL", "MXN", "CLP", "COP", "PEN"}
    VALID_TRENDS = {"rising", "falling", "stable", "volatile"}
    MAX_FACTORS = 50
    MAX_DATA_SOURCES = 20
    MAX_ERRORS = 20

    def validate(self) -> None:
        """
        Validate price estimation result according to business rules.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []

        # Validate prices
        price_fields = [
            ("estimated_price", self.estimated_price),
            ("min_price", self.min_price),
            ("max_price", self.max_price),
        ]

        if self.market_average is not None:
            price_fields.append(("market_average", self.market_average))

        for field_name, price in price_fields:
            if not isinstance(price, Decimal):
                errors.append(
                    f"{field_name} must be a Decimal, got {type(price).__name__}"
                )
            elif price < self.MIN_PRICE:
                errors.append(f"{field_name} {price} must be at least {self.MIN_PRICE}")
            elif price > self.MAX_PRICE:
                errors.append(f"{field_name} {price} must not exceed {self.MAX_PRICE}")

        # Validate currency
        if self.currency not in self.VALID_CURRENCIES:
            errors.append(
                f"currency must be one of {self.VALID_CURRENCIES}, got {self.currency}"
            )

        # Validate confidence score
        if not isinstance(self.confidence_score, int | float):
            errors.append(
                f"confidence_score must be a number, got {type(self.confidence_score).__name__}"
            )
        elif not (self.MIN_CONFIDENCE <= self.confidence_score <= self.MAX_CONFIDENCE):
            errors.append(
                f"confidence_score {self.confidence_score} must be between "
                f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
            )

        # Validate market trend
        if self.market_trend not in self.VALID_TRENDS:
            errors.append(
                f"market_trend must be one of {self.VALID_TRENDS}, got {self.market_trend}"
            )

        # Validate counts
        count_fields = [
            ("competitor_count", self.competitor_count),
            ("similar_products_analyzed", self.similar_products_analyzed),
        ]

        for field_name, count in count_fields:
            if not isinstance(count, int):
                errors.append(
                    f"{field_name} must be an integer, got {type(count).__name__}"
                )
            elif count < 0:
                errors.append(f"{field_name} must be non-negative, got {count}")

        # Validate multipliers
        multiplier_fields = [
            ("quality_multiplier", self.quality_multiplier),
            ("brand_premium", self.brand_premium),
        ]

        for field_name, multiplier in multiplier_fields:
            if not isinstance(multiplier, int | float):
                errors.append(
                    f"{field_name} must be a number, got {type(multiplier).__name__}"
                )
            elif multiplier < 0:
                errors.append(f"{field_name} must be non-negative, got {multiplier}")

        # Validate pricing factors
        if len(self.pricing_factors) > self.MAX_FACTORS:
            errors.append(
                f"Too many pricing factors: {len(self.pricing_factors)} (max: {self.MAX_FACTORS})"
            )

        for factor, weight in self.pricing_factors.items():
            if not isinstance(factor, str):
                errors.append("pricing_factors keys must be strings")
                break
            if not isinstance(weight, int | float):
                errors.append("pricing_factors values must be numbers")
                break
            if not (-1.0 <= weight <= 1.0):
                errors.append(
                    f"pricing factor weight {weight} must be between -1.0 and 1.0"
                )

        # Validate data sources
        if len(self.data_sources) > self.MAX_DATA_SOURCES:
            errors.append(
                f"Too many data sources: {len(self.data_sources)} (max: {self.MAX_DATA_SOURCES})"
            )

        for i, source in enumerate(self.data_sources):
            if not isinstance(source, str):
                errors.append(
                    f"data_sources[{i}] must be a string, got {type(source).__name__}"
                )

        # Validate errors list
        if len(self.price_validation_errors) > self.MAX_ERRORS:
            errors.append(
                f"Too many validation errors: {len(self.price_validation_errors)} (max: {self.MAX_ERRORS})"
            )

        for i, error in enumerate(self.price_validation_errors):
            if not isinstance(error, ValidationError):
                errors.append(f"price_validation_errors[{i}] must be a ValidationError")

        # Validate title validation if present
        if self.title_validation is not None and not isinstance(
            self.title_validation, TitleValidationResult
        ):
            errors.append(
                f"title_validation must be a TitleValidationResult, got {type(self.title_validation).__name__}"
            )

        # Validate confidence intervals
        if self.confidence_interval_95 is not None:
            if (
                not isinstance(self.confidence_interval_95, tuple)
                or len(self.confidence_interval_95) != 2
            ):
                errors.append("confidence_interval_95 must be a tuple of two Decimals")
            else:
                lower, upper = self.confidence_interval_95
                if not isinstance(lower, Decimal) or not isinstance(upper, Decimal):
                    errors.append("confidence_interval_95 values must be Decimals")
                elif lower >= upper:
                    errors.append(
                        "confidence_interval_95 lower bound must be less than upper bound"
                    )

        if self.confidence_interval_68 is not None:
            if (
                not isinstance(self.confidence_interval_68, tuple)
                or len(self.confidence_interval_68) != 2
            ):
                errors.append("confidence_interval_68 must be a tuple of two Decimals")
            else:
                lower, upper = self.confidence_interval_68
                if not isinstance(lower, Decimal) or not isinstance(upper, Decimal):
                    errors.append("confidence_interval_68 values must be Decimals")
                elif lower >= upper:
                    errors.append(
                        "confidence_interval_68 lower bound must be less than upper bound"
                    )

        # Business logic validation
        if self.min_price > self.estimated_price:
            errors.append("min_price cannot be greater than estimated_price")

        if self.max_price < self.estimated_price:
            errors.append("max_price cannot be less than estimated_price")

        if self.min_price >= self.max_price:
            errors.append("min_price must be less than max_price")

        if self.market_average is not None:
            if (
                self.market_average < self.min_price
                or self.market_average > self.max_price
            ):
                errors.append(
                    "market_average should be within min_price and max_price range"
                )

        if errors:
            from shared.value_objects.exceptions import MultipleValidationError

            raise MultipleValidationError(
                "Price estimation result validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors],
            )

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.

        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.

        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        if field_name in ("estimated_price", "min_price", "max_price"):
            if not isinstance(field_value, Decimal):
                raise ValueObjectValidationError(
                    f"{field_name} must be a Decimal, got {type(field_value).__name__}"
                )
            if field_value < self.MIN_PRICE:
                raise ValueObjectValidationError(
                    f"{field_name} {field_value} must be at least {self.MIN_PRICE}"
                )
            if field_value > self.MAX_PRICE:
                raise ValueObjectValidationError(
                    f"{field_name} {field_value} must not exceed {self.MAX_PRICE}"
                )

        elif field_name == "currency":
            if field_value not in self.VALID_CURRENCIES:
                raise ValueObjectValidationError(
                    f"currency must be one of {self.VALID_CURRENCIES}, got {field_value}"
                )

        elif field_name == "confidence_score":
            if not isinstance(field_value, int | float):
                raise ValueObjectValidationError(
                    f"confidence_score must be a number, got {type(field_value).__name__}"
                )
            if not (self.MIN_CONFIDENCE <= field_value <= self.MAX_CONFIDENCE):
                raise ValueObjectValidationError(
                    f"confidence_score {field_value} must be between "
                    f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
                )

        elif field_name == "market_trend":
            if field_value not in self.VALID_TRENDS:
                raise ValueObjectValidationError(
                    f"market_trend must be one of {self.VALID_TRENDS}, got {field_value}"
                )

    @property
    def has_high_confidence(self) -> bool:
        """Check if estimation has high confidence."""
        return self.confidence_score >= 0.8

    @property
    def has_validation_errors(self) -> bool:
        """Check if there are price validation errors."""
        return len(self.price_validation_errors) > 0

    @property
    def price_range_width(self) -> Decimal:
        """Calculate the width of the price range."""
        return self.max_price - self.min_price

    @property
    def price_range_percentage(self) -> float:
        """Calculate price range as percentage of estimated price."""
        if self.estimated_price == 0:
            return 0.0
        return float(self.price_range_width / self.estimated_price * 100)

    @property
    def is_above_market_average(self) -> bool:
        """Check if estimated price is above market average."""
        if self.market_average is None:
            return False
        return self.estimated_price > self.market_average

    @property
    def market_position(self) -> str:
        """Get market position relative to average."""
        if self.market_average is None:
            return "unknown"

        if self.estimated_price > self.market_average * Decimal("1.2"):
            return "premium"
        elif self.estimated_price > self.market_average * Decimal("1.1"):
            return "above_average"
        elif self.estimated_price < self.market_average * Decimal("0.8"):
            return "budget"
        elif self.estimated_price < self.market_average * Decimal("0.9"):
            return "below_average"
        else:
            return "average"

    @property
    def estimation_quality(self) -> str:
        """Get overall estimation quality."""
        if (
            self.has_high_confidence
            and self.similar_products_analyzed >= 5
            and not self.has_validation_errors
        ):
            return "high"
        elif self.confidence_score >= 0.6 and self.similar_products_analyzed >= 3:
            return "medium"
        else:
            return "low"

    @property
    def requires_manual_review(self) -> bool:
        """Check if price estimation requires manual review."""
        return (
            not self.has_high_confidence
            or self.has_validation_errors
            or self.similar_products_analyzed < 3
            or self.price_range_percentage > 50
        )

    def get_price_recommendation(self) -> dict[str, Any]:
        """Get price recommendation summary."""
        return {
            "recommended_price": float(self.estimated_price),
            "price_range": {
                "min": float(self.min_price),
                "max": float(self.max_price),
            },
            "currency": self.currency,
            "confidence": self.confidence_score,
            "market_position": self.market_position,
            "estimation_quality": self.estimation_quality,
            "requires_review": self.requires_manual_review,
            "market_trend": self.market_trend,
        }
