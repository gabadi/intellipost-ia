"""
MercadoLibre sale terms value object.

This module defines the MLSaleTerms value object for handling
MercadoLibre sale terms in a type-safe manner.
"""

from dataclasses import dataclass
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldRangeError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectValidationError,
)
from shared.value_objects.protocols import MercadoLibreValueObjectProtocol


@dataclass(frozen=True)
class MLSaleTerm:
    """Individual MercadoLibre sale term."""

    id: str
    name: str
    value_id: str | None = None
    value_name: str | None = None
    value_struct: dict[str, Any] | None = None
    values: list[dict[str, Any]] | None = None

    def __post_init__(self):
        """Validate sale term after initialization."""
        if not self.id:
            raise RequiredFieldError("id")
        if not self.name:
            raise RequiredFieldError("name")

        # Validate that we have some form of value
        if not any([self.value_id, self.value_name, self.value_struct, self.values]):
            raise InvalidFieldValueError(
                "sale_term_value",
                None,
                "At least one value field (value_id, value_name, value_struct, or values) must be provided",
            )


@dataclass(frozen=True, eq=False)
class MLSaleTerms(BaseValueObject, MercadoLibreValueObjectProtocol):
    """
    MercadoLibre sale terms value object.

    This value object encapsulates MercadoLibre sale terms,
    providing validation and serialization capabilities.
    """

    sale_terms: dict[str, MLSaleTerm]

    def validate(self) -> None:
        """Validate the MLSaleTerms value object."""
        errors = []

        # Validate sale_terms dict
        if not isinstance(self.sale_terms, dict):
            errors.append(InvalidFieldTypeError("sale_terms", self.sale_terms, "dict"))
        else:
            # Validate each sale term
            for term_id, sale_term in self.sale_terms.items():
                try:
                    if not isinstance(sale_term, MLSaleTerm):
                        errors.append(
                            InvalidFieldTypeError(
                                f"sale_terms[{term_id}]", sale_term, "MLSaleTerm"
                            )
                        )
                    else:
                        # Validate sale term ID matches key
                        if sale_term.id != term_id:
                            errors.append(
                                InvalidFieldValueError(
                                    f"sale_terms[{term_id}].id",
                                    sale_term.id,
                                    f"Sale term ID must match dictionary key '{term_id}'",
                                )
                            )
                except Exception as e:
                    errors.append(
                        ValueObjectValidationError(
                            f"Error validating sale term {term_id}: {str(e)}",
                            f"sale_terms[{term_id}]",
                        )
                    )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        if field_name == "sale_terms":
            if not isinstance(field_value, dict):
                raise InvalidFieldTypeError(field_name, field_value, "dict")

            for term_id, sale_term in field_value.items():
                if not isinstance(sale_term, MLSaleTerm):
                    raise InvalidFieldTypeError(
                        f"{field_name}[{term_id}]", sale_term, "MLSaleTerm"
                    )
        else:
            raise InvalidFieldValueError(
                field_name, field_value, f"Unknown field '{field_name}'"
            )

    def to_ml_api_format(self) -> dict[str, Any]:
        """Convert to MercadoLibre API format."""
        api_sale_terms = []

        for sale_term in self.sale_terms.values():
            term_data = {
                "id": sale_term.id,
                "name": sale_term.name,
            }

            if sale_term.value_id:
                term_data["value_id"] = sale_term.value_id
            if sale_term.value_name:
                term_data["value_name"] = sale_term.value_name
            if sale_term.value_struct:
                term_data["value_struct"] = sale_term.value_struct
            if sale_term.values:
                term_data["values"] = sale_term.values

            api_sale_terms.append(term_data)

        return {"sale_terms": api_sale_terms}

    @classmethod
    def from_ml_api_format(cls, data: dict[str, Any]) -> "MLSaleTerms":
        """Create from MercadoLibre API format."""
        if "sale_terms" not in data:
            raise InvalidFieldValueError(
                "sale_terms", None, "Missing 'sale_terms' field in API data"
            )

        sale_terms = {}

        for term_data in data["sale_terms"]:
            if not isinstance(term_data, dict):
                raise InvalidFieldTypeError("sale_term", term_data, "dict")

            if "id" not in term_data:
                raise RequiredFieldError("id")
            if "name" not in term_data:
                raise RequiredFieldError("name")

            term_id = term_data["id"]
            sale_term = MLSaleTerm(
                id=term_id,
                name=term_data["name"],
                value_id=term_data.get("value_id"),
                value_name=term_data.get("value_name"),
                value_struct=term_data.get("value_struct"),
                values=term_data.get("values"),
            )

            sale_terms[term_id] = sale_term

        return cls(sale_terms=sale_terms)

    def validate_ml_constraints(self) -> None:
        """Validate MercadoLibre-specific constraints."""
        errors = []

        # Validate each sale term follows ML constraints
        for term_id, sale_term in self.sale_terms.items():
            # Validate sale term name length
            if len(sale_term.name) > 255:
                errors.append(
                    InvalidFieldValueError(
                        f"sale_terms[{term_id}].name",
                        sale_term.name,
                        "Sale term name must be 255 characters or less",
                    )
                )

            # Validate value_name length if present
            if sale_term.value_name and len(sale_term.value_name) > 255:
                errors.append(
                    InvalidFieldValueError(
                        f"sale_terms[{term_id}].value_name",
                        sale_term.value_name,
                        "Sale term value name must be 255 characters or less",
                    )
                )

            # Validate warranty-specific constraints
            if sale_term.id == "WARRANTY_TYPE":
                self._validate_warranty_term(term_id, sale_term, errors)
            elif sale_term.id == "WARRANTY_TIME":
                self._validate_warranty_time_term(term_id, sale_term, errors)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def _validate_warranty_term(
        self, term_id: str, sale_term: MLSaleTerm, errors: list
    ) -> None:
        """Validate warranty type sale term."""
        valid_warranty_types = [
            "Garantía del vendedor",
            "Garantía de fábrica",
            "Sin garantía",
        ]

        if sale_term.value_name and sale_term.value_name not in valid_warranty_types:
            errors.append(
                InvalidFieldValueError(
                    f"sale_terms[{term_id}].value_name",
                    sale_term.value_name,
                    f"Invalid warranty type. Must be one of: {', '.join(valid_warranty_types)}",
                )
            )

    def _validate_warranty_time_term(
        self, term_id: str, sale_term: MLSaleTerm, errors: list
    ) -> None:
        """Validate warranty time sale term."""
        if sale_term.value_struct:
            if (
                "number" not in sale_term.value_struct
                or "unit" not in sale_term.value_struct
            ):
                errors.append(
                    InvalidFieldValueError(
                        f"sale_terms[{term_id}].value_struct",
                        sale_term.value_struct,
                        "Warranty time must have 'number' and 'unit' fields",
                    )
                )
            else:
                # Validate warranty time number
                try:
                    warranty_number = int(sale_term.value_struct["number"])
                    if warranty_number < 0 or warranty_number > 999:
                        errors.append(
                            InvalidFieldRangeError(
                                f"sale_terms[{term_id}].value_struct.number",
                                warranty_number,
                                min_value=0,
                                max_value=999,
                            )
                        )
                except (ValueError, TypeError):
                    errors.append(
                        InvalidFieldTypeError(
                            f"sale_terms[{term_id}].value_struct.number",
                            sale_term.value_struct["number"],
                            "integer",
                        )
                    )

                # Validate warranty time unit
                valid_units = ["días", "meses", "años"]
                warranty_unit = sale_term.value_struct["unit"]
                if warranty_unit not in valid_units:
                    errors.append(
                        InvalidFieldValueError(
                            f"sale_terms[{term_id}].value_struct.unit",
                            warranty_unit,
                            f"Invalid warranty unit. Must be one of: {', '.join(valid_units)}",
                        )
                    )

    def get_sale_term(self, term_id: str) -> MLSaleTerm | None:
        """Get a specific sale term by ID."""
        return self.sale_terms.get(term_id)

    def has_sale_term(self, term_id: str) -> bool:
        """Check if a sale term exists."""
        return term_id in self.sale_terms

    def get_sale_term_value(self, term_id: str) -> Any:
        """Get the value of a specific sale term."""
        sale_term = self.get_sale_term(term_id)
        if not sale_term:
            return None

        # Return the most appropriate value
        if sale_term.value_struct:
            return sale_term.value_struct
        elif sale_term.values:
            return sale_term.values
        elif sale_term.value_name:
            return sale_term.value_name
        elif sale_term.value_id:
            return sale_term.value_id
        else:
            return None

    def add_sale_term(self, sale_term: MLSaleTerm) -> "MLSaleTerms":
        """Add or update a sale term, returning a new instance."""
        new_sale_terms = self.sale_terms.copy()
        new_sale_terms[sale_term.id] = sale_term
        return MLSaleTerms(sale_terms=new_sale_terms)

    def remove_sale_term(self, term_id: str) -> "MLSaleTerms":
        """Remove a sale term, returning a new instance."""
        if term_id not in self.sale_terms:
            return self

        new_sale_terms = self.sale_terms.copy()
        del new_sale_terms[term_id]
        return MLSaleTerms(sale_terms=new_sale_terms)

    def get_sale_term_count(self) -> int:
        """Get the number of sale terms."""
        return len(self.sale_terms)

    def is_empty(self) -> bool:
        """Check if there are no sale terms."""
        return len(self.sale_terms) == 0

    def has_warranty(self) -> bool:
        """Check if warranty terms are present."""
        return self.has_sale_term("WARRANTY_TYPE") or self.has_sale_term(
            "WARRANTY_TIME"
        )

    def get_warranty_info(self) -> dict[str, Any]:
        """Get warranty information as a dictionary."""
        warranty_info = {}

        warranty_type = self.get_sale_term("WARRANTY_TYPE")
        if warranty_type:
            warranty_info["type"] = warranty_type.value_name

        warranty_time = self.get_sale_term("WARRANTY_TIME")
        if warranty_time and warranty_time.value_struct:
            warranty_info["time"] = warranty_time.value_struct

        return warranty_info

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLSaleTerms":
        """
        Create from dictionary, handling nested MLSaleTerm objects.

        Args:
            data: Dictionary containing the value object data.

        Returns:
            New instance of the value object.
        """
        try:
            if "sale_terms" in data:
                sale_terms = {}
                for term_id, term_data in data["sale_terms"].items():
                    if isinstance(term_data, dict):
                        sale_term = MLSaleTerm(**term_data)
                    else:
                        sale_term = term_data  # Already an MLSaleTerm
                    sale_terms[term_id] = sale_term

                return cls(sale_terms=sale_terms)
            else:
                return super().from_dict(data)  # type: ignore
        except Exception:
            return super().from_dict(data)  # type: ignore

    @classmethod
    def empty(cls) -> "MLSaleTerms":
        """Create an empty MLSaleTerms instance."""
        return cls(sale_terms={})

    @classmethod
    def with_warranty(
        cls, warranty_type: str, warranty_time: dict[str, Any] | None = None
    ) -> "MLSaleTerms":
        """Create MLSaleTerms with warranty information."""
        sale_terms = {}

        # Add warranty type
        warranty_type_term = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name=warranty_type,
        )
        sale_terms["WARRANTY_TYPE"] = warranty_type_term

        # Add warranty time if provided
        if warranty_time:
            warranty_time_term = MLSaleTerm(
                id="WARRANTY_TIME",
                name="Tiempo de garantía",
                value_struct=warranty_time,
            )
            sale_terms["WARRANTY_TIME"] = warranty_time_term

        return cls(sale_terms=sale_terms)
