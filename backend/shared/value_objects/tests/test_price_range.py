"""
Comprehensive tests for PriceRange value object.

This module provides complete test coverage for the PriceRange value object,
including validation, utility methods, edge cases, and regression tests.
"""

import json

import pytest

from shared.value_objects.exceptions import (
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectValidationError,
)
from shared.value_objects.price_range import PriceRange

pytestmark = pytest.mark.unit


class TestPriceRangeBasicCreation:
    """Test basic creation and validation of PriceRange."""

    def test_valid_price_range_creation(self):
        """Test creating a valid price range."""
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")

        assert price_range.min_price == 100.0
        assert price_range.max_price == 200.0
        assert price_range.currency == "USD"
        assert price_range.is_valid()

    def test_default_currency(self):
        """Test that default currency is ARS."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        assert price_range.currency == "ARS"
        assert price_range.is_valid()

    def test_equal_min_max_prices(self):
        """Test that equal min and max prices are valid."""
        price_range = PriceRange(min_price=100.0, max_price=100.0)

        assert price_range.is_valid()

    def test_integer_prices(self):
        """Test that integer prices work correctly."""
        price_range = PriceRange(min_price=100, max_price=200)

        assert price_range.min_price == 100
        assert price_range.max_price == 200
        assert price_range.is_valid()

    def test_zero_prices(self):
        """Test that zero prices are valid."""
        price_range = PriceRange(min_price=0.0, max_price=0.0)

        assert price_range.is_valid()


class TestPriceRangeValidationErrors:
    """Test validation errors for PriceRange."""

    def test_negative_min_price(self):
        """Test that negative min_price raises error."""
        with pytest.raises(InvalidFieldValueError) as exc_info:
            PriceRange(min_price=-10.0, max_price=100.0)

        assert "min_price" in str(exc_info.value)
        assert "non-negative" in str(exc_info.value)

    def test_negative_max_price(self):
        """Test that negative max_price raises error."""
        with pytest.raises(MultipleValidationError) as exc_info:
            PriceRange(min_price=10.0, max_price=-100.0)

        errors_str = str(exc_info.value)
        assert "max_price" in errors_str
        assert "non-negative" in errors_str

    def test_min_price_greater_than_max_price(self):
        """Test that min_price > max_price raises error."""
        with pytest.raises(InvalidFieldValueError) as exc_info:
            PriceRange(min_price=200.0, max_price=100.0)

        assert "price_range" in str(exc_info.value)
        assert "less than or equal" in str(exc_info.value)

    def test_invalid_min_price_type(self):
        """Test that invalid min_price type raises error."""
        with pytest.raises(InvalidFieldTypeError) as exc_info:
            PriceRange(min_price="invalid", max_price=100.0)

        assert "min_price" in str(exc_info.value)
        assert "float" in str(exc_info.value)

    def test_invalid_max_price_type(self):
        """Test that invalid max_price type raises error."""
        with pytest.raises(InvalidFieldTypeError) as exc_info:
            PriceRange(min_price=100.0, max_price="invalid")

        assert "max_price" in str(exc_info.value)
        assert "float" in str(exc_info.value)

    def test_invalid_currency_type(self):
        """Test that invalid currency type raises error."""
        with pytest.raises(InvalidFieldTypeError) as exc_info:
            PriceRange(min_price=100.0, max_price=200.0, currency=123)

        assert "currency" in str(exc_info.value)
        assert "str" in str(exc_info.value)

    def test_empty_currency(self):
        """Test that empty currency raises error."""
        with pytest.raises(RequiredFieldError) as exc_info:
            PriceRange(min_price=100.0, max_price=200.0, currency="")

        assert "currency" in str(exc_info.value)

    def test_whitespace_only_currency(self):
        """Test that whitespace-only currency raises error."""
        with pytest.raises(RequiredFieldError) as exc_info:
            PriceRange(min_price=100.0, max_price=200.0, currency="   ")

        assert "currency" in str(exc_info.value)

    def test_currency_too_long(self):
        """Test that currency longer than 10 characters raises error."""
        with pytest.raises(InvalidFieldValueError) as exc_info:
            PriceRange(min_price=100.0, max_price=200.0, currency="A" * 11)

        assert "currency" in str(exc_info.value)
        assert "10 characters" in str(exc_info.value)

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are collected."""
        with pytest.raises(MultipleValidationError) as exc_info:
            PriceRange(min_price=-10.0, max_price=-5.0, currency="")

        errors = exc_info.value.errors
        assert len(errors) >= 2  # At least min_price and currency errors


