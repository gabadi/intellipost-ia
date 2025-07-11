"""
Tests for MercadoLibre sale terms value object.
"""

import pytest

from shared.value_objects.exceptions import (
    InvalidFieldRangeError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    RequiredFieldError,
)
from shared.value_objects.mercadolibre.sale_terms import MLSaleTerm, MLSaleTerms

pytestmark = pytest.mark.unit


class TestMLSaleTerm:
    """Test cases for MLSaleTerm."""

    def test_valid_sale_term_creation(self):
        """Test creating a valid ML sale term."""
        term = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )

        assert term.id == "WARRANTY_TYPE"
        assert term.name == "Tipo de garantía"
        assert term.value_name == "Garantía de fábrica"

    def test_sale_term_with_value_struct(self):
        """Test sale term with value_struct."""
        term = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        assert term.id == "WARRANTY_TIME"
        assert term.name == "Tiempo de garantía"
        assert term.value_struct == {"number": 12, "unit": "meses"}

    def test_sale_term_missing_id(self):
        """Test sale term creation with missing ID."""
        with pytest.raises(RequiredFieldError):
            MLSaleTerm(id="", name="Garantía", value_name="Sí")

    def test_sale_term_missing_name(self):
        """Test sale term creation with missing name."""
        with pytest.raises(RequiredFieldError):
            MLSaleTerm(id="WARRANTY_TYPE", name="", value_name="Sí")

    def test_sale_term_missing_value(self):
        """Test sale term creation with no value fields."""
        with pytest.raises(InvalidFieldValueError):
            MLSaleTerm(id="WARRANTY_TYPE", name="Garantía")


