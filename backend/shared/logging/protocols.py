"""
Logging protocols for hexagonal architecture compliance.

This module defines the protocols that allow domain and application layers
to use logging without violating architecture boundaries by depending directly
on infrastructure implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """
    Protocol for basic logging functionality.

    This protocol defines the minimal interface that any logger implementation
    must provide to be used in the domain and application layers.
    """

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with optional structured data."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with optional structured data."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with optional structured data."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with optional structured data."""
        ...

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message with optional structured data."""
        ...


@runtime_checkable
class StructuredLoggerProtocol(LoggerProtocol, Protocol):
    """
    Protocol for structured logging with additional capabilities.

    Extends the basic logger protocol with structured logging features
    like performance tracking and audit logging.
    """

    def performance(self, operation: str, duration_ms: float, **kwargs: Any) -> None:
        """Log performance metrics for an operation."""
        ...

    def audit(self, action: str, resource: str, **kwargs: Any) -> None:
        """Log audit events for compliance and tracking."""
        ...


@runtime_checkable
class DomainLoggerProtocol(StructuredLoggerProtocol, Protocol):
    """
    Protocol for domain-specific logging functionality.

    Extends structured logging with domain-specific capabilities
    like business event logging and correlation tracking.
    """

    def business_event(self, event_type: str, entity_id: str, **kwargs: Any) -> None:
        """Log domain business events."""
        ...

    def with_correlation_id(self, correlation_id: str) -> "DomainLoggerProtocol":
        """Create a logger instance with a correlation ID for request tracing."""
        ...

    def with_context(self, **context: Any) -> "DomainLoggerProtocol":
        """Create a logger instance with additional context."""
        ...


class BaseLoggerAdapter(ABC):
    """
    Abstract base class for logger adapters.

    Provides common functionality for logger adapters that implement
    the logging protocols while wrapping actual logging implementations.
    """

    def __init__(self, name: str):
        self.name = name
        self._context: dict[str, Any] = {}

    def _get_context(self) -> dict[str, Any]:
        """Get the current logging context."""
        return self._context.copy()

    def _with_context(self, **additional_context: Any) -> dict[str, Any]:
        """Merge additional context with current context."""
        context = self._get_context()
        context.update(additional_context)
        return context

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message - must be implemented by subclasses."""
        ...
