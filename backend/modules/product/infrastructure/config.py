"""
Product module configuration.

This module provides configuration specific to the product management module,
including image processing, AI analysis, and product validation settings.
"""

from typing import Any

from pydantic import Field

from infrastructure.config.base_config import (
    BaseModuleConfig,
    DatabaseMixin,
    ExternalServiceMixin,
)


class ProductModuleConfig(BaseModuleConfig, DatabaseMixin, ExternalServiceMixin):
    """
    Configuration for the product management module.

    This configuration includes product validation, image processing,
    AI analysis settings, and product-specific business rules.
    """

    module_name: str = Field(default="product", description="Product module identifier")

    # Override database URL with default for product module
    database_url: str = Field(
        default="postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5432/intellipost_dev",
        description="Database connection URL for product module",
    )

    # Image processing configuration
    max_image_size_mb: int = Field(
        default=10, description="Maximum product image size in MB"
    )
    allowed_image_formats: list[str] = Field(
        default=["jpg", "jpeg", "png", "webp"],
        description="Allowed product image formats",
    )
    image_quality: int = Field(
        default=85, description="Image compression quality (1-100)"
    )
    thumbnail_sizes: list[tuple[int, int]] = Field(
        default=[(150, 150), (300, 300), (600, 600)],
        description="Thumbnail sizes to generate",
    )

    # AI analysis configuration
    ai_analysis_enabled: bool = Field(
        default=True, description="Enable AI analysis for products"
    )
    ai_confidence_threshold: float = Field(
        default=0.8, description="Minimum AI confidence threshold"
    )
    ai_timeout_seconds: int = Field(
        default=60, description="AI analysis timeout in seconds"
    )

    # Business rules configuration
    price_validation_enabled: bool = Field(
        default=True, description="Enable price validation"
    )
    min_price: float = Field(default=0.01, description="Minimum allowed product price")
    max_price: float = Field(
        default=100000.00, description="Maximum allowed product price"
    )

    # Content validation
    title_min_length: int = Field(default=5, description="Minimum product title length")
    title_max_length: int = Field(
        default=100, description="Maximum product title length"
    )
    description_min_length: int = Field(
        default=20, description="Minimum product description length"
    )
    description_max_length: int = Field(
        default=2000, description="Maximum product description length"
    )

    # Inventory management
    low_stock_threshold: int = Field(
        default=10, description="Low stock alert threshold"
    )
    auto_deactivate_out_of_stock: bool = Field(
        default=False, description="Auto-deactivate products when out of stock"
    )

    # Performance optimization
    cache_product_data: bool = Field(
        default=True, description="Enable product data caching"
    )
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")

    class Config(BaseModuleConfig.Config):
        """Pydantic configuration for product module."""

        env_prefix = "INTELLIPOST_PRODUCT_"

    def get_module_specific_settings(self) -> dict[str, Any]:
        """Get product module specific settings."""
        return {
            "image_processing": {
                "max_size_mb": self.max_image_size_mb,
                "allowed_formats": self.allowed_image_formats,
                "quality": self.image_quality,
                "thumbnail_sizes": self.thumbnail_sizes,
            },
            "ai_analysis": {
                "enabled": self.ai_analysis_enabled,
                "confidence_threshold": self.ai_confidence_threshold,
                "timeout_seconds": self.ai_timeout_seconds,
            },
            "business_rules": {
                "price_validation_enabled": self.price_validation_enabled,
                "min_price": self.min_price,
                "max_price": self.max_price,
            },
            "content_validation": {
                "title_min_length": self.title_min_length,
                "title_max_length": self.title_max_length,
                "description_min_length": self.description_min_length,
                "description_max_length": self.description_max_length,
            },
            "inventory": {
                "low_stock_threshold": self.low_stock_threshold,
                "auto_deactivate_out_of_stock": self.auto_deactivate_out_of_stock,
            },
            "performance": {
                "cache_product_data": self.cache_product_data,
                "cache_ttl_seconds": self.cache_ttl_seconds,
            },
        }


# Global product module configuration instance
product_config = ProductModuleConfig()
