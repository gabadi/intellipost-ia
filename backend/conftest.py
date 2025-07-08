"""
Pytest configuration for enforcing test marks.

This ensures all tests are properly categorized as unit or integration.
"""

import pytest


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """
    Enforce that all tests have either 'unit' or 'integration' marks.

    This hook runs after test collection and validates that every collected
    test has the required marks. If any test is missing marks, pytest will
    fail with a clear error message.
    """
    required_marks = {"unit", "integration"}
    unmarked_tests = []

    for item in items:
        # Get all marks for this test item
        test_marks = {mark.name for mark in item.iter_markers()}

        # Check if test has at least one required mark
        if not test_marks.intersection(required_marks):
            unmarked_tests.append(item.nodeid)

    if unmarked_tests:
        error_msg = (
            f"\n\nERROR: {len(unmarked_tests)} tests found without required marks!\n"
            f"All tests must have either @pytest.mark.unit or @pytest.mark.integration\n\n"
            f"Unmarked tests:\n"
        )
        for test in unmarked_tests:
            error_msg += f"  - {test}\n"

        error_msg += (
            "\nTo fix this:\n"
            "1. Add 'pytestmark = pytest.mark.unit' for unit tests\n"
            "2. Add 'pytestmark = pytest.mark.integration' for integration tests\n"
            "3. Or use @pytest.mark.unit/@pytest.mark.integration decorators\n"
        )

        pytest.exit(error_msg, returncode=1)
