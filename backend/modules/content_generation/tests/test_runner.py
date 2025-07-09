"""
Test runner for content generation module.

This script provides utilities for running different types of tests
and generating comprehensive test reports.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    print("🧪 Running unit tests...")

    cmd = ["python", "-m", "pytest", "tests/unit/", "-v" if verbose else "-q"]

    if coverage:
        cmd.extend(
            [
                "--cov=modules.content_generation",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]
        )

    cmd.extend(["--tb=short", "--strict-markers", "-m", "not slow"])

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("🔗 Running integration tests...")

    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/integration/",
        "-v" if verbose else "-q",
        "--tb=short",
        "--strict-markers",
        "-m",
        "integration",
    ]

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_api_tests(verbose=False):
    """Run API tests."""
    print("🌐 Running API tests...")

    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/api/",
        "-v" if verbose else "-q",
        "--tb=short",
        "--strict-markers",
        "-m",
        "api",
    ]

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_performance_tests(verbose=False):
    """Run performance tests."""
    print("⚡ Running performance tests...")

    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/test_performance.py",
        "-v" if verbose else "-q",
        "--tb=short",
        "--strict-markers",
        "-m",
        "performance",
        "-s",  # Show print statements for performance metrics
    ]

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_all_tests(verbose=False, coverage=False, include_slow=False):
    """Run all tests."""
    print("🚀 Running all tests...")

    cmd = ["python", "-m", "pytest", "tests/", "-v" if verbose else "-q"]

    if coverage:
        cmd.extend(
            [
                "--cov=modules.content_generation",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=70",
            ]
        )

    cmd.extend(["--tb=short", "--strict-markers"])

    if not include_slow:
        cmd.extend(["-m", "not slow"])

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function."""
    print(f"🎯 Running specific test: {test_path}")

    cmd = [
        "python",
        "-m",
        "pytest",
        test_path,
        "-v" if verbose else "-q",
        "--tb=long",
        "--strict-markers",
        "-s",
    ]

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_tests_with_markers(markers, verbose=False):
    """Run tests with specific markers."""
    print(f"🏷️ Running tests with markers: {markers}")

    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v" if verbose else "-q",
        "--tb=short",
        "--strict-markers",
        "-m",
        markers,
    ]

    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def check_test_requirements():
    """Check if test requirements are installed."""
    print("📋 Checking test requirements...")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "httpx",
        "psutil",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    print("✅ All test requirements are installed")
    return True


def generate_test_report():
    """Generate a comprehensive test report."""
    print("📊 Generating test report...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(__file__).parent.parent / "test_reports"
    report_dir.mkdir(exist_ok=True)

    # Run tests with JUnit XML output
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "--junitxml=" + str(report_dir / f"test_report_{timestamp}.xml"),
        "--html=" + str(report_dir / f"test_report_{timestamp}.html"),
        "--self-contained-html",
        "--cov=modules.content_generation",
        "--cov-report=html:" + str(report_dir / f"coverage_{timestamp}"),
        "--cov-report=xml:" + str(report_dir / f"coverage_{timestamp}.xml"),
        "-v",
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)

    if result.returncode == 0:
        print(f"✅ Test report generated in: {report_dir}")
        print(f"📄 HTML report: test_report_{timestamp}.html")
        print(f"📈 Coverage report: coverage_{timestamp}/index.html")
    else:
        print("❌ Test report generation failed")

    return result


def lint_tests():
    """Run linting on test files."""
    print("🧹 Linting test files...")

    test_dir = Path(__file__).parent

    # Run flake8 on test files
    cmd = [
        "python",
        "-m",
        "flake8",
        str(test_dir),
        "--max-line-length=100",
        "--ignore=E501,W503",
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ All test files pass linting")
    else:
        print("❌ Linting errors found in test files")

    return result


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Content Generation Test Runner")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "api", "performance", "all"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--slow", action="store_true", help="Include slow tests")
    parser.add_argument("--test", help="Run specific test file or function")
    parser.add_argument("--markers", help="Run tests with specific markers")
    parser.add_argument(
        "--report", action="store_true", help="Generate comprehensive test report"
    )
    parser.add_argument("--lint", action="store_true", help="Lint test files")
    parser.add_argument(
        "--check-requirements", action="store_true", help="Check test requirements"
    )

    args = parser.parse_args()

    # Check requirements first
    if args.check_requirements:
        if not check_test_requirements():
            sys.exit(1)
        return

    # Lint tests
    if args.lint:
        result = lint_tests()
        sys.exit(result.returncode)

    # Generate report
    if args.report:
        result = generate_test_report()
        sys.exit(result.returncode)

    # Run specific test
    if args.test:
        result = run_specific_test(args.test, args.verbose)
        sys.exit(result.returncode)

    # Run tests with markers
    if args.markers:
        result = run_tests_with_markers(args.markers, args.verbose)
        sys.exit(result.returncode)

    # Run tests by type
    if args.type == "unit":
        result = run_unit_tests(args.verbose, args.coverage)
    elif args.type == "integration":
        result = run_integration_tests(args.verbose)
    elif args.type == "api":
        result = run_api_tests(args.verbose)
    elif args.type == "performance":
        result = run_performance_tests(args.verbose)
    elif args.type == "all":
        result = run_all_tests(args.verbose, args.coverage, args.slow)
    else:
        print(f"Unknown test type: {args.type}")
        sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
