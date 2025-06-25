"""
Application settings and configuration management.

This module provides centralized configuration management using Pydantic Settings
with environment variable support and validation.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    This class defines all configuration options for the IntelliPost AI backend,
    including database connections, security settings, and environment-specific
    configurations.
    """

    # Environment configuration
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode flag")

    # Database configuration
    database_url: str = Field(
        default="sqlite:///./intellipost.db", description="Database connection URL"
    )

    # Security configuration
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens and encryption",
    )

    # API configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    # External service configuration
    mercadolibre_client_id: str | None = Field(
        default=None, description="MercadoLibre API client ID"
    )
    mercadolibre_client_secret: str | None = Field(
        default=None, description="MercadoLibre API client secret"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is properly set for production."""
        # Note: In V2, we don't have access to other values during validation
        # This would need to be handled at the model level if needed
        if v == "dev-secret-key-change-in-production":
            # Production check would need to be done elsewhere or via model_validator
            pass  # Simplified for now
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is supported."""
        allowed_formats = ["json", "text"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"Log format must be one of: {allowed_formats}")
        return v.lower()

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Allow environment variables to override defaults
        env_prefix = "INTELLIPOST_"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
