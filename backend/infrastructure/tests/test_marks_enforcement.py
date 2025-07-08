"""
Test that pytest configuration properly enforces test marks.

This is a unit test that verifies our CI/test configuration works correctly.
"""

import subprocess
from pathlib import Path

import pytest

# Mark this module as unit tests
pytestmark = pytest.mark.unit


class TestMarksEnforcement:
    """Test that pytest mark enforcement works correctly."""

    def test_unmarked_test_causes_failure(self):
        """Test that a test file without marks causes pytest to fail."""
        # Create a temporary test file without marks in the backend directory
        # (conftest.py only applies to files within the project structure)
        backend_dir = Path(__file__).parent.parent  # backend directory
        temp_test_file = backend_dir / "test_temp_unmarked_validation.py"

        unmarked_test_content = '''"""Temporary test without marks for validation."""

def test_this_has_no_marks():
    """This test has no pytest marks."""
    assert True
'''

        try:
            # Write the temporary test file
            temp_test_file.write_text(unmarked_test_content)

            # Run pytest on the temporary file
            result = subprocess.run(
                ["uv", "run", "pytest", str(temp_test_file), "-v"],
                capture_output=True,
                text=True,
                cwd=backend_dir,
            )

            # Pytest should fail (exit code != 0)
            assert result.returncode != 0, (
                f"Expected pytest to fail on unmarked test, but it passed. "
                f"stdout: {result.stdout}, stderr: {result.stderr}"
            )

            # Check that the error message contains our expected text
            output = result.stdout + result.stderr
            assert "tests found without required marks" in output, (
                f"Expected error message about missing marks not found. "
                f"Output: {output}"
            )

        finally:
            # Cleanup
            if temp_test_file.exists():
                temp_test_file.unlink()

    def test_marked_test_passes(self):
        """Test that a properly marked test passes pytest validation."""
        # Create a temporary test file with proper marks in the backend directory
        backend_dir = Path(__file__).parent.parent  # backend directory
        temp_test_file = backend_dir / "test_temp_marked_validation.py"

        marked_test_content = '''"""Temporary test with marks for validation."""
import pytest

pytestmark = pytest.mark.unit

def test_this_has_unit_mark():
    """This test has proper unit mark."""
    assert True
'''

        try:
            # Write the temporary test file
            temp_test_file.write_text(marked_test_content)

            # Run pytest on the temporary file
            result = subprocess.run(
                ["uv", "run", "pytest", str(temp_test_file), "-v"],
                capture_output=True,
                text=True,
                cwd=backend_dir,
            )

            # Pytest should pass (exit code == 0)
            assert result.returncode == 0, (
                f"Expected pytest to pass on marked test, but it failed. "
                f"stdout: {result.stdout}, stderr: {result.stderr}"
            )

            # Check that test actually ran and passed
            assert "1 passed" in result.stdout, (
                f"Expected '1 passed' in output. Output: {result.stdout}"
            )

        finally:
            # Cleanup
            if temp_test_file.exists():
                temp_test_file.unlink()

    def test_current_test_has_proper_marks(self):
        """Verify this test file itself has proper marks."""
        # This test verifies that our test enforcement is working
        # by checking that this very test file has the required marks
        import inspect

        # Get the current module
        current_module = inspect.getmodule(self)

        # Check that pytestmark is defined
        assert hasattr(current_module, "pytestmark"), (
            "This test module should have pytestmark defined"
        )

        # Check that it's a unit test mark
        pytestmark = current_module.pytestmark
        assert hasattr(pytestmark, "name"), "pytestmark should be a pytest mark object"
        assert pytestmark.name == "unit", f"Expected unit mark, got: {pytestmark.name}"
