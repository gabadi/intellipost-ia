"""
AI Content module configuration.

This module provides configuration specific to AI content generation,
including provider settings, model configurations, and content processing parameters.
"""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIContentModuleConfig(BaseSettings):
    """
    Configuration for the AI content generation module.

    This configuration includes AI provider settings, model configurations,
    content generation parameters, and quality control settings.
    """

    module_name: str = Field(
        default="ai_content", description="AI Content module identifier"
    )

    # Environment configuration (from BaseModuleConfig)
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode flag")

    # AI Provider configuration
    primary_provider: str = Field(
        default="gemini", description="Primary AI provider (gemini, openai, claude)"
    )
    fallback_provider: str | None = Field(
        default=None, description="Fallback AI provider"
    )

    # Gemini configuration
    gemini_api_key: str | None = Field(
        default=None, description="Google Gemini API key"
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash", description="Gemini model to use"
    )
    gemini_temperature: float = Field(
        default=0.7, description="Gemini temperature setting"
    )
    gemini_max_tokens: int = Field(default=2048, description="Gemini maximum tokens")

    # OpenAI configuration
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    openai_temperature: float = Field(
        default=0.7, description="OpenAI temperature setting"
    )
    openai_max_tokens: int = Field(default=2048, description="OpenAI maximum tokens")

    # Content generation settings
    max_title_length: int = Field(
        default=60, description="Maximum generated title length"
    )
    max_description_length: int = Field(
        default=500, description="Maximum generated description length"
    )
    min_description_length: int = Field(
        default=50, description="Minimum generated description length"
    )

    # Quality control
    quality_score_threshold: float = Field(
        default=0.7, description="Minimum quality score for generated content"
    )
    toxicity_threshold: float = Field(
        default=0.3, description="Maximum toxicity score allowed"
    )
    enable_content_filtering: bool = Field(
        default=True, description="Enable content filtering"
    )

    # Language settings
    default_language: str = Field(
        default="es", description="Default language for content generation"
    )
    supported_languages: list[str] = Field(
        default=["es", "en", "pt"],
        description="Supported languages for content generation",
    )

    # Image processing
    image_analysis_enabled: bool = Field(
        default=True, description="Enable image analysis for content generation"
    )
    max_images_per_request: int = Field(
        default=5, description="Maximum images to analyze per request"
    )
    image_analysis_timeout: int = Field(
        default=30, description="Image analysis timeout in seconds"
    )

    # Caching settings
    cache_generated_content: bool = Field(
        default=True, description="Enable caching of generated content"
    )
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")

    # Performance settings
    max_concurrent_requests: int = Field(
        default=3, description="Maximum concurrent AI requests"
    )
    request_timeout_seconds: int = Field(
        default=60, description="AI request timeout in seconds"
    )

    # Cost optimization
    daily_request_limit: int = Field(
        default=1000, description="Daily request limit per user"
    )
    monthly_cost_limit_usd: float = Field(
        default=100.0, description="Monthly cost limit in USD"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="INTELLIPOST_AI_CONTENT_",
    )

    def get_module_specific_settings(self) -> dict[str, Any]:
        """Get AI Content module specific settings."""
        return {
            "providers": {
                "primary": self.primary_provider,
                "fallback": self.fallback_provider,
            },
            "gemini": {
                "api_key": self.gemini_api_key,
                "model": self.gemini_model,
                "temperature": self.gemini_temperature,
                "max_tokens": self.gemini_max_tokens,
            },
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
            },
            "content_generation": {
                "max_title_length": self.max_title_length,
                "max_description_length": self.max_description_length,
                "min_description_length": self.min_description_length,
            },
            "quality_control": {
                "quality_score_threshold": self.quality_score_threshold,
                "toxicity_threshold": self.toxicity_threshold,
                "enable_content_filtering": self.enable_content_filtering,
            },
            "language": {
                "default": self.default_language,
                "supported": self.supported_languages,
            },
            "image_processing": {
                "analysis_enabled": self.image_analysis_enabled,
                "max_images_per_request": self.max_images_per_request,
                "analysis_timeout": self.image_analysis_timeout,
            },
            "caching": {
                "enabled": self.cache_generated_content,
                "ttl_hours": self.cache_ttl_hours,
            },
            "performance": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_timeout_seconds": self.request_timeout_seconds,
            },
            "cost_optimization": {
                "daily_request_limit": self.daily_request_limit,
                "monthly_cost_limit_usd": self.monthly_cost_limit_usd,
            },
        }


# Global AI Content module configuration instance
ai_content_config = AIContentModuleConfig()
