"""
Category analysis result value objects for content generation.

This module contains value objects for category prediction and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class CategoryAttribute(BaseValueObject):
    """
    Value object for a single category attribute.
    
    Represents an individual attribute or feature that contributes
    to category classification with confidence and metadata.
    """
    
    # Attribute identification
    name: str
    value: str | float | bool | None
    attribute_type: str  # text, numeric, boolean, enum
    
    # Confidence and importance
    confidence: float
    importance_weight: float
    
    # Metadata
    source: str = "ml_analysis"
    extraction_method: str = "automatic"
    
    # Business rule constants
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0
    MIN_IMPORTANCE = 0.0
    MAX_IMPORTANCE = 1.0
    VALID_TYPES = {"text", "numeric", "boolean", "enum", "list"}
    
    def validate(self) -> None:
        """
        Validate category attribute according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate name
        if not isinstance(self.name, str) or not self.name.strip():
            errors.append("name must be a non-empty string")
        
        # Validate attribute type
        if self.attribute_type not in self.VALID_TYPES:
            errors.append(f"attribute_type must be one of {self.VALID_TYPES}, got {self.attribute_type}")
        
        # Validate confidence
        if not isinstance(self.confidence, (int, float)):
            errors.append(f"confidence must be a number, got {type(self.confidence).__name__}")
        elif not (self.MIN_CONFIDENCE <= self.confidence <= self.MAX_CONFIDENCE):
            errors.append(
                f"confidence {self.confidence} must be between "
                f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
            )
        
        # Validate importance weight
        if not isinstance(self.importance_weight, (int, float)):
            errors.append(f"importance_weight must be a number, got {type(self.importance_weight).__name__}")
        elif not (self.MIN_IMPORTANCE <= self.importance_weight <= self.MAX_IMPORTANCE):
            errors.append(
                f"importance_weight {self.importance_weight} must be between "
                f"{self.MIN_IMPORTANCE} and {self.MAX_IMPORTANCE}"
            )
        
        # Validate value based on type
        if self.attribute_type == "numeric" and self.value is not None:
            if not isinstance(self.value, (int, float)):
                errors.append(f"numeric attribute value must be a number, got {type(self.value).__name__}")
        elif self.attribute_type == "boolean" and self.value is not None:
            if not isinstance(self.value, bool):
                errors.append(f"boolean attribute value must be a boolean, got {type(self.value).__name__}")
        elif self.attribute_type == "text" and self.value is not None:
            if not isinstance(self.value, str):
                errors.append(f"text attribute value must be a string, got {type(self.value).__name__}")
        
        # Validate source and extraction method
        if not isinstance(self.source, str) or not self.source.strip():
            errors.append("source must be a non-empty string")
        
        if not isinstance(self.extraction_method, str) or not self.extraction_method.strip():
            errors.append("extraction_method must be a non-empty string")
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Category attribute validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
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
        if field_name == "confidence":
            if not isinstance(field_value, (int, float)):
                raise ValueObjectValidationError(
                    f"confidence must be a number, got {type(field_value).__name__}"
                )
            if not (self.MIN_CONFIDENCE <= field_value <= self.MAX_CONFIDENCE):
                raise ValueObjectValidationError(
                    f"confidence {field_value} must be between "
                    f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
                )
        
        elif field_name == "importance_weight":
            if not isinstance(field_value, (int, float)):
                raise ValueObjectValidationError(
                    f"importance_weight must be a number, got {type(field_value).__name__}"
                )
            if not (self.MIN_IMPORTANCE <= field_value <= self.MAX_IMPORTANCE):
                raise ValueObjectValidationError(
                    f"importance_weight {field_value} must be between "
                    f"{self.MIN_IMPORTANCE} and {self.MAX_IMPORTANCE}"
                )
        
        elif field_name == "attribute_type":
            if field_value not in self.VALID_TYPES:
                raise ValueObjectValidationError(
                    f"attribute_type must be one of {self.VALID_TYPES}, got {field_value}"
                )
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if attribute has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_important(self) -> bool:
        """Check if attribute is considered important."""
        return self.importance_weight >= 0.5
    
    @property
    def weighted_confidence(self) -> float:
        """Calculate confidence weighted by importance."""
        return self.confidence * self.importance_weight


