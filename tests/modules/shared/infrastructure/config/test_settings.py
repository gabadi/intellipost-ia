"""Unit tests for settings configuration."""

import pytest

from infrastructure.config.settings import Settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.database_url == "postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5443/intellipost_dev"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert "http://localhost:3000" in settings.cors_origins

    def test_is_development_property(self):
        """Test is_development property."""
        settings = Settings()
        assert settings.is_development is True

        settings.environment = "production"
        assert settings.is_development is False

    def test_is_production_property(self):
        """Test is_production property."""
        settings = Settings()
        assert settings.is_production is False

        settings.environment = "production"
        assert settings.is_production is True

    def test_secret_key_validation_development(self):
        """Test secret key validation in development."""
        # Should not raise error in development
        settings = Settings(
            environment="development",
            secret_key="dev-secret-key-change-in-production"
        )
        assert settings.secret_key == "dev-secret-key-change-in-production"

    def test_secret_key_validation_production_fails(self):
        """Test secret key validation fails in production with default key."""
        with pytest.raises(ValueError, match="Secret key must be changed"):
            Settings(
                environment="production",
                secret_key="dev-secret-key-change-in-production"
            )

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
        with pytest.raises(ValueError, match="Log level must be one of"):
            Settings(log_level="INVALID")

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
        with pytest.raises(ValueError, match="Log format must be one of"):
            Settings(log_format="invalid")
