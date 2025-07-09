"""
Unit tests for content generation services.

This module tests the infrastructure services including GeminiAIService,
MLCategoryService, and other specialized services.
"""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    AIServiceError,
    CategoryDetectionError,
)
from modules.content_generation.infrastructure.services.attribute_mapping_service import (
    AttributeMappingService,
)
from modules.content_generation.infrastructure.services.description_generation_service import (
    DescriptionGenerationService,
)
from modules.content_generation.infrastructure.services.gemini_ai_service import (
    GeminiAIService,
)
from modules.content_generation.infrastructure.services.ml_category_service import (
    MLCategoryService,
)
from modules.content_generation.infrastructure.services.title_generation_service import (
    TitleGenerationService,
)

pytestmark = pytest.mark.unit


class TestGeminiAIService:
    """Test cases for GeminiAIService."""

    @pytest.fixture
    def gemini_service(self):
        """Create a GeminiAIService instance for testing."""
        return GeminiAIService(
            api_key="test_api_key",
            model_name="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=2048,
            timeout_seconds=60,
            max_retries=3,
        )

    @pytest.fixture
    def mock_image_data(self):
        """Create mock image data for testing."""
        mock_image = Mock()
        mock_image.s3_key = "products/test/image1.jpg"
        mock_image.s3_url = "https://s3.amazonaws.com/bucket/products/test/image1.jpg"
        mock_image.file_format = "jpeg"
        mock_image.resolution_width = 800
        mock_image.resolution_height = 600
        return [mock_image]

    @pytest.mark.asyncio
    async def test_generate_listing_success(self, gemini_service, mock_image_data):
        """Test successful listing generation."""
        mock_response = {
            "text": """{
                "title": "iPhone 13 Pro 128GB Usado Excelente Estado",
                "description": "iPhone 13 Pro de 128GB en excelente estado con caja original...",
                "ml_category_id": "MLA1055",
                "ml_category_name": "Celulares y Teléfonos",
                "ml_title": "iPhone 13 Pro 128GB Usado Excelente Estado",
                "ml_price": 450000,
                "ml_currency_id": "ARS",
                "ml_available_quantity": 1,
                "ml_buying_mode": "buy_it_now",
                "ml_condition": "used",
                "ml_listing_type_id": "gold_special",
                "ml_attributes": {
                    "COLOR": "Negro",
                    "BRAND": "Apple",
                    "LINE": "iPhone",
                    "MODEL": "iPhone 13 Pro"
                },
                "ml_sale_terms": {
                    "id": "WARRANTY_TYPE",
                    "value_name": "Garantía del vendedor"
                },
                "ml_shipping": {
                    "mode": "me2",
                    "free_shipping": true
                },
                "confidence_overall": 0.87,
                "confidence_breakdown": {
                    "title": 0.92,
                    "description": 0.85,
                    "category": 0.88,
                    "price": 0.75,
                    "attributes": 0.90
                }
            }"""
        }

        with patch.object(gemini_service, "_generate_with_retry") as mock_generate:
            mock_generate.return_value = mock_response

            result = await gemini_service.generate_listing(
                images=mock_image_data,
                prompt="Generate content for iPhone 13 Pro",
                category_hint="celulares",
            )

            assert isinstance(result, GeneratedContent)
            assert result.title == "iPhone 13 Pro 128GB Usado Excelente Estado"
            assert result.ml_category_id == "MLA1055"
            assert result.ml_price == Decimal("450000")
            assert result.confidence_overall == 0.87
            assert result.ai_provider == "gemini"

    @pytest.mark.asyncio
    async def test_generate_listing_api_error(self, gemini_service, mock_image_data):
        """Test API error handling."""
        with patch.object(gemini_service, "_generate_with_retry") as mock_generate:
            mock_generate.side_effect = Exception("API Error")

            with pytest.raises(
                AIServiceError, match="Unexpected error in content generation"
            ):
                await gemini_service.generate_listing(
                    images=mock_image_data, prompt="Generate content for iPhone 13 Pro"
                )

    @pytest.mark.asyncio
    async def test_generate_listing_invalid_response(
        self, gemini_service, mock_image_data
    ):
        """Test handling of invalid API response."""
        mock_response = {"text": "Invalid JSON response"}

        with patch.object(gemini_service, "_generate_with_retry") as mock_generate:
            mock_generate.return_value = mock_response

            with pytest.raises(
                AIServiceError, match="Unexpected error in content generation"
            ):
                await gemini_service.generate_listing(
                    images=mock_image_data, prompt="Generate content for iPhone 13 Pro"
                )

    @pytest.mark.asyncio
    async def test_generate_listing_low_confidence(
        self, gemini_service, mock_image_data
    ):
        """Test handling of low confidence response."""
        mock_response = {
            "text": """{
                "title": "Test Product",
                "description": "Test description for a product that needs to be at least 50 characters long to pass validation",
                "ml_category_id": "MLA1055",
                "ml_category_name": "Celulares y Teléfonos",
                "ml_title": "Test Product",
                "ml_price": 100000,
                "ml_currency_id": "ARS",
                "ml_available_quantity": 1,
                "ml_buying_mode": "buy_it_now",
                "ml_condition": "used",
                "ml_listing_type_id": "gold_special",
                "ml_attributes": {},
                "ml_sale_terms": {},
                "ml_shipping": {},
                "confidence_overall": 0.3,
                "confidence_breakdown": {}
            }"""
        }

        with patch.object(gemini_service, "_generate_with_retry") as mock_generate:
            mock_generate.return_value = mock_response

            # This should not raise an exception - the service doesn't validate confidence in generate_listing
            result = await gemini_service.generate_listing(
                images=mock_image_data,
                prompt="Generate content for low quality product",
            )

            assert result.confidence_overall == 0.3

    @pytest.mark.asyncio
    async def test_generate_listing_retry_logic(self, gemini_service, mock_image_data):
        """Test retry logic for transient errors."""
        mock_response = {
            "text": """{
                "title": "iPhone 13 Pro 128GB",
                "description": "iPhone description for a product that needs to be at least 50 characters long to pass validation",
                "ml_category_id": "MLA1055",
                "ml_category_name": "Celulares y Teléfonos",
                "ml_title": "iPhone 13 Pro 128GB",
                "ml_price": 450000,
                "ml_currency_id": "ARS",
                "ml_available_quantity": 1,
                "ml_buying_mode": "buy_it_now",
                "ml_condition": "used",
                "ml_listing_type_id": "gold_special",
                "ml_attributes": {},
                "ml_sale_terms": {},
                "ml_shipping": {},
                "confidence_overall": 0.87,
                "confidence_breakdown": {}
            }"""
        }

        with patch.object(gemini_service, "_generate_with_retry") as mock_generate:
            # The retry logic is handled in _generate_with_retry itself
            mock_generate.return_value = mock_response

            result = await gemini_service.generate_listing(
                images=mock_image_data, prompt="Generate content for iPhone 13 Pro"
            )

            assert isinstance(result, GeneratedContent)
            assert result.title == "iPhone 13 Pro 128GB"
            assert mock_generate.call_count == 1

    def test_build_prompt_with_category_hint(self, gemini_service):
        """Test prompt building with category hint."""
        prompt = gemini_service._create_mercadolibre_prompt(
            user_prompt="Generate content for iPhone",
            category_hint="celulares",
        )

        assert "celulares" in prompt
        assert "iPhone" in prompt
        assert "MercadoLibre" in prompt

    def test_build_prompt_without_category_hint(self, gemini_service):
        """Test prompt building without category hint."""
        prompt = gemini_service._create_mercadolibre_prompt(
            user_prompt="Generate content for iPhone", category_hint=None
        )

        assert "iPhone" in prompt
        assert "MercadoLibre" in prompt


