"""
Pytest configuration and fixtures for content generation tests.

This module provides shared fixtures and configuration for all tests.
"""

import asyncio
import os
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from modules.content_generation.domain.entities.ai_generation import (
    AIGeneration,
    GenerationStatus,
    ProcessingStep,
)
from modules.content_generation.domain.entities.confidence_score import ConfidenceScore
from modules.content_generation.domain.entities.generated_content import (
    GeneratedContent,
)


# Test data class for ImageData protocol
class TestImageData:
    """Test implementation of ImageData protocol."""

    def __init__(
        self,
        s3_key: str,
        s3_url: str,
        file_format: str,
        resolution_width: int,
        resolution_height: int,
    ):
        self.s3_key = s3_key
        self.s3_url = s3_url
        self.file_format = file_format
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height


# Configure pytest markers
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Domain entity fixtures
@pytest.fixture
def sample_generated_content():
    """Create sample generated content for testing."""
    return GeneratedContent(
        id=uuid4(),
        product_id=uuid4(),
        title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
        description="iPhone 13 Pro de 128GB en color negro. Excelente estado de conservación con mínimas marcas de uso. Incluye caja original y cargador. Batería en perfectas condiciones. Pantalla sin rayones. Ideal para quienes buscan tecnología Apple de calidad a precio accesible.",
        ml_category_id="MLA1055",
        ml_category_name="Celulares y Smartphones",
        ml_title="iPhone 13 Pro 128GB Negro Usado Excelente Estado",
        ml_price=Decimal("450000.00"),
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
            "CONDITION": "Usado",
            "SCREEN_SIZE": "6.1 pulgadas",
            "OPERATING_SYSTEM": "iOS",
        },
        ml_sale_terms={
            "id": "WARRANTY_TYPE",
            "value_id": "WARRANTY_TYPE_DEALER",
            "value_name": "Garantía del vendedor",
            "value_struct": None,
        },
        ml_shipping={"mode": "me2", "local_pick_up": True, "free_shipping": False},
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
        updated_at=None,
    )


