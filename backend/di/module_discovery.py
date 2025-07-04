"""
Module discovery system for automatic registration of API protocol implementations.

This system discovers modules that implement API protocols and registers them
with the API container, without importing module-internal protocols.
"""

import asyncio
import importlib
import logging
from typing import Any

from api.container import api_container


class ModuleDiscovery:
    """
    Discovers and registers module implementations of API protocols.

    This class uses a registry pattern to discover modules that implement
    API protocols and registers them with the API container.
    """

    def __init__(self):
        self._provider_registry: dict[str, list[dict[str, str | None]]] = {
            "authentication": [],
            "product": [],
            "content": [],
        }

    def register_authentication_provider(
        self, module_name: str, class_name: str, factory_function: str | None = None
    ) -> None:
        """Register an authentication provider implementation."""
        self._provider_registry["authentication"].append(
            {
                "module": module_name,
                "class": class_name,
                "factory": factory_function,
            }
        )

    def register_product_provider(
        self, module_name: str, class_name: str, factory_function: str | None = None
    ) -> None:
        """Register a product provider implementation."""
        self._provider_registry["product"].append(
            {
                "module": module_name,
                "class": class_name,
                "factory": factory_function,
            }
        )

    def register_content_provider(
        self, module_name: str, class_name: str, factory_function: str | None = None
    ) -> None:
        """Register a content provider implementation."""
        self._provider_registry["content"].append(
            {
                "module": module_name,
                "class": class_name,
                "factory": factory_function,
            }
        )

    async def discover_and_register_providers(self) -> None:
        """Discover and register all API protocol implementations."""
        # Register authentication providers
        for provider_info in self._provider_registry["authentication"]:
            try:
                provider = await self._create_provider_instance(provider_info)
                # Use duck typing - if it has the required methods, it satisfies the protocol
                if hasattr(provider, "authenticate_user") and hasattr(
                    provider, "register_user"
                ):
                    api_container.register_authentication_provider(provider)
            except Exception as e:
                logging.warning(f"Failed to register authentication provider: {e}")

        # Register product providers
        for provider_info in self._provider_registry["product"]:
            try:
                provider = await self._create_provider_instance(provider_info)
                # Use duck typing - if it has the required methods, it satisfies the protocol
                if hasattr(provider, "create_product") and hasattr(
                    provider, "get_product"
                ):
                    api_container.register_product_provider(provider)
            except Exception as e:
                logging.warning(f"Failed to register product provider: {e}")

        # Register content providers
        for provider_info in self._provider_registry["content"]:
            try:
                provider = await self._create_provider_instance(provider_info)
                # Use duck typing - if it has the required methods, it satisfies the protocol
                if hasattr(provider, "generate_content"):
                    api_container.register_content_provider(provider)
            except Exception as e:
                logging.warning(f"Failed to register content provider: {e}")

    async def _create_provider_instance(
        self, provider_info: dict[str, str | None]
    ) -> Any:
        """Create an instance of a provider from registry information."""
        module_name = provider_info["module"]
        if module_name is None:
            raise ValueError("Module name cannot be None")

        module = importlib.import_module(module_name)

        factory_name = provider_info["factory"]
        if factory_name is not None:
            # Use factory function
            factory_func = getattr(module, factory_name)
            # Support both sync and async factory functions
            if hasattr(factory_func, "__await__") or asyncio.iscoroutinefunction(
                factory_func
            ):
                return await factory_func()
            else:
                return factory_func()
        else:
            # Use class constructor
            class_name = provider_info["class"]
            if class_name is None:
                raise ValueError("Class name cannot be None")
            provider_class = getattr(module, class_name)
            return provider_class()


# Global module discovery instance
module_discovery = ModuleDiscovery()

# Register known implementations
# Note: This registration happens at application startup
# Each module can register its API protocol implementations here
module_discovery.register_authentication_provider(
    "modules.user_management.domain.services.authentication_factory",
    "EnhancedAuthenticationService",
    "create_enhanced_authentication_service",  # Factory function
)

# Product provider will be registered when a proper product service is implemented
# module_discovery.register_product_provider(
#     "modules.product_management.domain.services.product_factory",
#     "EnhancedProductService",
#     "create_enhanced_product_service"
# )

# Content provider would be registered when the implementation is ready
# module_discovery.register_content_provider(
#     "modules.content_generation.api.content_provider_impl",
#     "ContentProviderImpl",
#     "create_content_provider"
# )
