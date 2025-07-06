"""Application settings with environment variable support and validation."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment configuration
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode flag")

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

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.environment.lower() == "staging"

    # Database configuration
    database_url: str = Field(
        default="postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5443/intellipost_dev",
        description="Database connection URL",
    )
    database_test_url: str = Field(
        default="postgresql+asyncpg://test_user:test_password@localhost:5443/intellipost_test",
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

    # CORS configuration - secure by default
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3001",  # SvelteKit dev server
            "http://127.0.0.1:3001",
            "http://localhost:4173",  # SvelteKit preview
            "http://127.0.0.1:4173"
        ],
        description="Allowed CORS origins - production should use HTTPS",
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

    # User Management Module Configuration - Mobile-Optimized JWT Strategy
    user_jwt_secret_key: str = Field(
        default="dev-jwt-secret-change-in-production",
        description="JWT secret key for user authentication",
    )
    user_jwt_algorithm: str = Field(
        default="HS256", description="JWT algorithm for MVP security requirements"
    )
    user_jwt_access_token_expire_minutes: int = Field(
        default=15, description="Access token expiry time in minutes (battery optimization)"
    )
    user_jwt_refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiry time in days (user convenience)"
    )
    user_session_expire_hours: int = Field(
        default=24, description="User session expiry time in hours"
    )
    user_max_login_attempts: int = Field(
        default=5, description="Maximum login attempts before lockout"
    )
    user_password_min_length: int = Field(
        default=8, description="Minimum password length"
    )
    user_registration_enabled: bool = Field(
        default=False, description="Enable user registration functionality"
    )
    user_default_admin_email: str = Field(
        default="admin@intellipost.ai", description="Default admin user email"
    )
    user_default_admin_password: str = Field(
        default="admin123", description="Default admin user password"
    )

    # Product Management Module Configuration
    product_max_image_size_mb: int = Field(
        default=10, description="Maximum image size in MB"
    )
    product_ai_analysis_enabled: bool = Field(
        default=True, description="Enable AI analysis for products"
    )
    product_ai_confidence_threshold: float = Field(
        default=0.8, description="AI confidence threshold for auto-publishing"
    )
    product_cache_product_data: bool = Field(
        default=True, description="Enable product data caching"
    )
    product_cache_ttl_seconds: int = Field(
        default=300, description="Product cache TTL in seconds"
    )

    # MercadoLibre Integration Module Configuration
    mercadolibre_requests_per_minute: int = Field(
        default=200, description="MercadoLibre API requests per minute limit"
    )
    mercadolibre_default_country: str = Field(
        default="AR", description="Default MercadoLibre country code"
    )
    mercadolibre_sync_interval_minutes: int = Field(
        default=15, description="MercadoLibre sync interval in minutes"
    )

    # AI Content Generation Module Configuration
    ai_content_primary_provider: str = Field(
        default="gemini", description="Primary AI content provider"
    )
    ai_content_gemini_api_key: str | None = Field(
        default=None, description="Gemini API key"
    )
    ai_content_gemini_model: str = Field(
        default="gemini-1.5-flash", description="Gemini model name"
    )
    ai_content_max_title_length: int = Field(
        default=60, description="Maximum title length for generated content"
    )
    ai_content_max_description_length: int = Field(
        default=500, description="Maximum description length for generated content"
    )
    ai_content_quality_score_threshold: float = Field(
        default=0.7, description="Quality score threshold for content acceptance"
    )
    ai_content_default_language: str = Field(
        default="es", description="Default language for content generation"
    )

    # External API Keys
    google_gemini_api_key: str | None = Field(
        default=None, description="Google Gemini API key"
    )
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    photoroom_api_key: str | None = Field(default=None, description="PhotoRoom API key")

    @model_validator(mode="after")
    def validate_secret_key_for_production(self):
        """Validate that secret keys are properly set for production."""
        if self.environment.lower() == "production":
            if self.secret_key == "dev-secret-key-change-in-production":  # nosec B105
                raise ValueError(
                    "Secret key must be changed from default value in production"
                )
            if self.user_jwt_secret_key == "dev-jwt-secret-change-in-production":  # nosec B105
                raise ValueError(
                    "JWT secret key must be changed from default value in production"
                )
            # Ensure HTTPS origins in production
            for origin in self.cors_origins:
                if not origin.startswith("https://") and not origin.startswith("http://localhost"):
                    raise ValueError(
                        f"Production CORS origins must use HTTPS: {origin}"
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

    @field_validator("api_host")
    @classmethod
    def validate_api_host(cls, v: str) -> str:
        """Validate api_host and handle empty strings by returning default."""
        if not v or v.strip() == "":
            return "127.0.0.1"  # Return default if empty
        return v

    model_config = SettingsConfigDict(
        # Load environment files in order (later files override earlier ones)
        env_file=[
            "../.env",  # Base development config
            "../.env.local",  # Local overrides (gitignored)
            "../.env.testing",  # Testing overrides (when INTELLIPOST_ENVIRONMENT=testing)
            "../.env.staging",  # Staging overrides (when INTELLIPOST_ENVIRONMENT=staging)
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow environment variables to override defaults
        env_prefix="INTELLIPOST_",
        # Allow extra variables during migration - we'll clean this up later
        extra="ignore",
    )

    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        if self.is_testing:
            return self.database_test_url
        return self.database_url

    def get_api_url(self) -> str:
        """Get the full API URL for the current environment."""
        protocol = "https" if self.is_production else "http"
        if self.is_development or self.is_testing:
            return f"{protocol}://{self.api_host}:{self.api_port}"
        return f"{protocol}://{self.api_host}"  # Production uses standard ports

    def validate_configuration(self) -> dict[str, bool]:
        """Validate current configuration and return status."""
        validations = {
            "environment_set": bool(self.environment),
            "database_url_valid": bool(self.get_database_url()),
            "api_port_valid": 1000 <= self.api_port <= 65535,
            "secret_key_secure": (
                self.secret_key != "dev-secret-key-change-in-production"  # nosec B105
                if self.is_production
                else True
            ),
            "jwt_secret_secure": (
                self.user_jwt_secret_key != "dev-jwt-secret-change-in-production"  # nosec B105
                if self.is_production
                else True
            ),
            "cors_origins_secure": (
                all(origin.startswith("https://") or origin.startswith("http://localhost") 
                    for origin in self.cors_origins)
                if self.is_production
                else True
            ),
        }
        return validations


# Global settings instance
settings = Settings()
