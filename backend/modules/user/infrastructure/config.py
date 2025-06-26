"""
User module configuration.

This module provides configuration specific to the user management module,
including authentication settings, session management, and user-specific features.
"""

from typing import Any

from pydantic import Field

from infrastructure.config.base_config import BaseModuleConfig, DatabaseMixin


class UserModuleConfig(BaseModuleConfig, DatabaseMixin):
    """
    Configuration for the user management module.

    This configuration includes user authentication, session management,
    and user-specific security settings.
    """

    module_name: str = Field(default="user", description="User module identifier")

    # Override database URL with default for user module
    database_url: str = Field(
        default="postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5432/intellipost_dev",
        description="Database connection URL for user module",
    )

    # Authentication configuration
    jwt_secret_key: str = Field(
        default="user-jwt-secret-change-in-production",
        description="JWT secret key for user authentication",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(
        default=30, description="JWT token expiration in minutes"
    )

    # Session configuration
    session_expire_hours: int = Field(
        default=24, description="User session expiration in hours"
    )
    remember_me_expire_days: int = Field(
        default=30, description="Remember me token expiration in days"
    )

    # Password policy
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(
        default=True, description="Require uppercase letters in password"
    )
    password_require_lowercase: bool = Field(
        default=True, description="Require lowercase letters in password"
    )
    password_require_digits: bool = Field(
        default=True, description="Require digits in password"
    )
    password_require_special: bool = Field(
        default=True, description="Require special characters in password"
    )

    # Account security
    max_login_attempts: int = Field(
        default=5, description="Maximum login attempts before account lockout"
    )
    lockout_duration_minutes: int = Field(
        default=15, description="Account lockout duration in minutes"
    )

    # User profile settings
    profile_image_max_size_mb: int = Field(
        default=5, description="Maximum profile image size in MB"
    )
    allowed_image_formats: list[str] = Field(
        default=["jpg", "jpeg", "png", "webp"],
        description="Allowed profile image formats",
    )

    class Config(BaseModuleConfig.Config):
        """Pydantic configuration for user module."""

        env_prefix = "INTELLIPOST_USER_"

    def get_module_specific_settings(self) -> dict[str, Any]:
        """Get user module specific settings."""
        return {
            "authentication": {
                "jwt_secret_key": self.jwt_secret_key,
                "jwt_algorithm": self.jwt_algorithm,
                "jwt_expire_minutes": self.jwt_expire_minutes,
            },
            "session": {
                "session_expire_hours": self.session_expire_hours,
                "remember_me_expire_days": self.remember_me_expire_days,
            },
            "password_policy": {
                "min_length": self.password_min_length,
                "require_uppercase": self.password_require_uppercase,
                "require_lowercase": self.password_require_lowercase,
                "require_digits": self.password_require_digits,
                "require_special": self.password_require_special,
            },
            "security": {
                "max_login_attempts": self.max_login_attempts,
                "lockout_duration_minutes": self.lockout_duration_minutes,
            },
            "profile": {
                "image_max_size_mb": self.profile_image_max_size_mb,
                "allowed_image_formats": self.allowed_image_formats,
            },
        }


# Global user module configuration instance
user_config = UserModuleConfig()
