"""
Confidence Score domain entity.

This module defines the ConfidenceScore entity which represents
the confidence levels for different aspects of AI-generated content.
"""

from dataclasses import dataclass
from typing import Any

from modules.content_generation.domain.exceptions import InvalidContentError


@dataclass(frozen=True)
class ConfidenceScore:
    """
    Domain entity representing confidence scores for AI-generated content.

    This entity encapsulates confidence levels for different components
    of generated content (title, description, category, etc.).
    """

    overall: float
    breakdown: dict[str, float]

    def __post_init__(self):
        """Validate the confidence score entity."""
        self._validate_overall_score()
        self._validate_breakdown_scores()

    def _validate_overall_score(self):
        """Validate overall confidence score."""
        if not (0.0 <= self.overall <= 1.0):
            raise InvalidContentError(
                "Overall confidence must be between 0.0 and 1.0", "confidence"
            )

    def _validate_breakdown_scores(self):
        """Validate breakdown confidence scores."""
        for _component, score in self.breakdown.items():
            if not (0.0 <= score <= 1.0):
                raise InvalidContentError(
                    "Breakdown confidence scores must be between 0.0 and 1.0",
                    "confidence",
                )

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the overall confidence is high."""
        return self.overall >= threshold

    def get_weak_components(self, threshold: float = 0.6) -> dict[str, float]:
        """Get components with confidence below the threshold."""
        return {
            component: score
            for component, score in self.breakdown.items()
            if score < threshold
        }

    def get_strong_components(self, threshold: float = 0.8) -> dict[str, float]:
        """Get components with confidence above the threshold."""
        return {
            component: score
            for component, score in self.breakdown.items()
            if score >= threshold
        }

    def calculate_weighted_score(self, weights: dict[str, float]) -> float:
        """Calculate a weighted confidence score based on component importance."""
        if not weights:
            return self.overall

        total_weight = sum(weights.values())
        if total_weight == 0:
            return self.overall

        weighted_sum = 0.0
        for component, weight in weights.items():
            if component in self.breakdown:
                weighted_sum += self.breakdown[component] * weight

        return weighted_sum / total_weight

    def to_dict(self) -> dict[str, Any]:
        """Convert the confidence score to a dictionary representation."""
        return {
            "overall": self.overall,
            "breakdown": self.breakdown.copy(),
        }

    def meets_threshold(self, threshold: float = 0.7) -> bool:
        """Check if the overall confidence meets the threshold."""
        return self.overall >= threshold

    def has_low_component_confidence(self, threshold: float = 0.5) -> bool:
        """Check if any component has low confidence."""
        return any(score < threshold for score in self.breakdown.values())

    @classmethod
    def from_breakdown(cls, breakdown: dict[str, float]) -> "ConfidenceScore":
        """Create a ConfidenceScore from a breakdown dictionary."""
        if not breakdown:
            raise InvalidContentError("Breakdown cannot be empty", "confidence")

        overall = sum(breakdown.values()) / len(breakdown)
        return cls(overall=overall, breakdown=breakdown)

    @classmethod
    def create_default(cls) -> "ConfidenceScore":
        """Create a default confidence score with moderate confidence."""
        breakdown = {
            "title": 0.5,
            "description": 0.5,
            "category": 0.5,
            "price": 0.5,
            "attributes": 0.5,
        }
        return cls.from_breakdown(breakdown)