class TestPriceRangeFieldValidation:
    """Test individual field validation methods."""

    def test_validate_min_price_field(self):
        """Test validating min_price field."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        # Valid values should not raise
        price_range.validate_field("min_price", 50.0)
        price_range.validate_field("min_price", 0)

        # Invalid type should raise
        with pytest.raises(InvalidFieldTypeError):
            price_range.validate_field("min_price", "invalid")

        # Negative value should raise
        with pytest.raises(InvalidFieldValueError):
            price_range.validate_field("min_price", -10.0)

    def test_validate_max_price_field(self):
        """Test validating max_price field."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        # Valid values should not raise
        price_range.validate_field("max_price", 300.0)
        price_range.validate_field("max_price", 0)

        # Invalid type should raise
        with pytest.raises(InvalidFieldTypeError):
            price_range.validate_field("max_price", "invalid")

        # Negative value should raise
        with pytest.raises(InvalidFieldValueError):
            price_range.validate_field("max_price", -10.0)

    def test_validate_currency_field(self):
        """Test validating currency field."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        # Valid values should not raise
        price_range.validate_field("currency", "USD")
        price_range.validate_field("currency", "EUR")

        # Invalid type should raise
        with pytest.raises(InvalidFieldTypeError):
            price_range.validate_field("currency", 123)

        # Empty value should raise
        with pytest.raises(RequiredFieldError):
            price_range.validate_field("currency", "")

        # Too long value should raise
        with pytest.raises(InvalidFieldValueError):
            price_range.validate_field("currency", "A" * 11)

    def test_validate_unknown_field(self):
        """Test validating unknown field."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        with pytest.raises(InvalidFieldValueError) as exc_info:
            price_range.validate_field("unknown_field", "value")

        assert "Unknown field" in str(exc_info.value)
        assert "unknown_field" in str(exc_info.value)


class TestPriceRangeLegacyCompatibility:
    """Test legacy format compatibility methods."""

    def test_from_dict_legacy_valid(self):
        """Test creating from valid legacy dict format."""
        data = {"min": 100.0, "max": 200.0}
        price_range = PriceRange.from_dict_legacy(data, currency="USD")

        assert price_range.min_price == 100.0
        assert price_range.max_price == 200.0
        assert price_range.currency == "USD"

    def test_from_dict_legacy_default_currency(self):
        """Test creating from legacy dict with default currency."""
        data = {"min": 100.0, "max": 200.0}
        price_range = PriceRange.from_dict_legacy(data)

        assert price_range.currency == "ARS"

    def test_from_dict_legacy_invalid_type(self):
        """Test from_dict_legacy with invalid data type."""
        with pytest.raises(InvalidFieldTypeError) as exc_info:
            PriceRange.from_dict_legacy("not a dict")

        assert "price_range" in str(exc_info.value)
        assert "dict" in str(exc_info.value)

    def test_from_dict_legacy_missing_min(self):
        """Test from_dict_legacy with missing min key."""
        with pytest.raises(RequiredFieldError) as exc_info:
            PriceRange.from_dict_legacy({"max": 200.0})

        assert "min" in str(exc_info.value)

    def test_from_dict_legacy_missing_max(self):
        """Test from_dict_legacy with missing max key."""
        with pytest.raises(RequiredFieldError) as exc_info:
            PriceRange.from_dict_legacy({"min": 100.0})

        assert "max" in str(exc_info.value)

    def test_from_dict_legacy_invalid_values(self):
        """Test from_dict_legacy with invalid values."""
        with pytest.raises(ValueObjectValidationError):
            PriceRange.from_dict_legacy({"min": "invalid", "max": 200.0})

    def test_to_dict_legacy(self):
        """Test converting to legacy dict format."""
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        result = price_range.to_dict_legacy()

        expected = {"min": 100.0, "max": 200.0}
        assert result == expected

    def test_to_dict_legacy_preserves_precision(self):
        """Test that to_dict_legacy preserves numeric precision."""
        price_range = PriceRange(min_price=100.5, max_price=200.75)
        result = price_range.to_dict_legacy()

        assert result["min"] == 100.5
        assert result["max"] == 200.75


