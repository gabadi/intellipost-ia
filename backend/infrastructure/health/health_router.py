"""Health check API router."""

from datetime import UTC, datetime

from fastapi import APIRouter

from .health_schema import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring application status.

    Returns application health status, timestamp, and version information.
    This endpoint is used by monitoring systems and load balancers.
    """
    return HealthResponse(
        status="healthy", timestamp=datetime.now(UTC).isoformat(), version="1.0.0"
    )
