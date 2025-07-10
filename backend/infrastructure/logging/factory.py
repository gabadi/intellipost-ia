"""
Logging factory implementations.

This module contains the concrete factory implementations that create
appropriate logger instances based on the environment and requirements.
"""

import os

from shared.logging.factory_protocol import LoggerFactoryProtocol
from shared.logging.protocols import (
    DomainLoggerProtocol,
    LoggerProtocol,
    StructuredLoggerProtocol,
)

from .adapters import (
    DomainLoggerAdapter,
    StandardLoggerAdapter,
    StructuredLoggerAdapter,
    TestDomainLoggerAdapter,
    TestLoggerAdapter,
    TestStructuredLoggerAdapter,
)


class LoggerFactory:
    """
    Production logger factory implementation.

    This factory creates logger instances that integrate with the existing
    infrastructure logging system for production use.
    """

    def create_logger(self, name: str) -> LoggerProtocol:
        """
        Create a basic logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing LoggerProtocol
        """
        return StandardLoggerAdapter(name)

    def create_structured_logger(self, name: str) -> StructuredLoggerProtocol:
        """
        Create a structured logger instance with enhanced capabilities.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing StructuredLoggerProtocol
        """
        return StructuredLoggerAdapter(name)

    def create_domain_logger(self, name: str) -> DomainLoggerProtocol:
        """
        Create a domain logger instance with business event capabilities.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing DomainLoggerProtocol
        """
        return DomainLoggerAdapter(name)

    def create_test_logger(self, name: str) -> LoggerProtocol:
        """
        Create a test-friendly logger instance that doesn't produce output.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance suitable for testing
        """
        return TestLoggerAdapter(name)


class TestLoggerFactory:
    """
    Test logger factory implementation.

    This factory creates test-friendly logger instances that capture
    log messages without producing output, suitable for testing environments.
    """

    def create_logger(self, name: str) -> LoggerProtocol:
        """
        Create a test-friendly basic logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Test logger instance implementing LoggerProtocol
        """
        return TestLoggerAdapter(name)

    def create_structured_logger(self, name: str) -> StructuredLoggerProtocol:
        """
        Create a test-friendly structured logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Test logger instance implementing StructuredLoggerProtocol
        """
        return TestStructuredLoggerAdapter(name)

    def create_domain_logger(self, name: str) -> DomainLoggerProtocol:
        """
        Create a test-friendly domain logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Test logger instance implementing DomainLoggerProtocol
        """
        return TestDomainLoggerAdapter(name)

    def create_test_logger(self, name: str) -> LoggerProtocol:
        """
        Create a test-friendly logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Test logger instance suitable for testing
        """
        return TestLoggerAdapter(name)


def get_logger_factory() -> LoggerFactoryProtocol:
    """
    Get the appropriate logger factory based on the environment.

    Returns:
        LoggerFactory for production or TestLoggerFactory for testing
    """
    # Check if we're in a testing environment
    if (
        os.getenv("TESTING") == "true"
        or os.getenv("PYTEST_CURRENT_TEST")
        or "pytest" in os.getenv("_", "").lower()
    ):
        return TestLoggerFactory()

    return LoggerFactory()


# Global factory instance for dependency injection
logger_factory = get_logger_factory()
