"""
Logging protocols for content generation module.

This module defines the logging protocols specific to the content generation domain,
ensuring hexagonal architecture compliance by keeping logging contracts in the domain layer.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ContentLoggerProtocol(Protocol):
    """
    Protocol for content generation logging functionality.

    This protocol defines the logging interface needed by the content generation domain
    and application layers.
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
