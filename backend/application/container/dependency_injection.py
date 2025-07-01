"""Dependency injection container for application layer services."""

from typing import Any, TypeVar

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container for application orchestration."""

    def __init__(self) -> None:
        self._services: dict[type[Any], Any] = {}
        self._singletons: dict[type[Any], Any] = {}

    def register(self, service_type: type[T], implementation: T) -> None:
        """Register a service implementation."""
        self._services[service_type] = implementation

    def register_singleton(self, service_type: type[T], implementation: T) -> None:
        """Register a singleton service implementation."""
        self._singletons[service_type] = implementation

    def get(self, service_type: type[T]) -> T:
        """Get a service instance."""
        if service_type in self._singletons:
            return self._singletons[service_type]

        if service_type in self._services:
            return self._services[service_type]

        raise ValueError(f"Service {service_type} not registered")

    def clear(self) -> None:
        """Clear all registered services (useful for testing)."""
        self._services.clear()
        self._singletons.clear()


# Global container instance
container = DIContainer()
