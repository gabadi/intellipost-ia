"""Backend test configuration that imports from main conftest."""

import sys
from pathlib import Path

# Add the main tests directory to Python path
main_tests_dir = Path(__file__).parent.parent / "tests"
sys.path.insert(0, str(main_tests_dir))

# Import all fixtures from main conftest
# This allows backend tests to access the centralized fixtures
try:
    from conftest import (
        event_loop,
        postgres_container,
        database_url,
        test_engine,
        async_session,
        test_settings,
        unit_test_settings,
        sample_image_bytes,
        sample_upload_files,
        product_factory,
        image_data_factory,
    )
    
    # Re-export all fixtures so they're available to backend tests
    __all__ = [
        "event_loop",
        "postgres_container", 
        "database_url",
        "test_engine",
        "async_session",
        "test_settings",
        "unit_test_settings",
        "sample_image_bytes",
        "sample_upload_files", 
        "product_factory",
        "image_data_factory",
    ]
    
except ImportError as e:
    # Fallback: define minimal fixtures locally if import fails
    import asyncio
    import pytest
    
    @pytest.fixture(scope="session")
    def event_loop():
        """Fallback event loop fixture."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
        
    @pytest.fixture
    def sample_image_bytes():
        """Fallback sample image bytes for testing."""
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