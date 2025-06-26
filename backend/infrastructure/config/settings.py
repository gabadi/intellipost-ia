"""Application settings with environment variable support and validation."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment configuration
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode flag")

    # Database configuration
    database_url: str = Field(
        default="postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5432/intellipost_dev",
        description="Database connection URL",
    )
    database_test_url: str = Field(
        default="postgresql+asyncpg://test_user:test_password@localhost:5433/intellipost_test",
        description="Test database connection URL",
    )

    # Database connection settings
    database_pool_size: int = Field(
        default=20, description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10, description="Database connection pool max overflow"
    )
    database_pool_timeout: int = Field(
        default=30, description="Database connection pool timeout in seconds"
    )
    database_pool_recycle: int = Field(
        default=3600, description="Database connection pool recycle time in seconds"
    )

    # Security configuration
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens and encryption",
    )

    # API configuration
    # Default to localhost for security. Use INTELLIPOST_API_HOST="0.0.0.0" in production if needed
    api_host: str = Field(default="127.0.0.1", description="API host")  # nosec B104
    api_port: int = Field(default=8000, description="API port")

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    # Object Storage configuration (MinIO/S3)
    s3_endpoint_url: str | None = Field(
        default="http://localhost:9001",
        description="S3-compatible endpoint URL (MinIO for dev)",
    )
    s3_access_key: str = Field(default="dev_access_key", description="S3 access key")
    s3_secret_key: str = Field(default="dev_secret_key", description="S3 secret key")
    s3_bucket_name: str = Field(
        default="intellipost-storage", description="S3 bucket name"
    )
    s3_region: str = Field(default="us-east-1", description="S3 region")

    # External service configuration
    mercadolibre_client_id: str | None = Field(
        default=None, description="MercadoLibre API client ID"
    )
    mercadolibre_client_secret: str | None = Field(
        default=None, description="MercadoLibre API client secret"
    )

    @model_validator(mode="after")
    def validate_secret_key_for_production(self):
        """Validate that secret key is properly set for production."""
        if (
            self.environment.lower() == "production"
            and self.secret_key == "dev-secret-key-change-in-production"  # nosec B105
        ):
            raise ValueError(
                "Secret key must be changed from default value in production"
            )
        return self

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

        # Look for .env file in project root (one level up from backend)
        env_file = "../.env"
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

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment.lower() == "testing"

    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        if self.is_testing:
            return self.database_test_url
        return self.database_url


# Global settings instance
settings = Settings()