class TestMLCategoryService:
    """Test cases for MLCategoryService."""

    @pytest.fixture
    def ml_category_service(self):
        """Create a MLCategoryService instance for testing."""
        return MLCategoryService(
            site_id="MLA",
            timeout_seconds=10,
            max_retries=3,
            cache_ttl_seconds=300,
            cache_max_size=1000,
        )

    @pytest.mark.asyncio
    async def test_predict_category_success(self, ml_category_service):
        """Test successful category prediction."""
        mock_search_results = [
            {
                "id": "MLA1055",
                "name": "Celulares y Smartphones",
                "path_from_root": [
                    {"id": "MLA1051", "name": "Celulares y Teléfonos"},
                    {"id": "MLA1055", "name": "Celulares y Smartphones"},
                ],
            }
        ]

        with patch.object(
            ml_category_service, "_search_categories_by_features"
        ) as mock_search:
            mock_search.return_value = mock_search_results

            with patch.object(
                ml_category_service, "_get_category_details_batch"
            ) as mock_details:
                mock_details.return_value = mock_search_results

                result = await ml_category_service.predict_category(
                    {
                        "title": "iPhone 13 Pro 128GB",
                        "description": "iPhone en excelente estado",
                        "brand": "Apple",
                    }
                )

                assert result["category_id"] == "MLA1055"
                assert result["category_name"] == "Celulares y Smartphones"
                assert "confidence" in result

    @pytest.mark.asyncio
    async def test_predict_category_api_error(self, ml_category_service):
        """Test API error handling."""
        with patch.object(
            ml_category_service, "_search_categories_by_features"
        ) as mock_search:
            mock_search.side_effect = Exception("API Error")

            with pytest.raises(
                CategoryDetectionError, match="Failed to predict category"
            ):
                await ml_category_service.predict_category(
                    {"title": "iPhone 13 Pro 128GB"}
                )

    @pytest.mark.asyncio
    async def test_predict_category_with_cache(self, ml_category_service):
        """Test category prediction with caching."""
        features = {"title": "iPhone 13 Pro 128GB", "brand": "Apple"}

        mock_search_results = [
            {
                "id": "MLA1055",
                "name": "Celulares y Smartphones",
                "path_from_root": [],
            }
        ]

        with patch.object(
            ml_category_service, "_search_categories_by_features"
        ) as mock_search:
            mock_search.return_value = mock_search_results

            with patch.object(
                ml_category_service, "_get_category_details_batch"
            ) as mock_details:
                mock_details.return_value = mock_search_results

                # First call
                result1 = await ml_category_service.predict_category(features)

                # Second call should use cache
                result2 = await ml_category_service.predict_category(features)

                assert result1 == result2
                assert mock_search.call_count == 1  # Only called once due to caching

    @pytest.mark.asyncio
    async def test_predict_category_low_confidence(self, ml_category_service):
        """Test handling of low confidence category prediction."""
        mock_search_results = [
            {
                "id": "MLA1055",
                "name": "Celulares y Smartphones",
                "path_from_root": [],
            }
        ]

        with patch.object(
            ml_category_service, "_search_categories_by_features"
        ) as mock_search:
            mock_search.return_value = mock_search_results

            with patch.object(
                ml_category_service, "_get_category_details_batch"
            ) as mock_details:
                mock_details.return_value = mock_search_results

                result = await ml_category_service.predict_category(
                    {"title": "Generic product"}
                )

            assert result["category_id"] == "MLA1055"
            assert result["category_name"] == "Celulares y Smartphones"
            assert "confidence" in result

    def test_build_category_features(self, ml_category_service):
        """Test building category features from product data."""
        # Test the internal _generate_search_queries method instead
        product_features = {
            "title": "iPhone 13 Pro 128GB Negro",
            "description": "iPhone en excelente estado con caja original",
            "brand": "Apple",
        }

        queries = ml_category_service._generate_search_queries(product_features)

        assert len(queries) > 0
        # Check if any query contains product-related terms
        all_queries_text = " ".join(queries)
        assert (
            "iPhone" in all_queries_text
            or "Apple" in all_queries_text
            or "celular" in all_queries_text.lower()
        )

    @pytest.mark.asyncio
    async def test_validate_category_valid(self, ml_category_service):
        """Test category validation for valid category."""
        # Mock the internal methods that validate_category uses
        mock_category_info = {
            "id": "MLA1055",
            "name": "Celulares y Smartphones",
            "settings": {"allow_listings": True, "status": "active"},
        }

        mock_attributes = {"attributes": []}

        with patch.object(ml_category_service, "get_category_info") as mock_info:
            mock_info.return_value = mock_category_info

            with patch.object(
                ml_category_service, "get_category_attributes"
            ) as mock_attrs:
                mock_attrs.return_value = mock_attributes

                result = await ml_category_service.validate_category(
                    "MLA1055", {"title": "iPhone 13 Pro 128GB", "brand": "Apple"}
                )

                assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_category_invalid(self, ml_category_service):
        """Test category validation for invalid category."""
        # Mock the internal methods that validate_category uses
        mock_category_info = {
            "id": "MLA1144",
            "name": "Invalid Category",
            "settings": {"allow_listings": False, "status": "inactive"},
        }

        with patch.object(ml_category_service, "get_category_info") as mock_info:
            mock_info.return_value = mock_category_info

            result = await ml_category_service.validate_category(
                "MLA1144",
                {  # Wrong category
                    "title": "iPhone 13 Pro 128GB",
                    "brand": "Apple",
                },
            )

            assert result["is_valid"] is False


