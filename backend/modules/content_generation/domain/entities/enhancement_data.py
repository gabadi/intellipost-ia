"""
Enhancement Data domain entity.

This module defines the EnhancementData entity that encapsulates
all data needed for content enhancement operations.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EnhancementData:
    """
    Domain entity representing data for content enhancement operations.

    This entity encapsulates all the information needed to enhance
    generated content including type-specific parameters, style preferences,
    and constraints.

    Attributes:
        enhancement_type: Type of enhancement (title, description, attributes)
        target_length: Optional target length for enhanced content
        style_preferences: List of style preferences for enhancement
        keywords: List of keywords to include in enhancement
        constraints: Dictionary of constraints for enhancement
        custom_attributes: Additional custom attributes for enhancement
        focus_areas: Areas to focus on during enhancement
        tone: Desired tone for the enhanced content
        audience_context: Additional context about target audience
    """

    enhancement_type: str
    target_length: int | None = None
    style_preferences: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    constraints: dict[str, str] = field(default_factory=dict)
    custom_attributes: dict[str, Any] = field(default_factory=dict)
    focus_areas: list[str] = field(default_factory=list)
    tone: str | None = None
    audience_context: str | None = None

    def __post_init__(self) -> None:
        """Validate enhancement data after initialization."""
        valid_types = {"title", "description", "attributes"}
        if self.enhancement_type not in valid_types:
            raise ValueError(
                f"Invalid enhancement_type '{self.enhancement_type}'. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        if self.target_length is not None and self.target_length <= 0:
            raise ValueError("target_length must be positive")

    @classmethod
    def create_minimal(cls, enhancement_type: str) -> "EnhancementData":
        """
        Create minimal enhancement data with just the type.

        Args:
            enhancement_type: Type of enhancement

        Returns:
            EnhancementData instance with minimal configuration
        """
        return cls(enhancement_type=enhancement_type)

    @classmethod
    def from_dict_legacy(cls, data: dict[str, Any]) -> "EnhancementData":
        """
        Create EnhancementData from legacy dictionary format.

        This method provides backward compatibility with the old
        additional_data dict format used throughout the system.

        Args:
            data: Legacy dictionary with enhancement data

        Returns:
            EnhancementData instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Legacy data must be a dictionary")

        # Extract enhancement type (required)
        enhancement_type = data.get("enhancement_type")
        if not enhancement_type:
            raise ValueError("enhancement_type is required in legacy data")

        # Extract optional fields with defaults
        target_length = data.get("target_length")
        if target_length is not None:
            target_length = int(target_length)

        style_preferences = data.get("style_preferences", [])
        if isinstance(style_preferences, str):
            style_preferences = [style_preferences]
        elif not isinstance(style_preferences, list):
            style_preferences = []

        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]
        elif not isinstance(keywords, list):
            keywords = []

        constraints = data.get("constraints", {})
        if not isinstance(constraints, dict):
            constraints = {}

        custom_attributes = data.get("custom_attributes", {})
        if not isinstance(custom_attributes, dict):
            custom_attributes = {}

        focus_areas = data.get("focus_areas", [])
        if isinstance(focus_areas, str):
            focus_areas = [focus_areas]
        elif not isinstance(focus_areas, list):
            focus_areas = []

        tone = data.get("tone")
        audience_context = data.get("audience_context")

        # Handle legacy fields that might be in different locations
        # Support common legacy patterns
        if "max_length" in data and target_length is None:
            target_length = int(data["max_length"])

        if "styles" in data and not style_preferences:
            styles = data["styles"]
            if isinstance(styles, str):
                style_preferences = [styles]
            elif isinstance(styles, list):
                style_preferences = styles

        if "keyword_list" in data and not keywords:
            keyword_list = data["keyword_list"]
            if isinstance(keyword_list, str):
                keywords = [keyword_list]
            elif isinstance(keyword_list, list):
                keywords = keyword_list

        return cls(
            enhancement_type=enhancement_type,
            target_length=target_length,
            style_preferences=style_preferences,
            keywords=keywords,
            constraints=constraints,
            custom_attributes=custom_attributes,
            focus_areas=focus_areas,
            tone=tone,
            audience_context=audience_context,
        )

    def to_dict_legacy(self) -> dict[str, Any]:
        """
        Convert to legacy dictionary format.

        This method provides backward compatibility by converting
        the EnhancementData to the old dict format.

        Returns:
            Dictionary in legacy format
        """
        result = {
            "enhancement_type": self.enhancement_type,
        }

        if self.target_length is not None:
            result["target_length"] = self.target_length

        if self.style_preferences:
            result["style_preferences"] = self.style_preferences

        if self.keywords:
            result["keywords"] = self.keywords

        if self.constraints:
            result["constraints"] = self.constraints

        if self.custom_attributes:
            result["custom_attributes"] = self.custom_attributes

        if self.focus_areas:
            result["focus_areas"] = self.focus_areas

        if self.tone:
            result["tone"] = self.tone

        if self.audience_context:
            result["audience_context"] = self.audience_context

        return result

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary format.

        Returns:
            Dictionary representation of the enhancement data
        """
        return self.to_dict_legacy()

    def is_valid_for_type(self) -> bool:
        """
        Check if the enhancement data is valid for the specified type.

        Returns:
            True if valid for the enhancement type, False otherwise
        """
        if self.enhancement_type == "title":
            return self._is_valid_for_title()
        elif self.enhancement_type == "description":
            return self._is_valid_for_description()
        elif self.enhancement_type == "attributes":
            return self._is_valid_for_attributes()

        return False

    def _is_valid_for_title(self) -> bool:
        """Check if valid for title enhancement."""
        # Title enhancements should have reasonable length constraints
        if self.target_length is not None:
            return 10 <= self.target_length <= 60  # ML title limits
        return True

    def _is_valid_for_description(self) -> bool:
        """Check if valid for description enhancement."""
        # Description enhancements can have longer content
        if self.target_length is not None:
            return 50 <= self.target_length <= 5000  # Reasonable description limits
        return True

    def _is_valid_for_attributes(self) -> bool:
        """Check if valid for attributes enhancement."""
        # Attributes enhancement typically doesn't use target_length
        return True

    def get_type_specific_constraints(self) -> dict[str, Any]:
        """
        Get constraints specific to the enhancement type.

        Returns:
            Dictionary with type-specific constraints
        """
        base_constraints = dict(self.constraints)

        if self.enhancement_type == "title":
            if self.target_length:
                base_constraints["max_length"] = min(self.target_length, 60)
            else:
                base_constraints["max_length"] = 60
        elif self.enhancement_type == "description":
            if self.target_length:
                base_constraints["target_length"] = self.target_length
        elif self.enhancement_type == "attributes":
            # Attributes don't typically have length constraints
            pass

        return base_constraints

    def get_enhancement_context(self) -> dict[str, Any]:
        """
        Get context information for enhancement operations.

        Returns:
            Dictionary with context information for AI services
        """
        context = {
            "type": self.enhancement_type,
            "constraints": self.get_type_specific_constraints(),
        }

        if self.style_preferences:
            context["style_preferences"] = self.style_preferences

        if self.keywords:
            context["keywords"] = self.keywords

        if self.focus_areas:
            context["focus_areas"] = self.focus_areas

        if self.tone:
            context["tone"] = self.tone

        if self.audience_context:
            context["audience_context"] = self.audience_context

        if self.custom_attributes:
            context["custom_attributes"] = self.custom_attributes

        return context

    def merge_with_legacy_data(self, legacy_data: dict[str, Any]) -> "EnhancementData":
        """
        Merge current enhancement data with legacy data.

        This allows for gradual migration where some services might
        still provide additional legacy fields.

        Args:
            legacy_data: Additional legacy data to merge

        Returns:
            New EnhancementData instance with merged data
        """
        merged_dict = self.to_dict_legacy()

        # Merge non-conflicting fields from legacy data
        for key, value in legacy_data.items():
            if key not in merged_dict and value is not None:
                merged_dict[key] = value

        return self.from_dict_legacy(merged_dict)
