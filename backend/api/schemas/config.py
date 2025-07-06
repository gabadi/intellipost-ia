"""Configuration API schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class FeatureFlagsResponse(BaseModel):
    """Feature flags response schema."""

    registration_enabled: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "registration_enabled": True,
            }
        }
    )


class ConfigValidationResponse(BaseModel):
    """Configuration validation response schema."""

    environment: str
    is_production_ready: bool
    validations: dict[str, Any]
    warnings: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "environment": "development",
                "is_production_ready": False,
                "validations": {
                    "database_connection": True,
                    "required_secrets": False,
                    "redis_connection": True,
                },
                "warnings": [
                    "MercadoLibre app ID not configured",
                    "MercadoLibre app secret not configured",
                ],
            }
        }
    )
