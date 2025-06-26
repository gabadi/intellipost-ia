"""
Comprehensive health checker for IntelliPost AI backend.

This module provides detailed health checks for database, external services,
and system components to ensure proper deployment and monitoring.
"""

import time
from typing import Any

import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.logging import get_structured_logger
from infrastructure.config.settings import Settings


class HealthChecker:
    """
    Comprehensive health checker for application components.

    This class provides detailed health checks for various system components
    including database, external services, and system resources.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_structured_logger("health")
        self._start_time = time.time()

    async def check_database(self, session: AsyncSession) -> dict[str, Any]:
        """
        Check database connectivity and performance.

        Args:
            session: Database session

        Returns:
            Dictionary containing database health status
        """
        try:
            start_time = time.time()

            # Simple connectivity check
            result = await session.execute(text("SELECT 1"))
            result.fetchone()

            # Connection pool info (if available)
            pool_info = {}
            try:
                if hasattr(session.bind, "pool") and session.bind.pool is not None:  # type: ignore[attr-defined]
                    pool = session.bind.pool  # type: ignore[attr-defined]
                    pool_info = {
                        "pool_size": getattr(pool, "size", lambda: 0)(),
                        "checked_out": getattr(pool, "checkedout", lambda: 0)(),
                        "overflow": getattr(pool, "overflow", lambda: 0)(),
                        "invalid": getattr(pool, "invalid", lambda: 0)(),
                    }
            except AttributeError:
                pool_info = {"info": "Pool information not available"}

            response_time = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "pool_info": pool_info,
                "database_url": self.settings.database_url.split("@")[1]
                if "@" in self.settings.database_url
                else "hidden",
            }

        except Exception as e:
            self.logger.error(
                "Database health check failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def check_external_services(self) -> dict[str, Any]:
        """
        Check external service connectivity.

        Returns:
            Dictionary containing external service health status
        """
        services = {}

        # Check MercadoLibre API (if configured)
        if self.settings.mercadolibre_client_id:
            services["mercadolibre"] = await self._check_mercadolibre()

        # Check S3/MinIO (if configured)
        if self.settings.s3_endpoint_url:
            services["s3_storage"] = await self._check_s3()

        return services

    async def _check_mercadolibre(self) -> dict[str, Any]:
        """Check MercadoLibre API connectivity."""
        try:
            import httpx

            start_time = time.time()

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.mercadolibre.com/sites")

            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                }
            else:
                return {
                    "status": "degraded",
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def _check_s3(self) -> dict[str, Any]:
        """Check S3/MinIO connectivity."""
        try:
            try:
                import boto3  # type: ignore[import-untyped]
            except ImportError:
                return {
                    "status": "unavailable",
                    "error": "boto3 not installed",
                    "error_type": "ImportError",
                }

            start_time = time.time()

            # Create S3 client
            s3_client = boto3.client(
                "s3",
                endpoint_url=self.settings.s3_endpoint_url,
                aws_access_key_id=self.settings.s3_access_key,
                aws_secret_access_key=self.settings.s3_secret_key,
                region_name=self.settings.s3_region,
            )

            # List buckets (lightweight operation)
            response = s3_client.list_buckets()

            response_time = (time.time() - start_time) * 1000

            bucket_count = len(response.get("Buckets", []))

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "bucket_count": bucket_count,
                "endpoint": self.settings.s3_endpoint_url,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def check_system_resources(self) -> dict[str, Any]:
        """
        Check system resource usage.

        Returns:
            Dictionary containing system resource information
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                "status": "healthy",
                "cpu": {"usage_percent": cpu_percent, "count": psutil.cpu_count()},
                "memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "used_percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2),
                },
                "process": {
                    "memory_mb": round(process_memory.rss / 1024 / 1024, 2),
                    "pid": process.pid,
                    "threads": process.num_threads(),
                },
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    def get_application_info(self) -> dict[str, Any]:
        """
        Get application information.

        Returns:
            Dictionary containing application metadata
        """
        uptime_seconds = time.time() - self._start_time

        return {
            "name": "IntelliPost AI Backend",
            "version": "0.1.0",
            "environment": self.settings.environment,
            "debug": self.settings.debug,
            "uptime_seconds": round(uptime_seconds, 2),
            "python_version": __import__("sys").version.split()[0],
            "log_level": self.settings.log_level,
            "log_format": self.settings.log_format,
        }

    async def perform_full_health_check(
        self, session: AsyncSession | None = None
    ) -> dict[str, Any]:
        """
        Perform comprehensive health check.

        Args:
            session: Optional database session

        Returns:
            Complete health check report
        """
        start_time = time.time()

        health_report = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "checks": {},
            "application": self.get_application_info(),
        }

        # Check system resources
        health_report["checks"]["system"] = self.check_system_resources()

        # Check database if session provided
        if session:
            health_report["checks"]["database"] = await self.check_database(session)

        # Check external services
        health_report["checks"][
            "external_services"
        ] = await self.check_external_services()

        # Determine overall status
        all_checks = []

        # Collect statuses from all checks
        for _check_category, check_result in health_report["checks"].items():
            if isinstance(check_result, dict):
                if "status" in check_result:
                    all_checks.append(check_result["status"])
                else:
                    # For nested checks (like external_services)
                    for _service_name, service_check in check_result.items():
                        if (
                            isinstance(service_check, dict)
                            and "status" in service_check
                        ):
                            all_checks.append(service_check["status"])

        # Determine overall status
        if "unhealthy" in all_checks:
            health_report["overall_status"] = "unhealthy"
        elif "degraded" in all_checks:
            health_report["overall_status"] = "degraded"
        else:
            health_report["overall_status"] = "healthy"

        # Add timing information
        health_report["check_duration_ms"] = round((time.time() - start_time) * 1000, 2)

        # Log health check
        self.logger.info(
            "Health check completed",
            overall_status=health_report["overall_status"],
            duration_ms=health_report["check_duration_ms"],
            checks_performed=len(all_checks),
        )

        return health_report


# Global health checker instance
health_checker: HealthChecker | None = None


def get_health_checker(settings: Settings) -> HealthChecker:
    """
    Get or create health checker instance.

    Args:
        settings: Application settings

    Returns:
        HealthChecker instance
    """
    global health_checker
    if health_checker is None:
        health_checker = HealthChecker(settings)
    return health_checker