@pytest.fixture
def sample_ai_generation():
    """Create sample AI generation for testing."""
    return AIGeneration(
        id=uuid4(),
        product_id=uuid4(),
        status=GenerationStatus.PROCESSING,
        current_step=ProcessingStep.TITLE_GENERATION,
        progress_percentage=45.0,
        estimated_completion_seconds=15,
        error_message=None,
        error_code=None,
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture
def sample_confidence_score():
    """Create sample confidence score for testing."""
    return ConfidenceScore(
        overall=0.89,
        breakdown={
            "title": 0.95,
            "description": 0.87,
            "category": 0.92,
            "price": 0.82,
            "attributes": 0.91,
        },
    )


@pytest.fixture
def sample_image_data():
    """Create sample image data for testing."""
    return [
        TestImageData(
            s3_key="products/test/iphone13pro_front.jpg",
            s3_url="https://s3.amazonaws.com/bucket/products/test/iphone13pro_front.jpg",
            file_format="jpeg",
            resolution_width=800,
            resolution_height=600,
        ),
        TestImageData(
            s3_key="products/test/iphone13pro_back.jpg",
            s3_url="https://s3.amazonaws.com/bucket/products/test/iphone13pro_back.jpg",
            file_format="jpeg",
            resolution_width=800,
            resolution_height=600,
        ),
        TestImageData(
            s3_key="products/test/iphone13pro_box.jpg",
            s3_url="https://s3.amazonaws.com/bucket/products/test/iphone13pro_box.jpg",
            file_format="jpeg",
            resolution_width=800,
            resolution_height=600,
        ),
    ]


# Service mocks
@pytest.fixture
def mock_ai_service():
    """Create mock AI service for testing."""
    mock_service = Mock()
    mock_service.generate_listing = AsyncMock()
    mock_service.enhance_content = AsyncMock()
    mock_service.validate_content = AsyncMock()
    return mock_service


@pytest.fixture
def mock_category_service():
    """Create mock category service for testing."""
    mock_service = Mock()
    mock_service.predict_category = AsyncMock()
    mock_service.validate_category = AsyncMock()
    mock_service.get_category_attributes = AsyncMock()
    return mock_service


@pytest.fixture
def mock_title_service():
    """Create mock title service for testing."""
    mock_service = Mock()
    mock_service.generate_title = Mock()
    mock_service.generate_variations = Mock()
    mock_service.validate_title = Mock()
    mock_service.optimize_for_seo = Mock()
    return mock_service


@pytest.fixture
def mock_description_service():
    """Create mock description service for testing."""
    mock_service = Mock()
    mock_service.generate_description = Mock()
    mock_service.validate_description = Mock()
    mock_service.format_for_mobile = Mock()
    mock_service.enhance_description = Mock()
    return mock_service


@pytest.fixture
def mock_attribute_service():
    """Create mock attribute service for testing."""
    mock_service = Mock()
    mock_service.map_attributes = Mock()
    mock_service.validate_attributes = Mock()
    mock_service.enhance_attributes = Mock()
    mock_service.get_required_attributes = Mock()
    mock_service.get_optional_attributes = Mock()
    return mock_service


# Repository mocks
@pytest.fixture
def mock_content_repository():
    """Create mock content repository for testing."""
    mock_repository = Mock()
    mock_repository.save = AsyncMock()
    mock_repository.find_by_id = AsyncMock()
    mock_repository.find_by_product_id = AsyncMock()
    mock_repository.find_latest_by_product_id = AsyncMock()
    mock_repository.find_versions_by_product_id = AsyncMock()
    mock_repository.delete = AsyncMock()
    return mock_repository


@pytest.fixture
def mock_generation_repository():
    """Create mock generation repository for testing."""
    mock_repository = Mock()
    mock_repository.save = AsyncMock()
    mock_repository.find_by_id = AsyncMock()
    mock_repository.find_by_product_id = AsyncMock()
    mock_repository.find_active_by_product_id = AsyncMock()
    mock_repository.update_status = AsyncMock()
    mock_repository.delete = AsyncMock()
    return mock_repository


# Test data fixtures
@pytest.fixture
def sample_product_data():
    """Create sample product data for testing."""
    return {
        "title": "iPhone 13 Pro 128GB Negro Usado Excelente Estado",
        "brand": "Apple",
        "model": "iPhone 13 Pro",
        "color": "Negro",
        "storage": "128GB",
        "condition": "Usado",
        "screen_size": "6.1 pulgadas",
        "operating_system": "iOS",
        "features": [
            "Pantalla Super Retina XDR de 6.1 pulgadas",
            "Chip A15 Bionic",
            "Sistema de cámaras Pro",
            "Batería de larga duración",
            "Resistente al agua IP68",
        ],
        "accessories": [
            "Caja original",
            "Cargador Lightning",
            "Cable USB-C a Lightning",
            "Documentación",
        ],
        "price_range": {"min": 400000, "max": 500000},
        "target_audience": "usuarios de smartphones premium",
        "selling_points": [
            "Excelente estado de conservación",
            "Incluye caja original",
            "Batería en perfectas condiciones",
            "Pantalla sin rayones",
            "Precio competitivo",
        ],
    }


@pytest.fixture
def sample_ml_category_data():
    """Create sample MercadoLibre category data for testing."""
    return {
        "id": "MLA1055",
        "name": "Celulares y Smartphones",
        "confidence": 0.92,
        "path_from_root": [
            {"id": "MLA1051", "name": "Celulares y Teléfonos"},
            {"id": "MLA1055", "name": "Celulares y Smartphones"},
        ],
        "attributes": [
            {"id": "BRAND", "name": "Marca", "required": True},
            {"id": "MODEL", "name": "Modelo", "required": True},
            {"id": "COLOR", "name": "Color", "required": False},
            {
                "id": "STORAGE_CAPACITY",
                "name": "Capacidad de almacenamiento",
                "required": False,
            },
            {"id": "CONDITION", "name": "Condición", "required": True},
            {"id": "SCREEN_SIZE", "name": "Tamaño de pantalla", "required": False},
            {"id": "OPERATING_SYSTEM", "name": "Sistema operativo", "required": False},
        ],
        "low_confidence": False,
    }


@pytest.fixture
def sample_gemini_response():
    """Create sample Gemini API response for testing."""
    return {
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
            "OPERATING_SYSTEM": "iOS",
        },
        "sale_terms": {"WARRANTY_TYPE": "Garantía del vendedor"},
        "shipping": {"mode": "me2", "local_pick_up": True, "free_shipping": False},
        "confidence": {
            "overall": 0.89,
            "breakdown": {
                "title": 0.95,
                "description": 0.87,
                "category": 0.92,
                "price": 0.82,
                "attributes": 0.91,
            },
        },
    }


