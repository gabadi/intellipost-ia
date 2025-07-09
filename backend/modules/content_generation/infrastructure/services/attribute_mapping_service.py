"""
Attribute Mapping Service implementation.

This module provides specialized attribute mapping for MercadoLibre categories,
ensuring proper category-specific attribute detection and validation.
"""

import logging
from typing import Any

from modules.content_generation.domain.exceptions import (
    AttributeMappingError,
    AttributeValidationError,
)

logger = logging.getLogger(__name__)


class AttributeMappingService:
    """
    Attribute mapping service for MercadoLibre categories.

    This service maps product features to category-specific MercadoLibre
    attributes, ensuring proper listing compliance.
    """

    def __init__(self):
        """Initialize the attribute mapping service."""

        # MercadoLibre category attribute mappings
        self.category_attributes = {
            "MLA1055": {  # Celulares y Teléfonos
                "required": ["BRAND", "MODEL", "OPERATING_SYSTEM"],
                "optional": ["COLOR", "STORAGE_CAPACITY", "RAM_MEMORY", "SCREEN_SIZE"],
                "mappings": {
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "storage": "STORAGE_CAPACITY",
                    "ram": "RAM_MEMORY",
                    "screen_size": "SCREEN_SIZE",
                    "os": "OPERATING_SYSTEM",
                },
            },
            "MLA1144": {  # Cámaras y Accesorios
                "required": ["BRAND", "MODEL", "CAMERA_TYPE"],
                "optional": ["COLOR", "MEGAPIXELS", "OPTICAL_ZOOM", "DIGITAL_ZOOM"],
                "mappings": {
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "megapixels": "MEGAPIXELS",
                    "zoom": "OPTICAL_ZOOM",
                    "type": "CAMERA_TYPE",
                },
            },
            "MLA1430": {  # Ropa y Accesorios
                "required": ["BRAND", "GENDER", "SIZE"],
                "optional": ["COLOR", "MATERIAL", "SEASON", "STYLE"],
                "mappings": {
                    "brand": "BRAND",
                    "gender": "GENDER",
                    "size": "SIZE",
                    "color": "COLOR",
                    "material": "MATERIAL",
                    "season": "SEASON",
                    "style": "STYLE",
                },
            },
            "MLA1276": {  # Hogar, Muebles y Jardín
                "required": ["BRAND", "ITEM_CONDITION"],
                "optional": ["COLOR", "MATERIAL", "DIMENSIONS", "WEIGHT"],
                "mappings": {
                    "brand": "BRAND",
                    "condition": "ITEM_CONDITION",
                    "color": "COLOR",
                    "material": "MATERIAL",
                    "dimensions": "DIMENSIONS",
                    "weight": "WEIGHT",
                },
            },
            "MLA1168": {  # Deportes y Fitness
                "required": ["BRAND", "SPORT_TYPE"],
                "optional": ["COLOR", "SIZE", "MATERIAL", "GENDER"],
                "mappings": {
                    "brand": "BRAND",
                    "sport": "SPORT_TYPE",
                    "color": "COLOR",
                    "size": "SIZE",
                    "material": "MATERIAL",
                    "gender": "GENDER",
                },
            },
            "MLA1000": {  # Electrónicos, Audio y Video
                "required": ["BRAND", "MODEL"],
                "optional": ["COLOR", "POWER_CONSUMPTION", "CONNECTIVITY", "FEATURES"],
                "mappings": {
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "power": "POWER_CONSUMPTION",
                    "connectivity": "CONNECTIVITY",
                    "features": "FEATURES",
                },
            },
        }

        # Attribute validation rules
        self.attribute_validation_rules = {
            "BRAND": {
                "type": "string",
                "max_length": 50,
                "required": True,
                "validation": "brand_validation",
            },
            "MODEL": {
                "type": "string",
                "max_length": 100,
                "required": True,
                "validation": "model_validation",
            },
            "COLOR": {
                "type": "string",
                "max_length": 30,
                "allowed_values": [
                    "Negro",
                    "Blanco",
                    "Gris",
                    "Azul",
                    "Rojo",
                    "Verde",
                    "Amarillo",
                    "Rosa",
                    "Violeta",
                    "Naranja",
                    "Marrón",
                    "Dorado",
                    "Plateado",
                ],
                "validation": "color_validation",
            },
            "SIZE": {
                "type": "string",
                "max_length": 20,
                "validation": "size_validation",
            },
            "MATERIAL": {
                "type": "string",
                "max_length": 50,
                "validation": "material_validation",
            },
            "ITEM_CONDITION": {
                "type": "string",
                "allowed_values": ["Nuevo", "Usado", "Reacondicionado"],
                "validation": "condition_validation",
            },
            "STORAGE_CAPACITY": {
                "type": "string",
                "allowed_values": [
                    "16 GB",
                    "32 GB",
                    "64 GB",
                    "128 GB",
                    "256 GB",
                    "512 GB",
                    "1 TB",
                ],
                "validation": "storage_validation",
            },
            "RAM_MEMORY": {
                "type": "string",
                "allowed_values": [
                    "1 GB",
                    "2 GB",
                    "3 GB",
                    "4 GB",
                    "6 GB",
                    "8 GB",
                    "12 GB",
                    "16 GB",
                ],
                "validation": "memory_validation",
            },
            "OPERATING_SYSTEM": {
                "type": "string",
                "allowed_values": ["Android", "iOS", "Windows", "Otro"],
                "validation": "os_validation",
            },
        }

        # Common attribute value mappings
        self.value_mappings = {
            "condition": {
                "new": "Nuevo",
                "used": "Usado",
                "refurbished": "Reacondicionado",
                "like_new": "Nuevo",
                "good": "Usado",
                "fair": "Usado",
            },
            "color": {
                "black": "Negro",
                "white": "Blanco",
                "gray": "Gris",
                "grey": "Gris",
                "blue": "Azul",
                "red": "Rojo",
                "green": "Verde",
                "yellow": "Amarillo",
                "pink": "Rosa",
                "purple": "Violeta",
                "orange": "Naranja",
                "brown": "Marrón",
                "gold": "Dorado",
                "silver": "Plateado",
            },
            "gender": {
                "male": "Hombre",
                "female": "Mujer",
                "unisex": "Unisex",
                "men": "Hombre",
                "women": "Mujer",
                "man": "Hombre",
                "woman": "Mujer",
            },
            "size": {
                "xs": "XS",
                "s": "S",
                "m": "M",
                "l": "L",
                "xl": "XL",
                "xxl": "XXL",
                "small": "S",
                "medium": "M",
                "large": "L",
                "extra_large": "XL",
            },
        }

        logger.info("Initialized Attribute Mapping Service")

    async def map_attributes(
        self,
        product_features: dict[str, Any],
        category_id: str,
    ) -> dict[str, Any]:
        """
        Map product features to MercadoLibre attributes.

        Args:
            product_features: Product features extracted from AI/user input
            category_id: MercadoLibre category ID

        Returns:
            Dict containing mapped attributes

        Raises:
            AttributeMappingError: If attribute mapping fails
        """
        try:
            # Get category attribute configuration
            category_config = self.category_attributes.get(category_id)
            if not category_config:
                logger.warning(
                    f"No attribute mapping found for category: {category_id}"
                )
                return self._create_default_attributes(product_features)

            mapped_attributes = {}

            # Map required attributes
            for attr_id in category_config["required"]:
                value = self._extract_attribute_value(
                    attr_id, product_features, category_config["mappings"]
                )
                if value:
                    mapped_attributes[attr_id] = value
                else:
                    logger.warning(f"Missing required attribute: {attr_id}")

            # Map optional attributes
            for attr_id in category_config["optional"]:
                value = self._extract_attribute_value(
                    attr_id, product_features, category_config["mappings"]
                )
                if value:
                    mapped_attributes[attr_id] = value

            # Validate all mapped attributes
            validated_attributes = self._validate_mapped_attributes(mapped_attributes)

            logger.info(
                f"Mapped {len(validated_attributes)} attributes for category {category_id}"
            )

            return validated_attributes

        except Exception as e:
            logger.error(f"Error mapping attributes for category {category_id}: {e}")
            raise AttributeMappingError(
                f"Failed to map attributes: {str(e)}",
                category_id=category_id,
                error_code="ATTRIBUTE_MAPPING_FAILED",
            ) from e

    async def validate_attributes(
        self,
        attributes: dict[str, Any],
        category_id: str,
    ) -> dict[str, Any]:
        """
        Validate attributes against MercadoLibre requirements.

        Args:
            attributes: Attributes to validate
            category_id: MercadoLibre category ID

        Returns:
            Dict containing validation results

        Raises:
            AttributeValidationError: If validation fails
        """
        try:
            validation_errors = {}
            warnings = []

            # Get category configuration
            category_config = self.category_attributes.get(category_id)
            if not category_config:
                warnings.append(
                    f"No validation rules found for category: {category_id}"
                )
                return {
                    "is_valid": True,
                    "validation_errors": validation_errors,
                    "warnings": warnings,
                }

            # Validate required attributes
            for attr_id in category_config["required"]:
                if attr_id not in attributes:
                    validation_errors[attr_id] = (
                        f"Required attribute {attr_id} is missing"
                    )
                else:
                    # Validate attribute value
                    attr_validation = self._validate_attribute_value(
                        attr_id, attributes[attr_id]
                    )
                    if not attr_validation["is_valid"]:
                        validation_errors[attr_id] = attr_validation["error"]

            # Validate optional attributes
            for attr_id in category_config["optional"]:
                if attr_id in attributes:
                    attr_validation = self._validate_attribute_value(
                        attr_id, attributes[attr_id]
                    )
                    if not attr_validation["is_valid"]:
                        validation_errors[attr_id] = attr_validation["error"]

            # Check for unknown attributes
            known_attributes = set(
                category_config["required"] + category_config["optional"]
            )
            unknown_attributes = set(attributes.keys()) - known_attributes

            if unknown_attributes:
                warnings.append(f"Unknown attributes: {', '.join(unknown_attributes)}")

            return {
                "is_valid": len(validation_errors) == 0,
                "validation_errors": validation_errors,
                "warnings": warnings,
                "validated_attributes": len(attributes),
                "required_attributes_present": len(
                    [attr for attr in category_config["required"] if attr in attributes]
                ),
                "optional_attributes_present": len(
                    [attr for attr in category_config["optional"] if attr in attributes]
                ),
            }

        except Exception as e:
            logger.error(f"Error validating attributes for category {category_id}: {e}")
            raise AttributeValidationError(
                f"Failed to validate attributes: {str(e)}",
                category_id=category_id,
                error_code="ATTRIBUTE_VALIDATION_FAILED",
            ) from e

    async def get_required_attributes(
        self,
        category_id: str,
    ) -> list[str]:
        """
        Get required attributes for a category.

        Args:
            category_id: MercadoLibre category ID

        Returns:
            List of required attribute IDs
        """
        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return []

        return category_config["required"]

    async def get_optional_attributes(
        self,
        category_id: str,
    ) -> list[str]:
        """
        Get optional attributes for a category.

        Args:
            category_id: MercadoLibre category ID

        Returns:
            List of optional attribute IDs
        """
        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return []

        return category_config["optional"]

    async def calculate_attribute_confidence(
        self,
        attributes: dict[str, Any],
        product_features: dict[str, Any],
    ) -> float:
        """
        Calculate confidence score for mapped attributes.

        Args:
            attributes: Mapped attributes
            product_features: Original product features

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not attributes:
            return 0.0

        confidence = 0.0
        total_weight = 0.0

        for attr_id, attr_value in attributes.items():
            # Calculate confidence for each attribute
            attr_confidence = self._calculate_single_attribute_confidence(
                attr_id, attr_value, product_features
            )

            # Weight required attributes higher
            weight = 0.7 if self._is_required_attribute(attr_id) else 0.3

            confidence += attr_confidence * weight
            total_weight += weight

        return confidence / total_weight if total_weight > 0 else 0.0

    def _extract_attribute_value(
        self,
        attr_id: str,
        product_features: dict[str, Any],
        mappings: dict[str, str],
    ) -> str | None:
        """Extract attribute value from product features."""
        # Find the mapping for this attribute
        feature_key = None
        for feature_name, mapped_attr_id in mappings.items():
            if mapped_attr_id == attr_id:
                feature_key = feature_name
                break

        if not feature_key:
            return None

        # Get the raw value
        raw_value = product_features.get(feature_key)
        if not raw_value:
            return None

        # Apply value mappings
        mapped_value = self._apply_value_mapping(feature_key, raw_value)

        # Validate and format the value
        formatted_value = self._format_attribute_value(attr_id, mapped_value)

        return formatted_value

    def _apply_value_mapping(self, feature_key: str, raw_value: str) -> str:
        """Apply value mapping to raw feature value."""
        if not isinstance(raw_value, str):
            raw_value = str(raw_value)

        # Check if there's a mapping for this feature
        if feature_key in self.value_mappings:
            mapping = self.value_mappings[feature_key]
            raw_value_lower = raw_value.lower()

            # Look for exact match
            if raw_value_lower in mapping:
                return mapping[raw_value_lower]

            # Look for partial match
            for key, value in mapping.items():
                if key in raw_value_lower:
                    return value

        # Return capitalized version if no mapping found
        return raw_value.strip().title()

    def _format_attribute_value(self, attr_id: str, value: str) -> str:
        """Format attribute value according to ML requirements."""
        if not value:
            return ""

        # Get validation rules for this attribute
        rules = self.attribute_validation_rules.get(attr_id, {})

        # Apply max length
        max_length = rules.get("max_length")
        if max_length and len(value) > max_length:
            value = value[:max_length]

        # Apply allowed values constraint
        allowed_values = rules.get("allowed_values")
        if allowed_values:
            # Find closest match
            value_lower = value.lower()
            for allowed_value in allowed_values:
                if (
                    allowed_value.lower() == value_lower
                    or allowed_value.lower() in value_lower
                ):
                    return allowed_value

        return value.strip()

    def _validate_mapped_attributes(self, attributes: dict[str, Any]) -> dict[str, Any]:
        """Validate all mapped attributes."""
        validated_attributes = {}

        for attr_id, attr_value in attributes.items():
            validation_result = self._validate_attribute_value(attr_id, attr_value)

            if validation_result["is_valid"]:
                validated_attributes[attr_id] = attr_value
            else:
                logger.warning(
                    f"Invalid attribute {attr_id}: {validation_result['error']}"
                )

        return validated_attributes

    def _validate_attribute_value(self, attr_id: str, value: Any) -> dict[str, Any]:
        """Validate a single attribute value."""
        rules = self.attribute_validation_rules.get(attr_id, {})

        if not rules:
            return {"is_valid": True}

        # Check if value is empty for required attribute
        if rules.get("required", False) and not value:
            return {
                "is_valid": False,
                "error": f"Required attribute {attr_id} cannot be empty",
            }

        # Check type
        expected_type = rules.get("type", "string")
        if expected_type == "string" and not isinstance(value, str):
            return {"is_valid": False, "error": f"Attribute {attr_id} must be a string"}

        # Check max length
        max_length = rules.get("max_length")
        if max_length and len(str(value)) > max_length:
            return {
                "is_valid": False,
                "error": f"Attribute {attr_id} exceeds maximum length of {max_length}",
            }

        # Check allowed values
        allowed_values = rules.get("allowed_values")
        if allowed_values and str(value) not in allowed_values:
            return {
                "is_valid": False,
                "error": f"Attribute {attr_id} must be one of: {', '.join(allowed_values)}",
            }

        return {"is_valid": True}

    def _calculate_single_attribute_confidence(
        self,
        attr_id: str,
        attr_value: Any,
        product_features: dict[str, Any],
    ) -> float:
        """Calculate confidence for a single attribute."""
        confidence = 0.0

        # Base confidence for having a value
        if attr_value:
            confidence += 0.5

        # Higher confidence for validated values
        validation_result = self._validate_attribute_value(attr_id, attr_value)
        if validation_result["is_valid"]:
            confidence += 0.3

        # Higher confidence for values that match allowed values
        rules = self.attribute_validation_rules.get(attr_id, {})
        allowed_values = rules.get("allowed_values")
        if allowed_values and str(attr_value) in allowed_values:
            confidence += 0.2

        return min(confidence, 1.0)

    def _is_required_attribute(self, attr_id: str) -> bool:
        """Check if attribute is required in any category."""
        for category_config in self.category_attributes.values():
            if attr_id in category_config["required"]:
                return True
        return False

    def _create_default_attributes(
        self, product_features: dict[str, Any]
    ) -> dict[str, Any]:
        """Create default attributes for unknown categories."""
        default_attributes = {}

        # Map common attributes
        if product_features.get("brand"):
            default_attributes["BRAND"] = product_features["brand"]

        if product_features.get("model"):
            default_attributes["MODEL"] = product_features["model"]

        if product_features.get("color"):
            default_attributes["COLOR"] = self._apply_value_mapping(
                "color", product_features["color"]
            )

        if product_features.get("condition"):
            default_attributes["ITEM_CONDITION"] = self._apply_value_mapping(
                "condition", product_features["condition"]
            )

        return default_attributes

    def get_attribute_info(self, attr_id: str) -> dict[str, Any]:
        """Get information about a specific attribute."""
        rules = self.attribute_validation_rules.get(attr_id, {})

        return {
            "id": attr_id,
            "type": rules.get("type", "string"),
            "required": rules.get("required", False),
            "max_length": rules.get("max_length"),
            "allowed_values": rules.get("allowed_values"),
            "validation_method": rules.get("validation"),
        }

    def get_category_attribute_info(self, category_id: str) -> dict[str, Any]:
        """Get attribute information for a specific category."""
        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return {}

        return {
            "category_id": category_id,
            "required_attributes": category_config["required"],
            "optional_attributes": category_config["optional"],
            "attribute_mappings": category_config["mappings"],
            "total_attributes": len(
                category_config["required"] + category_config["optional"]
            ),
        }

    def suggest_missing_attributes(
        self,
        current_attributes: dict[str, Any],
        category_id: str,
        product_features: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Suggest missing attributes that could be added."""
        suggestions = []

        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return suggestions

        # Check for missing required attributes
        for attr_id in category_config["required"]:
            if attr_id not in current_attributes:
                # Try to extract from product features
                potential_value = self._extract_attribute_value(
                    attr_id, product_features, category_config["mappings"]
                )

                suggestions.append(
                    {
                        "attribute_id": attr_id,
                        "type": "required",
                        "suggested_value": potential_value,
                        "confidence": 0.8 if potential_value else 0.3,
                    }
                )

        # Check for missing optional attributes
        for attr_id in category_config["optional"]:
            if attr_id not in current_attributes:
                potential_value = self._extract_attribute_value(
                    attr_id, product_features, category_config["mappings"]
                )

                if potential_value:
                    suggestions.append(
                        {
                            "attribute_id": attr_id,
                            "type": "optional",
                            "suggested_value": potential_value,
                            "confidence": 0.6,
                        }
                    )

        return suggestions