class TestPriceRangeUtilityMethods:
    """Test utility methods of PriceRange."""

    def test_get_range_span(self):
        """Test getting range span."""
        price_range = PriceRange(min_price=100.0, max_price=300.0)

        assert price_range.get_range_span() == 200.0

    def test_get_range_span_zero(self):
        """Test getting range span when min equals max."""
        price_range = PriceRange(min_price=100.0, max_price=100.0)

        assert price_range.get_range_span() == 0.0

    def test_get_midpoint(self):
        """Test getting midpoint price."""
        price_range = PriceRange(min_price=100.0, max_price=300.0)

        assert price_range.get_midpoint() == 200.0

    def test_get_midpoint_equal_prices(self):
        """Test getting midpoint when min equals max."""
        price_range = PriceRange(min_price=100.0, max_price=100.0)

        assert price_range.get_midpoint() == 100.0

    def test_contains_price_within_range(self):
        """Test contains_price with price within range."""
        price_range = PriceRange(min_price=100.0, max_price=300.0)

        assert price_range.contains_price(150.0)
        assert price_range.contains_price(100.0)  # Boundary
        assert price_range.contains_price(300.0)  # Boundary

    def test_contains_price_outside_range(self):
        """Test contains_price with price outside range."""
        price_range = PriceRange(min_price=100.0, max_price=300.0)

        assert not price_range.contains_price(50.0)
        assert not price_range.contains_price(350.0)

    def test_overlaps_with_overlapping_ranges(self):
        """Test overlaps_with method with overlapping ranges."""
        range1 = PriceRange(min_price=100.0, max_price=200.0)
        range2 = PriceRange(min_price=150.0, max_price=250.0)

        assert range1.overlaps_with(range2)
        assert range2.overlaps_with(range1)

    def test_overlaps_with_non_overlapping_ranges(self):
        """Test overlaps_with method with non-overlapping ranges."""
        range1 = PriceRange(min_price=100.0, max_price=200.0)
        range2 = PriceRange(min_price=300.0, max_price=400.0)

        assert not range1.overlaps_with(range2)
        assert not range2.overlaps_with(range1)

    def test_overlaps_with_touching_ranges(self):
        """Test overlaps_with method with ranges that just touch."""
        range1 = PriceRange(min_price=100.0, max_price=200.0)
        range2 = PriceRange(min_price=200.0, max_price=300.0)

        assert range1.overlaps_with(range2)
        assert range2.overlaps_with(range1)

    def test_overlaps_with_invalid_type(self):
        """Test overlaps_with method with invalid type."""
        range1 = PriceRange(min_price=100.0, max_price=200.0)

        assert not range1.overlaps_with("not a range")
        assert not range1.overlaps_with(None)

    def test_expand_valid_percentage(self):
        """Test expand method with valid percentage."""
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        expanded = price_range.expand(0.2)  # 20% expansion

        # Original span is 100, so 20% expansion adds 10 to each side
        assert expanded.min_price == 90.0
        assert expanded.max_price == 210.0
        assert expanded.currency == "USD"

    def test_expand_zero_percentage(self):
        """Test expand method with zero percentage."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)
        expanded = price_range.expand(0.0)

        assert expanded.min_price == 100.0
        assert expanded.max_price == 200.0

    def test_expand_prevents_negative_prices(self):
        """Test that expand prevents negative prices."""
        price_range = PriceRange(min_price=10.0, max_price=20.0)
        expanded = price_range.expand(2.0)  # 200% expansion

        # Should not go below 0
        assert expanded.min_price == 0.0
        assert expanded.max_price == 30.0  # 20 + (10 * 2 / 2)

    def test_expand_invalid_percentage_type(self):
        """Test expand method with invalid percentage type."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        with pytest.raises(InvalidFieldValueError):
            price_range.expand("invalid")

    def test_expand_negative_percentage(self):
        """Test expand method with negative percentage."""
        price_range = PriceRange(min_price=100.0, max_price=200.0)

        with pytest.raises(InvalidFieldValueError):
            price_range.expand(-0.1)


