"""
Logging configuration for the IntelliPost AI backend.

This module provides structured logging with JSON format for production
and human-readable format for development, with sensitive data filtering.
"""

import logging
import logging.config
import sys
from typing import Any

from .settings import Settings


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from log records."""

    SENSITIVE_FIELDS = {
        "password",
        "secret",
        "key",
        "token",
        "api_key",
        "client_secret",
        "access_token",
        "refresh_token",
        "authorization",
        "credential",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter sensitive data from log records."""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Simple string filtering for common patterns
            for field in self.SENSITIVE_FIELDS:
                if field in record.msg.lower():
                    record.msg = record.msg.replace(
                        record.msg, "[FILTERED: Sensitive data removed]"
                    )

        # Filter from extra fields if present
        if hasattr(record, "__dict__"):
            for key in list(record.__dict__.keys()):
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    record.__dict__[key] = "[FILTERED]"

        return True


def setup_logging(settings: Settings) -> None:
    """
    Configure application logging based on settings.

    Args:
        settings: Application settings containing logging configuration.
    """

    # Base logging configuration
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sensitive_filter": {
                "()": SensitiveDataFilter,
            },
        },
        "formatters": {
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "level": settings.log_level,
                "formatter": settings.log_format,
                "filters": ["sensitive_filter"],
            },
        },
        "loggers": {
            "intellipost": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
    }

    # Apply logging configuration
    logging.config.dictConfig(config)

    # Create logger for this module
    logger = logging.getLogger("intellipost.logging")
    logger.info(
        f"Logging configured - Level: {settings.log_level}, Format: {settings.log_format}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"intellipost.{name}")


# Request logging middleware will be added to main.py
class RequestLoggingMiddleware:
    """Middleware to log HTTP requests and responses."""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("request")

    async def __call__(self, scope, receive, send):
        """Process request and log details."""
        if scope["type"] == "http":
            # Log request
            self.logger.info(
                f"Request: {scope['method']} {scope['path']} - "
                f"Client: {scope.get('client', ['unknown', 0])[0]}"
            )

        await self.app(scope, receive, send)
