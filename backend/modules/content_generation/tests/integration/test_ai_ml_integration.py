"""
Integration tests for AI and ML services.

This module tests the integration with external AI and ML APIs
including Google Gemini and MercadoLibre category detection.
"""

import os
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from modules.content_generation.application.use_cases.generate_content import (
    GenerateContentUseCase,
)
from modules.content_generation.domain.entities.ai_generation import (
    AIGeneration,
    GenerationStatus,
)
from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    AIServiceError,
    CategoryDetectionError,
    QualityThresholdError,
)
from modules.content_generation.domain.ports.ai_service_protocols import ImageData
from modules.content_generation.infrastructure.services.gemini_ai_service import (
    GeminiAIService,
)
from modules.content_generation.infrastructure.services.ml_category_service import (
    MLCategoryService,
)


@pytest.mark.integration
class TestGeminiAIIntegration:
    """Integration tests for Gemini AI service."""

    @pytest.fixture
    def gemini_service(self):
        """Create GeminiAIService with test configuration."""
        return GeminiAIService(
            api_key=os.getenv("GEMINI_API_KEY", "test_key"),
            model_name="gemini-2.5-flash",
            max_retries=2,
            timeout_seconds=10,
        )

    @pytest.fixture
    def sample_images(self):
        """Sample image data for testing."""
        from modules.content_generation.tests.conftest import TestImageData

        return [
            TestImageData(
                s3_key="test/iphone13pro.jpg",
                s3_url="https://example.com/iphone13pro.jpg",
                file_format="jpeg",
                resolution_width=800,
                resolution_height=600,
            ),
            TestImageData(
                s3_key="test/iphone13pro_back.jpg",
                s3_url="https://example.com/iphone13pro_back.jpg",
                file_format="jpeg",
                resolution_width=800,
                resolution_height=600,
            ),
        ]

    @pytest.mark.asyncio
    async def test_gemini_api_integration_success(self, gemini_service, sample_images):
        """Test successful integration with Gemini API."""
        # Mock the actual API response
        mock_response = Mock()
        mock_response.text = """{
            "title": "iPhone 13 Pro 128GB Negro Usado Excelente Estado",
            "description": "iPhone 13 Pro de 128GB en color negro. Excelente estado de conservación con mínimas marcas de uso. Incluye caja original y cargador. Batería en perfectas condiciones. Pantalla sin rayones. Ideal para quienes buscan tecnología Apple de calidad a precio accesible.",
            "category": "MLA1055",
            "price": 450000,
            "attributes": {
                "BRAND": "Apple",
                "MODEL": "iPhone 13 Pro",
                "COLOR": "Negro",
                "STORAGE_CAPACITY": "128GB",
                "CONDITION": "Usado",
                "SCREEN_SIZE": "6.1 pulgadas",
                "OPERATING_SYSTEM": "iOS"
            },
            "confidence": {
                "overall": 0.89,
                "breakdown": {
                    "title": 0.95,
                    "description": 0.87,
                    "category": 0.92,
                    "price": 0.82,
                    "attributes": 0.91
                }
            }
        }"""

        with patch.object(gemini_service, "_client") as mock_client:
            mock_client.generate_content.return_value = mock_response

            result = await gemini_service.generate_listing(
                images=sample_images,
                prompt="Smartphone Apple iPhone 13 Pro usado en excelente estado",
                category_hint="celulares",
            )

            # Verify result structure
            assert isinstance(result, GeneratedContent)
            assert result.title == "iPhone 13 Pro 128GB Negro Usado Excelente Estado"
            assert result.ml_category_id == "MLA1055"
            assert result.ml_price == Decimal("450000")
            assert result.confidence_overall == 0.89
            assert result.ai_provider == "gemini"
            assert result.ai_model_version == "2.5-flash"

            # Verify attributes
            assert result.ml_attributes["BRAND"] == "Apple"
            assert result.ml_attributes["MODEL"] == "iPhone 13 Pro"
            assert result.ml_attributes["COLOR"] == "Negro"
            assert result.ml_attributes["STORAGE_CAPACITY"] == "128GB"

            # Verify description quality
            assert len(result.description) > 100
            assert "iPhone" in result.description
            assert "128GB" in result.description
            assert "negro" in result.description.lower()

    @pytest.mark.asyncio
    async def test_gemini_api_rate_limiting(self, gemini_service, sample_images):
        """Test rate limiting behavior."""
        # Mock rate limit error followed by success
        mock_response = Mock()
        mock_response.text = """{
            "title": "iPhone 13 Pro 128GB",
            "description": "iPhone description",
            "category": "MLA1055",
            "price": 450000,
            "attributes": {},
            "confidence": {"overall": 0.85, "breakdown": {}}
        }"""

        with patch.object(gemini_service, "_client") as mock_client:
            # First call rate limited, second succeeds
            mock_client.generate_content.side_effect = [
                Exception("Rate limit exceeded"),
                mock_response,
            ]

            result = await gemini_service.generate_listing(
                images=sample_images, prompt="Generate content for iPhone"
            )

            assert isinstance(result, GeneratedContent)
            assert mock_client.generate_content.call_count == 2

    @pytest.mark.asyncio
    async def test_gemini_api_timeout_handling(self, gemini_service, sample_images):
        """Test timeout handling."""
        with patch.object(gemini_service, "_client") as mock_client:
            mock_client.generate_content.side_effect = TimeoutError("Request timeout")

            with pytest.raises(AIServiceError, match="Request timeout"):
                await gemini_service.generate_listing(
                    images=sample_images, prompt="Generate content for iPhone"
                )

    @pytest.mark.asyncio
    async def test_gemini_api_multimodal_processing(
        self, gemini_service, sample_images
    ):
        """Test multimodal processing with multiple images."""
        mock_response = Mock()
        mock_response.text = """{
            "title": "iPhone 13 Pro 128GB Negro Con Accesorios",
            "description": "iPhone 13 Pro con múltiples accesorios visibles en las imágenes. Estado impecable.",
            "category": "MLA1055",
            "price": 480000,
            "attributes": {"BRAND": "Apple", "INCLUDES_ACCESSORIES": "Si"},
            "confidence": {"overall": 0.92, "breakdown": {"title": 0.95, "description": 0.90}}
        }"""

        with patch.object(gemini_service, "_client") as mock_client:
            mock_client.generate_content.return_value = mock_response

            result = await gemini_service.generate_listing(
                images=sample_images,  # Multiple images
                prompt="Analizar iPhone con accesorios",
            )

            assert isinstance(result, GeneratedContent)
            assert "accesorios" in result.description.lower()
            assert result.ml_attributes.get("INCLUDES_ACCESSORIES") == "Si"
            assert result.confidence_overall == 0.92

    @pytest.mark.asyncio
    async def test_gemini_api_error_recovery(self, gemini_service, sample_images):
        """Test error recovery and retry logic."""
        mock_response = Mock()
        mock_response.text = """{
            "title": "iPhone 13 Pro 128GB",
            "description": "iPhone recovery test",
            "category": "MLA1055",
            "price": 450000,
            "attributes": {},
            "confidence": {"overall": 0.85, "breakdown": {}}
        }"""

        with patch.object(gemini_service, "_client") as mock_client:
            # Multiple failures followed by success
            mock_client.generate_content.side_effect = [
                Exception("Network error"),
                Exception("Server error"),
                mock_response,
            ]

            result = await gemini_service.generate_listing(
                images=sample_images, prompt="Generate content for iPhone"
            )

            assert isinstance(result, GeneratedContent)
            assert mock_client.generate_content.call_count == 3