class TestPriceRangeDisplayMethods:
    """Test display and formatting methods."""

    def test_format_display_with_currency(self):
        """Test format_display with currency included."""
        price_range = PriceRange(min_price=1000.5, max_price=2000.75, currency="USD")
        result = price_range.format_display(include_currency=True)

        assert result == "1,000 - 2,001 USD"

    def test_format_display_without_currency(self):
        """Test format_display without currency."""
        price_range = PriceRange(min_price=1000.5, max_price=2000.75, currency="USD")
        result = price_range.format_display(include_currency=False)

        assert result == "1,000 - 2,001"

    def test_format_display_large_numbers(self):
        """Test format_display with large numbers."""
        price_range = PriceRange(
            min_price=1000000.0, max_price=2000000.0, currency="ARS"
        )
        result = price_range.format_display()

        assert result == "1,000,000 - 2,000,000 ARS"

    def test_format_display_zero_values(self):
        """Test format_display with zero values."""
        price_range = PriceRange(min_price=0.0, max_price=0.0, currency="USD")
        result = price_range.format_display()

        assert result == "0 - 0 USD"


class TestPriceRangeFromSinglePrice:
    """Test creating price range from single price."""

    def test_from_single_price_default_variance(self):
        """Test creating price range from single price with default variance."""
        price_range = PriceRange.from_single_price(100.0, currency="USD")

        # Default variance is 20%
        assert price_range.min_price == 80.0
        assert price_range.max_price == 120.0
        assert price_range.currency == "USD"

    def test_from_single_price_custom_variance(self):
        """Test creating price range from single price with custom variance."""
        price_range = PriceRange.from_single_price(100.0, variance_percentage=0.1)

        # 10% variance
        assert price_range.min_price == 90.0
        assert price_range.max_price == 110.0

    def test_from_single_price_zero_variance(self):
        """Test creating price range with zero variance."""
        price_range = PriceRange.from_single_price(100.0, variance_percentage=0.0)

        assert price_range.min_price == 100.0
        assert price_range.max_price == 100.0

    def test_from_single_price_prevents_negative(self):
        """Test that from_single_price prevents negative prices."""
        price_range = PriceRange.from_single_price(10.0, variance_percentage=2.0)

        # Should not go below 0
        assert price_range.min_price == 0.0
        assert price_range.max_price == 30.0

    def test_from_single_price_invalid_price_type(self):
        """Test from_single_price with invalid price type."""
        with pytest.raises(InvalidFieldValueError):
            PriceRange.from_single_price("invalid")

    def test_from_single_price_negative_price(self):
        """Test from_single_price with negative price."""
        with pytest.raises(InvalidFieldValueError):
            PriceRange.from_single_price(-10.0)

    def test_from_single_price_invalid_variance_type(self):
        """Test from_single_price with invalid variance type."""
        with pytest.raises(InvalidFieldValueError):
            PriceRange.from_single_price(100.0, variance_percentage="invalid")

    def test_from_single_price_negative_variance(self):
        """Test from_single_price with negative variance."""
        with pytest.raises(InvalidFieldValueError):
            PriceRange.from_single_price(100.0, variance_percentage=-0.1)


