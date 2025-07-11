"""
Logging protocols for user management module.

This module defines the logging protocols specific to the user management domain,
ensuring hexagonal architecture compliance by keeping logging contracts in the domain layer.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class UserLoggerProtocol(Protocol):
    """
    Protocol for user management logging functionality.

    This protocol defines the logging interface needed by the user management domain
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
