"""
ProductImageMetadata value object for product image metadata.

This module contains the ProductImageMetadata value object that encapsulates
image processing metadata with proper validation and business rules.
"""

from dataclasses import dataclass, field
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class ProductImageMetadata(BaseValueObject):
    """
    Value object for product image metadata.

    Encapsulates processing metadata with validation rules for
    AI processing results, quality metrics, and processing history.
    """

    # AI analysis results
    ai_analysis: dict[str, Any] = field(default_factory=dict)

    # Quality metrics
    quality_score: float | None = None
    sharpness_score: float | None = None
    brightness_score: float | None = None
    contrast_score: float | None = None

    # Object detection
    detected_objects: list[dict[str, Any]] = field(default_factory=list)

    # Color analysis
    dominant_colors: list[str] = field(default_factory=list)
    color_palette: list[str] = field(default_factory=list)

    # Processing history
    processing_steps: list[dict[str, Any]] = field(default_factory=list)
    processing_errors: list[str] = field(default_factory=list)

    # Technical metadata
    compression_ratio: float | None = None
    file_hash: str | None = None

    # Business rule constants
    MIN_QUALITY_SCORE = 0.0
    MAX_QUALITY_SCORE = 1.0
    MAX_DETECTED_OBJECTS = 100
    MAX_DOMINANT_COLORS = 10
    MAX_COLOR_PALETTE = 20
    MAX_PROCESSING_STEPS = 50
    MAX_PROCESSING_ERRORS = 20

    def validate(self) -> None:
        """
        Validate image metadata according to business rules.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []

        # Validate quality scores
        for score_name, score_value in [
            ("quality_score", self.quality_score),
            ("sharpness_score", self.sharpness_score),
            ("brightness_score", self.brightness_score),
            ("contrast_score", self.contrast_score),
        ]:
            if score_value is not None:
                if not isinstance(score_value, int | float):
                    errors.append(
                        f"{score_name} must be a number, got {type(score_value).__name__}"
                    )
                elif not (
                    self.MIN_QUALITY_SCORE <= score_value <= self.MAX_QUALITY_SCORE
                ):
                    errors.append(
                        f"{score_name} {score_value} must be between "
                        f"{self.MIN_QUALITY_SCORE} and {self.MAX_QUALITY_SCORE}"
                    )

        # Validate compression ratio
        if self.compression_ratio is not None:
            if not isinstance(self.compression_ratio, int | float):
                errors.append(
                    f"compression_ratio must be a number, got {type(self.compression_ratio).__name__}"
                )
            elif self.compression_ratio <= 0:
                errors.append(
                    f"compression_ratio must be positive, got {self.compression_ratio}"
                )

        # Validate collections sizes
        if len(self.detected_objects) > self.MAX_DETECTED_OBJECTS:
            errors.append(
                f"Too many detected objects: {len(self.detected_objects)} "
                f"(max: {self.MAX_DETECTED_OBJECTS})"
            )

        if len(self.dominant_colors) > self.MAX_DOMINANT_COLORS:
            errors.append(
                f"Too many dominant colors: {len(self.dominant_colors)} "
                f"(max: {self.MAX_DOMINANT_COLORS})"
            )

        if len(self.color_palette) > self.MAX_COLOR_PALETTE:
            errors.append(
                f"Too many palette colors: {len(self.color_palette)} "
                f"(max: {self.MAX_COLOR_PALETTE})"
            )

        if len(self.processing_steps) > self.MAX_PROCESSING_STEPS:
            errors.append(
                f"Too many processing steps: {len(self.processing_steps)} "
                f"(max: {self.MAX_PROCESSING_STEPS})"
            )

        if len(self.processing_errors) > self.MAX_PROCESSING_ERRORS:
            errors.append(
                f"Too many processing errors: {len(self.processing_errors)} "
                f"(max: {self.MAX_PROCESSING_ERRORS})"
            )

        # Validate color formats
        for color_list, list_name in [
            (self.dominant_colors, "dominant_colors"),
            (self.color_palette, "color_palette"),
        ]:
            for i, color in enumerate(color_list):
                if not isinstance(color, str):
                    errors.append(
                        f"{list_name}[{i}] must be a string, got {type(color).__name__}"
                    )
                elif not self._is_valid_color_format(color):
                    errors.append(f"{list_name}[{i}] has invalid color format: {color}")

        # Validate detected objects structure
        for i, obj in enumerate(self.detected_objects):
            if not isinstance(obj, dict):
                errors.append(
                    f"detected_objects[{i}] must be a dict, got {type(obj).__name__}"
                )
                continue

            # Validate required fields
            required_fields = ["label", "confidence"]
            for field_name in required_fields:
                if field_name not in obj:
                    errors.append(
                        f"detected_objects[{i}] missing required field: {field_name}"
                    )

            # Validate confidence if present
            if "confidence" in obj:
                confidence = obj["confidence"]
                if not isinstance(confidence, int | float):
                    errors.append(
                        f"detected_objects[{i}].confidence must be a number, "
                        f"got {type(confidence).__name__}"
                    )
                elif not (0.0 <= confidence <= 1.0):
                    errors.append(
                        f"detected_objects[{i}].confidence {confidence} "
                        f"must be between 0.0 and 1.0"
                    )

        # Validate processing steps structure
        for i, step in enumerate(self.processing_steps):
            if not isinstance(step, dict):
                errors.append(
                    f"processing_steps[{i}] must be a dict, got {type(step).__name__}"
                )
                continue

            # Validate required fields
            required_fields = ["step_name", "timestamp"]
            for field_name in required_fields:
                if field_name not in step:
                    errors.append(
                        f"processing_steps[{i}] missing required field: {field_name}"
                    )

        if errors:
            from shared.value_objects.exceptions import MultipleValidationError

            raise MultipleValidationError(
                "Image metadata validation failed",
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
            "quality_score",
            "sharpness_score",
            "brightness_score",
            "contrast_score",
        ):
            if field_value is not None:
                if not isinstance(field_value, int | float):
                    raise ValueObjectValidationError(
                        f"{field_name} must be a number, got {type(field_value).__name__}"
                    )
                if not (
                    self.MIN_QUALITY_SCORE <= field_value <= self.MAX_QUALITY_SCORE
                ):
                    raise ValueObjectValidationError(
                        f"{field_name} {field_value} must be between "
                        f"{self.MIN_QUALITY_SCORE} and {self.MAX_QUALITY_SCORE}"
                    )

        elif field_name == "compression_ratio":
            if field_value is not None:
                if not isinstance(field_value, int | float):
                    raise ValueObjectValidationError(
                        f"compression_ratio must be a number, got {type(field_value).__name__}"
                    )
                if field_value <= 0:
                    raise ValueObjectValidationError(
                        f"compression_ratio must be positive, got {field_value}"
                    )

        elif field_name in ("ai_analysis", "detected_objects", "processing_steps"):
            if not isinstance(field_value, dict | list):
                raise ValueObjectValidationError(
                    f"{field_name} must be a dict or list, got {type(field_value).__name__}"
                )

        elif field_name in ("dominant_colors", "color_palette", "processing_errors"):
            if not isinstance(field_value, list):
                raise ValueObjectValidationError(
                    f"{field_name} must be a list, got {type(field_value).__name__}"
                )

    def _is_valid_color_format(self, color: str) -> bool:
        """
        Validate color format (hex, rgb, etc.).

        Args:
            color: Color string to validate.

        Returns:
            True if color format is valid.
        """
        # Check hex format (#RRGGBB or #RGB)
        if color.startswith("#"):
            hex_part = color[1:]
            if len(hex_part) in (3, 6) and all(
                c in "0123456789abcdefABCDEF" for c in hex_part
            ):
                return True

        # Check rgb/rgba format
        if color.startswith(("rgb(", "rgba(")):
            return True

        # Check named colors (basic validation)
        named_colors = {
            "red",
            "green",
            "blue",
            "yellow",
            "orange",
            "purple",
            "pink",
            "brown",
            "black",
            "white",
            "gray",
            "grey",
            "transparent",
        }
        return color.lower() in named_colors

    @property
    def has_ai_analysis(self) -> bool:
        """Check if AI analysis data is present."""
        return bool(self.ai_analysis)

    @property
    def has_quality_metrics(self) -> bool:
        """Check if quality metrics are present."""
        return any(
            [
                self.quality_score is not None,
                self.sharpness_score is not None,
                self.brightness_score is not None,
                self.contrast_score is not None,
            ]
        )

    @property
    def has_object_detection(self) -> bool:
        """Check if object detection results are present."""
        return len(self.detected_objects) > 0

    @property
    def has_color_analysis(self) -> bool:
        """Check if color analysis is present."""
        return len(self.dominant_colors) > 0 or len(self.color_palette) > 0

    @property
    def average_quality_score(self) -> float | None:
        """Calculate average quality score from available metrics."""
        scores = [
            score
            for score in [
                self.quality_score,
                self.sharpness_score,
                self.brightness_score,
                self.contrast_score,
            ]
            if score is not None
        ]

        if not scores:
            return None

        return sum(scores) / len(scores)

    @property
    def processing_status(self) -> str:
        """Get processing status based on steps and errors."""
        if self.processing_errors:
            return "error"
        elif self.processing_steps:
            return "processed"
        else:
            return "pending"

    def add_processing_step(self, step_name: str, **kwargs) -> "ProductImageMetadata":
        """
        Add a processing step to the metadata.

        Args:
            step_name: Name of the processing step.
            **kwargs: Additional step metadata.

        Returns:
            New ProductImageMetadata with added step.
        """
        from datetime import UTC, datetime

        new_step = {
            "step_name": step_name,
            "timestamp": datetime.now(UTC).isoformat(),
            **kwargs,
        }

        new_steps = list(self.processing_steps) + [new_step]

        # Validate step count
        if len(new_steps) > self.MAX_PROCESSING_STEPS:
            new_steps = new_steps[-self.MAX_PROCESSING_STEPS :]

        return self.__class__(
            ai_analysis=self.ai_analysis,
            quality_score=self.quality_score,
            sharpness_score=self.sharpness_score,
            brightness_score=self.brightness_score,
            contrast_score=self.contrast_score,
            detected_objects=self.detected_objects,
            dominant_colors=self.dominant_colors,
            color_palette=self.color_palette,
            processing_steps=new_steps,
            processing_errors=self.processing_errors,
            compression_ratio=self.compression_ratio,
            file_hash=self.file_hash,
        )

    def add_processing_error(self, error_message: str) -> "ProductImageMetadata":
        """
        Add a processing error to the metadata.

        Args:
            error_message: Error message to add.

        Returns:
            New ProductImageMetadata with added error.
        """
        new_errors = list(self.processing_errors) + [error_message]

        # Validate error count
        if len(new_errors) > self.MAX_PROCESSING_ERRORS:
            new_errors = new_errors[-self.MAX_PROCESSING_ERRORS :]

        return self.__class__(
            ai_analysis=self.ai_analysis,
            quality_score=self.quality_score,
            sharpness_score=self.sharpness_score,
            brightness_score=self.brightness_score,
            contrast_score=self.contrast_score,
            detected_objects=self.detected_objects,
            dominant_colors=self.dominant_colors,
            color_palette=self.color_palette,
            processing_steps=self.processing_steps,
            processing_errors=new_errors,
            compression_ratio=self.compression_ratio,
            file_hash=self.file_hash,
        )
