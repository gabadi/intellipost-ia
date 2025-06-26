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

from infrastructure.config.settings import Settings


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
    """Create an async database engine for testing."""
    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_size=5,
        max_overflow=10,
    )
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


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.

    This is needed for session-scoped async fixtures to work properly.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
