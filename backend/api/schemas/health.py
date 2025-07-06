"""Health check API schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: str
    version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00.000000",
                "version": "1.0.0",
            }
        }
    )


class DetailedHealthResponse(BaseModel):
    """Detailed health check response schema with service status."""

    status: str
    timestamp: str
    version: str
    services: dict[str, Any]
    ml_integration: dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00.000000",
                "version": "1.0.0",
                "services": {
                    "database": {"status": "healthy", "response_time_ms": 25},
                    "authentication": {"status": "healthy"},
                },
                "ml_integration": {
                    "status": "healthy",
                    "background_service": True,
                    "token_refresh_scheduler": True,
                    "active_connections": 5,
                },
            }
        }
    )
