"""
Logging factory protocol for dependency injection.

This module defines the factory protocol that allows the dependency injection
system to create appropriate logger instances without the domain and application
layers needing to know about specific logging implementations.
"""

from typing import Protocol, runtime_checkable

from .protocols import DomainLoggerProtocol, LoggerProtocol, StructuredLoggerProtocol


@runtime_checkable
class LoggerFactoryProtocol(Protocol):
    """
    Protocol for logger factory implementations.

    This protocol defines the interface for creating different types of loggers
    based on the needs of different layers in the hexagonal architecture.
    """

    def create_logger(self, name: str) -> LoggerProtocol:
        """
        Create a basic logger instance.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing LoggerProtocol
        """
        ...

    def create_structured_logger(self, name: str) -> StructuredLoggerProtocol:
        """
        Create a structured logger instance with enhanced capabilities.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing StructuredLoggerProtocol
        """
        ...

    def create_domain_logger(self, name: str) -> DomainLoggerProtocol:
        """
        Create a domain logger instance with business event capabilities.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance implementing DomainLoggerProtocol
        """
        ...

    def create_test_logger(self, name: str) -> LoggerProtocol:
        """
        Create a test-friendly logger instance that doesn't produce output.

        Args:
            name: Logger name, typically __name__ of the calling module

        Returns:
            Logger instance suitable for testing
        """
        ...