@pytest.mark.integration
class TestMLCategoryIntegration:
    """Integration tests for MercadoLibre category service."""

    @pytest.fixture
    def ml_category_service(self):
        """Create MLCategoryService with test configuration."""
        return MLCategoryService(
            api_base_url="https://api.mercadolibre.com",
            cache_ttl=60,  # Short TTL for testing
            max_retries=2,
            timeout=5.0,
        )

    @pytest.mark.asyncio
    async def test_ml_category_api_integration_success(self, ml_category_service):
        """Test successful integration with MercadoLibre category API."""
        # Mock the ML API response
        mock_response = {
            "id": "MLA1055",
            "name": "Celulares y Smartphones",
            "confidence": 0.91,
            "path_from_root": [
                {"id": "MLA1051", "name": "Celulares y Teléfonos"},
                {"id": "MLA1055", "name": "Celulares y Smartphones"},
            ],
            "attributes": [
                {"id": "BRAND", "name": "Marca", "required": True},
                {"id": "MODEL", "name": "Modelo", "required": True},
                {"id": "COLOR", "name": "Color", "required": False},
            ],
        }

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )
            mock_get.return_value.__aenter__.return_value.status = 200

            result = await ml_category_service.predict_category(
                {
                    "title": "iPhone 13 Pro 128GB Negro Usado",
                    "description": "iPhone en excelente estado",
                    "brand": "Apple",
                    "model": "iPhone 13 Pro",
                    "color": "Negro",
                    "condition": "Usado",
                }
            )

            # Verify result structure
            assert result["category_id"] == "MLA1055"
            assert result["category_name"] == "Celulares y Smartphones"
            assert result["confidence"] == 0.91
            assert result["path_from_root"] == mock_response["path_from_root"]
            assert "attributes" in result
            assert result["low_confidence"] is False

    @pytest.mark.asyncio
    async def test_ml_category_api_with_category_hint(self, ml_category_service):
        """Test category prediction with category hint."""
        mock_response = {
            "id": "MLA1055",
            "name": "Celulares y Smartphones",
            "confidence": 0.95,  # Higher confidence with hint
            "path_from_root": [],
        }

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )
            mock_get.return_value.__aenter__.return_value.status = 200

            result = await ml_category_service.predict_category(
                product_features={"title": "iPhone 13 Pro", "brand": "Apple"},
                category_hint="celulares",
            )

            assert result["category_id"] == "MLA1055"
            assert result["confidence"] == 0.95
            assert result["low_confidence"] is False

    @pytest.mark.asyncio
    async def test_ml_category_api_low_confidence_handling(self, ml_category_service):
        """Test handling of low confidence predictions."""
        mock_response = {
            "id": "MLA1144",  # Generic category
            "name": "Otros",
            "confidence": 0.35,  # Low confidence
            "path_from_root": [],
        }

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )
            mock_get.return_value.__aenter__.return_value.status = 200

            result = await ml_category_service.predict_category(
                {
                    "title": "Generic product without clear category",
                    "description": "Unclear product description",
                }
            )

            assert result["category_id"] == "MLA1144"
            assert result["confidence"] == 0.35
            assert result["low_confidence"] is True

    @pytest.mark.asyncio
    async def test_ml_category_api_error_handling(self, ml_category_service):
        """Test error handling for ML API failures."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 500
            mock_get.return_value.__aenter__.return_value.text.return_value = (
                "Internal server error"
            )

            with pytest.raises(CategoryDetectionError, match="MercadoLibre API error"):
                await ml_category_service.predict_category({"title": "iPhone 13 Pro"})

    @pytest.mark.asyncio
    async def test_ml_category_api_caching(self, ml_category_service):
        """Test caching behavior."""
        features = {
            "title": "iPhone 13 Pro 128GB",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
        }

        mock_response = {
            "id": "MLA1055",
            "name": "Celulares y Smartphones",
            "confidence": 0.88,
            "path_from_root": [],
        }

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )
            mock_get.return_value.__aenter__.return_value.status = 200

            # First call
            result1 = await ml_category_service.predict_category(features)

            # Second call should use cache
            result2 = await ml_category_service.predict_category(features)

            assert result1 == result2
            assert mock_get.call_count == 1  # Only called once due to caching

    @pytest.mark.asyncio
    async def test_ml_category_api_timeout(self, ml_category_service):
        """Test timeout handling."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.side_effect = TimeoutError("Request timeout")

            with pytest.raises(CategoryDetectionError, match="Request timeout"):
                await ml_category_service.predict_category({"title": "iPhone 13 Pro"})


