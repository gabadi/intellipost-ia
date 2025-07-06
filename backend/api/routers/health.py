"""Health check API router."""

import time
from datetime import UTC, datetime

from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.health import HealthResponse, DetailedHealthResponse
from infrastructure.database import get_database_session

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response) -> HealthResponse:
    """
    Basic health check endpoint for monitoring application status.

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


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    response: Response, 
    db_session: AsyncSession = Depends(get_database_session)
) -> DetailedHealthResponse:
    """
    Detailed health check endpoint with service status information.

    Returns comprehensive health status including database, ML services,
    and background task status. Used for operational monitoring.
    """
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    timestamp = datetime.now(UTC).isoformat()
    services = {}
    ml_integration = None
    overall_status = "healthy"

    # Check database connectivity
    try:
        from sqlalchemy import text
        start_time = time.time()
        await db_session.execute(text("SELECT 1"))
        response_time = int((time.time() - start_time) * 1000)
        services["database"] = {
            "status": "healthy",
            "response_time_ms": response_time
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check authentication service
    try:
        from modules.user_management.infrastructure.services.jose_jwt_service import JoseJWTService
        from infrastructure.config.settings import settings
        
        jwt_service = JoseJWTService(
            secret_key=settings.user_jwt_secret_key,
            algorithm=settings.user_jwt_algorithm,
            access_token_expire_minutes=settings.user_jwt_access_token_expire_minutes,
            refresh_token_expire_days=settings.user_jwt_refresh_token_expire_days,
        )
        
        # Test JWT service by creating a test token
        test_token = jwt_service.create_access_token({"test": "user"})
        if test_token:
            services["authentication"] = {"status": "healthy"}
        else:
            services["authentication"] = {"status": "unhealthy", "error": "Token generation failed"}
            overall_status = "degraded"
    except Exception as e:
        services["authentication"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check ML integration status
    try:
        from modules.user_management.infrastructure.services.ml_background_tasks import get_ml_background_status
        
        ml_status = await get_ml_background_status()
        ml_integration = {
            "status": "healthy" if ml_status.get("service_running") else "stopped",
            "background_service": ml_status.get("service_running", False),
            "database_connected": ml_status.get("database_connected", False),
            "token_refresh_scheduler": ml_status.get("token_refresh_scheduler") is not None,
        }
        
        # Add active connections count if available
        if ml_status.get("token_refresh_scheduler"):
            ml_integration["scheduler_status"] = ml_status["token_refresh_scheduler"]

    except Exception as e:
        ml_integration = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=timestamp,
        version="1.0.0",
        services=services,
        ml_integration=ml_integration
    )