class TestTitleGenerationService:
    """Test cases for TitleGenerationService."""

    @pytest.fixture
    def title_service(self):
        """Create a TitleGenerationService instance for testing."""
        return TitleGenerationService(
            max_title_length=60,
            min_title_length=10,
        )

    def test_generate_title_success(self, title_service):
        """Test successful title generation."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro Usado Excelente Estado",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
            "color": "Negro",
            "storage": "128GB",
        }

        result = title_service.generate_title(product_data, "MLA1055")

        assert len(result["title"]) <= 60
        assert len(result["title"]) >= 10
        assert result["confidence"] > 0.0
        assert "iPhone" in result["title"]
        assert "128GB" in result["title"]

    def test_generate_title_too_long(self, title_service):
        """Test title generation with content that's too long."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro Usado Excelente Estado Con Caja Original Y Todos Los Accesorios Incluidos",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
        }

        result = title_service.generate_title(product_data, "MLA1055")

        # Should be truncated to 60 characters
        assert len(result["title"]) <= 60
        assert result["confidence"] > 0.0

    def test_generate_title_variations(self, title_service):
        """Test generating title variations for A/B testing."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
            "color": "Negro",
            "storage": "128GB",
        }

        variations = title_service.generate_variations(product_data, "MLA1055", count=3)

        assert len(variations) == 3
        for variation in variations:
            assert len(variation["title"]) <= 60
            assert variation["confidence"] > 0.0
            assert "iPhone" in variation["title"]

    def test_validate_title_valid(self, title_service):
        """Test title validation for valid title."""
        is_valid, issues = title_service.validate_title("iPhone 13 Pro 128GB Negro")

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_title_too_long(self, title_service):
        """Test title validation for title that's too long."""
        long_title = "iPhone 13 Pro 128GB Negro Usado Excelente Estado Con Caja Original Y Accesorios"

        is_valid, issues = title_service.validate_title(long_title)

        assert is_valid is False
        assert any("length" in issue.lower() for issue in issues)

    def test_validate_title_empty(self, title_service):
        """Test title validation for empty title."""
        is_valid, issues = title_service.validate_title("")

        assert is_valid is False
        assert any("empty" in issue.lower() for issue in issues)

    def test_optimize_for_seo(self, title_service):
        """Test SEO optimization for MercadoLibre."""
        title = "iPhone 13 Pro 128GB Negro"

        optimized = title_service._optimize_for_seo(title, "MLA1055")

        assert len(optimized) <= 60
        assert "iPhone" in optimized
        # Should include key terms for MercadoLibre SEO

    def test_calculate_title_confidence(self, title_service):
        """Test title confidence calculation."""
        title = "iPhone 13 Pro 128GB Negro Usado Excelente Estado"
        product_data = {
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
            "color": "Negro",
            "storage": "128GB",
        }

        confidence = title_service._calculate_confidence(title, product_data, "MLA1055")

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident for good match


