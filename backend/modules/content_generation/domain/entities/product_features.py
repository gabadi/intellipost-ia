"""
Product Features value object for content generation domain.

This module defines the ProductFeatures value object that encapsulates
all product-related information used in content generation processes.
"""

from dataclasses import dataclass, field
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectValidationError,
)


@dataclass(frozen=True, eq=False)
class ProductFeatures(BaseValueObject):
    """
    Product features value object for content generation.

    This value object encapsulates all product attributes and features
    needed for AI content generation, providing type safety and validation.
    """

    # Core product information
    brand: str | None = None
    model: str | None = None
    category: str | None = None
    description: str | None = None

    # Physical attributes
    color: str | None = None
    size: str | None = None
    material: str | None = None
    dimensions: str | None = None
    weight: str | None = None

    # Product condition and status
    condition: str = "new"
    availability: str = "available"

    # Technical specifications
    technical_specs: dict[str, str] = field(default_factory=dict)

    # MercadoLibre specific attributes
    ml_category_id: str | None = None
    ml_category_name: str | None = None

    # Pricing information
    price: float | None = None
    currency: str = "ARS"

    # Additional features and metadata
    features: list[str] = field(default_factory=list)
    accessories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # Product type and classification
    product_type: str | None = None
    subcategory: str | None = None

    # Gender/target audience (for clothing, etc.)
    gender: str | None = None
    age_group: str | None = None
    target_audience: str | None = None

    # Quality and certification
    quality_rating: str | None = None
    certifications: list[str] = field(default_factory=list)

    # Warranty and support
    warranty: str | None = None
    support_contact: str | None = None

    # Additional metadata
    image_count: int = 0
    source: str | None = None
    extraction_confidence: float | None = None

    # Extended attributes for complex products
    extended_attributes: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate the ProductFeatures value object."""
        errors = []

        # Validate condition values
        valid_conditions = {
            "new",
            "nuevo",
            "used",
            "usado",
            "refurbished",
            "reacondicionado",
            "like_new",
            "como_nuevo",
            "fair",
            "good",
        }
        if self.condition and self.condition.lower() not in valid_conditions:
            errors.append(
                InvalidFieldValueError(
                    "condition",
                    self.condition,
                    f"Condition must be one of: {', '.join(valid_conditions)}",
                )
            )

        # Validate availability values
        valid_availability = {
            "available",
            "disponible",
            "out_of_stock",
            "agotado",
            "discontinued",
        }
        if self.availability and self.availability.lower() not in valid_availability:
            errors.append(
                InvalidFieldValueError(
                    "availability",
                    self.availability,
                    f"Availability must be one of: {', '.join(valid_availability)}",
                )
            )

        # Validate string fields are not empty if provided
        string_fields = [
            "brand",
            "model",
            "category",
            "description",
            "color",
            "size",
            "material",
        ]
        for field_name in string_fields:
            field_value = getattr(self, field_name)
            if field_value is not None:
                if not isinstance(field_value, str):
                    errors.append(InvalidFieldTypeError(field_name, field_value, "str"))
                elif len(field_value.strip()) == 0:
                    errors.append(
                        InvalidFieldValueError(
                            field_name,
                            field_value,
                            f"{field_name} cannot be empty string",
                        )
                    )

        # Validate technical_specs is a dict with string values
        if not isinstance(self.technical_specs, dict):
            errors.append(
                InvalidFieldTypeError("technical_specs", self.technical_specs, "dict")
            )
        else:
            for key, value in self.technical_specs.items():
                if not isinstance(key, str):
                    errors.append(
                        InvalidFieldValueError(
                            "technical_specs",
                            key,
                            "All technical_specs keys must be strings",
                        )
                    )
                if not isinstance(value, str):
                    errors.append(
                        InvalidFieldValueError(
                            "technical_specs",
                            value,
                            "All technical_specs values must be strings",
                        )
                    )

        # Validate lists contain only strings
        list_fields = ["features", "accessories", "tags", "certifications"]
        for field_name in list_fields:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, list):
                errors.append(InvalidFieldTypeError(field_name, field_value, "list"))
            else:
                for item in field_value:
                    if not isinstance(item, str):
                        errors.append(
                            InvalidFieldValueError(
                                field_name,
                                item,
                                f"All {field_name} items must be strings",
                            )
                        )

        # Validate price if provided
        if self.price is not None:
            if not isinstance(self.price, (int, float)):
                errors.append(InvalidFieldTypeError("price", self.price, "float"))
            elif self.price < 0:
                errors.append(
                    InvalidFieldValueError(
                        "price", self.price, "Price must be non-negative"
                    )
                )

        # Validate currency
        if not isinstance(self.currency, str):
            errors.append(InvalidFieldTypeError("currency", self.currency, "str"))
        elif len(self.currency.strip()) == 0:
            errors.append(RequiredFieldError("currency"))

        # Validate image_count
        if not isinstance(self.image_count, int):
            errors.append(InvalidFieldTypeError("image_count", self.image_count, "int"))
        elif self.image_count < 0:
            errors.append(
                InvalidFieldValueError(
                    "image_count", self.image_count, "Image count must be non-negative"
                )
            )

        # Validate extraction_confidence if provided
        if self.extraction_confidence is not None:
            if not isinstance(self.extraction_confidence, (int, float)):
                errors.append(
                    InvalidFieldTypeError(
                        "extraction_confidence", self.extraction_confidence, "float"
                    )
                )
            elif not 0.0 <= self.extraction_confidence <= 1.0:
                errors.append(
                    InvalidFieldValueError(
                        "extraction_confidence",
                        self.extraction_confidence,
                        "Extraction confidence must be between 0.0 and 1.0",
                    )
                )

        # Validate extended_attributes is a dict
        if not isinstance(self.extended_attributes, dict):
            errors.append(
                InvalidFieldTypeError(
                    "extended_attributes", self.extended_attributes, "dict"
                )
            )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        # This method would contain field-specific validation logic
        # For brevity, implementing basic validation here
        if field_name in [
            "brand",
            "model",
            "category",
            "description",
            "color",
            "size",
            "material",
        ]:
            if field_value is not None and not isinstance(field_value, str):
                raise InvalidFieldTypeError(field_name, field_value, "str")
        elif field_name == "technical_specs":
            if not isinstance(field_value, dict):
                raise InvalidFieldTypeError(field_name, field_value, "dict")
        elif field_name in ["features", "accessories", "tags", "certifications"]:
            if not isinstance(field_value, list):
                raise InvalidFieldTypeError(field_name, field_value, "list")
        elif field_name == "price":
            if field_value is not None and not isinstance(field_value, (int, float)):
                raise InvalidFieldTypeError(field_name, field_value, "float")
        elif field_name == "image_count":
            if not isinstance(field_value, int):
                raise InvalidFieldTypeError(field_name, field_value, "int")
        else:
            # For unknown fields, just check they're not None for required fields
            pass

    @classmethod
    def from_dict_legacy(cls, data: dict[str, Any]) -> "ProductFeatures":
        """
        Create ProductFeatures from legacy dict format for backward compatibility.

        Args:
            data: Dictionary with product features in legacy format

        Returns:
            New ProductFeatures instance

        Raises:
            ValueObjectValidationError: If dict format is invalid
        """
        if not isinstance(data, dict):
            raise InvalidFieldTypeError("product_features", data, "dict")

        try:
            # Map legacy fields to new structure
            mapped_data = {}

            # Direct mappings
            direct_mappings = {
                "brand": "brand",
                "model": "model",
                "category": "category",
                "description": "description",
                "color": "color",
                "size": "size",
                "material": "material",
                "condition": "condition",
                "price": "price",
                "currency": "currency",
                "dimensions": "dimensions",
                "weight": "weight",
                "ml_category_id": "ml_category_id",
                "ml_category_name": "ml_category_name",
                "gender": "gender",
                "target_audience": "target_audience",
                "warranty": "warranty",
                "image_count": "image_count",
                "source": "source",
            }

            for legacy_key, new_key in direct_mappings.items():
                if legacy_key in data:
                    value = data[legacy_key]
                    # Handle type conversions for specific fields
                    if new_key == "price" and value is not None:
                        try:
                            mapped_data[new_key] = float(value)
                        except (ValueError, TypeError):
                            mapped_data[new_key] = None
                    elif new_key == "image_count":
                        try:
                            mapped_data[new_key] = int(value)
                        except (ValueError, TypeError):
                            mapped_data[new_key] = 0
                    else:
                        mapped_data[new_key] = value

            # Handle nested structures
            if "technical_specs" in data:
                if isinstance(data["technical_specs"], dict):
                    mapped_data["technical_specs"] = {
                        str(k): str(v) for k, v in data["technical_specs"].items()
                    }
                else:
                    mapped_data["technical_specs"] = {}

            # Handle list fields
            list_mappings = {
                "features": "features",
                "accessories": "accessories",
                "tags": "tags",
                "certifications": "certifications",
            }

            for legacy_key, new_key in list_mappings.items():
                if legacy_key in data:
                    if isinstance(data[legacy_key], list):
                        mapped_data[new_key] = [str(item) for item in data[legacy_key]]
                    else:
                        mapped_data[new_key] = []

            # Handle any remaining fields in extended_attributes
            known_fields = (
                set(direct_mappings.keys())
                | set(list_mappings.keys())
                | {"technical_specs"}
            )
            extended_attrs = {}
            for key, value in data.items():
                if key not in known_fields and not key.startswith("_"):
                    extended_attrs[key] = value

            if extended_attrs:
                mapped_data["extended_attributes"] = extended_attrs

            return cls(**mapped_data)

        except (ValueError, TypeError) as e:
            raise ValueObjectValidationError(
                f"Failed to convert dict to ProductFeatures: {str(e)}",
                "product_features",
            ) from e

    def to_dict_legacy(self) -> dict[str, Any]:
        """
        Convert to legacy dict format for backward compatibility.

        Returns:
            Dictionary in legacy format
        """
        result = {}

        # Add all non-None fields
        if self.brand is not None:
            result["brand"] = self.brand
        if self.model is not None:
            result["model"] = self.model
        if self.category is not None:
            result["category"] = self.category
        if self.description is not None:
            result["description"] = self.description
        if self.color is not None:
            result["color"] = self.color
        if self.size is not None:
            result["size"] = self.size
        if self.material is not None:
            result["material"] = self.material
        if self.dimensions is not None:
            result["dimensions"] = self.dimensions
        if self.weight is not None:
            result["weight"] = self.weight
        if self.condition != "new":  # Only include if not default
            result["condition"] = self.condition
        if self.price is not None:
            result["price"] = self.price
        if self.currency != "ARS":  # Only include if not default
            result["currency"] = self.currency
        if self.ml_category_id is not None:
            result["ml_category_id"] = self.ml_category_id
        if self.ml_category_name is not None:
            result["ml_category_name"] = self.ml_category_name
        if self.gender is not None:
            result["gender"] = self.gender
        if self.target_audience is not None:
            result["target_audience"] = self.target_audience
        if self.warranty is not None:
            result["warranty"] = self.warranty
        if self.image_count > 0:
            result["image_count"] = self.image_count
        if self.source is not None:
            result["source"] = self.source

        # Add collections if not empty
        if self.technical_specs:
            result["technical_specs"] = dict(self.technical_specs)
        if self.features:
            result["features"] = list(self.features)
        if self.accessories:
            result["accessories"] = list(self.accessories)
        if self.tags:
            result["tags"] = list(self.tags)
        if self.certifications:
            result["certifications"] = list(self.certifications)

        # Add extended attributes
        if self.extended_attributes:
            result.update(self.extended_attributes)

        return result

    def has_basic_info(self) -> bool:
        """Check if the product has basic information (brand or model or category)."""
        return bool(self.brand or self.model or self.category)

    def has_detailed_info(self) -> bool:
        """Check if the product has detailed information."""
        return bool(
            self.has_basic_info()
            and (self.description or self.technical_specs or self.features)
        )

    def get_display_name(self) -> str:
        """Get a display name for the product."""
        parts = []
        if self.brand:
            parts.append(self.brand)
        if self.model:
            parts.append(self.model)
        if not parts and self.category:
            parts.append(self.category)
        return " ".join(parts) if parts else "Unknown Product"

    def get_key_features(self, max_features: int = 5) -> list[str]:
        """Get key features for display."""
        key_features = []

        # Add color if available
        if self.color:
            key_features.append(f"Color: {self.color}")

        # Add size if available
        if self.size:
            key_features.append(f"Size: {self.size}")

        # Add condition if not new
        if self.condition != "new":
            key_features.append(f"Condition: {self.condition}")

        # Add technical specs
        for spec_name, spec_value in list(self.technical_specs.items())[:3]:
            key_features.append(f"{spec_name}: {spec_value}")

        # Add features from features list
        remaining_slots = max_features - len(key_features)
        if remaining_slots > 0:
            key_features.extend(self.features[:remaining_slots])

        return key_features[:max_features]

    def merge_with(self, other: "ProductFeatures") -> "ProductFeatures":
        """
        Merge this ProductFeatures with another, preferring non-None values.

        Args:
            other: Another ProductFeatures instance to merge with

        Returns:
            New ProductFeatures instance with merged data
        """
        if not isinstance(other, ProductFeatures):
            raise InvalidFieldTypeError("other", other, "ProductFeatures")

        # Merge simple fields (prefer non-None values)
        merged_data = {}

        simple_fields = [
            "brand",
            "model",
            "category",
            "description",
            "color",
            "size",
            "material",
            "dimensions",
            "weight",
            "condition",
            "availability",
            "ml_category_id",
            "ml_category_name",
            "price",
            "currency",
            "product_type",
            "subcategory",
            "gender",
            "age_group",
            "target_audience",
            "quality_rating",
            "warranty",
            "support_contact",
            "source",
        ]

        for field_name in simple_fields:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)
            merged_data[field_name] = other_value if other_value is not None else self_value

        # Merge numeric fields (prefer higher values)
        merged_data["image_count"] = max(self.image_count, other.image_count)

        # Merge confidence (prefer higher confidence)
        if (
            self.extraction_confidence is not None
            and other.extraction_confidence is not None
        ):
            merged_data["extraction_confidence"] = max(
                self.extraction_confidence, other.extraction_confidence
            )
        else:
            merged_data["extraction_confidence"] = (
                self.extraction_confidence or other.extraction_confidence
            )

        # Merge dictionaries
        merged_data["technical_specs"] = {
            **self.technical_specs,
            **other.technical_specs,
        }
        merged_data["extended_attributes"] = {
            **self.extended_attributes,
            **other.extended_attributes,
        }

        # Merge lists (combine and deduplicate)
        merged_data["features"] = list(dict.fromkeys(self.features + other.features))
        merged_data["accessories"] = list(
            dict.fromkeys(self.accessories + other.accessories)
        )
        merged_data["tags"] = list(dict.fromkeys(self.tags + other.tags))
        merged_data["certifications"] = list(
            dict.fromkeys(self.certifications + other.certifications)
        )

        return ProductFeatures(**merged_data)

    def extract_for_category(self, category_id: str) -> dict[str, Any]:
        """
        Extract features relevant for a specific MercadoLibre category.

        Args:
            category_id: MercadoLibre category ID

        Returns:
            Dictionary with category-relevant features
        """
        result = self.to_dict_legacy()

        # Add category-specific logic here if needed
        # This could be expanded based on category requirements

        return result

    @classmethod
    def create_minimal(
        cls,
        brand: str | None = None,
        model: str | None = None,
        category: str | None = None,
        description: str | None = None,
    ) -> "ProductFeatures":
        """
        Create a minimal ProductFeatures instance with basic information.

        Args:
            brand: Product brand
            model: Product model
            category: Product category
            description: Product description

        Returns:
            New ProductFeatures instance
        """
        return cls(brand=brand, model=model, category=category, description=description)

    def is_empty(self) -> bool:
        """Check if the ProductFeatures instance has no meaningful data."""
        return (
            not self.brand
            and not self.model
            and not self.category
            and not self.description
            and not self.technical_specs
            and not self.features
            and not self.extended_attributes
        )

    def get_completeness_score(self) -> float:
        """
        Calculate a completeness score for the product features.

        Returns:
            Score between 0.0 and 1.0 indicating completeness
        """
        score = 0.0
        total_weight = 0.0

        # Core information (higher weight)
        core_fields = {
            "brand": 0.2,
            "model": 0.2,
            "category": 0.15,
            "description": 0.15,
        }

        for field_name, weight in core_fields.items():
            total_weight += weight
            if getattr(self, field_name):
                score += weight

        # Additional fields (lower weight)
        additional_fields = {
            "color": 0.05,
            "size": 0.05,
            "condition": 0.05,
            "price": 0.05,
            "technical_specs": 0.05,
            "features": 0.05,
        }

        for field_name, weight in additional_fields.items():
            total_weight += weight
            field_value = getattr(self, field_name)
            if field_value and (
                (isinstance(field_value, (dict, list)) and len(field_value) > 0)
                or (isinstance(field_value, str) and len(field_value.strip()) > 0)
                or (isinstance(field_value, (int, float)) and field_value > 0)
            ):
                score += weight

        return score / total_weight if total_weight > 0 else 0.0
