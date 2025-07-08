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
        user="test_user",
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