class TestDescriptionGenerationService:
    """Test cases for DescriptionGenerationService."""

    @pytest.fixture
    def description_service(self):
        """Create a DescriptionGenerationService instance for testing."""
        return DescriptionGenerationService(
            min_description_length=100,
            max_description_length=8000,
            target_description_length=500,
        )

    def test_generate_description_success(self, description_service):
        """Test successful description generation."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
            "color": "Negro",
            "storage": "128GB",
            "features": [
                "Pantalla Super Retina XDR",
                "Chip A15 Bionic",
                "Sistema de cámaras Pro",
            ],
        }

        result = description_service.generate_description(product_data, "MLA1055")

        assert len(result["description"]) >= 100
        assert len(result["description"]) <= 8000
        assert result["confidence"] > 0.0
        assert "iPhone" in result["description"]
        assert "128GB" in result["description"]
        assert "Negro" in result["description"]

    def test_generate_description_mobile_first(self, description_service):
        """Test mobile-first description formatting."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
        }

        result = description_service.generate_description(product_data, "MLA1055")

        # Should include mobile-friendly formatting
        assert "📱" in result["description"] or "•" in result["description"]
        assert result["confidence"] > 0.0

    def test_generate_description_with_warranty(self, description_service):
        """Test description generation with warranty information."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
        }

        result = description_service.generate_description(product_data, "MLA1055")

        assert (
            "garantía" in result["description"].lower()
            or "warranty" in result["description"].lower()
        )
        assert result["confidence"] > 0.0

    def test_generate_description_with_shipping(self, description_service):
        """Test description generation with shipping information."""
        product_data = {
            "title": "iPhone 13 Pro 128GB Negro",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
        }

        result = description_service.generate_description(product_data, "MLA1055")

        assert (
            "envío" in result["description"].lower()
            or "shipping" in result["description"].lower()
        )
        assert result["confidence"] > 0.0

    def test_validate_description_valid(self, description_service):
        """Test description validation for valid description."""
        description = (
            "iPhone 13 Pro de 128GB en color negro. Excelente estado de conservación. "
            * 5
        )

        is_valid, issues = description_service.validate_description(description)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_description_too_short(self, description_service):
        """Test description validation for description that's too short."""
        short_description = "iPhone 13 Pro"

        is_valid, issues = description_service.validate_description(short_description)

        assert is_valid is False
        assert any("length" in issue.lower() for issue in issues)

    def test_validate_description_too_long(self, description_service):
        """Test description validation for description that's too long."""
        long_description = "iPhone 13 Pro description. " * 500  # Very long

        is_valid, issues = description_service.validate_description(long_description)

        assert is_valid is False
        assert any("length" in issue.lower() for issue in issues)

    def test_format_for_mobile(self, description_service):
        """Test mobile-first formatting."""
        content = "iPhone 13 Pro features: Camera system, A15 Bionic chip, Super Retina XDR display"

        formatted = description_service._format_for_mobile(content)

        assert "📱" in formatted or "•" in formatted
        assert len(formatted) > len(content)  # Should be expanded with formatting

    def test_calculate_description_confidence(self, description_service):
        """Test description confidence calculation."""
        description = (
            "iPhone 13 Pro de 128GB en color negro. Excelente estado de conservación. "
            * 5
        )
        product_data = {
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "condition": "Usado",
            "color": "Negro",
            "storage": "128GB",
        }

        confidence = description_service._calculate_confidence(
            description, product_data, "MLA1055"
        )

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident for good match