@dataclass(frozen=True)
class CategoryAttributes(BaseValueObject):
    """
    Value object for a collection of category attributes.
    
    Represents all attributes extracted for category analysis
    with aggregated metrics and validation.
    """
    
    # Attributes collection
    attributes: list[CategoryAttribute] = field(default_factory=list)
    
    # Aggregated metrics
    total_attributes: int = 0
    high_confidence_count: int = 0
    average_confidence: float = 0.0
    average_importance: float = 0.0
    
    # Extraction metadata
    extraction_timestamp: datetime = field(default_factory=lambda: datetime.now())
    extraction_source: str = "content_analysis"
    
    # Business rule constants
    MAX_ATTRIBUTES = 100
    MIN_CONFIDENCE_THRESHOLD = 0.3
    
    def __post_init__(self):
        """Calculate aggregated metrics after initialization."""
        # Calculate derived fields
        object.__setattr__(self, 'total_attributes', len(self.attributes))
        
        if self.attributes:
            confidences = [attr.confidence for attr in self.attributes]
            importances = [attr.importance_weight for attr in self.attributes]
            
            object.__setattr__(self, 'average_confidence', sum(confidences) / len(confidences))
            object.__setattr__(self, 'average_importance', sum(importances) / len(importances))
            object.__setattr__(self, 'high_confidence_count', 
                              sum(1 for attr in self.attributes if attr.is_high_confidence))
        
        super().__post_init__()
    
    def validate(self) -> None:
        """
        Validate category attributes according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate attributes list
        if not isinstance(self.attributes, list):
            errors.append(f"attributes must be a list, got {type(self.attributes).__name__}")
            # Can't validate further if not a list
            if errors:
                from shared.value_objects.exceptions import MultipleValidationError
                raise MultipleValidationError(
                    "Category attributes validation failed",
                    errors=[ValueObjectValidationError(msg) for msg in errors]
                )
        
        # Validate list size
        if len(self.attributes) > self.MAX_ATTRIBUTES:
            errors.append(f"Too many attributes: {len(self.attributes)} (max: {self.MAX_ATTRIBUTES})")
        
        # Validate each attribute
        for i, attribute in enumerate(self.attributes):
            if not isinstance(attribute, CategoryAttribute):
                errors.append(f"attributes[{i}] must be a CategoryAttribute, got {type(attribute).__name__}")
        
        # Validate extraction source
        if not isinstance(self.extraction_source, str) or not self.extraction_source.strip():
            errors.append("extraction_source must be a non-empty string")
        
        # Validate calculated metrics consistency
        if self.total_attributes != len(self.attributes):
            errors.append(f"total_attributes {self.total_attributes} doesn't match actual count {len(self.attributes)}")
        
        if self.attributes:
            actual_high_confidence = sum(1 for attr in self.attributes if attr.is_high_confidence)
            if self.high_confidence_count != actual_high_confidence:
                errors.append(
                    f"high_confidence_count {self.high_confidence_count} doesn't match "
                    f"actual count {actual_high_confidence}"
                )
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Category attributes validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
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
        if field_name == "attributes":
            if not isinstance(field_value, list):
                raise ValueObjectValidationError(
                    f"attributes must be a list, got {type(field_value).__name__}"
                )
            if len(field_value) > self.MAX_ATTRIBUTES:
                raise ValueObjectValidationError(
                    f"Too many attributes: {len(field_value)} (max: {self.MAX_ATTRIBUTES})"
                )
    
    @property
    def has_attributes(self) -> bool:
        """Check if there are any attributes."""
        return len(self.attributes) > 0
    
    @property
    def confidence_ratio(self) -> float:
        """Calculate ratio of high confidence attributes."""
        if not self.attributes:
            return 0.0
        return self.high_confidence_count / len(self.attributes)
    
    def get_attributes_by_type(self, attribute_type: str) -> list[CategoryAttribute]:
        """Get attributes of a specific type."""
        return [attr for attr in self.attributes if attr.attribute_type == attribute_type]
    
    def get_high_confidence_attributes(self) -> list[CategoryAttribute]:
        """Get only high confidence attributes."""
        return [attr for attr in self.attributes if attr.is_high_confidence]
    
    def get_top_attributes(self, count: int = 10) -> list[CategoryAttribute]:
        """Get top attributes by weighted confidence."""
        return sorted(
            self.attributes,
            key=lambda attr: attr.weighted_confidence,
            reverse=True
        )[:count]


@dataclass(frozen=True)
class CategoryInfo(BaseValueObject):
    """
    Value object for category information.
    
    Represents detailed information about a specific category
    including metadata and classification details.
    """
    
    # Category identification
    category_id: str
    category_name: str
    category_path: str | None = None  # Full hierarchical path
    
    # Category metadata
    description: str | None = None
    parent_category_id: str | None = None
    level: int = 0  # Hierarchy level (0 = root)
    
    # Classification properties
    is_leaf_category: bool = True
    allowed_attributes: list[str] = field(default_factory=list)
    required_attributes: list[str] = field(default_factory=list)
    
    # External mappings
    ml_category_id: str | None = None  # MercadoLibre category ID
    external_mappings: dict[str, str] = field(default_factory=dict)
    
    # Business rule constants
    MAX_CATEGORY_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_LEVEL = 10
    MAX_ATTRIBUTES = 100
    
    def validate(self) -> None:
        """
        Validate category info according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate category ID
        if not isinstance(self.category_id, str) or not self.category_id.strip():
            errors.append("category_id must be a non-empty string")
        
        # Validate category name
        if not isinstance(self.category_name, str) or not self.category_name.strip():
            errors.append("category_name must be a non-empty string")
        elif len(self.category_name) > self.MAX_CATEGORY_NAME_LENGTH:
            errors.append(
                f"category_name length {len(self.category_name)} exceeds "
                f"maximum {self.MAX_CATEGORY_NAME_LENGTH}"
            )
        
        # Validate description
        if self.description is not None:
            if not isinstance(self.description, str):
                errors.append(f"description must be a string, got {type(self.description).__name__}")
            elif len(self.description) > self.MAX_DESCRIPTION_LENGTH:
                errors.append(
                    f"description length {len(self.description)} exceeds "
                    f"maximum {self.MAX_DESCRIPTION_LENGTH}"
                )
        
        # Validate level
        if not isinstance(self.level, int):
            errors.append(f"level must be an integer, got {type(self.level).__name__}")
        elif self.level < 0:
            errors.append(f"level must be non-negative, got {self.level}")
        elif self.level > self.MAX_LEVEL:
            errors.append(f"level {self.level} exceeds maximum {self.MAX_LEVEL}")
        
        # Validate attribute lists
        if len(self.allowed_attributes) > self.MAX_ATTRIBUTES:
            errors.append(
                f"Too many allowed attributes: {len(self.allowed_attributes)} "
                f"(max: {self.MAX_ATTRIBUTES})"
            )
        
        if len(self.required_attributes) > self.MAX_ATTRIBUTES:
            errors.append(
                f"Too many required attributes: {len(self.required_attributes)} "
                f"(max: {self.MAX_ATTRIBUTES})"
            )
        
        # Validate attribute list contents
        for i, attr in enumerate(self.allowed_attributes):
            if not isinstance(attr, str):
                errors.append(f"allowed_attributes[{i}] must be a string, got {type(attr).__name__}")
        
        for i, attr in enumerate(self.required_attributes):
            if not isinstance(attr, str):
                errors.append(f"required_attributes[{i}] must be a string, got {type(attr).__name__}")
        
        # Validate that required attributes are subset of allowed attributes
        if self.allowed_attributes and self.required_attributes:
            allowed_set = set(self.allowed_attributes)
            required_set = set(self.required_attributes)
            if not required_set.issubset(allowed_set):
                missing = required_set - allowed_set
                errors.append(f"Required attributes not in allowed list: {missing}")
        
        # Validate external mappings
        if not isinstance(self.external_mappings, dict):
            errors.append(f"external_mappings must be a dict, got {type(self.external_mappings).__name__}")
        else:
            for key, value in self.external_mappings.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"external_mappings must have string keys and values")
                    break
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Category info validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
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
        if field_name in ("category_id", "category_name"):
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueObjectValidationError(f"{field_name} must be a non-empty string")
        
        elif field_name == "level":
            if not isinstance(field_value, int):
                raise ValueObjectValidationError(f"level must be an integer, got {type(field_value).__name__}")
            if field_value < 0:
                raise ValueObjectValidationError(f"level must be non-negative, got {field_value}")
            if field_value > self.MAX_LEVEL:
                raise ValueObjectValidationError(f"level {field_value} exceeds maximum {self.MAX_LEVEL}")
        
        elif field_name == "is_leaf_category":
            if not isinstance(field_value, bool):
                raise ValueObjectValidationError(f"is_leaf_category must be a boolean, got {type(field_value).__name__}")
    
    @property
    def has_ml_mapping(self) -> bool:
        """Check if category has MercadoLibre mapping."""
        return self.ml_category_id is not None
    
    @property
    def has_external_mappings(self) -> bool:
        """Check if category has external mappings."""
        return len(self.external_mappings) > 0
    
    @property
    def is_root_category(self) -> bool:
        """Check if this is a root category."""
        return self.level == 0 and self.parent_category_id is None


