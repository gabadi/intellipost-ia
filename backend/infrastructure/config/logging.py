"""
Enhanced structured logging configuration for the IntelliPost AI backend.

This module provides comprehensive structured logging with JSON format,
correlation IDs, performance metrics, security events, and observability features.

Architectural Decision: Custom Structured Logger vs Simple Logger
===============================================================

This implementation uses a CUSTOM STRUCTURED LOGGER rather than a simple
logging setup for the following reasons:

1. **Observability Requirements**: Modern applications need structured logs
   for effective monitoring, alerting, and debugging in production

2. **Correlation Tracking**: Distributed systems require request tracing
   across multiple services and components

3. **Security Monitoring**: Built-in security event detection and filtering
   for compliance and threat detection

4. **Performance Monitoring**: Automatic performance metrics collection
   for application optimization

5. **Sensitive Data Protection**: Automatic filtering of sensitive information
   from logs to prevent data leaks

6. **Production Readiness**: JSON format integrates with log aggregation
   systems like ELK stack, Splunk, or CloudWatch

For simple applications, basic logging would suffice. For production
applications requiring observability, structured logging is essential.

The custom implementation provides more control than third-party solutions
while maintaining compatibility with standard Python logging.
"""

import contextvars
import json
import logging
import logging.config
import sys
import time
import uuid
from typing import Any

from .settings import Settings

# Context variables for request tracing
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="")


class StructuredFormatter(logging.Formatter):
    """
    Enhanced structured formatter with correlation IDs and context.

    This formatter creates structured log entries with additional context
    for observability and distributed tracing.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data."""
        # Base log structure
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }

        # Add correlation context if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_entry["user_id"] = user_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "stack_info",
                    "exc_info",
                    "exc_text",
                }:
                    log_entry[key] = value

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class SensitiveDataFilter(logging.Filter):
    """Enhanced filter to remove sensitive data from log records."""

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
        "jwt",
        "auth",
        "bearer",
        "session_id",
        "cookie",
        "csrf",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter sensitive data from log records."""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Advanced pattern filtering
            message = record.msg
            for field in self.SENSITIVE_FIELDS:
                if field in message.lower():
                    message = f"[FILTERED: Contains sensitive field '{field}']"
                    break
            record.msg = message

        # Filter from extra fields
        if hasattr(record, "__dict__"):
            for key in list(record.__dict__.keys()):
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    record.__dict__[key] = "[FILTERED]"

        return True


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance context to log records."""
        if not hasattr(record, "duration_ms"):
            # Add default performance context
            record.performance = {"timestamp": time.time(), "level": record.levelname}
        return True


class SecurityEventFilter(logging.Filter):
    """Filter to identify and enrich security-related events."""

    SECURITY_KEYWORDS = {
        "login",
        "logout",
        "authentication",
        "authorization",
        "permission",
        "denied",
        "forbidden",
        "unauthorized",
        "failed",
        "attack",
        "breach",
        "intrusion",
        "suspicious",
        "malware",
        "injection",
        "xss",
        "csrf",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Identify and mark security events."""
        message = record.getMessage().lower()

        if any(keyword in message for keyword in self.SECURITY_KEYWORDS):
            record.security_event = True
            record.security_level = (
                "high" if "failed" in message or "denied" in message else "medium"
            )

        return True


def setup_logging(settings: Settings) -> None:
    """
    Configure enhanced structured logging based on settings.

    Args:
        settings: Application settings containing logging configuration.
    """

    # Enhanced logging configuration with structured logging
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sensitive_filter": {
                "()": SensitiveDataFilter,
            },
            "performance_filter": {
                "()": PerformanceFilter,
            },
            "security_filter": {
                "()": SecurityEventFilter,
            },
        },
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
                "datefmt": "%Y-%m-%dT%H:%M:%S.%fZ",
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "level": settings.log_level,
                "formatter": "structured" if settings.log_format == "json" else "text",
                "filters": [
                    "sensitive_filter",
                    "performance_filter",
                    "security_filter",
                ],
            },
            "security": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "level": "WARNING",
                "formatter": "structured",
                "filters": ["security_filter"],
            },
        },
        "loggers": {
            "intellipost": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "intellipost.security": {
                "level": "INFO",
                "handlers": ["security", "console"],
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
            "sqlalchemy.engine": {
                "level": "WARNING",
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
        "Enhanced structured logging configured",
        extra={
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "features": [
                "correlation_tracking",
                "performance_metrics",
                "security_events",
            ],
        },
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


def set_correlation_id(correlation_id: str | None = None) -> str:
    """
    Set correlation ID for request tracing.

    Args:
        correlation_id: Optional correlation ID, generates one if not provided

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    correlation_id_var.set(correlation_id)
    return correlation_id


def set_request_id(request_id: str | None = None) -> str:
    """
    Set request ID for request tracing.

    Args:
        request_id: Optional request ID, generates one if not provided

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)
    return request_id


def set_user_id(user_id: str) -> None:
    """
    Set user ID for request tracing.

    Args:
        user_id: User identifier
    """
    user_id_var.set(user_id)


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id_var.get()


def get_request_id() -> str:
    """Get current request ID."""
    return request_id_var.get()


def get_user_id() -> str:
    """Get current user ID."""
    return user_id_var.get()


class StructuredLogger:
    """
    Enhanced logger with structured logging capabilities.

    This logger provides additional methods for structured logging
    with performance tracking and security event detection.
    """

    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.name = name

    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with structured data."""
        self.logger.critical(message, extra=kwargs)

    def performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics."""
        self.logger.info(
            f"Performance: {operation}",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "performance_metric": True,
                **kwargs,
            },
        )

    def security_event(self, event_type: str, severity: str = "medium", **kwargs):
        """Log security events."""
        security_logger = logging.getLogger("intellipost.security")
        security_logger.warning(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "severity": severity,
                "security_event": True,
                **kwargs,
            },
        )

    def audit(self, action: str, resource: str, **kwargs):
        """Log audit events."""
        self.logger.info(
            f"Audit: {action} on {resource}",
            extra={
                "action": action,
                "resource": resource,
                "audit_event": True,
                **kwargs,
            },
        )


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Enhanced request logging middleware
class StructuredRequestLoggingMiddleware:
    """Enhanced middleware for structured HTTP request/response logging."""

    def __init__(self, app):
        self.app = app
        self.logger = get_structured_logger("request")

    async def __call__(self, scope, receive, send):
        """Process request with structured logging."""
        if scope["type"] == "http":
            # Generate request tracking IDs
            request_id = set_request_id()
            correlation_id = set_correlation_id()

            start_time = time.time()

            # Log request start
            self.logger.info(
                "HTTP request started",
                method=scope["method"],
                path=scope["path"],
                query_string=scope.get("query_string", b"").decode(),
                client_ip=scope.get("client", ["unknown"])[0],
                user_agent=dict(scope.get("headers", []))
                .get(b"user-agent", b"")
                .decode(),
                request_id=request_id,
                correlation_id=correlation_id,
            )

            # Wrap send to log response
            async def logging_send(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    duration_ms = (time.time() - start_time) * 1000

                    # Log request completion
                    self.logger.info(
                        "HTTP request completed",
                        status_code=status_code,
                        duration_ms=round(duration_ms, 2),
                        request_id=request_id,
                        correlation_id=correlation_id,
                    )

                    # Log performance metrics
                    self.logger.performance(
                        "http_request",
                        duration_ms=duration_ms,
                        status_code=status_code,
                        method=scope["method"],
                        path=scope["path"],
                    )

                await send(message)

            await self.app(scope, receive, logging_send)
        else:
            await self.app(scope, receive, send)
