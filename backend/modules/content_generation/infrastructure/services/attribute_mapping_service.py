"""
Attribute Mapping Service implementation.

This module provides specialized attribute mapping for MercadoLibre categories,
ensuring proper category-specific attribute detection and validation.
"""

from dataclasses import dataclass, field
from typing import Any

from modules.content_generation.domain.entities import ProductFeatures
from modules.content_generation.domain.exceptions import (
    AttributeMappingError,
    AttributeValidationError,
)
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)
from modules.content_generation.domain.value_objects.ml_attributes import MLAttributes
from modules.content_generation.domain.value_objects.validation_results import (
    ContentValidationResult,
)


@dataclass(frozen=True)
class AttributeValidationResult:
    """Internal attribute validation result data structure."""

    is_valid: bool
    error: str | None = None


@dataclass(frozen=True)
class AttributeInfo:
    """Internal attribute information data structure."""

    attribute_id: str
    attribute_type: str
    required: bool
    max_length: int | None = None
    allowed_values: list[str] | None = None
    validation_method: str | None = None


@dataclass(frozen=True)
class CategoryAttributeInfo:
    """Internal category attribute information data structure."""

    category_id: str
    required_attributes: list[str]
    optional_attributes: list[str]
    attribute_mappings: dict[str, str]
    total_attributes: int


@dataclass(frozen=True)
class AttributeSuggestion:
    """Internal attribute suggestion data structure."""

    attribute_id: str
    suggestion_type: str
    suggested_value: str | None
    confidence: float


@dataclass(frozen=True)
class AttributeValidationRules:
    """Attribute validation rules data structure."""

    attribute_type: str = "string"
    max_length: int | None = None
    required: bool = False
    allowed_values: list[str] = field(default_factory=list)
    validation_method: str | None = None


@dataclass(frozen=True)
class CategoryConfig:
    """Category configuration data structure."""

    required_attributes: list[str]
    optional_attributes: list[str]
    attribute_mappings: dict[str, str]


