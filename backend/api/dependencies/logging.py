"""
Logging dependency injection for FastAPI.

This module provides dependency injection for logging throughout the application,
ensuring hexagonal architecture compliance by using protocols instead of
direct infrastructure dependencies.
"""

from typing import Annotated

from fastapi import Depends

from infrastructure.logging.factory import logger_factory
from shared.logging.factory_protocol import LoggerFactoryProtocol
from shared.logging.protocols import (
    DomainLoggerProtocol,
    LoggerProtocol,
    StructuredLoggerProtocol,
)


def get_logger_factory() -> LoggerFactoryProtocol:
    """
    Get the logger factory instance.

    Returns:
        LoggerFactoryProtocol implementation
    """
    return logger_factory


def get_logger(name: str = "app") -> LoggerProtocol:
    """
    Get a basic logger instance.

    Args:
        name: Logger name, defaults to "app"

    Returns:
        Logger instance implementing LoggerProtocol
    """
    factory = get_logger_factory()
    return factory.create_logger(name)


def get_structured_logger(name: str = "app") -> StructuredLoggerProtocol:
    """
    Get a structured logger instance.

    Args:
        name: Logger name, defaults to "app"

    Returns:
        Logger instance implementing StructuredLoggerProtocol
    """
    factory = get_logger_factory()
    return factory.create_structured_logger(name)


def get_domain_logger(name: str = "app") -> DomainLoggerProtocol:
    """
    Get a domain logger instance.

    Args:
        name: Logger name, defaults to "app"

    Returns:
        Logger instance implementing DomainLoggerProtocol
    """
    factory = get_logger_factory()
    return factory.create_domain_logger(name)


# Dependency factories for specific module contexts
def create_logger_dependency(module_name: str):
    """
    Create a logger dependency factory for a specific module.

    Args:
        module_name: Name of the module requesting the logger

    Returns:
        Dependency function that returns a logger for the module
    """

    def get_module_logger() -> LoggerProtocol:
        factory = get_logger_factory()
        return factory.create_logger(module_name)

    return get_module_logger


def create_structured_logger_dependency(module_name: str):
    """
    Create a structured logger dependency factory for a specific module.

    Args:
        module_name: Name of the module requesting the logger

    Returns:
        Dependency function that returns a structured logger for the module
    """

    def get_module_structured_logger() -> StructuredLoggerProtocol:
        factory = get_logger_factory()
        return factory.create_structured_logger(module_name)

    return get_module_structured_logger


def create_domain_logger_dependency(module_name: str):
    """
    Create a domain logger dependency factory for a specific module.

    Args:
        module_name: Name of the module requesting the logger

    Returns:
        Dependency function that returns a domain logger for the module
    """

    def get_module_domain_logger() -> DomainLoggerProtocol:
        factory = get_logger_factory()
        return factory.create_domain_logger(module_name)

    return get_module_domain_logger


# Pre-configured dependency functions for common use cases
def get_product_logger() -> LoggerProtocol:
    """Get logger for product management module."""
    return create_logger_dependency("modules.product_management")()


def get_content_logger() -> StructuredLoggerProtocol:
    """Get structured logger for content generation module."""
    return create_structured_logger_dependency("modules.content_generation")()


def get_user_logger() -> DomainLoggerProtocol:
    """Get domain logger for user management module."""
    return create_domain_logger_dependency("modules.user_management")()


# Type aliases for convenience
LoggerFactoryDep = Annotated[LoggerFactoryProtocol, Depends(get_logger_factory)]
LoggerDep = Annotated[LoggerProtocol, Depends(get_logger)]
StructuredLoggerDep = Annotated[
    StructuredLoggerProtocol, Depends(get_structured_logger)
]
DomainLoggerDep = Annotated[DomainLoggerProtocol, Depends(get_domain_logger)]

# Module-specific logger type aliases
ProductLoggerDep = Annotated[LoggerProtocol, Depends(get_product_logger)]
ContentLoggerDep = Annotated[StructuredLoggerProtocol, Depends(get_content_logger)]
UserLoggerDep = Annotated[DomainLoggerProtocol, Depends(get_user_logger)]
