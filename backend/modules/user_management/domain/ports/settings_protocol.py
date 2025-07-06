"""
Settings protocol for user management module.

This protocol defines the interface for accessing configuration
settings needed by the user management module.
"""

from typing import Protocol


class SettingsProtocol(Protocol):
    """Protocol for accessing application settings."""

    @property
    def ml_encryption_key(self) -> str | None:
        """Get MercadoLibre encryption key."""
        ...

    @property
    def ml_app_id(self) -> str | None:
        """Get MercadoLibre application ID."""
        ...

    @property
    def ml_app_secret(self) -> str | None:
        """Get MercadoLibre application secret."""
        ...

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        ...

    @property
    def environment(self) -> str:
        """Get current environment name."""
        ...

    @property
    def database_url(self) -> str:
        """Get database URL."""
        ...
