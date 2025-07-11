"""
Price Range value object.

This module defines the PriceRange value object for handling
price ranges in a type-safe manner across the application.
"""

from dataclasses import dataclass
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectValidationError,
)

# ISO 4217 Currency Codes - Common currencies used in the application
VALID_CURRENCY_CODES = {
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLP",
    "CNY",
    "COP",
    "CRC",
    "CUC",
    "CUP",
    "CVE",
    "CZK",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "GBP",
    "GEL",
    "GGP",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "IMP",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JEP",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KMF",
    "KPW",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRU",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLE",
    "SLL",
    "SOS",
    "SRD",
    "STN",
    "SVC",
    "SYP",
    "SZL",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TVD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "UYU",
    "UYW",
    "UZS",
    "VED",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XCD",
    "XDR",
    "XOF",
    "XPF",
    "YER",
    "ZAR",
    "ZMW",
    "ZWL",
}


@dataclass(frozen=True, eq=False)
class PriceRange(BaseValueObject):
    """
    Price range value object.

    This value object encapsulates a price range with minimum and maximum values,
    providing validation and serialization capabilities.
    """

    min_price: float
    max_price: float
    currency: str = "ARS"

    def validate(self) -> None:
        """Validate the PriceRange value object."""
        errors = []

        # Validate min_price
        if not isinstance(self.min_price, int | float):
            errors.append(InvalidFieldTypeError("min_price", self.min_price, "float"))
        elif self.min_price < 0:
            errors.append(
                InvalidFieldValueError(
                    "min_price", self.min_price, "Minimum price must be non-negative"
                )
            )

        # Validate max_price
        if not isinstance(self.max_price, int | float):
            errors.append(InvalidFieldTypeError("max_price", self.max_price, "float"))
        elif self.max_price < 0:
            errors.append(
                InvalidFieldValueError(
                    "max_price", self.max_price, "Maximum price must be non-negative"
                )
            )

        # Validate currency
        if not isinstance(self.currency, str):
            errors.append(InvalidFieldTypeError("currency", self.currency, "str"))
        elif not self.currency or len(self.currency.strip()) == 0:
            errors.append(RequiredFieldError("currency"))
        elif len(self.currency) > 10:
            errors.append(
                InvalidFieldValueError(
                    "currency",
                    self.currency,
                    "Currency code must be 10 characters or less",
                )
            )
        elif self.currency.upper() not in VALID_CURRENCY_CODES:
            errors.append(
                InvalidFieldValueError(
                    "currency",
                    self.currency,
                    f"Invalid currency code '{self.currency}'. Must be a valid ISO 4217 currency code",
                )
            )

        # Validate min <= max
        if (
            isinstance(self.min_price, int | float)
            and isinstance(self.max_price, int | float)
            and self.min_price > self.max_price
        ):
            errors.append(
                InvalidFieldValueError(
                    "price_range",
                    f"min:{self.min_price}, max:{self.max_price}",
                    "Minimum price must be less than or equal to maximum price",
                )
            )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        if field_name == "min_price":
            if not isinstance(field_value, int | float):
                raise InvalidFieldTypeError(field_name, field_value, "float")
            if field_value < 0:
                raise InvalidFieldValueError(
                    field_name, field_value, "Minimum price must be non-negative"
                )
        elif field_name == "max_price":
            if not isinstance(field_value, int | float):
                raise InvalidFieldTypeError(field_name, field_value, "float")
            if field_value < 0:
                raise InvalidFieldValueError(
                    field_name, field_value, "Maximum price must be non-negative"
                )
        elif field_name == "currency":
            if not isinstance(field_value, str):
                raise InvalidFieldTypeError(field_name, field_value, "str")
            if not field_value or len(field_value.strip()) == 0:
                raise RequiredFieldError(field_name)
            if len(field_value) > 10:
                raise InvalidFieldValueError(
                    field_name,
                    field_value,
                    "Currency code must be 10 characters or less",
                )
            if field_value.upper() not in VALID_CURRENCY_CODES:
                raise InvalidFieldValueError(
                    field_name,
                    field_value,
                    f"Invalid currency code '{field_value}'. Must be a valid ISO 4217 currency code",
                )
        else:
            raise InvalidFieldValueError(
                field_name, field_value, f"Unknown field '{field_name}'"
            )

    @classmethod
    def from_dict_legacy(
        cls, data: dict[str, float], currency: str = "ARS"
    ) -> "PriceRange":
        """
        Create from legacy dict format for backward compatibility.

        Args:
            data: Dictionary with 'min' and 'max' keys
            currency: Currency code (defaults to ARS)

        Returns:
            New PriceRange instance

        Raises:
            ValueObjectValidationError: If dict format is invalid
        """
        if not isinstance(data, dict):
            raise InvalidFieldTypeError("price_range", data, "dict")

        if "min" not in data:
            raise RequiredFieldError("min")
        if "max" not in data:
            raise RequiredFieldError("max")

        try:
            return cls(
                min_price=float(data["min"]),
                max_price=float(data["max"]),
                currency=currency,
            )
        except (ValueError, TypeError) as e:
            raise ValueObjectValidationError(
                f"Failed to convert dict to PriceRange: {str(e)}", "price_range"
            ) from e

    def to_dict_legacy(self) -> dict[str, float]:
        """
        Convert to legacy dict format for backward compatibility.

        Returns:
            Dictionary with 'min' and 'max' keys
        """
        return {"min": self.min_price, "max": self.max_price}

    def get_range_span(self) -> float:
        """Get the span (difference) between max and min prices."""
        return self.max_price - self.min_price

    def get_midpoint(self) -> float:
        """Get the midpoint price between min and max."""
        return (self.min_price + self.max_price) / 2

    def contains_price(self, price: float) -> bool:
        """Check if a price falls within this range (inclusive)."""
        return self.min_price <= price <= self.max_price

    def overlaps_with(self, other: "PriceRange") -> bool:
        """Check if this price range overlaps with another."""
        if not isinstance(other, PriceRange):
            return False
        return self.min_price <= other.max_price and self.max_price >= other.min_price

    def expand(self, percentage: float) -> "PriceRange":
        """
        Expand the price range by a percentage.

        Args:
            percentage: Percentage to expand (e.g., 0.1 for 10%)

        Returns:
            New PriceRange with expanded values
        """
        if not isinstance(percentage, int | float) or percentage < 0:
            raise InvalidFieldValueError(
                "percentage", percentage, "Percentage must be a non-negative number"
            )

        span = self.get_range_span()
        expansion = span * percentage / 2  # Split expansion between min and max

        new_min = max(0, self.min_price - expansion)  # Don't go below 0
        new_max = self.max_price + expansion

        return PriceRange(min_price=new_min, max_price=new_max, currency=self.currency)

    def format_display(self, include_currency: bool = True) -> str:
        """
        Format the price range for display.

        Args:
            include_currency: Whether to include currency in the display

        Returns:
            Formatted string representation
        """
        min_formatted = f"{self.min_price:,.0f}"
        max_formatted = f"{self.max_price:,.0f}"

        if include_currency:
            return f"{min_formatted} - {max_formatted} {self.currency}"
        else:
            return f"{min_formatted} - {max_formatted}"

    @classmethod
    def from_single_price(
        cls, price: float, variance_percentage: float = 0.2, currency: str = "ARS"
    ) -> "PriceRange":
        """
        Create a price range from a single price with variance.

        Args:
            price: Base price
            variance_percentage: Variance percentage (e.g., 0.2 for ±20%)
            currency: Currency code

        Returns:
            New PriceRange instance
        """
        if not isinstance(price, int | float) or price < 0:
            raise InvalidFieldValueError(
                "price", price, "Price must be a non-negative number"
            )

        if not isinstance(variance_percentage, int | float) or variance_percentage < 0:
            raise InvalidFieldValueError(
                "variance_percentage",
                variance_percentage,
                "Variance percentage must be non-negative",
            )

        variance = price * variance_percentage
        min_price = max(0, price - variance)  # Don't go below 0
        max_price = price + variance

        return cls(min_price=min_price, max_price=max_price, currency=currency)
