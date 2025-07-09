"""
Base configuration module for all IntelliPost modules.

This module provides the foundation for module-specific configurations,
ensuring consistency while allowing module-specific customization.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseModuleConfig(BaseSettings, ABC):
    """
    Base configuration class for all modules.

    This abstract base class ensures that all module configurations
    follow the same pattern while allowing customization per module.
    """

    # Module identification
    module_name: str = Field(description="Module name for identification")

    # Environment configuration
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode flag")

    # Common logging configuration
    log_level: str = Field(default="INFO", description="Module-specific logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment.lower() == "testing"

    @abstractmethod
    def get_module_specific_settings(self) -> dict[str, Any]:
        """
        Get module-specific settings.

        Each module must implement this method to return its specific
        configuration options.
        """
        pass

    def get_logger_name(self) -> str:
        """Get the logger name for this module."""
        return f"intellipost.{self.module_name}"


class DatabaseMixin:
    """Mixin for modules that need database configuration."""

    database_url: str = Field(
        default="postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5432/intellipost_dev",
        description="Database connection URL for this module",
    )
    database_pool_size: int = Field(
        default=5, description="Module-specific database pool size"
    )
    database_max_overflow: int = Field(
        default=2, description="Module-specific database pool max overflow"
    )


class ExternalServiceMixin:
    """Mixin for modules that interact with external services."""

    service_timeout: int = Field(
        default=30, description="External service timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3, description="Number of retry attempts for external services"
    )
    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per minute"
    )
