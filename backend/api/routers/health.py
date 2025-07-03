"""Health check API router."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response

from api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response) -> HealthResponse:
    """
    Health check endpoint for monitoring application status.

    Returns application health status, timestamp, and version information.
    This endpoint is used by monitoring systems and load balancers.
    """
    # Add CORS headers directly for testing
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return HealthResponse(
        status="healthy", timestamp=datetime.now(UTC).isoformat(), version="1.0.0"
    )