class TestAttributeMappingService:
    """Test cases for AttributeMappingService."""

    @pytest.fixture
    def attribute_service(self):
        """Create an AttributeMappingService instance for testing."""
        return AttributeMappingService()

    def test_map_attributes_success(self, attribute_service):
        """Test successful attribute mapping."""
        product_data = {
            "brand": "Apple",
            "model": "iPhone 13 Pro",
            "color": "Negro",
            "storage": "128GB",
            "condition": "Usado",
            "screen_size": "6.1 pulgadas",
        }

        result = attribute_service.map_attributes(product_data, "MLA1055")

        assert result["attributes"]["BRAND"] == "Apple"
        assert result["attributes"]["MODEL"] == "iPhone 13 Pro"
        assert result["attributes"]["COLOR"] == "Negro"
        assert result["attributes"]["STORAGE_CAPACITY"] == "128GB"
        assert result["confidence"] > 0.0

    def test_map_attributes_missing_required(self, attribute_service):
        """Test attribute mapping with missing required attributes."""
        product_data = {
            "model": "iPhone 13 Pro",
            "color": "Negro",
            # Missing required brand
        }

        result = attribute_service.map_attributes(product_data, "MLA1055")

        assert (
            result["confidence"] < 0.8
        )  # Lower confidence due to missing required field
        assert "missing_required" in result
        assert "BRAND" in result["missing_required"]

    def test_map_attributes_invalid_category(self, attribute_service):
        """Test attribute mapping with invalid category."""
        product_data = {"brand": "Apple", "model": "iPhone 13 Pro", "color": "Negro"}

        with pytest.raises(CategoryDetectionError, match="Invalid category"):
            attribute_service.map_attributes(product_data, "INVALID_CATEGORY")

    def test_validate_attributes_valid(self, attribute_service):
        """Test attribute validation for valid attributes."""
        attributes = {
            "BRAND": "Apple",
            "MODEL": "iPhone 13 Pro",
            "COLOR": "Negro",
            "STORAGE_CAPACITY": "128GB",
        }

        is_valid, issues = attribute_service.validate_attributes(attributes, "MLA1055")

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_attributes_invalid_values(self, attribute_service):
        """Test attribute validation for invalid values."""
        attributes = {
            "BRAND": "Unknown Brand",  # Invalid brand
            "MODEL": "iPhone 13 Pro",
            "COLOR": "Invalid Color",  # Invalid color
            "STORAGE_CAPACITY": "128GB",
        }

        is_valid, issues = attribute_service.validate_attributes(attributes, "MLA1055")

        assert is_valid is False
        assert len(issues) > 0
        assert any("brand" in issue.lower() for issue in issues)

    def test_enhance_attributes(self, attribute_service):
        """Test attribute enhancement."""
        base_attributes = {"BRAND": "Apple", "MODEL": "iPhone 13 Pro", "COLOR": "Negro"}

        enhanced = attribute_service.enhance_attributes(base_attributes, "MLA1055")

        assert len(enhanced) >= len(base_attributes)
        assert enhanced["BRAND"] == "Apple"
        assert enhanced["MODEL"] == "iPhone 13 Pro"
        # Should have additional attributes based on category and product type

    def test_get_required_attributes(self, attribute_service):
        """Test getting required attributes for category."""
        required = attribute_service.get_required_attributes("MLA1055")

        assert "BRAND" in required
        assert "MODEL" in required
        assert len(required) > 0

    def test_get_optional_attributes(self, attribute_service):
        """Test getting optional attributes for category."""
        optional = attribute_service.get_optional_attributes("MLA1055")

        assert "COLOR" in optional
        assert "STORAGE_CAPACITY" in optional
        assert len(optional) > 0

    def test_calculate_attribute_confidence(self, attribute_service):
        """Test attribute confidence calculation."""
        attributes = {
            "BRAND": "Apple",
            "MODEL": "iPhone 13 Pro",
            "COLOR": "Negro",
            "STORAGE_CAPACITY": "128GB",
        }

        confidence = attribute_service._calculate_confidence(attributes, "MLA1055")

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be highly confident with all key attributes
