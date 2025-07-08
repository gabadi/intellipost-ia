"""
Pytest configuration and fixtures for product management tests.

This module provides shared fixtures and configuration for testing.
"""

import asyncio
import contextlib
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from infrastructure.database import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def postgres_container():
    """Start PostgreSQL test container."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        postgres.start()
        yield postgres


@pytest.fixture(scope="session")
async def minio_container():
    """Start MinIO test container."""
    with MinioContainer() as minio:
        minio.start()
        yield minio


@pytest.fixture(scope="session")
async def test_engine(postgres_container):
    """Create test database engine."""
    connection_url = postgres_container.get_connection_url().replace(
        "psycopg2", "asyncpg"
    )

    engine = create_async_engine(
        connection_url,
        echo=False,  # Set to True for SQL debugging
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def async_session(test_engine) -> AsyncGenerator[AsyncSession]:
    """Create async database session for tests."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def clean_database(async_session):
    """Clean database between tests."""
    # Clean up all product-related tables
    await async_session.execute("DELETE FROM product_images")
    await async_session.execute("DELETE FROM products")
    await async_session.commit()


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes for testing."""
    # Create a minimal valid JPEG header
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
        b"\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01"
        b"\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff"
        b"\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"
    )


@pytest.fixture
def sample_upload_files(sample_image_bytes):
    """Create sample UploadFile objects for testing."""
    from io import BytesIO

    from fastapi import UploadFile

    files = []
    for i in range(3):
        file_like = BytesIO(sample_image_bytes)
        upload_file = UploadFile(filename=f"test_image_{i}.jpg", file=file_like)
        files.append(upload_file)

    return files


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    from unittest.mock import Mock

    from infrastructure.config.settings import Settings

    settings = Mock(spec=Settings)
    settings.s3_bucket_name = "test-bucket"
    settings.s3_endpoint_url = "http://localhost:9000"
    settings.s3_access_key = "testkey"
    settings.s3_secret_key = "testsecret"
    settings.s3_region = "us-east-1"
    settings.product_max_image_size_mb = 10
    return settings


@pytest.fixture
def real_minio_settings(minio_container):
    """Create real MinIO settings for integration tests."""
    from unittest.mock import Mock

    from infrastructure.config.settings import Settings

    settings = Mock(spec=Settings)
    settings.s3_bucket_name = "test-bucket"
    settings.s3_endpoint_url = minio_container.get_connection_url()
    settings.s3_access_key = minio_container.access_key
    settings.s3_secret_key = minio_container.secret_key
    settings.s3_region = "us-east-1"
    settings.product_max_image_size_mb = 10
    return settings


# Performance testing fixtures
@pytest.fixture(scope="session")
def performance_test_images():
    """Create multiple test images for performance testing."""
    images = []
    base_content = b"x" * 1024  # 1KB base image

    # Create images of different sizes
    sizes = [1, 5, 10, 25, 50]  # KB

    for size_kb in sizes:
        for i in range(5):  # 5 images per size
            content = base_content * size_kb
            images.append(
                {
                    "filename": f"perf_test_{size_kb}kb_{i}.jpg",
                    "content": content,
                    "size_kb": size_kb,
                }
            )

    return images


# Error simulation fixtures
@pytest.fixture
def s3_error_simulator():
    """Fixture to simulate various S3 errors."""
    from botocore.exceptions import ClientError

    def create_error(error_code, message="Test error"):
        return ClientError(
            error_response={
                "Error": {
                    "Code": error_code,
                    "Message": message,
                }
            },
            operation_name="test_operation",
        )

    return {
        "no_such_bucket": create_error("NoSuchBucket"),
        "access_denied": create_error("AccessDenied"),
        "no_such_key": create_error("NoSuchKey"),
        "invalid_request": create_error("InvalidRequest"),
    }


# Database test data factories
@pytest.fixture
def product_factory():
    """Factory for creating test Product entities."""
    from uuid import uuid4

    from modules.product_management.domain.entities.product import Product
    from modules.product_management.domain.entities.product_status import ProductStatus

    def create_product(**kwargs):
        defaults = {
            "id": uuid4(),
            "user_id": uuid4(),
            "status": ProductStatus.UPLOADING,
            "prompt_text": "Test product description",
        }
        defaults.update(kwargs)
        return Product(**defaults)

    return create_product


@pytest.fixture
def image_data_factory():
    """Factory for creating test image data."""
    from uuid import uuid4

    def create_image_data(**kwargs):
        defaults = {
            "product_id": uuid4(),
            "original_filename": "test.jpg",
            "s3_key": "products/user/product/test.jpg",
            "s3_url": "https://bucket.s3.amazonaws.com/products/user/product/test.jpg",
            "file_size_bytes": 1024,
            "file_format": "jpg",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "is_primary": False,
        }
        defaults.update(kwargs)
        return defaults

    return create_image_data


# Cleanup utilities
@pytest.fixture(autouse=True)
async def cleanup_temp_files():
    """Auto cleanup any temporary files created during tests."""
    import shutil
    import tempfile

    temp_dirs = []

    def create_temp_dir():
        temp_dir = tempfile.mkdtemp(prefix="product_test_")
        temp_dirs.append(temp_dir)
        return temp_dir

    yield create_temp_dir

    # Cleanup
    for temp_dir in temp_dirs:
        with contextlib.suppress(Exception):
            shutil.rmtree(temp_dir)


# Async context managers for testing
@pytest.fixture
def async_context_manager():
    """Helper for testing async context managers."""
    import asyncio
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def test_context(value):
        try:
            yield value
        finally:
            await asyncio.sleep(0)  # Ensure async behavior

    return test_context
