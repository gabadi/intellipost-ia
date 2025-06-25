"""Tests for confidence score value object."""

import pytest

from backend.modules.confidence_score import ConfidenceScore


class TestConfidenceScore:
    """Test the ConfidenceScore value object."""

    def test_valid_score_creation(self):
        """Test creating a valid confidence score."""
        score = ConfidenceScore(0.8)
        assert score.score == 0.8

    def test_invalid_score_too_low(self):
        """Test that scores below 0.0 raise ValueError."""
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            ConfidenceScore(-0.1)

    def test_invalid_score_too_high(self):
        """Test that scores above 1.0 raise ValueError."""
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            ConfidenceScore(1.1)

    def test_boundary_values(self):
        """Test boundary values 0.0 and 1.0."""
        low_score = ConfidenceScore(0.0)
        high_score = ConfidenceScore(1.0)
        assert low_score.score == 0.0
        assert high_score.score == 1.0

    def test_is_high_property(self):
        """Test is_high property for various scores."""
        high_score = ConfidenceScore(0.9)
        medium_score = ConfidenceScore(0.7)
        low_score = ConfidenceScore(0.3)

        assert high_score.is_high is True
        assert medium_score.is_high is False
        assert low_score.is_high is False

    def test_is_medium_property(self):
        """Test is_medium property for various scores."""
        high_score = ConfidenceScore(0.9)
        medium_score = ConfidenceScore(0.7)
        low_score = ConfidenceScore(0.3)

        assert high_score.is_medium is False
        assert medium_score.is_medium is True
        assert low_score.is_medium is False

    def test_is_low_property(self):
        """Test is_low property for various scores."""
        high_score = ConfidenceScore(0.9)
        medium_score = ConfidenceScore(0.7)
        low_score = ConfidenceScore(0.3)

        assert high_score.is_low is False
        assert medium_score.is_low is False
        assert low_score.is_low is True

    def test_level_property(self):
        """Test level property returns correct string representation."""
        high_score = ConfidenceScore(0.9)
        medium_score = ConfidenceScore(0.7)
        low_score = ConfidenceScore(0.3)

        assert high_score.level == "high"
        assert medium_score.level == "medium"
        assert low_score.level == "low"

    def test_class_methods(self):
        """Test convenience class methods."""
        high = ConfidenceScore.high()
        medium = ConfidenceScore.medium()
        low = ConfidenceScore.low()

        assert high.score == 0.9
        assert medium.score == 0.7
        assert low.score == 0.3

        assert high.is_high is True
        assert medium.is_medium is True
        assert low.is_low is True

    def test_threshold_edge_cases(self):
        """Test scores exactly at threshold boundaries."""
        # Exactly at high threshold
        high_threshold = ConfidenceScore(0.8)
        assert high_threshold.is_high is True
        assert high_threshold.is_medium is False

        # Just below high threshold
        just_below_high = ConfidenceScore(0.79)
        assert just_below_high.is_high is False
        assert just_below_high.is_medium is True

        # Exactly at medium threshold
        medium_threshold = ConfidenceScore(0.5)
        assert medium_threshold.is_medium is True
        assert medium_threshold.is_low is False

        # Just below medium threshold
        just_below_medium = ConfidenceScore(0.49)
        assert just_below_medium.is_medium is False
        assert just_below_medium.is_low is True

    def test_frozen_dataclass(self):
        """Test that ConfidenceScore is immutable."""
        score = ConfidenceScore(0.8)
        with pytest.raises(AttributeError):
            score.score = 0.9  # type: ignore

    def test_equality(self):
        """Test equality comparison between confidence scores."""
        score1 = ConfidenceScore(0.8)
        score2 = ConfidenceScore(0.8)
        score3 = ConfidenceScore(0.7)

        assert score1 == score2
        assert score1 != score3
