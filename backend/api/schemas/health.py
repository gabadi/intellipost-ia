"""Health check API schemas."""

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