@pytest.mark.integration
class TestCompleteWorkflowIntegration:
    """Integration tests for complete content generation workflow."""

    @pytest.fixture
    def use_case(self):
        """Create GenerateContentUseCase with mocked dependencies."""
        # This would normally be dependency-injected
        # Import migration service
        from modules.content_generation.domain.services.value_object_migration_service import (
            ValueObjectMigrationService,
        )

        migration_service = ValueObjectMigrationService()

        return GenerateContentUseCase(
            ai_service=Mock(),
            content_repository=Mock(),
            title_service=Mock(),
            description_service=Mock(),
            validation_service=Mock(),
            attribute_service=Mock(),
            category_service=Mock(),
            migration_service=migration_service,
        )

    @pytest.fixture
    def sample_images(self):
        """Sample image data for testing."""
        return [
            ImageData(
                s3_key="test/product1.jpg",
                s3_url="https://example.com/product1.jpg",
                file_format="jpeg",
                resolution_width=800,
                resolution_height=600,
            )
        ]

    @pytest.mark.asyncio
    async def test_complete_workflow_success(self, use_case, sample_images):
        """Test complete content generation workflow."""
        product_id = uuid4()

        # Mock AI service response
        mock_generated_content = GeneratedContent(
            id=uuid4(),
            product_id=product_id,
            title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
            description="iPhone 13 Pro de 128GB en excelente estado...",
            ml_category_id="MLA1055",
            ml_category_name="Celulares y Smartphones",
            ml_title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
            ml_price=Decimal("450000"),
            ml_currency_id="ARS",
            ml_available_quantity=1,
            ml_buying_mode="buy_it_now",
            ml_condition="used",
            ml_listing_type_id="gold_special",
            ml_attributes={
                "BRAND": "Apple",
                "MODEL": "iPhone 13 Pro",
                "COLOR": "Negro",
                "STORAGE_CAPACITY": "128GB",
            },
            ml_sale_terms={},
            ml_shipping={},
            confidence_overall=0.89,
            confidence_breakdown={
                "title": 0.95,
                "description": 0.87,
                "category": 0.92,
                "price": 0.82,
                "attributes": 0.91,
            },
            ai_provider="gemini",
            ai_model_version="2.5-flash",
            generation_time_ms=2340,
            version=1,
            generated_at=datetime.now(UTC),
        )

        # Mock category service response
        mock_category = {
            "category_id": "MLA1055",
            "category_name": "Celulares y Smartphones",
            "confidence": 0.92,
            "low_confidence": False,
        }

        # Configure mocks
        use_case.ai_service.generate_listing.return_value = mock_generated_content
        use_case.category_service.predict_category.return_value = mock_category
        use_case.title_service.generate_title.return_value = {
            "title": "iPhone 13 Pro 128GB Negro Usado Excelente Estado",
            "confidence": 0.95,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "iPhone 13 Pro de 128GB en excelente estado...",
            "confidence": 0.87,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {
                "BRAND": "Apple",
                "MODEL": "iPhone 13 Pro",
                "COLOR": "Negro",
                "STORAGE_CAPACITY": "128GB",
            },
            "confidence": 0.91,
        }

        # Mock repositories
        use_case.generation_repository.save.return_value = None
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        # Execute workflow
        result = await use_case.execute(
            product_id=product_id,
            images=sample_images,
            prompt="Smartphone Apple iPhone 13 Pro usado",
            category_hint="celulares",
            price_range={"min": 400000, "max": 500000},
            target_audience="usuarios de smartphones premium",
            regenerate=False,
        )

        # Verify result
        assert isinstance(result, AIGeneration)
        assert result.product_id == product_id
        assert result.status == GenerationStatus.COMPLETED
        assert result.progress_percentage == 100.0

        # Verify service calls
        use_case.ai_service.generate_listing.assert_called_once()
        use_case.category_service.predict_category.assert_called_once()
        use_case.title_service.generate_title.assert_called_once()
        use_case.description_service.generate_description.assert_called_once()
        use_case.attribute_service.map_attributes.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_with_ai_service_failure(self, use_case, sample_images):
        """Test workflow handling AI service failure."""
        product_id = uuid4()

        # Configure AI service to fail
        use_case.ai_service.generate_listing.side_effect = AIServiceError(
            "AI service unavailable"
        )
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        # Execute workflow
        result = await use_case.execute(
            product_id=product_id,
            images=sample_images,
            prompt="Test product",
            regenerate=False,
        )

        # Verify failure handling
        assert isinstance(result, AIGeneration)
        assert result.status == GenerationStatus.FAILED
        assert result.error_message == "AI service unavailable"
        assert result.error_code == "AI_SERVICE_ERROR"

    @pytest.mark.asyncio
    async def test_workflow_with_category_detection_failure(
        self, use_case, sample_images
    ):
        """Test workflow handling category detection failure."""
        product_id = uuid4()

        # Configure category service to fail
        use_case.category_service.predict_category.side_effect = CategoryDetectionError(
            "Category detection failed"
        )
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        # Execute workflow
        result = await use_case.execute(
            product_id=product_id,
            images=sample_images,
            prompt="Test product",
            regenerate=False,
        )

        # Verify failure handling
        assert isinstance(result, AIGeneration)
        assert result.status == GenerationStatus.FAILED
        assert result.error_message == "Category detection failed"
        assert result.error_code == "CATEGORY_DETECTION_ERROR"

    @pytest.mark.asyncio
    async def test_workflow_with_quality_threshold_failure(
        self, use_case, sample_images
    ):
        """Test workflow handling quality threshold failure."""
        product_id = uuid4()

        # Configure AI service to return low quality content
        use_case.ai_service.generate_listing.side_effect = QualityThresholdError(
            "Content quality below threshold"
        )
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        # Execute workflow
        result = await use_case.execute(
            product_id=product_id,
            images=sample_images,
            prompt="Test product",
            regenerate=False,
        )

        # Verify failure handling
        assert isinstance(result, AIGeneration)
        assert result.status == GenerationStatus.FAILED
        assert result.error_message == "Content quality below threshold"
        assert result.error_code == "QUALITY_THRESHOLD_ERROR"

    @pytest.mark.asyncio
    async def test_workflow_regeneration(self, use_case, sample_images):
        """Test workflow with regeneration flag."""
        product_id = uuid4()

        # Mock existing generation
        existing_generation = AIGeneration(
            id=uuid4(),
            product_id=product_id,
            status=GenerationStatus.COMPLETED,
            current_step=None,
            progress_percentage=100.0,
            estimated_completion_seconds=0,
            error_message=None,
            error_code=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

        use_case.generation_repository.find_by_product_id.return_value = (
            existing_generation
        )
        use_case.generation_repository.save.return_value = None

        # Execute workflow with regeneration
        result = await use_case.execute(
            product_id=product_id,
            images=sample_images,
            prompt="Test product",
            regenerate=True,
        )

        # Verify new generation was created
        assert isinstance(result, AIGeneration)
        assert result.product_id == product_id
        assert result.id != existing_generation.id  # New generation ID
