"""Test configuration for unit tests that don't require database containers."""

import os
import sys
from pathlib import Path

import pytest

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from infrastructure.config.settings import Settings


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """
    Create test settings for unit tests.

    This provides a lightweight settings instance for unit tests
    that don't require database connections.
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