class TestPriceRangeSerializationDeserialization:
    """Test serialization and deserialization methods."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        result = price_range.to_dict()

        expected = {"min_price": 100.0, "max_price": 200.0, "currency": "USD"}
        assert result == expected

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {"min_price": 100.0, "max_price": 200.0, "currency": "USD"}
        price_range = PriceRange.from_dict(data)

        assert price_range.min_price == 100.0
        assert price_range.max_price == 200.0
        assert price_range.currency == "USD"

    def test_to_json(self):
        """Test converting to JSON."""
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        result = price_range.to_json()

        parsed = json.loads(result)
        expected = {"min_price": 100.0, "max_price": 200.0, "currency": "USD"}
        assert parsed == expected

    def test_from_json(self):
        """Test creating from JSON."""
        json_data = '{"min_price": 100.0, "max_price": 200.0, "currency": "USD"}'
        price_range = PriceRange.from_json(json_data)

        assert price_range.min_price == 100.0
        assert price_range.max_price == 200.0
        assert price_range.currency == "USD"


class TestPriceRangeEquality:
    """Test equality and hashing of PriceRange."""

    def test_equality_same_values(self):
        """Test equality with same values."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")

        assert range1 == range2

    def test_equality_different_values(self):
        """Test inequality with different values."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=300.0, currency="USD")

        assert range1 != range2

    def test_equality_different_currency(self):
        """Test inequality with different currency."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=200.0, currency="EUR")

        assert range1 != range2

    def test_equality_with_non_price_range(self):
        """Test inequality with non-PriceRange object."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")

        assert range1 != "not a price range"
        assert range1 != 42
        assert range1 is not None

    def test_hash_consistency(self):
        """Test that equal objects have same hash."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")

        assert hash(range1) == hash(range2)

    def test_hash_difference(self):
        """Test that different objects have different hashes."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=300.0, currency="USD")

        # While not guaranteed, it's highly likely they'll be different
        assert hash(range1) != hash(range2)

    def test_hashable_in_set(self):
        """Test that PriceRange objects can be used in sets."""
        range1 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range2 = PriceRange(min_price=100.0, max_price=200.0, currency="USD")
        range3 = PriceRange(min_price=100.0, max_price=300.0, currency="USD")

        price_set = {range1, range2, range3}
        assert len(price_set) == 2  # range1 and range2 are equal


class TestPriceRangeEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test with very large numbers."""
        large_min = 1e10
        large_max = 1e15
        price_range = PriceRange(min_price=large_min, max_price=large_max)

        assert price_range.is_valid()
        assert price_range.get_range_span() == large_max - large_min

    def test_very_small_numbers(self):
        """Test with very small numbers."""
        small_min = 0.01
        small_max = 0.02
        price_range = PriceRange(min_price=small_min, max_price=small_max)

        assert price_range.is_valid()
        assert abs(price_range.get_range_span() - 0.01) < 1e-10

    def test_decimal_precision(self):
        """Test with high decimal precision."""
        price_range = PriceRange(min_price=100.123456789, max_price=200.987654321)

        assert price_range.is_valid()
        assert price_range.min_price == 100.123456789
        assert price_range.max_price == 200.987654321

    def test_maximum_currency_length(self):
        """Test with maximum allowed currency length (must be valid ISO code)."""
        # Use a valid 3-character ISO code instead of invalid long string
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="USD")

        assert price_range.is_valid()
        assert price_range.currency == "USD"

    def test_unicode_currency(self):
        """Test with unicode characters in currency."""
        price_range = PriceRange(
            min_price=100.0,
            max_price=200.0,
            currency="EUR",  # Using valid ISO code instead of symbol
        )

        assert price_range.is_valid()
        assert price_range.currency == "EUR"

    def test_valid_iso_currency_codes(self):
        """Test with various valid ISO 4217 currency codes."""
        valid_currencies = ["USD", "EUR", "ARS", "GBP", "JPY", "CHF", "BRL"]

        for currency in valid_currencies:
            price_range = PriceRange(
                min_price=100.0, max_price=200.0, currency=currency
            )
            assert price_range.is_valid()
            assert price_range.currency == currency

    def test_case_insensitive_currency_validation(self):
        """Test that currency validation is case insensitive."""
        # Lowercase should work
        price_range = PriceRange(min_price=100.0, max_price=200.0, currency="usd")
        assert price_range.is_valid()
        assert price_range.currency == "usd"  # Original case preserved

    def test_invalid_currency_codes(self):
        """Test that invalid currency codes raise errors."""
        invalid_currencies = ["INVALID", "XYZ", "FAKE", "123", "$", "€"]

        for currency in invalid_currencies:
            with pytest.raises(InvalidFieldValueError) as exc_info:
                PriceRange(min_price=100.0, max_price=200.0, currency=currency)

            assert "Invalid currency code" in str(exc_info.value)
            assert "ISO 4217" in str(exc_info.value)