@dataclass(frozen=True)
class CategoryPredictionResult(BaseValueObject):
    """
    Value object for category prediction results.
    
    Encapsulates ML-based category prediction results including
    confidence scores, alternative predictions, and analysis metadata.
    """
    
    # Primary prediction
    predicted_category: CategoryInfo
    confidence_score: float
    
    # Alternative predictions
    alternative_predictions: list[tuple[CategoryInfo, float]] = field(default_factory=list)
    
    # Prediction details
    prediction_method: str = "ml_classification"
    model_version: str = "1.0"
    feature_importance: dict[str, float] = field(default_factory=dict)
    
    # Analysis attributes
    analyzed_attributes: CategoryAttributes = field(default_factory=CategoryAttributes)
    
    # Prediction metadata
    prediction_timestamp: datetime = field(default_factory=lambda: datetime.now())
    processing_time_ms: int | None = None
    
    # Quality metrics
    prediction_quality: str = "unknown"  # high, medium, low, unknown
    needs_human_review: bool = False
    
    # Business rule constants
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0
    MAX_ALTERNATIVES = 10
    MAX_FEATURES = 100
    QUALITY_LEVELS = {"high", "medium", "low", "unknown"}
    
    def validate(self) -> None:
        """
        Validate category prediction result according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate predicted category
        if not isinstance(self.predicted_category, CategoryInfo):
            errors.append(f"predicted_category must be a CategoryInfo, got {type(self.predicted_category).__name__}")
        
        # Validate confidence score
        if not isinstance(self.confidence_score, (int, float)):
            errors.append(f"confidence_score must be a number, got {type(self.confidence_score).__name__}")
        elif not (self.MIN_CONFIDENCE <= self.confidence_score <= self.MAX_CONFIDENCE):
            errors.append(
                f"confidence_score {self.confidence_score} must be between "
                f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
            )
        
        # Validate alternative predictions
        if len(self.alternative_predictions) > self.MAX_ALTERNATIVES:
            errors.append(
                f"Too many alternative predictions: {len(self.alternative_predictions)} "
                f"(max: {self.MAX_ALTERNATIVES})"
            )
        
        for i, (category, confidence) in enumerate(self.alternative_predictions):
            if not isinstance(category, CategoryInfo):
                errors.append(f"alternative_predictions[{i}][0] must be a CategoryInfo")
            if not isinstance(confidence, (int, float)):
                errors.append(f"alternative_predictions[{i}][1] must be a number")
            elif not (self.MIN_CONFIDENCE <= confidence <= self.MAX_CONFIDENCE):
                errors.append(
                    f"alternative_predictions[{i}][1] confidence {confidence} "
                    f"must be between {self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
                )
        
        # Validate feature importance
        if len(self.feature_importance) > self.MAX_FEATURES:
            errors.append(
                f"Too many features: {len(self.feature_importance)} (max: {self.MAX_FEATURES})"
            )
        
        for feature, importance in self.feature_importance.items():
            if not isinstance(feature, str):
                errors.append("feature_importance keys must be strings")
                break
            if not isinstance(importance, (int, float)):
                errors.append("feature_importance values must be numbers")
                break
            if not (0.0 <= importance <= 1.0):
                errors.append(f"feature importance {importance} must be between 0.0 and 1.0")
        
        # Validate analyzed attributes
        if not isinstance(self.analyzed_attributes, CategoryAttributes):
            errors.append(f"analyzed_attributes must be a CategoryAttributes, got {type(self.analyzed_attributes).__name__}")
        
        # Validate prediction quality
        if self.prediction_quality not in self.QUALITY_LEVELS:
            errors.append(f"prediction_quality must be one of {self.QUALITY_LEVELS}, got {self.prediction_quality}")
        
        # Validate processing time
        if self.processing_time_ms is not None:
            if not isinstance(self.processing_time_ms, int):
                errors.append(f"processing_time_ms must be an integer, got {type(self.processing_time_ms).__name__}")
            elif self.processing_time_ms < 0:
                errors.append(f"processing_time_ms must be non-negative, got {self.processing_time_ms}")
        
        # Validate method and version
        if not isinstance(self.prediction_method, str) or not self.prediction_method.strip():
            errors.append("prediction_method must be a non-empty string")
        
        if not isinstance(self.model_version, str) or not self.model_version.strip():
            errors.append("model_version must be a non-empty string")
        
        # Business logic validation
        if self.confidence_score < 0.5 and not self.needs_human_review:
            errors.append("Low confidence predictions should require human review")
        
        if self.prediction_quality == "low" and not self.needs_human_review:
            errors.append("Low quality predictions should require human review")
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Category prediction result validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
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
        if field_name == "confidence_score":
            if not isinstance(field_value, (int, float)):
                raise ValueObjectValidationError(
                    f"confidence_score must be a number, got {type(field_value).__name__}"
                )
            if not (self.MIN_CONFIDENCE <= field_value <= self.MAX_CONFIDENCE):
                raise ValueObjectValidationError(
                    f"confidence_score {field_value} must be between "
                    f"{self.MIN_CONFIDENCE} and {self.MAX_CONFIDENCE}"
                )
        
        elif field_name == "prediction_quality":
            if field_value not in self.QUALITY_LEVELS:
                raise ValueObjectValidationError(
                    f"prediction_quality must be one of {self.QUALITY_LEVELS}, got {field_value}"
                )
        
        elif field_name == "needs_human_review":
            if not isinstance(field_value, bool):
                raise ValueObjectValidationError(
                    f"needs_human_review must be a boolean, got {type(field_value).__name__}"
                )
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if prediction has high confidence."""
        return self.confidence_score >= 0.8
    
    @property
    def has_alternatives(self) -> bool:
        """Check if there are alternative predictions."""
        return len(self.alternative_predictions) > 0
    
    @property
    def top_alternative(self) -> tuple[CategoryInfo, float] | None:
        """Get the top alternative prediction."""
        if not self.alternative_predictions:
            return None
        return max(self.alternative_predictions, key=lambda x: x[1])
    
    @property
    def confidence_gap(self) -> float:
        """Calculate confidence gap between primary and top alternative."""
        top_alt = self.top_alternative
        if not top_alt:
            return self.confidence_score
        return self.confidence_score - top_alt[1]
    
    @property
    def is_confident_prediction(self) -> bool:
        """Check if this is a confident prediction."""
        return (
            self.is_high_confidence and 
            self.confidence_gap >= 0.2 and 
            self.prediction_quality in ("high", "medium")
        )
    
    def get_prediction_summary(self) -> dict[str, Any]:
        """Get a summary of the prediction results."""
        return {
            "predicted_category_id": self.predicted_category.category_id,
            "predicted_category_name": self.predicted_category.category_name,
            "confidence_score": self.confidence_score,
            "prediction_quality": self.prediction_quality,
            "is_high_confidence": self.is_high_confidence,
            "needs_human_review": self.needs_human_review,
            "alternatives_count": len(self.alternative_predictions),
            "confidence_gap": self.confidence_gap,
            "attributes_analyzed": self.analyzed_attributes.total_attributes,
            "processing_time_ms": self.processing_time_ms,
        }