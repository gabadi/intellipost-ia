"""
MercadoLibre shipping value object.

This module defines the MLShipping value object for handling
MercadoLibre shipping information in a type-safe manner.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldRangeError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
)
from shared.value_objects.protocols import MercadoLibreValueObjectProtocol


@dataclass(frozen=True)
class MLShippingMethod:
    """Individual MercadoLibre shipping method."""

    id: int
    name: str
    cost: Decimal
    currency_id: str = "ARS"
    list_cost: Decimal | None = None
    option_cost: Decimal | None = None

    def __post_init__(self):
        """Validate shipping method after initialization."""
        if not self.name:
            raise RequiredFieldError("name")
        if self.cost < 0:
            raise InvalidFieldRangeError("cost", self.cost, min_value=0)
        if self.list_cost is not None and self.list_cost < 0:
            raise InvalidFieldRangeError("list_cost", self.list_cost, min_value=0)
        if self.option_cost is not None and self.option_cost < 0:
            raise InvalidFieldRangeError("option_cost", self.option_cost, min_value=0)


@dataclass(frozen=True)
class MLShippingLocation:
    """MercadoLibre shipping location information."""

    neighborhood: dict[str, Any] | None = None
    city: dict[str, Any] | None = None
    state: dict[str, Any] | None = None
    country: dict[str, Any] | None = None
    zip_code: str | None = None

    def __post_init__(self):
        """Validate shipping location after initialization."""
        # At least one location component should be provided
        if not any(
            [self.neighborhood, self.city, self.state, self.country, self.zip_code]
        ):
            raise InvalidFieldValueError(
                "location", None, "At least one location component must be provided"
            )


@dataclass(frozen=True, eq=False)
class MLShipping(BaseValueObject, MercadoLibreValueObjectProtocol):
    """
    MercadoLibre shipping value object.

    This value object encapsulates MercadoLibre shipping information,
    providing validation and serialization capabilities.
    """

    mode: str  # "me1", "me2", "not_specified", "custom"
    free_shipping: bool = False
    methods: list[MLShippingMethod] | None = None
    tags: list[str] | None = None
    dimensions: dict[str, Any] | None = None
    local_pick_up: bool = False
    free_methods: list[dict[str, Any]] | None = None
    cost: Decimal | None = None
    currency_id: str = "ARS"

    def validate(self) -> None:
        """Validate the MLShipping value object."""
        errors = []

        # Validate mode
        valid_modes = ["me1", "me2", "not_specified", "custom"]
        if self.mode not in valid_modes:
            errors.append(
                InvalidFieldValueError(
                    "mode",
                    self.mode,
                    f"Invalid shipping mode. Must be one of: {', '.join(valid_modes)}",
                )
            )

        # Validate methods if present
        if self.methods is not None:
            if not isinstance(self.methods, list):
                errors.append(InvalidFieldTypeError("methods", self.methods, "list"))
            else:
                for i, method in enumerate(self.methods):
                    if not isinstance(method, MLShippingMethod):
                        errors.append(
                            InvalidFieldTypeError(
                                f"methods[{i}]", method, "MLShippingMethod"
                            )
                        )

        # Validate tags if present
        if self.tags is not None:
            if not isinstance(self.tags, list):
                errors.append(InvalidFieldTypeError("tags", self.tags, "list"))
            else:
                for i, tag in enumerate(self.tags):
                    if not isinstance(tag, str):
                        errors.append(InvalidFieldTypeError(f"tags[{i}]", tag, "str"))

        # Validate dimensions if present
        if self.dimensions is not None:
            if not isinstance(self.dimensions, dict):
                errors.append(
                    InvalidFieldTypeError("dimensions", self.dimensions, "dict")
                )
            else:
                # Validate dimension fields
                for dim_field in ["weight", "width", "height", "length"]:
                    if dim_field in self.dimensions:
                        dim_value = self.dimensions[dim_field]
                        if not isinstance(dim_value, int | float | str):
                            errors.append(
                                InvalidFieldTypeError(
                                    f"dimensions.{dim_field}",
                                    dim_value,
                                    "number or string",
                                )
                            )

        # Validate cost if present
        if self.cost is not None:
            if not isinstance(self.cost, Decimal):
                errors.append(InvalidFieldTypeError("cost", self.cost, "Decimal"))
            elif self.cost < 0:
                errors.append(InvalidFieldRangeError("cost", self.cost, min_value=0))

        # Validate free_methods if present
        if self.free_methods is not None:
            if not isinstance(self.free_methods, list):
                errors.append(
                    InvalidFieldTypeError("free_methods", self.free_methods, "list")
                )
            else:
                for i, method in enumerate(self.free_methods):
                    if not isinstance(method, dict):
                        errors.append(
                            InvalidFieldTypeError(f"free_methods[{i}]", method, "dict")
                        )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        if field_name == "mode":
            valid_modes = ["me1", "me2", "not_specified", "custom"]
            if field_value not in valid_modes:
                raise InvalidFieldValueError(
                    field_name,
                    field_value,
                    f"Invalid shipping mode. Must be one of: {', '.join(valid_modes)}",
                )
        elif field_name == "free_shipping":
            if not isinstance(field_value, bool):
                raise InvalidFieldTypeError(field_name, field_value, "bool")
        elif field_name == "methods":
            if field_value is not None:
                if not isinstance(field_value, list):
                    raise InvalidFieldTypeError(field_name, field_value, "list")
                for i, method in enumerate(field_value):
                    if not isinstance(method, MLShippingMethod):
                        raise InvalidFieldTypeError(
                            f"{field_name}[{i}]", method, "MLShippingMethod"
                        )
        elif field_name == "tags":
            if field_value is not None:
                if not isinstance(field_value, list):
                    raise InvalidFieldTypeError(field_name, field_value, "list")
                for i, tag in enumerate(field_value):
                    if not isinstance(tag, str):
                        raise InvalidFieldTypeError(f"{field_name}[{i}]", tag, "str")
        elif field_name == "dimensions":
            if field_value is not None:
                if not isinstance(field_value, dict):
                    raise InvalidFieldTypeError(field_name, field_value, "dict")
        elif field_name == "local_pick_up":
            if not isinstance(field_value, bool):
                raise InvalidFieldTypeError(field_name, field_value, "bool")
        elif field_name == "cost":
            if field_value is not None:
                if not isinstance(field_value, Decimal):
                    raise InvalidFieldTypeError(field_name, field_value, "Decimal")
                if field_value < 0:
                    raise InvalidFieldRangeError(field_name, field_value, min_value=0)
        elif field_name == "currency_id":
            if not isinstance(field_value, str):
                raise InvalidFieldTypeError(field_name, field_value, "str")
        else:
            raise InvalidFieldValueError(
                field_name, field_value, f"Unknown field '{field_name}'"
            )

    def to_ml_api_format(self) -> dict[str, Any]:
        """Convert to MercadoLibre API format."""
        api_data = {
            "mode": self.mode,
            "free_shipping": self.free_shipping,
            "local_pick_up": self.local_pick_up,
        }

        if self.methods:
            api_data["methods"] = [
                {
                    "id": method.id,
                    "name": method.name,
                    "cost": float(method.cost),
                    "currency_id": method.currency_id,
                    "list_cost": float(method.list_cost) if method.list_cost else None,
                    "option_cost": float(method.option_cost)
                    if method.option_cost
                    else None,
                }
                for method in self.methods
            ]

        if self.tags:
            api_data["tags"] = self.tags

        if self.dimensions:
            api_data["dimensions"] = self.dimensions

        if self.free_methods:
            api_data["free_methods"] = self.free_methods

        if self.cost is not None:
            api_data["cost"] = float(self.cost)
            api_data["currency_id"] = self.currency_id

        return api_data

    @classmethod
    def from_ml_api_format(cls, data: dict[str, Any]) -> "MLShipping":
        """Create from MercadoLibre API format."""
        if "mode" not in data:
            raise RequiredFieldError("mode")

        # Convert methods if present
        methods = None
        if "methods" in data and data["methods"]:
            methods = []
            for method_data in data["methods"]:
                method = MLShippingMethod(
                    id=method_data["id"],
                    name=method_data["name"],
                    cost=Decimal(str(method_data["cost"])),
                    currency_id=method_data.get("currency_id", "ARS"),
                    list_cost=Decimal(str(method_data["list_cost"]))
                    if method_data.get("list_cost")
                    else None,
                    option_cost=Decimal(str(method_data["option_cost"]))
                    if method_data.get("option_cost")
                    else None,
                )
                methods.append(method)

        return cls(
            mode=data["mode"],
            free_shipping=data.get("free_shipping", False),
            methods=methods,
            tags=data.get("tags"),
            dimensions=data.get("dimensions"),
            local_pick_up=data.get("local_pick_up", False),
            free_methods=data.get("free_methods"),
            cost=Decimal(str(data["cost"])) if data.get("cost") is not None else None,
            currency_id=data.get("currency_id", "ARS"),
        )

    def validate_ml_constraints(self) -> None:
        """Validate MercadoLibre-specific constraints."""
        errors = []

        # Validate mode-specific constraints
        if self.mode == "me1":
            # MercadoLibre shipping mode 1 constraints
            if self.free_shipping and self.cost is not None and self.cost > 0:
                errors.append(
                    InvalidFieldValueError(
                        "cost",
                        self.cost,
                        "Cost must be 0 when free_shipping is True for mode 'me1'",
                    )
                )
        elif self.mode == "me2":
            # MercadoLibre shipping mode 2 constraints
            if not self.methods:
                errors.append(
                    InvalidFieldValueError(
                        "methods", self.methods, "Methods are required for mode 'me2'"
                    )
                )
        elif self.mode == "custom":
            # Custom shipping mode constraints
            if not self.cost:
                errors.append(
                    InvalidFieldValueError(
                        "cost", self.cost, "Cost is required for custom shipping mode"
                    )
                )

        # Validate currency constraints
        valid_currencies = ["ARS", "USD", "BRL", "CLP", "COP", "MXN", "PEN", "UYU"]
        if self.currency_id not in valid_currencies:
            errors.append(
                InvalidFieldValueError(
                    "currency_id",
                    self.currency_id,
                    f"Invalid currency. Must be one of: {', '.join(valid_currencies)}",
                )
            )

        # Validate dimensions constraints
        if self.dimensions:
            for dim_field in ["weight", "width", "height", "length"]:
                if dim_field in self.dimensions:
                    try:
                        dim_value = float(self.dimensions[dim_field])
                        if dim_value <= 0:
                            errors.append(
                                InvalidFieldRangeError(
                                    f"dimensions.{dim_field}", dim_value, min_value=0
                                )
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            InvalidFieldTypeError(
                                f"dimensions.{dim_field}",
                                self.dimensions[dim_field],
                                "number",
                            )
                        )

        # Validate tags constraints
        if self.tags:
            valid_tags = [
                "mandatory_free_shipping",
                "fulfillment",
                "self_service_in",
                "self_service_out",
                "cross_docking",
                "drop_off",
            ]
            for tag in self.tags:
                if tag not in valid_tags:
                    errors.append(
                        InvalidFieldValueError(
                            "tags",
                            tag,
                            f"Invalid tag. Must be one of: {', '.join(valid_tags)}",
                        )
                    )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def is_free_shipping(self) -> bool:
        """Check if shipping is free."""
        return self.free_shipping

    def has_local_pickup(self) -> bool:
        """Check if local pickup is available."""
        return self.local_pick_up

    def get_shipping_cost(self) -> Decimal:
        """Get the shipping cost."""
        if self.free_shipping:
            return Decimal("0")
        return self.cost or Decimal("0")

    def get_method_count(self) -> int:
        """Get the number of shipping methods."""
        return len(self.methods) if self.methods else 0

    def has_methods(self) -> bool:
        """Check if shipping methods are defined."""
        return self.methods is not None and len(self.methods) > 0

    def get_method_by_id(self, method_id: int) -> MLShippingMethod | None:
        """Get a shipping method by ID."""
        if not self.methods:
            return None

        for method in self.methods:
            if method.id == method_id:
                return method
        return None

    def add_method(self, method: MLShippingMethod) -> "MLShipping":
        """Add a shipping method, returning a new instance."""
        current_methods = self.methods or []
        new_methods = current_methods + [method]

        return MLShipping(
            mode=self.mode,
            free_shipping=self.free_shipping,
            methods=new_methods,
            tags=self.tags,
            dimensions=self.dimensions,
            local_pick_up=self.local_pick_up,
            free_methods=self.free_methods,
            cost=self.cost,
            currency_id=self.currency_id,
        )

    def remove_method(self, method_id: int) -> "MLShipping":
        """Remove a shipping method by ID, returning a new instance."""
        if not self.methods:
            return self

        new_methods = [m for m in self.methods if m.id != method_id]

        return MLShipping(
            mode=self.mode,
            free_shipping=self.free_shipping,
            methods=new_methods if new_methods else None,
            tags=self.tags,
            dimensions=self.dimensions,
            local_pick_up=self.local_pick_up,
            free_methods=self.free_methods,
            cost=self.cost,
            currency_id=self.currency_id,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLShipping":
        """
        Create from dictionary, handling nested MLShippingMethod objects.

        Args:
            data: Dictionary containing the value object data.

        Returns:
            New instance of the value object.
        """
        try:
            # Handle methods field specially
            if "methods" in data and data["methods"] is not None:
                methods = []
                for method_data in data["methods"]:
                    if isinstance(method_data, dict):
                        method = MLShippingMethod(**method_data)
                    else:
                        method = method_data  # Already an MLShippingMethod
                    methods.append(method)

                # Create a copy of data with converted methods
                converted_data = data.copy()
                converted_data["methods"] = methods

                return super().from_dict(converted_data)  # type: ignore
            else:
                return super().from_dict(data)  # type: ignore
        except Exception:
            return super().from_dict(data)  # type: ignore

    @classmethod
    def not_specified(cls) -> "MLShipping":
        """Create a shipping instance with mode 'not_specified'."""
        return cls(mode="not_specified")

    @classmethod
    def create_free_shipping(cls) -> "MLShipping":
        """Create a free shipping instance."""
        return cls(mode="me1", free_shipping=True, cost=Decimal("0"))

    @classmethod
    def custom_shipping(cls, cost: Decimal, currency_id: str = "ARS") -> "MLShipping":
        """Create a custom shipping instance with specified cost."""
        return cls(mode="custom", cost=cost, currency_id=currency_id)