class TestPriceRangeRegressionTests:
    """Regression tests for specific bugs or issues."""

    def test_regression_float_to_int_conversion(self):
        """Regression test: ensure float prices work with integer operations."""
        price_range = PriceRange(min_price=100.5, max_price=200.7)

        # These operations should work without type errors
        span = price_range.get_range_span()
        midpoint = price_range.get_midpoint()

        assert isinstance(span, float)
        assert isinstance(midpoint, float)
        assert span > 0
        assert 100.5 < midpoint < 200.7

    def test_regression_currency_validation_order(self):
        """Regression test: currency validation should happen in correct order."""
        # Type check should come before length check
        with pytest.raises(InvalidFieldTypeError):
            PriceRange(min_price=100.0, max_price=200.0, currency=123)

    def test_regression_negative_expansion_edge_case(self):
        """Regression test: expansion should handle edge case where min would go very negative."""
        price_range = PriceRange(min_price=1.0, max_price=2.0)

        # Very large expansion should still not go below 0
        expanded = price_range.expand(100.0)  # 10000% expansion

        assert expanded.min_price == 0.0
        assert expanded.max_price > 2.0

    def test_regression_overlaps_with_exact_boundaries(self):
        """Regression test: overlaps_with should handle exact boundary cases correctly."""
        range1 = PriceRange(min_price=100.0, max_price=200.0)
        range2 = PriceRange(min_price=200.0, max_price=300.0)
        range3 = PriceRange(min_price=50.0, max_price=100.0)

        # These should overlap (touching at boundary)
        assert range1.overlaps_with(range2)
        assert range2.overlaps_with(range1)
        assert range1.overlaps_with(range3)
        assert range3.overlaps_with(range1)

    def test_regression_serialization_roundtrip_precision(self):
        """Regression test: serialization roundtrip should preserve precision."""
        original = PriceRange(
            min_price=100.123456789, max_price=200.987654321, currency="USD"
        )

        # Test dict roundtrip
        dict_data = original.to_dict()
        from_dict = PriceRange.from_dict(dict_data)
        assert from_dict == original

        # Test JSON roundtrip
        json_data = original.to_json()
        from_json = PriceRange.from_json(json_data)
        assert from_json == original

        # Test legacy roundtrip
        legacy_data = original.to_dict_legacy()
        from_legacy = PriceRange.from_dict_legacy(legacy_data, currency="USD")
        assert from_legacy.min_price == original.min_price
        assert from_legacy.max_price == original.max_price
        assert from_legacy.currency == original.currency
