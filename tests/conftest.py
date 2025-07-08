"""Test configuration and fixtures."""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from infrastructure.config.settings import Settings  # noqa: E402


def check_database_connection() -> bool:
    """
    Check if database is available for testing.

    Returns True if database is available, False otherwise.
    """
    try:
        import socket
        import asyncpg

        # Extract connection details from test settings
        settings = Settings()
        db_url = settings.get_database_url()

        # Parse database URL to extract host and port
        if "localhost:5432" in db_url:
            host, port = "localhost", 5432
        elif "127.0.0.1:5432" in db_url:
            host, port = "127.0.0.1", 5432
        elif "localhost:5443" in db_url:
            host, port = "localhost", 5443
        elif "127.0.0.1:5443" in db_url:
            host, port = "127.0.0.1", 5443
        else:
            # Try to parse the URL more robustly
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432

        # Try to connect to the database port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        return result == 0

    except Exception:
        return False


# Skip integration tests if database is not available
def pytest_configure(config):
    """Configure pytest to skip tests based on database availability."""
    if not check_database_connection():
        # Add skip marker for integration tests
        config.addinivalue_line(
            "markers",
            "integration: marks tests as integration tests (skipped when database unavailable)"
        )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip integration tests when database is unavailable."""
    if not check_database_connection():
        skip_integration = pytest.mark.skip(
            reason="Database not available - skipping integration tests"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
            # Also skip tests that require database connection
            if "requires_db" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Start a PostgreSQL test container for the entire test session.

    This fixture provides an isolated PostgreSQL instance for testing,
    following the tech stack requirement to use real databases for tests.
    """
    with PostgresContainer(
        "postgres:15-alpine",
        username="test_user",
        password="test_password",
        dbname="test_db",
    ) as postgres:
        # Set environment variable for tests
        os.environ["INTELLIPOST_ENVIRONMENT"] = "testing"
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container: PostgresContainer) -> str:
    """Get the database URL for the test container."""
    # Use asyncpg driver for async SQLAlchemy
    return postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine(database_url: str):
    """Create an async database engine for testing with Alembic migrations."""
    from alembic import command
    from alembic.config import Config
    
    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_size=5,
        max_overflow=10,
    )
    
    # Run Alembic migrations to create tables
    alembic_cfg = Config(str(Path(__file__).parent.parent / "backend" / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url.replace("+asyncpg", ""))
    
    # Upgrade to head (latest migration)
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async database session for each test.

    This fixture provides a clean database session for each test,
    with automatic rollback to ensure test isolation.
    """
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Transaction will be rolled back automatically


@pytest.fixture(scope="function")
def test_settings(database_url: str) -> Settings:
    """
    Create test settings with the test database URL.

    This ensures that tests use the test container database
    instead of the default development database.
    """
    # Override environment variables for testing
    os.environ.update({
        "INTELLIPOST_ENVIRONMENT": "testing",
        "INTELLIPOST_DATABASE_URL": database_url,
        "INTELLIPOST_DATABASE_TEST_URL": database_url,
        "INTELLIPOST_DEBUG": "false",
        "INTELLIPOST_SECRET_KEY": "test-secret-key-for-testing-only",
        "INTELLIPOST_S3_ENDPOINT_URL": "http://localhost:9001",
        "INTELLIPOST_S3_ACCESS_KEY": "test_access_key",
        "INTELLIPOST_S3_SECRET_KEY": "test_secret_key",
        "INTELLIPOST_S3_BUCKET_NAME": "test-bucket",
    })

    return Settings()


@pytest.fixture(scope="function")
def unit_test_settings() -> Settings:
    """
    Create lightweight test settings for unit tests.

    This provides a lightweight settings instance for unit tests
    that don't require database connections or containers.
    """
    # Set minimal environment variables for testing
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ.update({
        "INTELLIPOST_ENVIRONMENT": "testing",
        "INTELLIPOST_DEBUG": "false",
        "INTELLIPOST_LOG_LEVEL": "INFO",
        "INTELLIPOST_SECRET_KEY": "test-secret-key-for-testing-only",
    })

    try:
        settings = Settings()
        yield settings
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.

    This is needed for session-scoped async fixtures to work properly.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Product Management Test Fixtures
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
def product_factory():
    """Factory for creating test Product entities."""
    from typing import Any
    from uuid import uuid4

    def create_product(**kwargs: Any):
        # Import locally to avoid circular imports
        from modules.product_management.domain.entities.product import Product
        from modules.product_management.domain.entities.product_status import ProductStatus
        
        return Product(
            id=kwargs.get("id", uuid4()),
            user_id=kwargs.get("user_id", uuid4()),
            status=kwargs.get("status", ProductStatus.UPLOADING),
            prompt_text=kwargs.get("prompt_text", "Test product description"),
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["id", "user_id", "status", "prompt_text"]
            },
        )

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
