"""Backend test configuration and custom pytest hooks."""

import pytest


def pytest_collection_modifyitems(items):
    """
    Ensure all tests have required markers.

    This hook runs after test collection and validates that every test
    has either a 'unit' or 'integration' marker. This enforces our
    bulletproof marker system where no test can run without explicit
    classification.
    """
    required_markers = {"unit", "integration", "performance", "e2e"}

    for item in items:
        # Get all markers for this test item
        test_markers = {mark.name for mark in item.iter_markers()}

        # Check if any required marker is present
        if not test_markers.intersection(required_markers):
            # Collect test file and function information
            test_path = item.nodeid

            # Create a helpful error message and exit pytest
            error_msg = (
                f"❌ MARKER VALIDATION FAILED\n"
                f"Test '{test_path}' must have one of these markers: {', '.join(sorted(required_markers))}\n"
                f"💡 Solution: Add 'pytestmark = pytest.mark.unit' for unit tests or "
                f"'pytestmark = pytest.mark.integration' for integration tests to the test file."
            )
            pytest.exit(error_msg, returncode=1)
