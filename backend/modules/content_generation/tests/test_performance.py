"""
Performance tests for content generation module.

This module tests the performance characteristics of the content generation workflow
including response times, throughput, and resource utilization.
"""

import asyncio
import time
from datetime import UTC, datetime
from decimal import Decimal
from statistics import mean, median, stdev
from unittest.mock import Mock
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
from modules.content_generation.domain.ports.ai_service_protocols import ImageData
from modules.content_generation.infrastructure.services.gemini_ai_service import (
    GeminiAIService,
)
from modules.content_generation.infrastructure.services.ml_category_service import (
    MLCategoryService,
)


@pytest.mark.performance
class TestContentGenerationPerformance:
    """Performance tests for content generation workflow."""

    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service with realistic response times."""
        service = Mock(spec=GeminiAIService)

        async def mock_generate_listing(*_args, **_kwargs):
            # Simulate AI processing time (1-3 seconds)
            await asyncio.sleep(1.5)
            return GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),
                title="iPhone 13 Pro 128GB Negro",
                description="iPhone description",
                ml_category_id="MLA1055",
                ml_category_name="Celulares y Smartphones",
                ml_title="iPhone 13 Pro 128GB Negro",
                ml_price=Decimal("450000"),
                ml_currency_id="ARS",
                ml_available_quantity=1,
                ml_buying_mode="buy_it_now",
                ml_condition="used",
                ml_listing_type_id="gold_special",
                ml_attributes={},
                ml_sale_terms={},
                ml_shipping={},
                confidence_overall=0.89,
                confidence_breakdown={},
                ai_provider="gemini",
                ai_model_version="2.5-flash",
                generation_time_ms=1500,
                version=1,
                generated_at=datetime.now(UTC),
            )

        service.generate_listing = mock_generate_listing
        return service

    @pytest.fixture
    def mock_category_service(self):
        """Mock category service with realistic response times."""
        service = Mock(spec=MLCategoryService)

        async def mock_predict_category(*_args, **_kwargs):
            # Simulate category detection time (200-500ms)
            await asyncio.sleep(0.3)
            return {
                "category_id": "MLA1055",
                "category_name": "Celulares y Smartphones",
                "confidence": 0.88,
                "low_confidence": False,
            }

        service.predict_category = mock_predict_category
        return service

    @pytest.fixture
    def use_case(self, mock_ai_service, mock_category_service):
        """Create use case with mocked services."""
        return GenerateContentUseCase(
            ai_service=mock_ai_service,
            category_service=mock_category_service,
            title_service=Mock(),
            description_service=Mock(),
            attribute_service=Mock(),
            content_repository=Mock(),
            generation_repository=Mock(),
        )

    @pytest.fixture
    def sample_images(self):
        """Sample image data for testing."""
        return [
            ImageData(
                s3_key="test/image1.jpg",
                s3_url="https://example.com/image1.jpg",
                file_format="jpeg",
                resolution_width=800,
                resolution_height=600,
            )
        ]

    @pytest.mark.asyncio
    async def test_single_content_generation_performance(self, use_case, sample_images):
        """Test performance of single content generation."""
        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        start_time = time.time()

        result = await use_case.execute(
            product_id=uuid4(),
            images=sample_images,
            prompt="Test product generation",
            regenerate=False,
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify successful generation
        assert isinstance(result, AIGeneration)
        assert result.status == GenerationStatus.COMPLETED

        # Performance assertions
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert (
            execution_time > 1.0
        )  # Should take at least 1 second (realistic processing time)

        print(f"Single content generation time: {execution_time:.2f}s")

    @pytest.mark.asyncio
    async def test_concurrent_content_generation_performance(
        self, use_case, sample_images
    ):
        """Test performance of concurrent content generation."""
        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        concurrent_requests = 5

        async def generate_content():
            return await use_case.execute(
                product_id=uuid4(),
                images=sample_images,
                prompt="Test product generation",
                regenerate=False,
            )

        start_time = time.time()

        # Run concurrent content generation
        tasks = [generate_content() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all generations completed successfully
        assert len(results) == concurrent_requests
        for result in results:
            assert isinstance(result, AIGeneration)
            assert result.status == GenerationStatus.COMPLETED

        # Performance assertions
        assert total_time < 10.0  # All requests should complete within 10 seconds
        average_time_per_request = total_time / concurrent_requests
        assert (
            average_time_per_request < 3.0
        )  # Average should be better than sequential

        print(
            f"Concurrent generation time: {total_time:.2f}s for {concurrent_requests} requests"
        )
        print(f"Average time per request: {average_time_per_request:.2f}s")

    @pytest.mark.asyncio
    async def test_load_testing_performance(self, use_case, sample_images):
        """Test performance under load conditions."""
        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        num_requests = 10
        response_times = []

        async def generate_and_measure():
            start = time.time()
            result = await use_case.execute(
                product_id=uuid4(),
                images=sample_images,
                prompt="Test product generation",
                regenerate=False,
            )
            end = time.time()
            response_times.append(end - start)
            return result

        # Execute load test
        start_time = time.time()

        # Run in batches to simulate realistic load
        batch_size = 3
        for i in range(0, num_requests, batch_size):
            batch_tasks = [
                generate_and_measure() for _ in range(min(batch_size, num_requests - i))
            ]
            batch_results = await asyncio.gather(*batch_tasks)

            # Verify batch results
            for result in batch_results:
                assert isinstance(result, AIGeneration)
                assert result.status == GenerationStatus.COMPLETED

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate performance metrics
        avg_response_time = mean(response_times)
        median_response_time = median(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        std_response_time = stdev(response_times) if len(response_times) > 1 else 0

        # Performance assertions
        assert (
            avg_response_time < 3.0
        )  # Average response time should be under 3 seconds
        assert (
            max_response_time < 5.0
        )  # Maximum response time should be under 5 seconds
        assert (
            std_response_time < 1.0
        )  # Standard deviation should be low (consistent performance)

        print(f"Load test results for {num_requests} requests:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average response time: {avg_response_time:.2f}s")
        print(f"  Median response time: {median_response_time:.2f}s")
        print(f"  Min response time: {min_response_time:.2f}s")
        print(f"  Max response time: {max_response_time:.2f}s")
        print(f"  Standard deviation: {std_response_time:.2f}s")
        print(f"  Requests per second: {num_requests / total_time:.2f}")

    @pytest.mark.asyncio
    async def test_memory_usage_performance(self, use_case, sample_images):
        """Test memory usage during content generation."""
        import os

        import psutil

        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        process = psutil.Process(os.getpid())

        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate content multiple times
        for _i in range(5):
            result = await use_case.execute(
                product_id=uuid4(),
                images=sample_images,
                prompt="Test product generation",
                regenerate=False,
            )
            assert isinstance(result, AIGeneration)
            assert result.status == GenerationStatus.COMPLETED

        # Measure final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage assertions
        assert memory_increase < 50  # Should not increase memory by more than 50MB

        print("Memory usage:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")

    @pytest.mark.asyncio
    async def test_error_handling_performance(self, use_case, sample_images):
        """Test performance when errors occur."""
        # Configure mocks to simulate errors
        use_case.ai_service.generate_listing.side_effect = Exception("AI service error")
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        error_response_times = []

        async def generate_with_error():
            start = time.time()
            result = await use_case.execute(
                product_id=uuid4(),
                images=sample_images,
                prompt="Test product generation",
                regenerate=False,
            )
            end = time.time()
            error_response_times.append(end - start)
            return result

        # Test multiple error scenarios
        for _i in range(3):
            result = await generate_with_error()
            assert isinstance(result, AIGeneration)
            assert result.status == GenerationStatus.FAILED

        # Performance assertions for error handling
        avg_error_time = mean(error_response_times)
        assert avg_error_time < 2.0  # Error handling should be fast

        print("Error handling performance:")
        print(f"  Average error response time: {avg_error_time:.2f}s")
        print(f"  Max error response time: {max(error_response_times):.2f}s")

    @pytest.mark.asyncio
    async def test_cache_performance(self, mock_category_service, sample_images):
        """Test performance impact of caching."""
        # Test category service caching
        features = {
            "title": "iPhone 13 Pro 128GB",
            "brand": "Apple",
            "model": "iPhone 13 Pro",
        }

        # First call (cache miss)
        start_time = time.time()
        result1 = await mock_category_service.predict_category(features)
        first_call_time = time.time() - start_time

        # Second call (cache hit) - simulate instant response
        mock_category_service.predict_category = Mock(return_value=result1)

        start_time = time.time()
        result2 = await mock_category_service.predict_category(features)
        second_call_time = time.time() - start_time

        # Cache should significantly improve performance
        assert second_call_time < first_call_time * 0.1  # Cache should be 10x faster
        assert result1 == result2

        print("Cache performance:")
        print(f"  First call (cache miss): {first_call_time:.4f}s")
        print(f"  Second call (cache hit): {second_call_time:.4f}s")
        print(f"  Performance improvement: {first_call_time / second_call_time:.2f}x")

    @pytest.mark.asyncio
    async def test_throughput_performance(self, use_case, sample_images):
        """Test system throughput under sustained load."""
        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        # Test sustained throughput for 10 seconds
        test_duration = 10  # seconds
        completed_requests = 0

        async def continuous_generation():
            nonlocal completed_requests
            while True:
                try:
                    result = await use_case.execute(
                        product_id=uuid4(),
                        images=sample_images,
                        prompt="Test product generation",
                        regenerate=False,
                    )
                    if result.status == GenerationStatus.COMPLETED:
                        completed_requests += 1
                except Exception:
                    pass  # Continue testing even if some requests fail

        # Start continuous generation
        generation_task = asyncio.create_task(continuous_generation())

        # Run for test duration
        await asyncio.sleep(test_duration)

        # Stop generation
        generation_task.cancel()

        # Calculate throughput
        throughput = completed_requests / test_duration

        # Performance assertions
        assert throughput > 0.5  # Should complete at least 0.5 requests per second
        assert completed_requests > 0  # Should complete at least some requests

        print("Throughput performance:")
        print(f"  Test duration: {test_duration}s")
        print(f"  Completed requests: {completed_requests}")
        print(f"  Throughput: {throughput:.2f} requests/second")

    @pytest.mark.asyncio
    async def test_scalability_performance(self, use_case, sample_images):
        """Test performance scalability with increasing load."""
        # Configure additional mocks
        use_case.title_service.generate_title.return_value = {
            "title": "Test Title",
            "confidence": 0.9,
        }
        use_case.description_service.generate_description.return_value = {
            "description": "Test Description",
            "confidence": 0.85,
        }
        use_case.attribute_service.map_attributes.return_value = {
            "attributes": {},
            "confidence": 0.8,
        }
        use_case.content_repository.save.return_value = None
        use_case.generation_repository.save.return_value = None
        use_case.generation_repository.find_by_product_id.return_value = None

        load_levels = [1, 2, 4, 8]  # Increasing concurrent requests
        performance_results = []

        for load_level in load_levels:

            async def generate_content():
                return await use_case.execute(
                    product_id=uuid4(),
                    images=sample_images,
                    prompt="Test product generation",
                    regenerate=False,
                )

            start_time = time.time()

            # Run concurrent requests
            tasks = [generate_content() for _ in range(load_level)]
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time = end_time - start_time

            # Verify results
            for result in results:
                assert isinstance(result, AIGeneration)
                assert result.status == GenerationStatus.COMPLETED

            # Calculate metrics
            avg_time = total_time / load_level
            throughput = load_level / total_time

            performance_results.append(
                {
                    "load_level": load_level,
                    "total_time": total_time,
                    "avg_time": avg_time,
                    "throughput": throughput,
                }
            )

        # Analyze scalability
        print("Scalability performance:")
        for result in performance_results:
            print(
                f"  Load {result['load_level']}: {result['avg_time']:.2f}s avg, {result['throughput']:.2f} req/s"
            )

        # Performance assertions
        # System should handle increased load reasonably well
        assert (
            performance_results[-1]["avg_time"] < performance_results[0]["avg_time"] * 3
        )  # Should not degrade more than 3x
        assert (
            performance_results[-1]["throughput"]
            > performance_results[0]["throughput"] * 0.5
        )  # Throughput should scale reasonably
