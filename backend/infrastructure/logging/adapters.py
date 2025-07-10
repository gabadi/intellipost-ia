"""
Logging adapters that implement the logging protocols.

This module contains the concrete implementations of the logging protocols
that wrap the existing infrastructure logging system.
"""

from typing import Any

from infrastructure.config.logging import (
    get_logger,
    get_structured_logger,
    set_correlation_id,
)
from shared.logging.protocols import (
    BaseLoggerAdapter,
    DomainLoggerProtocol,
    StructuredLoggerProtocol,
)


class StandardLoggerAdapter(BaseLoggerAdapter):
    """
    Adapter that wraps the standard logging system to implement LoggerProtocol.

    This adapter provides a clean interface for basic logging functionality
    while maintaining compatibility with the existing logging infrastructure.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._logger = get_logger(name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with optional structured data."""
        context = self._with_context(**kwargs)
        self._logger.debug(message, extra=context)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with optional structured data."""
        context = self._with_context(**kwargs)
        self._logger.info(message, extra=context)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with optional structured data."""
        context = self._with_context(**kwargs)
        self._logger.warning(message, extra=context)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with optional structured data."""
        context = self._with_context(**kwargs)
        self._logger.error(message, extra=context)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message with optional structured data."""
        context = self._with_context(**kwargs)
        self._logger.critical(message, extra=context)


class StructuredLoggerAdapter(StandardLoggerAdapter):
    """
    Adapter that wraps the structured logging system to implement StructuredLoggerProtocol.

    This adapter provides enhanced logging capabilities including performance
    tracking and audit logging while maintaining protocol compliance.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._structured_logger = get_structured_logger(name)

    def performance(self, operation: str, duration_ms: float, **kwargs: Any) -> None:
        """Log performance metrics for an operation."""
        context = self._with_context(**kwargs)
        self._structured_logger.performance(operation, duration_ms, **context)

    def audit(self, action: str, resource: str, **kwargs: Any) -> None:
        """Log audit events for compliance and tracking."""
        context = self._with_context(**kwargs)
        self._structured_logger.audit(action, resource, **context)


class DomainLoggerAdapter(StructuredLoggerAdapter):
    """
    Adapter that provides domain-specific logging capabilities.

    This adapter extends structured logging with business event tracking
    and correlation management for domain layer usage.
    """

    def __init__(self, name: str, correlation_id: str | None = None):
        super().__init__(name)
        if correlation_id:
            self._context["correlation_id"] = correlation_id

    def business_event(self, event_type: str, entity_id: str, **kwargs: Any) -> None:
        """Log domain business events."""
        context = self._with_context(
            event_type=event_type,
            entity_id=entity_id,
            business_event=True,
            **kwargs,
        )
        self._structured_logger.info(f"Business event: {event_type}", **context)

    def with_correlation_id(self, correlation_id: str) -> DomainLoggerProtocol:
        """Create a logger instance with a correlation ID for request tracing."""
        new_adapter = DomainLoggerAdapter(self.name, correlation_id)
        new_adapter._context = self._context.copy()
        new_adapter._context["correlation_id"] = correlation_id
        set_correlation_id(correlation_id)
        return new_adapter

    def with_context(self, **context: Any) -> DomainLoggerProtocol:
        """Create a logger instance with additional context."""
        new_adapter = DomainLoggerAdapter(self.name)
        new_adapter._context = self._with_context(**context)
        return new_adapter


class TestLoggerAdapter(BaseLoggerAdapter):
    """
    Test-friendly logger adapter that captures logs without output.

    This adapter is designed for testing environments where you want to
    verify logging behavior without producing actual log output.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.logged_messages: list[dict[str, Any]] = []

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal method to capture log messages for testing."""
        context = self._with_context(**kwargs)
        self.logged_messages.append(
            {"level": level, "message": message, "context": context}
        )

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message (captured for testing)."""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message (captured for testing)."""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message (captured for testing)."""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message (captured for testing)."""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message (captured for testing)."""
        self._log("CRITICAL", message, **kwargs)

    def clear_logs(self) -> None:
        """Clear captured log messages."""
        self.logged_messages.clear()

    def get_logs(self, level: str | None = None) -> list[dict[str, Any]]:
        """
        Get captured log messages, optionally filtered by level.

        Args:
            level: Optional log level to filter by

        Returns:
            List of captured log messages
        """
        if level is None:
            return self.logged_messages.copy()
        return [msg for msg in self.logged_messages if msg["level"] == level]


class TestStructuredLoggerAdapter(TestLoggerAdapter, StructuredLoggerProtocol):
    """Test-friendly structured logger adapter."""

    def performance(self, operation: str, duration_ms: float, **kwargs: Any) -> None:
        """Log performance metrics (captured for testing)."""
        context = self._with_context(
            operation=operation, duration_ms=duration_ms, **kwargs
        )
        self._log("INFO", f"Performance: {operation}", **context)

    def audit(self, action: str, resource: str, **kwargs: Any) -> None:
        """Log audit events (captured for testing)."""
        context = self._with_context(action=action, resource=resource, **kwargs)
        self._log("INFO", f"Audit: {action} on {resource}", **context)


class TestDomainLoggerAdapter(TestStructuredLoggerAdapter, DomainLoggerProtocol):
    """Test-friendly domain logger adapter."""

    def __init__(self, name: str, correlation_id: str | None = None):
        super().__init__(name)
        if correlation_id:
            self._context["correlation_id"] = correlation_id

    def business_event(self, event_type: str, entity_id: str, **kwargs: Any) -> None:
        """Log domain business events (captured for testing)."""
        context = self._with_context(
            event_type=event_type,
            entity_id=entity_id,
            business_event=True,
            **kwargs,
        )
        self._log("INFO", f"Business event: {event_type}", **context)

    def with_correlation_id(self, correlation_id: str) -> DomainLoggerProtocol:
        """Create a logger instance with a correlation ID for request tracing."""
        new_adapter = TestDomainLoggerAdapter(self.name, correlation_id)
        new_adapter._context = self._context.copy()
        new_adapter._context["correlation_id"] = correlation_id
        return new_adapter

    def with_context(self, **context: Any) -> DomainLoggerProtocol:
        """Create a logger instance with additional context."""
        new_adapter = TestDomainLoggerAdapter(self.name)
        new_adapter._context = self._with_context(**context)
        return new_adapter