# Environment fixtures
@pytest.fixture
def test_environment():
    """Set up test environment variables."""
    test_env = {
        "GEMINI_API_KEY": "test_gemini_key",
        "ML_API_BASE_URL": "https://api.mercadolibre.com",
        "CONTENT_GENERATION_CACHE_TTL": "300",
        "CONTENT_GENERATION_MAX_RETRIES": "3",
        "CONTENT_GENERATION_QUALITY_THRESHOLD": "0.7",
        "CONTENT_GENERATION_RATE_LIMIT": "60",
        "CONTENT_GENERATION_TIMEOUT": "30",
    }

    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value

    yield test_env

    # Clean up environment variables
    for key in test_env:
        if key in os.environ:
            del os.environ[key]


# Error simulation fixtures
@pytest.fixture
def ai_service_error():
    """Create AI service error for testing."""
    from modules.content_generation.domain.exceptions import AIServiceError

    return AIServiceError("AI service temporarily unavailable", provider="test")


@pytest.fixture
def category_detection_error():
    """Create category detection error for testing."""
    from modules.content_generation.domain.exceptions import CategoryDetectionError

    return CategoryDetectionError("Category detection failed")


@pytest.fixture
def quality_threshold_error():
    """Create quality threshold error for testing."""
    from modules.content_generation.domain.exceptions import QualityThresholdError

    return QualityThresholdError(
        "Generated content quality below threshold", quality_score=0.5, threshold=0.8
    )


@pytest.fixture
def invalid_content_error():
    """Create invalid content error for testing."""
    from modules.content_generation.domain.exceptions import InvalidContentError

    return InvalidContentError("Invalid content format", content_type="test")


@pytest.fixture
def entity_not_found_error():
    """Create entity not found error for testing."""
    from modules.content_generation.domain.exceptions import EntityNotFoundError

    return EntityNotFoundError("Entity not found", entity_type="test", entity_id="123")


# Test utilities
@pytest.fixture
def assert_performance():
    """Utility fixture for performance assertions."""

    def _assert_performance(
        execution_time: float, expected_max_time: float, operation_name: str
    ) -> None:
        """Assert that execution time is within expected bounds."""
        assert execution_time <= expected_max_time, (
            f"{operation_name} took {execution_time:.2f}s, "
            f"expected <= {expected_max_time:.2f}s"
        )
        assert execution_time >= 0, f"{operation_name} execution time must be positive"

    return _assert_performance


@pytest.fixture
def assert_content_quality():
    """Utility fixture for content quality assertions."""

    def _assert_content_quality(
        generated_content: GeneratedContent, min_confidence: float = 0.7
    ) -> None:
        """Assert that generated content meets quality standards."""
        assert generated_content.confidence_overall >= min_confidence, (
            f"Content confidence {generated_content.confidence_overall} "
            f"below minimum {min_confidence}"
        )
        assert len(generated_content.title) <= 60, "Title exceeds maximum length"
        assert len(generated_content.title) > 0, "Title cannot be empty"
        assert len(generated_content.description) >= 100, "Description too short"
        assert generated_content.ml_price > 0, "Price must be positive"
        assert generated_content.ml_available_quantity > 0, "Quantity must be positive"

    return _assert_content_quality


# Skip markers for different test types
@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API key is not available."""

    def _skip_if_no_api_key(api_key_env_var: str) -> None:
        if not os.getenv(api_key_env_var):
            pytest.skip(f"Skipping test: {api_key_env_var} not set")

    return _skip_if_no_api_key


@pytest.fixture
def skip_if_slow():
    """Skip test if slow tests are disabled."""

    def _skip_if_slow():
        if os.getenv("RUN_SLOW_TESTS", "false").lower() != "true":
            pytest.skip("Skipping slow test: set RUN_SLOW_TESTS=true to run")

    return _skip_if_slow


@pytest.fixture
def skip_if_no_external_deps():
    """Skip test if external dependencies are not available."""

    def _skip_if_no_external_deps():
        if os.getenv("RUN_EXTERNAL_TESTS", "false").lower() != "true":
            pytest.skip("Skipping external test: set RUN_EXTERNAL_TESTS=true to run")

    return _skip_if_no_external_deps