class AttributeMappingService:
    """
    Attribute mapping service for MercadoLibre categories.

    This service maps product features to category-specific MercadoLibre
    attributes, ensuring proper listing compliance.
    """

    def __init__(self, logger: ContentLoggerProtocol):
        """Initialize the attribute mapping service.

        Args:
            logger: Logger protocol for logging operations
        """
        self.logger = logger

        # MercadoLibre category attribute mappings
        self.category_attributes: dict[str, CategoryConfig] = {
            "MLA1055": CategoryConfig(  # Celulares y Teléfonos
                required_attributes=["BRAND", "MODEL", "OPERATING_SYSTEM"],
                optional_attributes=[
                    "COLOR",
                    "STORAGE_CAPACITY",
                    "RAM_MEMORY",
                    "SCREEN_SIZE",
                ],
                attribute_mappings={
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "storage": "STORAGE_CAPACITY",
                    "ram": "RAM_MEMORY",
                    "screen_size": "SCREEN_SIZE",
                    "os": "OPERATING_SYSTEM",
                },
            ),
            "MLA1144": CategoryConfig(  # Cámaras y Accesorios
                required_attributes=["BRAND", "MODEL", "CAMERA_TYPE"],
                optional_attributes=[
                    "COLOR",
                    "MEGAPIXELS",
                    "OPTICAL_ZOOM",
                    "DIGITAL_ZOOM",
                ],
                attribute_mappings={
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "megapixels": "MEGAPIXELS",
                    "zoom": "OPTICAL_ZOOM",
                    "type": "CAMERA_TYPE",
                },
            ),
            "MLA1430": CategoryConfig(  # Ropa y Accesorios
                required_attributes=["BRAND", "GENDER", "SIZE"],
                optional_attributes=["COLOR", "MATERIAL", "SEASON", "STYLE"],
                attribute_mappings={
                    "brand": "BRAND",
                    "gender": "GENDER",
                    "size": "SIZE",
                    "color": "COLOR",
                    "material": "MATERIAL",
                    "season": "SEASON",
                    "style": "STYLE",
                },
            ),
            "MLA1276": CategoryConfig(  # Hogar, Muebles y Jardín
                required_attributes=["BRAND", "ITEM_CONDITION"],
                optional_attributes=["COLOR", "MATERIAL", "DIMENSIONS", "WEIGHT"],
                attribute_mappings={
                    "brand": "BRAND",
                    "condition": "ITEM_CONDITION",
                    "color": "COLOR",
                    "material": "MATERIAL",
                    "dimensions": "DIMENSIONS",
                    "weight": "WEIGHT",
                },
            ),
            "MLA1168": CategoryConfig(  # Deportes y Fitness
                required_attributes=["BRAND", "SPORT_TYPE"],
                optional_attributes=["COLOR", "SIZE", "MATERIAL", "GENDER"],
                attribute_mappings={
                    "brand": "BRAND",
                    "sport": "SPORT_TYPE",
                    "color": "COLOR",
                    "size": "SIZE",
                    "material": "MATERIAL",
                    "gender": "GENDER",
                },
            ),
            "MLA1000": CategoryConfig(  # Electrónicos, Audio y Video
                required_attributes=["BRAND", "MODEL"],
                optional_attributes=[
                    "COLOR",
                    "POWER_CONSUMPTION",
                    "CONNECTIVITY",
                    "FEATURES",
                ],
                attribute_mappings={
                    "brand": "BRAND",
                    "model": "MODEL",
                    "color": "COLOR",
                    "power": "POWER_CONSUMPTION",
                    "connectivity": "CONNECTIVITY",
                    "features": "FEATURES",
                },
            ),
        }

        # Attribute validation rules
        self.attribute_validation_rules: dict[str, AttributeValidationRules] = {
            "BRAND": AttributeValidationRules(
                attribute_type="string",
                max_length=50,
                required=True,
                validation_method="brand_validation",
            ),
            "MODEL": AttributeValidationRules(
                attribute_type="string",
                max_length=100,
                required=True,
                validation_method="model_validation",
            ),
            "COLOR": AttributeValidationRules(
                attribute_type="string",
                max_length=30,
                allowed_values=[
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
                validation_method="color_validation",
            ),
            "SIZE": AttributeValidationRules(
                attribute_type="string",
                max_length=20,
                validation_method="size_validation",
            ),
            "MATERIAL": AttributeValidationRules(
                attribute_type="string",
                max_length=50,
                validation_method="material_validation",
            ),
            "ITEM_CONDITION": AttributeValidationRules(
                attribute_type="string",
                allowed_values=["Nuevo", "Usado", "Reacondicionado"],
                validation_method="condition_validation",
            ),
            "STORAGE_CAPACITY": AttributeValidationRules(
                attribute_type="string",
                allowed_values=[
                    "16 GB",
                    "32 GB",
                    "64 GB",
                    "128 GB",
                    "256 GB",
                    "512 GB",
                    "1 TB",
                ],
                validation_method="storage_validation",
            ),
            "RAM_MEMORY": AttributeValidationRules(
                attribute_type="string",
                allowed_values=[
                    "1 GB",
                    "2 GB",
                    "3 GB",
                    "4 GB",
                    "6 GB",
                    "8 GB",
                    "12 GB",
                    "16 GB",
                ],
                validation_method="memory_validation",
            ),
            "OPERATING_SYSTEM": AttributeValidationRules(
                attribute_type="string",
                allowed_values=["Android", "iOS", "Windows", "Otro"],
                validation_method="os_validation",
            ),
        }

        # Common attribute value mappings
        self.value_mappings: dict[str, dict[str, str]] = {
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

        self.logger.info("Initialized Attribute Mapping Service")

    async def map_attributes(
        self,
        product_features: ProductFeatures,
        category_id: str,
    ) -> MLAttributes:
        """
        Map product features to MercadoLibre attributes.

        Args:
            product_features: Product features extracted from AI/user input
            category_id: MercadoLibre category ID

        Returns:
            MLAttributes containing mapped attributes

        Raises:
            AttributeMappingError: If attribute mapping fails
        """
        try:
            # Get category attribute configuration
            category_config = self.category_attributes.get(category_id)
            if not category_config:
                self.logger.warning(
                    f"No attribute mapping found for category: {category_id}"
                )
                default_attributes = self._create_default_attributes(product_features)
                return MLAttributes(
                    category_id=category_id,
                    mapped_attributes=default_attributes,
                    confidence_score=0.3,  # Low confidence for default mapping
                    required_attributes=[],
                    optional_attributes=[],
                    mapped_count=len(default_attributes),
                    missing_required=[],
                    completeness_score=0.3,
                    mapping_warnings=[
                        "No category configuration found, using default mapping"
                    ],
                )

            mapped_attributes: dict[str, Any] = {}
            missing_required: list[str] = []

            # Map required attributes
            required_attrs = category_config.required_attributes
            mappings = category_config.attribute_mappings
            for attr_id in required_attrs:
                value = self._extract_attribute_value(
                    attr_id, product_features, mappings
                )
                if value:
                    mapped_attributes[attr_id] = value
                else:
                    missing_required.append(attr_id)
                    self.logger.warning(f"Missing required attribute: {attr_id}")

            # Map optional attributes
            optional_attrs = category_config.optional_attributes
            for attr_id in optional_attrs:
                value = self._extract_attribute_value(
                    attr_id, product_features, mappings
                )
                if value:
                    mapped_attributes[attr_id] = value

            # Validate all mapped attributes
            validated_attributes = self._validate_mapped_attributes(mapped_attributes)

            # Calculate confidence and completeness scores
            total_required = len(required_attrs)
            mapped_required = len(
                [attr for attr in required_attrs if attr in validated_attributes]
            )
            completeness_score = (
                mapped_required / total_required if total_required > 0 else 1.0
            )
            confidence_score = min(
                0.9, completeness_score + 0.1
            )  # Base confidence on completeness

            # Create mapping warnings
            warnings = []
            if missing_required:
                warnings.append(f"Missing {len(missing_required)} required attributes")

            self.logger.info(
                f"Mapped {len(validated_attributes)} attributes for category {category_id}"
            )

            return MLAttributes(
                category_id=category_id,
                mapped_attributes=validated_attributes,
                confidence_score=confidence_score,
                required_attributes=required_attrs,
                optional_attributes=optional_attrs,
                mapped_count=len(validated_attributes),
                missing_required=missing_required,
                completeness_score=completeness_score,
                accuracy_score=0.8,  # Fixed score, could be enhanced with validation
                relevance_score=0.8,  # Fixed score, could be enhanced with validation
                mapping_warnings=warnings,
            )

        except Exception as e:
            self.logger.error(
                f"Error mapping attributes for category {category_id}: {e}"
            )
            raise AttributeMappingError(
                f"Failed to map attributes: {str(e)}",
                category_id=category_id,
                error_code="ATTRIBUTE_MAPPING_FAILED",
            ) from e

    async def validate_attributes(
        self,
        attributes: MLAttributes,
        category_id: str,
    ) -> ContentValidationResult:
        """
        Validate attributes against MercadoLibre requirements.

        Args:
            attributes: MLAttributes to validate
            category_id: MercadoLibre category ID

        Returns:
            ContentValidationResult containing validation results

        Raises:
            AttributeValidationError: If validation fails
        """
        try:
            validation_errors: list[str] = []
            warnings: list[str] = []

            # Get category configuration
            category_config = self.category_attributes.get(category_id)
            if not category_config:
                warnings.append(
                    f"No validation rules found for category: {category_id}"
                )
                return ContentValidationResult(
                    valid=True,
                    validation_score=0.7,
                    content_quality_score=0.7,
                    validation_warnings=warnings,
                    validation_engine="attribute_mapping_service",
                )

            # Use the mapped attributes from the MLAttributes object
            attr_dict = attributes.mapped_attributes

            # Validate required attributes
            required_attrs = category_config.required_attributes
            for attr_id in required_attrs:
                if attr_id not in attr_dict:
                    validation_errors.append(f"Required attribute {attr_id} is missing")
                else:
                    # Validate attribute value
                    attr_validation = self._validate_attribute_value(
                        attr_id, attr_dict[attr_id]
                    )
                    if not attr_validation.is_valid:
                        validation_errors.append(f"{attr_id}: {attr_validation.error}")

            # Validate optional attributes
            optional_attrs = category_config.optional_attributes
            for attr_id in optional_attrs:
                if attr_id in attr_dict:
                    attr_validation = self._validate_attribute_value(
                        attr_id, attr_dict[attr_id]
                    )
                    if not attr_validation.is_valid:
                        validation_errors.append(f"{attr_id}: {attr_validation.error}")

            # Check for unknown attributes
            known_attributes = set(required_attrs + optional_attrs)
            unknown_attributes = set(attr_dict.keys()) - known_attributes

            if unknown_attributes:
                warnings.append(
                    f"Unknown attributes: {', '.join(list(unknown_attributes))}"
                )

            # Calculate validation score based on completeness and errors
            is_valid = len(validation_errors) == 0
            required_present = len(
                [attr for attr in required_attrs if attr in attr_dict]
            )
            completeness = (
                required_present / len(required_attrs) if required_attrs else 1.0
            )
            validation_score = max(0.1, completeness - (len(validation_errors) * 0.1))

            return ContentValidationResult(
                valid=is_valid,
                validation_score=validation_score,
                content_quality_score=validation_score,
                validation_errors=validation_errors,
                validation_warnings=warnings,
                validation_engine="attribute_mapping_service",
            )

        except Exception as e:
            self.logger.error(
                f"Error validating attributes for category {category_id}: {e}"
            )
            raise AttributeValidationError(
                f"Failed to validate attributes: {str(e)}",
                category_id=category_id,
                attribute_name="unknown",
                attribute_value="unknown",
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

        return category_config.required_attributes

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

        return category_config.optional_attributes

    async def calculate_attribute_confidence(
        self,
        attributes: MLAttributes,
        product_features: ProductFeatures,
    ) -> float:
        """
        Calculate confidence score for mapped attributes.

        Args:
            attributes: MLAttributes containing mapped attributes
            product_features: Original product features

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Use the confidence score already calculated in MLAttributes
        # but enhance it with product features analysis
        base_confidence = attributes.confidence_score

        if not attributes.mapped_attributes:
            return 0.0

        confidence = 0.0
        total_weight = 0.0

        for attr_id, attr_value in attributes.mapped_attributes.items():
            # Calculate confidence for each attribute
            attr_confidence = self._calculate_single_attribute_confidence(
                attr_id, attr_value, product_features
            )

            # Weight required attributes higher
            weight = 0.7 if attr_id in attributes.required_attributes else 0.3

            confidence += attr_confidence * weight
            total_weight += weight

        calculated_confidence = confidence / total_weight if total_weight > 0 else 0.0

        # Return weighted average of base confidence and calculated confidence
        return (base_confidence * 0.4) + (calculated_confidence * 0.6)

    def _extract_attribute_value(
        self,
        attr_id: str,
        product_features: ProductFeatures,
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

        # Get the raw value from ProductFeatures
        raw_value = getattr(product_features, feature_key, None)
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
        rules = self.attribute_validation_rules.get(attr_id)

        if rules:
            # Apply max length
            if rules.max_length and len(value) > rules.max_length:
                value = value[: rules.max_length]

            # Apply allowed values constraint
            if rules.allowed_values:
                # Find closest match
                value_lower = value.lower()
                for allowed_value in rules.allowed_values:
                    if (
                        allowed_value.lower() == value_lower
                        or allowed_value.lower() in value_lower
                    ):
                        return allowed_value

        return value.strip()

    def _validate_mapped_attributes(self, attributes: dict[str, Any]) -> dict[str, Any]:
        """Validate all mapped attributes."""
        validated_attributes: dict[str, Any] = {}

        for attr_id, attr_value in attributes.items():
            validation_result = self._validate_attribute_value(attr_id, attr_value)

            if validation_result.is_valid:
                validated_attributes[attr_id] = attr_value
            else:
                self.logger.warning(
                    f"Invalid attribute {attr_id}: {validation_result.error}"
                )

        return validated_attributes

    def _validate_attribute_value(
        self, attr_id: str, value: Any
    ) -> AttributeValidationResult:
        """Validate a single attribute value."""
        rules = self.attribute_validation_rules.get(attr_id)

        if not rules:
            return AttributeValidationResult(is_valid=True)

        # Check if value is empty for required attribute
        if rules.required and not value:
            return AttributeValidationResult(
                is_valid=False,
                error=f"Required attribute {attr_id} cannot be empty",
            )

        # Check type
        if rules.attribute_type == "string" and not isinstance(value, str):
            return AttributeValidationResult(
                is_valid=False, error=f"Attribute {attr_id} must be a string"
            )

        # Check max length
        if rules.max_length and len(str(value)) > rules.max_length:
            return AttributeValidationResult(
                is_valid=False,
                error=f"Attribute {attr_id} exceeds maximum length of {rules.max_length}",
            )

        # Check allowed values
        if rules.allowed_values and str(value) not in rules.allowed_values:
            return AttributeValidationResult(
                is_valid=False,
                error=f"Attribute {attr_id} must be one of: {', '.join(rules.allowed_values)}",
            )

        return AttributeValidationResult(is_valid=True)

    def _calculate_single_attribute_confidence(
        self,
        attr_id: str,
        attr_value: Any,
        product_features: ProductFeatures,
    ) -> float:
        """Calculate confidence for a single attribute."""
        confidence = 0.0

        # Base confidence for having a value
        if attr_value:
            confidence += 0.5

        # Higher confidence for validated values
        validation_result = self._validate_attribute_value(attr_id, attr_value)
        if validation_result.is_valid:
            confidence += 0.3

        # Higher confidence for values that match allowed values
        rules = self.attribute_validation_rules.get(attr_id)
        if rules and rules.allowed_values and str(attr_value) in rules.allowed_values:
            confidence += 0.2

        return min(confidence, 1.0)

    def _is_required_attribute(self, attr_id: str) -> bool:
        """Check if attribute is required in any category."""
        for category_config in self.category_attributes.values():
            if attr_id in category_config.required_attributes:
                return True
        return False

    def _create_default_attributes(
        self, product_features: ProductFeatures
    ) -> dict[str, Any]:
        """Create default attributes for unknown categories."""
        default_attributes: dict[str, Any] = {}

        # Map common attributes
        if product_features.brand:
            default_attributes["BRAND"] = product_features.brand

        if product_features.model:
            default_attributes["MODEL"] = product_features.model

        if product_features.color:
            default_attributes["COLOR"] = self._apply_value_mapping(
                "color", product_features.color
            )

        if product_features.condition:
            default_attributes["ITEM_CONDITION"] = self._apply_value_mapping(
                "condition", product_features.condition
            )

        return default_attributes

    def get_attribute_info(self, attr_id: str) -> AttributeInfo:
        """Get information about a specific attribute."""
        rules = self.attribute_validation_rules.get(attr_id)

        if not rules:
            return AttributeInfo(
                attribute_id=attr_id,
                attribute_type="string",
                required=False,
            )

        return AttributeInfo(
            attribute_id=attr_id,
            attribute_type=rules.attribute_type,
            required=rules.required,
            max_length=rules.max_length,
            allowed_values=rules.allowed_values,
            validation_method=rules.validation_method,
        )

    def get_category_attribute_info(
        self, category_id: str
    ) -> CategoryAttributeInfo | None:
        """Get attribute information for a specific category."""
        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return None

        return CategoryAttributeInfo(
            category_id=category_id,
            required_attributes=category_config.required_attributes,
            optional_attributes=category_config.optional_attributes,
            attribute_mappings=category_config.attribute_mappings,
            total_attributes=len(category_config.required_attributes)
            + len(category_config.optional_attributes),
        )

    def suggest_missing_attributes(
        self,
        current_attributes: dict[str, Any],
        category_id: str,
        product_features: ProductFeatures,
    ) -> list[AttributeSuggestion]:
        """Suggest missing attributes that could be added."""
        suggestions: list[AttributeSuggestion] = []

        category_config = self.category_attributes.get(category_id)
        if not category_config:
            return suggestions

        # Check for missing required attributes
        required_attrs = category_config.required_attributes
        for attr_id in required_attrs:
            if attr_id not in current_attributes:
                # Try to extract from product features
                mappings = category_config.attribute_mappings
                potential_value = self._extract_attribute_value(
                    attr_id, product_features, mappings
                )

                suggestions.append(
                    AttributeSuggestion(
                        attribute_id=attr_id,
                        suggestion_type="required",
                        suggested_value=potential_value,
                        confidence=0.8 if potential_value else 0.3,
                    )
                )

        # Check for missing optional attributes
        optional_attrs = category_config.optional_attributes
        mappings = category_config.attribute_mappings
        for attr_id in optional_attrs:
            if attr_id not in current_attributes:
                potential_value = self._extract_attribute_value(
                    attr_id, product_features, mappings
                )

                if potential_value:
                    suggestions.append(
                        AttributeSuggestion(
                            attribute_id=attr_id,
                            suggestion_type="optional",
                            suggested_value=potential_value,
                            confidence=0.6,
                        )
                    )

        return suggestions