class TestMLSaleTerms:
    """Test cases for MLSaleTerms."""

    def test_valid_sale_terms_creation(self):
        """Test creating valid ML sale terms."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        assert len(sale_terms.sale_terms) == 2
        assert sale_terms.has_sale_term("WARRANTY_TYPE")
        assert sale_terms.has_sale_term("WARRANTY_TIME")
        assert not sale_terms.is_empty()
        assert sale_terms.has_warranty()

    def test_empty_sale_terms(self):
        """Test creating empty ML sale terms."""
        sale_terms = MLSaleTerms.empty()

        assert len(sale_terms.sale_terms) == 0
        assert sale_terms.is_empty()
        assert sale_terms.get_sale_term_count() == 0
        assert not sale_terms.has_warranty()

    def test_get_sale_term(self):
        """Test getting a specific sale term."""
        term = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": term})

        retrieved = sale_terms.get_sale_term("WARRANTY_TYPE")
        assert retrieved == term

        not_found = sale_terms.get_sale_term("NONEXISTENT")
        assert not_found is None

    def test_get_sale_term_value(self):
        """Test getting sale term value."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        warranty_type = sale_terms.get_sale_term_value("WARRANTY_TYPE")
        assert warranty_type == "Garantía de fábrica"

        warranty_time = sale_terms.get_sale_term_value("WARRANTY_TIME")
        assert warranty_time == {"number": 12, "unit": "meses"}

        missing_value = sale_terms.get_sale_term_value("NONEXISTENT")
        assert missing_value is None

    def test_add_sale_term(self):
        """Test adding a sale term."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": term1})

        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )
        updated_sale_terms = sale_terms.add_sale_term(term2)

        # Original should be unchanged
        assert len(sale_terms.sale_terms) == 1

        # New instance should have both
        assert len(updated_sale_terms.sale_terms) == 2
        assert updated_sale_terms.has_sale_term("WARRANTY_TYPE")
        assert updated_sale_terms.has_sale_term("WARRANTY_TIME")

    def test_remove_sale_term(self):
        """Test removing a sale term."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )
        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        updated_sale_terms = sale_terms.remove_sale_term("WARRANTY_TYPE")

        # Original should be unchanged
        assert len(sale_terms.sale_terms) == 2

        # New instance should have one less
        assert len(updated_sale_terms.sale_terms) == 1
        assert not updated_sale_terms.has_sale_term("WARRANTY_TYPE")
        assert updated_sale_terms.has_sale_term("WARRANTY_TIME")

    def test_get_warranty_info(self):
        """Test getting warranty information."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        warranty_info = sale_terms.get_warranty_info()

        assert warranty_info["type"] == "Garantía de fábrica"
        assert warranty_info["time"] == {"number": 12, "unit": "meses"}

    def test_with_warranty_factory_method(self):
        """Test creating sale terms with warranty using factory method."""
        sale_terms = MLSaleTerms.with_warranty(
            warranty_type="Garantía de fábrica",
            warranty_time={"number": 12, "unit": "meses"},
        )

        assert sale_terms.has_warranty()
        assert sale_terms.has_sale_term("WARRANTY_TYPE")
        assert sale_terms.has_sale_term("WARRANTY_TIME")

        warranty_info = sale_terms.get_warranty_info()
        assert warranty_info["type"] == "Garantía de fábrica"
        assert warranty_info["time"] == {"number": 12, "unit": "meses"}

    def test_with_warranty_type_only(self):
        """Test creating sale terms with warranty type only."""
        sale_terms = MLSaleTerms.with_warranty("Garantía de fábrica")

        assert sale_terms.has_warranty()
        assert sale_terms.has_sale_term("WARRANTY_TYPE")
        assert not sale_terms.has_sale_term("WARRANTY_TIME")

    def test_validation_invalid_sale_terms_type(self):
        """Test validation with invalid sale terms type."""
        with pytest.raises(InvalidFieldTypeError):
            MLSaleTerms(sale_terms="not a dict")

    def test_validation_invalid_term_in_dict(self):
        """Test validation with invalid sale term in dict."""
        with pytest.raises(InvalidFieldTypeError):
            MLSaleTerms(sale_terms={"WARRANTY_TYPE": "not a MLSaleTerm"})

    def test_validation_mismatched_term_id(self):
        """Test validation with mismatched sale term ID."""
        term = MLSaleTerm(id="WARRANTY_TYPE", name="Garantía", value_name="Sí")

        with pytest.raises(InvalidFieldValueError):
            MLSaleTerms(sale_terms={"DIFFERENT_ID": term})  # ID mismatch

    def test_to_ml_api_format(self):
        """Test converting to MercadoLibre API format."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        result = sale_terms.to_ml_api_format()

        assert "sale_terms" in result
        assert len(result["sale_terms"]) == 2

        # Check term structure
        warranty_type = next(
            t for t in result["sale_terms"] if t["id"] == "WARRANTY_TYPE"
        )
        assert warranty_type["name"] == "Tipo de garantía"
        assert warranty_type["value_name"] == "Garantía de fábrica"

        warranty_time = next(
            t for t in result["sale_terms"] if t["id"] == "WARRANTY_TIME"
        )
        assert warranty_time["name"] == "Tiempo de garantía"
        assert warranty_time["value_struct"] == {"number": 12, "unit": "meses"}

    def test_from_ml_api_format(self):
        """Test creating from MercadoLibre API format."""
        api_data = {
            "sale_terms": [
                {
                    "id": "WARRANTY_TYPE",
                    "name": "Tipo de garantía",
                    "value_name": "Garantía de fábrica",
                },
                {
                    "id": "WARRANTY_TIME",
                    "name": "Tiempo de garantía",
                    "value_struct": {"number": 12, "unit": "meses"},
                },
            ]
        }

        sale_terms = MLSaleTerms.from_ml_api_format(api_data)

        assert len(sale_terms.sale_terms) == 2
        assert sale_terms.has_sale_term("WARRANTY_TYPE")
        assert sale_terms.has_sale_term("WARRANTY_TIME")

        warranty_type = sale_terms.get_sale_term("WARRANTY_TYPE")
        assert warranty_type.name == "Tipo de garantía"
        assert warranty_type.value_name == "Garantía de fábrica"

        warranty_time = sale_terms.get_sale_term("WARRANTY_TIME")
        assert warranty_time.name == "Tiempo de garantía"
        assert warranty_time.value_struct == {"number": 12, "unit": "meses"}

    def test_validate_ml_constraints(self):
        """Test MercadoLibre-specific constraints validation."""
        # Valid sale terms
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        sale_terms = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        # Should not raise any exception
        sale_terms.validate_ml_constraints()

    def test_validate_ml_constraints_long_names(self):
        """Test ML constraints validation with long names."""
        long_name = "a" * 256
        term = MLSaleTerm(
            id="WARRANTY_TYPE", name=long_name, value_name="Garantía de fábrica"
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": term})

        with pytest.raises(InvalidFieldValueError):
            sale_terms.validate_ml_constraints()

    def test_validate_warranty_type_constraints(self):
        """Test warranty type validation."""
        # Valid warranty type
        term = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": term})
        sale_terms.validate_ml_constraints()

        # Invalid warranty type
        invalid_term = MLSaleTerm(
            id="WARRANTY_TYPE", name="Tipo de garantía", value_name="Invalid warranty"
        )
        invalid_sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": invalid_term})

        with pytest.raises(InvalidFieldValueError):
            invalid_sale_terms.validate_ml_constraints()

    def test_validate_warranty_time_constraints(self):
        """Test warranty time validation."""
        # Valid warranty time
        term = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TIME": term})
        sale_terms.validate_ml_constraints()

        # Invalid warranty time - missing fields
        invalid_term1 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12},  # Missing unit
        )
        invalid_sale_terms1 = MLSaleTerms(sale_terms={"WARRANTY_TIME": invalid_term1})

        with pytest.raises(InvalidFieldValueError):
            invalid_sale_terms1.validate_ml_constraints()

        # Invalid warranty time - invalid number
        invalid_term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": -1, "unit": "meses"},
        )
        invalid_sale_terms2 = MLSaleTerms(sale_terms={"WARRANTY_TIME": invalid_term2})

        with pytest.raises(InvalidFieldRangeError):
            invalid_sale_terms2.validate_ml_constraints()

        # Invalid warranty time - invalid unit
        invalid_term3 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "invalid"},
        )
        invalid_sale_terms3 = MLSaleTerms(sale_terms={"WARRANTY_TIME": invalid_term3})

        with pytest.raises(InvalidFieldValueError):
            invalid_sale_terms3.validate_ml_constraints()

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        term1 = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        term2 = MLSaleTerm(
            id="WARRANTY_TIME",
            name="Tiempo de garantía",
            value_struct={"number": 12, "unit": "meses"},
        )

        original = MLSaleTerms(
            sale_terms={"WARRANTY_TYPE": term1, "WARRANTY_TIME": term2}
        )

        # Convert to dict
        data = original.to_dict()

        # Convert back
        restored = MLSaleTerms.from_dict(data)

        assert original == restored
        assert len(restored.sale_terms) == 2
        assert restored.has_sale_term("WARRANTY_TYPE")
        assert restored.has_sale_term("WARRANTY_TIME")

    def test_json_serialization(self):
        """Test JSON serialization."""
        term = MLSaleTerm(
            id="WARRANTY_TYPE",
            name="Tipo de garantía",
            value_name="Garantía de fábrica",
        )
        sale_terms = MLSaleTerms(sale_terms={"WARRANTY_TYPE": term})

        # To JSON
        json_str = sale_terms.to_json()

        # From JSON
        restored = MLSaleTerms.from_json(json_str)

        assert sale_terms == restored
        assert restored.has_sale_term("WARRANTY_TYPE")
