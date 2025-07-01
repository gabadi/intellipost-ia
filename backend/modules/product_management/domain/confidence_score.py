"""
Confidence score definitions for AI-generated content.

This module contains the confidence scoring system for AI content generation.
Based on PR feedback, implementing numeric confidence scores instead of enum.
"""

from dataclasses import dataclass
from typing import ClassVar

from .exceptions import InvalidConfidenceScoreError


@dataclass(frozen=True)
class ConfidenceScore:
    """
    Numeric confidence score for AI-generated content.

    Represents confidence as a float between 0.0 and 1.0, with named
    thresholds for common use cases.
    """

    score: float

    # Threshold constants
    HIGH_THRESHOLD: ClassVar[float] = 0.8
    MEDIUM_THRESHOLD: ClassVar[float] = 0.5
    LOW_THRESHOLD: ClassVar[float] = 0.2

    def __post_init__(self) -> None:
        """Validate score is within valid range."""
        if not (0.0 <= self.score <= 1.0):
            raise InvalidConfidenceScoreError(self.score)

    @property
    def is_high(self) -> bool:
        """Check if confidence is high (>= 0.8)."""
        return self.score >= self.HIGH_THRESHOLD

    @property
    def is_medium(self) -> bool:
        """Check if confidence is medium (>= 0.5 and < 0.8)."""
        return self.MEDIUM_THRESHOLD <= self.score < self.HIGH_THRESHOLD

    @property
    def is_low(self) -> bool:
        """Check if confidence is low (< 0.5)."""
        return self.score < self.MEDIUM_THRESHOLD

    @property
    def level(self) -> str:
        """Get human-readable confidence level."""
        if self.is_high:
            return "high"
        elif self.is_medium:
            return "medium"
        else:
            return "low"

    @classmethod
    def high(cls) -> "ConfidenceScore":
        """Create a high confidence score (0.9)."""
        return cls(0.9)

    @classmethod
    def medium(cls) -> "ConfidenceScore":
        """Create a medium confidence score (0.7)."""
        return cls(0.7)

    @classmethod
    def low(cls) -> "ConfidenceScore":
        """Create a low confidence score (0.3)."""
        return cls(0.3)
