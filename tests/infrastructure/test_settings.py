"""Tests for application settings configuration."""

import pytest
from pydantic import ValidationError

from backend.infrastructure.config.settings import Settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_default_settings(self):
        """Test settings with .env file values loaded."""
        settings = Settings()

        # These values come from the .env file
        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.database_url == "postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5443/intellipost_dev"
        assert settings.api_host == "0.0.0.0"  # From .env file
        assert settings.api_port == 8000
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert "http://localhost:3000" in settings.cors_origins

    def test_is_development_property(self):
        """Test is_development property."""
        settings = Settings(environment="development")
        assert settings.is_development is True

        settings = Settings(environment="production")
        assert settings.is_development is False

    def test_is_production_property(self):
        """Test is_production property."""
        settings = Settings(environment="development")
        assert settings.is_production is False

        settings = Settings(environment="production")
        assert settings.is_production is True

    def test_is_testing_property(self):
        """Test is_testing property."""
        settings = Settings(environment="testing")
        assert settings.is_testing is True

        settings = Settings(environment="development")
        assert settings.is_testing is False

    def test_get_database_url_development(self):
        """Test get_database_url for development environment."""
        settings = Settings(environment="development")
        assert "intellipost_dev" in settings.get_database_url()

    def test_get_database_url_testing(self):
        """Test get_database_url for testing environment."""
        settings = Settings(environment="testing")
        assert "intellipost_test" in settings.get_database_url()

    def test_secret_key_validation_development(self):
        """Test secret key validation allows default in development."""
        settings = Settings(
            environment="development",
            secret_key="dev-secret-key-change-in-production"
        )
        assert settings.secret_key == "dev-secret-key-change-in-production"

    def test_secret_key_validation_production_fails(self):
        """Test secret key validation fails in production with default key."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                environment="production",
                secret_key="dev-secret-key-change-in-production"
            )

        assert "Secret key must be changed" in str(exc_info.value)

    def test_secret_key_validation_production_passes(self):
        """Test secret key validation passes in production with custom key."""
        settings = Settings(
            environment="production",
            secret_key="custom-production-secret-key"
        )
        assert settings.secret_key == "custom-production-secret-key"

    def test_log_level_validation_valid(self):
        """Test log level validation with valid values."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level

    def test_log_level_validation_case_insensitive(self):
        """Test log level validation is case insensitive."""
        settings = Settings(log_level="info")
        assert settings.log_level == "INFO"

    def test_log_level_validation_invalid(self):
        """Test log level validation with invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(log_level="INVALID")

        assert "Log level must be one of" in str(exc_info.value)

    def test_log_format_validation_valid(self):
        """Test log format validation with valid values."""
        for format_val in ["json", "text"]:
            settings = Settings(log_format=format_val)
            assert settings.log_format == format_val

    def test_log_format_validation_case_insensitive(self):
        """Test log format validation is case insensitive."""
        settings = Settings(log_format="JSON")
        assert settings.log_format == "json"

    def test_log_format_validation_invalid(self):
        """Test log format validation with invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(log_format="invalid")

        assert "Log format must be one of" in str(exc_info.value)

    def test_api_host_validation_empty_string(self):
        """Test api_host validation handles empty strings."""
        settings = Settings(api_host="")
        assert settings.api_host == "127.0.0.1"

    def test_api_host_validation_whitespace_only(self):
        """Test api_host validation handles whitespace-only strings."""
        settings = Settings(api_host="   ")
        assert settings.api_host == "127.0.0.1"

    def test_api_host_validation_valid_value(self):
        """Test api_host validation preserves valid values."""
        settings = Settings(api_host="192.168.1.1")
        assert settings.api_host == "192.168.1.1"

    def test_database_pool_settings(self):
        """Test database pool configuration settings."""
        settings = Settings()

        assert settings.database_pool_size == 20
        assert settings.database_max_overflow == 10
        assert settings.database_pool_timeout == 30
        assert settings.database_pool_recycle == 3600

    def test_user_management_configuration(self):
        """Test user management module configuration."""
        settings = Settings()

        # These values come from the .env file
        assert settings.user_jwt_secret_key == "OnB81rZ_67Cmq7ob9xPrW4HgSQWfrvyaeCeHsqLFDfs"
        assert settings.user_jwt_expire_minutes == 30
        assert settings.user_session_expire_hours == 24
        assert settings.user_max_login_attempts == 5
        assert settings.user_password_min_length == 8

    def test_product_management_configuration(self):
        """Test product management module configuration."""
        settings = Settings()

        assert settings.product_max_image_size_mb == 10
        assert settings.product_ai_analysis_enabled is True
        assert settings.product_ai_confidence_threshold == 0.8
        assert settings.product_cache_product_data is True
        assert settings.product_cache_ttl_seconds == 300

    def test_mercadolibre_configuration(self):
        """Test MercadoLibre integration configuration."""
        settings = Settings()

        assert settings.mercadolibre_requests_per_minute == 200
        assert settings.mercadolibre_default_country == "AR"
        assert settings.mercadolibre_sync_interval_minutes == 15

    def test_ai_content_configuration(self):
        """Test AI content generation configuration."""
        settings = Settings()

        assert settings.ai_content_primary_provider == "gemini"
        assert settings.ai_content_gemini_model == "gemini-1.5-flash"
        assert settings.ai_content_max_title_length == 60
        assert settings.ai_content_max_description_length == 500
        assert settings.ai_content_quality_score_threshold == 0.7
        assert settings.ai_content_default_language == "es"

    def test_s3_configuration(self):
        """Test S3/MinIO configuration."""
        settings = Settings()

        assert settings.s3_endpoint_url == "http://localhost:9001"
        assert settings.s3_access_key == "dev_access_key"
        assert settings.s3_secret_key == "dev_secret_key"
        assert settings.s3_bucket_name == "intellipost-storage"
        assert settings.s3_region == "us-east-1"

    def test_custom_settings_override(self):
        """Test that custom settings properly override defaults."""
        custom_settings = Settings(
            environment="staging",
            debug=False,
            api_port=9000,
            log_level="DEBUG",
            database_pool_size=50
        )

        assert custom_settings.environment == "staging"
        assert custom_settings.debug is False
        assert custom_settings.api_port == 9000
        assert custom_settings.log_level == "DEBUG"
        assert custom_settings.database_pool_size == 50

    def test_external_api_keys_from_env(self):
        """Test that external API keys come from .env file."""
        settings = Settings()

        # These values come from the .env file
        assert settings.mercadolibre_client_id == "your-ml-client-id"
        assert settings.mercadolibre_client_secret == "your-ml-client-secret"
        assert settings.ai_content_gemini_api_key == "your-gemini-api-key"
        assert settings.google_gemini_api_key == "your-gemini-api-key"
        assert settings.openai_api_key == "your-openai-api-key"
        assert settings.photoroom_api_key == "your-photoroom-api-key"
