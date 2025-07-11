"""
ML attributes value objects for content generation.

This module contains value objects for MercadoLibre attribute mapping results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class MLAttributes(BaseValueObject):
    """
    Value object for MercadoLibre attribute mapping results.

    Encapsulates the mapped attributes from product features to MercadoLibre
    category-specific attributes with validation and confidence scores.
    """

    # Core attributes
    category_id: str
    mapped_attributes: dict[str, Any]
    confidence_score: float

    # Attribute metadata
    required_attributes: list[str] = field(default_factory=list)
    optional_attributes: list[str] = field(default_factory=list)
    mapped_count: int = 0
    missing_required: list[str] = field(default_factory=list)

    # Quality metrics
    completeness_score: float | None = None
    accuracy_score: float | None = None
    relevance_score: float | None = None

    # Mapping details
    mapping_warnings: list[str] = field(default_factory=list)
    mapping_suggestions: list[str] = field(default_factory=list)

    # Metadata
    mapping_timestamp: datetime = field(default_factory=lambda: datetime.now())
    mapping_engine: str = field(default="ml_attribute_mapper")
    mapping_version: str = field(default="1.0")

    # Business rule constants
    MIN_CONFIDENCE_SCORE = 0.0
    MAX_CONFIDENCE_SCORE = 1.0
    MAX_ATTRIBUTES = 100
    MAX_WARNINGS = 50
    MAX_SUGGESTIONS = 50

    def validate(self) -> None:
        """
        Validate ML attributes according to business rules.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []

        # Validate category_id
        if not isinstance(self.category_id, str) or not self.category_id.strip():
            errors.append("category_id must be a non-empty string")

        # Validate confidence score
        if not isinstance(self.confidence_score, int | float):
            errors.append(
                f"confidence_score must be a number, got {type(self.confidence_score).__name__}"
            )
        elif not (
            self.MIN_CONFIDENCE_SCORE
            <= self.confidence_score
            <= self.MAX_CONFIDENCE_SCORE
        ):
            errors.append(
                f"confidence_score {self.confidence_score} must be between "
                f"{self.MIN_CONFIDENCE_SCORE} and {self.MAX_CONFIDENCE_SCORE}"
            )

        # Validate mapped_attributes
        if not isinstance(self.mapped_attributes, dict):
            errors.append(
                f"mapped_attributes must be a dict, got {type(self.mapped_attributes).__name__}"
            )
        elif len(self.mapped_attributes) > self.MAX_ATTRIBUTES:
            errors.append(
                f"Too many mapped attributes: {len(self.mapped_attributes)} (max: {self.MAX_ATTRIBUTES})"
            )

        # Validate mapped_count
        if not isinstance(self.mapped_count, int) or self.mapped_count < 0:
            errors.append("mapped_count must be a non-negative integer")

        # Validate optional scores
        score_fields = [
            ("completeness_score", self.completeness_score),
            ("accuracy_score", self.accuracy_score),
            ("relevance_score", self.relevance_score),
        ]

        for field_name, score in score_fields:
            if score is not None:
                if not isinstance(score, int | float):
                    errors.append(
                        f"{field_name} must be a number, got {type(score).__name__}"
                    )
                elif not (
                    self.MIN_CONFIDENCE_SCORE <= score <= self.MAX_CONFIDENCE_SCORE
                ):
                    errors.append(
                        f"{field_name} {score} must be between "
                        f"{self.MIN_CONFIDENCE_SCORE} and {self.MAX_CONFIDENCE_SCORE}"
                    )

        # Validate lists
        list_fields = [
            ("required_attributes", self.required_attributes),
            ("optional_attributes", self.optional_attributes),
            ("missing_required", self.missing_required),
        ]

        for field_name, field_list in list_fields:
            if not isinstance(field_list, list):
                errors.append(
                    f"{field_name} must be a list, got {type(field_list).__name__}"
                )
            else:
                for i, item in enumerate(field_list):
                    if not isinstance(item, str):
                        errors.append(
                            f"{field_name}[{i}] must be a string, got {type(item).__name__}"
                        )

        # Validate warnings and suggestions
        if len(self.mapping_warnings) > self.MAX_WARNINGS:
            errors.append(
                f"Too many mapping warnings: {len(self.mapping_warnings)} (max: {self.MAX_WARNINGS})"
            )

        if len(self.mapping_suggestions) > self.MAX_SUGGESTIONS:
            errors.append(
                f"Too many mapping suggestions: {len(self.mapping_suggestions)} (max: {self.MAX_SUGGESTIONS})"
            )

        for i, warning in enumerate(self.mapping_warnings):
            if not isinstance(warning, str):
                errors.append(
                    f"mapping_warnings[{i}] must be a string, got {type(warning).__name__}"
                )

        for i, suggestion in enumerate(self.mapping_suggestions):
            if not isinstance(suggestion, str):
                errors.append(
                    f"mapping_suggestions[{i}] must be a string, got {type(suggestion).__name__}"
                )

        # Validate engine and version
        if not isinstance(self.mapping_engine, str) or not self.mapping_engine:
            errors.append("mapping_engine must be a non-empty string")

        if not isinstance(self.mapping_version, str) or not self.mapping_version:
            errors.append("mapping_version must be a non-empty string")

        # Business logic validation
        if self.mapped_count != len(self.mapped_attributes):
            errors.append(
                f"mapped_count {self.mapped_count} must match actual mapped attributes count {len(self.mapped_attributes)}"
            )

        if (
            len(self.missing_required) > 0
            and self.completeness_score
            and self.completeness_score > 0.8
        ):
            errors.append(
                "High completeness score inconsistent with missing required attributes"
            )

        if errors:
            from shared.value_objects.exceptions import MultipleValidationError

            raise MultipleValidationError(
                "ML attributes validation failed",
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
        if field_name in (
            "confidence_score",
            "completeness_score",
            "accuracy_score",
            "relevance_score",
        ):
            if field_value is not None:
                if not isinstance(field_value, int | float):
                    raise ValueObjectValidationError(
                        f"{field_name} must be a number, got {type(field_value).__name__}"
                    )
                if not (
                    self.MIN_CONFIDENCE_SCORE
                    <= field_value
                    <= self.MAX_CONFIDENCE_SCORE
                ):
                    raise ValueObjectValidationError(
                        f"{field_name} {field_value} must be between "
                        f"{self.MIN_CONFIDENCE_SCORE} and {self.MAX_CONFIDENCE_SCORE}"
                    )

        elif field_name == "category_id":
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueObjectValidationError(
                    "category_id must be a non-empty string"
                )

        elif field_name == "mapped_count":
            if not isinstance(field_value, int) or field_value < 0:
                raise ValueObjectValidationError(
                    "mapped_count must be a non-negative integer"
                )

    @property
    def has_warnings(self) -> bool:
        """Check if there are mapping warnings."""
        return len(self.mapping_warnings) > 0

    @property
    def has_suggestions(self) -> bool:
        """Check if there are mapping suggestions."""
        return len(self.mapping_suggestions) > 0

    @property
    def has_missing_required(self) -> bool:
        """Check if there are missing required attributes."""
        return len(self.missing_required) > 0

    @property
    def is_complete(self) -> bool:
        """Check if all required attributes are mapped."""
        return len(self.missing_required) == 0

    @property
    def mapping_quality(self) -> str:
        """Get overall mapping quality assessment."""
        if self.confidence_score >= 0.9 and self.is_complete:
            return "excellent"
        elif self.confidence_score >= 0.7 and self.is_complete:
            return "good"
        elif self.confidence_score >= 0.5:
            return "fair"
        else:
            return "poor"

    @property
    def is_production_ready(self) -> bool:
        """Check if attributes are ready for production."""
        return (
            self.confidence_score >= 0.7 and self.is_complete and not self.has_warnings
        )

    def add_warning(self, warning_message: str) -> "MLAttributes":
        """
        Add a mapping warning to the result.

        Args:
            warning_message: Warning message to add.

        Returns:
            New MLAttributes with added warning.
        """
        new_warnings = list(self.mapping_warnings) + [warning_message]

        if len(new_warnings) > self.MAX_WARNINGS:
            new_warnings = new_warnings[-self.MAX_WARNINGS :]

        return self.__class__(
            category_id=self.category_id,
            mapped_attributes=self.mapped_attributes,
            confidence_score=self.confidence_score,
            required_attributes=self.required_attributes,
            optional_attributes=self.optional_attributes,
            mapped_count=self.mapped_count,
            missing_required=self.missing_required,
            completeness_score=self.completeness_score,
            accuracy_score=self.accuracy_score,
            relevance_score=self.relevance_score,
            mapping_warnings=new_warnings,
            mapping_suggestions=self.mapping_suggestions,
            mapping_timestamp=self.mapping_timestamp,
            mapping_engine=self.mapping_engine,
            mapping_version=self.mapping_version,
        )

    def add_suggestion(self, suggestion_message: str) -> "MLAttributes":
        """
        Add a mapping suggestion to the result.

        Args:
            suggestion_message: Suggestion message to add.

        Returns:
            New MLAttributes with added suggestion.
        """
        new_suggestions = list(self.mapping_suggestions) + [suggestion_message]

        if len(new_suggestions) > self.MAX_SUGGESTIONS:
            new_suggestions = new_suggestions[-self.MAX_SUGGESTIONS :]

        return self.__class__(
            category_id=self.category_id,
            mapped_attributes=self.mapped_attributes,
            confidence_score=self.confidence_score,
            required_attributes=self.required_attributes,
            optional_attributes=self.optional_attributes,
            mapped_count=self.mapped_count,
            missing_required=self.missing_required,
            completeness_score=self.completeness_score,
            accuracy_score=self.accuracy_score,
            relevance_score=self.relevance_score,
            mapping_warnings=self.mapping_warnings,
            mapping_suggestions=new_suggestions,
            mapping_timestamp=self.mapping_timestamp,
            mapping_engine=self.mapping_engine,
            mapping_version=self.mapping_version,
        )
