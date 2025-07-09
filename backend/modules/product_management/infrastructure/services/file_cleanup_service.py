"""
File cleanup service for managing temporary files and orphaned storage.

This module provides cleanup mechanisms for uploaded files, failed uploads,
and orphaned files that are no longer referenced in the database.
"""
# type: ignore[reportUnknownMemberType,reportUnknownVariableType,reportUnknownArgumentType]

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.logging import get_logger
from modules.product_management.infrastructure.models.product_model import (
    ProductImageModel,
)
from modules.product_management.infrastructure.services.file_storage_service import (
    FileStorageService,
)

logger = get_logger(__name__)


class FileCleanupService:
    """Service for cleaning up temporary and orphaned files."""

    def __init__(
        self,
        file_storage_service: FileStorageService,
        session: AsyncSession,
    ):
        self.file_storage = file_storage_service
        self.session = session
        self.temp_file_retention_hours = 24  # Keep temp files for 24 hours
        self.orphaned_file_retention_hours = 168  # Keep orphaned files for 7 days

    async def cleanup_temporary_files(self, temp_dir: str | Path) -> dict[str, Any]:
        """
        Clean up temporary uploaded files.

        Args:
            temp_dir: Directory containing temporary files

        Returns:
            dict: Cleanup statistics
        """
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            logger.info(f"Temporary directory {temp_dir} does not exist")
            return {"cleaned": 0, "total_size_bytes": 0, "errors": []}

        cleaned_count = 0
        total_size = 0
        errors: list[str] = []
        cutoff_time = datetime.now(UTC) - timedelta(
            hours=self.temp_file_retention_hours
        )

        try:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    try:
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(
                            file_path.stat().st_mtime, tz=UTC
                        )

                        if file_mtime < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_count += 1
                            total_size += file_size
                            logger.debug(f"Cleaned temporary file: {file_path}")

                    except Exception as e:
                        error_msg = f"Failed to clean {file_path}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)

            logger.info(
                f"Temporary file cleanup completed: {cleaned_count} files, "
                f"{total_size} bytes, {len(errors)} errors"
            )

            return {
                "cleaned": cleaned_count,
                "total_size_bytes": total_size,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Error during temporary file cleanup: {e}")
            return {"cleaned": 0, "total_size_bytes": 0, "errors": [str(e)]}

    async def find_orphaned_files(
        self, user_id: UUID | None = None
    ) -> list[dict[str, Any]]:
        """
        Find files in storage that are not referenced in the database.

        Args:
            user_id: Optional user ID to limit search scope

        Returns:
            list[dict]: List of orphaned file information
        """
        try:
            # Get all S3 files
            prefix = f"products/{user_id}/" if user_id else "products/"
            s3_files = await self.file_storage.list_files_by_prefix(prefix)

            # Get all database file references
            stmt = select(ProductImageModel.s3_key)
            if user_id:
                # Join with products to filter by user
                from modules.product_management.infrastructure.models.product_model import (
                    ProductModel,
                )

                stmt = stmt.join(
                    ProductModel, ProductImageModel.product_id == ProductModel.id
                ).where(ProductModel.user_id == user_id)

            result = await self.session.execute(stmt)
            referenced_keys = {row[0] for row in result.fetchall()}

            # Find orphaned files
            orphaned_files: list[dict[str, Any]] = []
            cutoff_time = datetime.now(UTC) - timedelta(
                hours=self.orphaned_file_retention_hours
            )

            for s3_file in s3_files:
                if s3_file["key"] not in referenced_keys:
                    # Check if file is old enough to be considered orphaned
                    file_time = datetime.fromisoformat(
                        s3_file["last_modified"].replace("Z", "+00:00")
                    )
                    if file_time < cutoff_time:
                        orphaned_files.append(
                            {
                                "key": s3_file["key"],
                                "size": s3_file["size"],
                                "last_modified": s3_file["last_modified"],
                                "age_hours": (
                                    datetime.now(UTC) - file_time
                                ).total_seconds()
                                / 3600,
                            }
                        )

            logger.info(f"Found {len(orphaned_files)} orphaned files")
            return orphaned_files

        except Exception as e:
            logger.error(f"Error finding orphaned files: {e}")
            raise ValueError(f"Failed to find orphaned files: {e}") from e

    async def cleanup_orphaned_files(
        self,
        user_id: UUID | None = None,
        dry_run: bool = False,
        max_files: int = 100,
    ) -> dict[str, Any]:
        """
        Clean up orphaned files from storage.

        Args:
            user_id: Optional user ID to limit cleanup scope
            dry_run: If True, only report what would be cleaned without deleting
            max_files: Maximum number of files to clean in one operation

        Returns:
            dict: Cleanup statistics
        """
        try:
            orphaned_files = await self.find_orphaned_files(user_id)

            if not orphaned_files:
                logger.info("No orphaned files found")
                return {
                    "cleaned": 0,
                    "total_size_bytes": 0,
                    "errors": [],
                    "dry_run": dry_run,
                }

            # Limit the number of files to process
            files_to_clean = orphaned_files[:max_files]

            cleaned_count = 0
            total_size = 0
            errors: list[str] = []

            for file_info in files_to_clean:
                try:
                    if not dry_run:
                        success = await self.file_storage.delete_file(file_info["key"])
                        if success:
                            cleaned_count += 1
                            total_size += file_info["size"]
                        else:
                            errors.append(f"Failed to delete {file_info['key']}")
                    else:
                        # Dry run - just count what would be cleaned
                        cleaned_count += 1
                        total_size += file_info["size"]

                except Exception as e:
                    error_msg = f"Error cleaning {file_info['key']}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            action = "Would clean" if dry_run else "Cleaned"
            logger.info(
                f"{action} {cleaned_count} orphaned files, "
                f"{total_size} bytes, {len(errors)} errors"
            )

            return {
                "cleaned": cleaned_count,
                "total_size_bytes": total_size,
                "errors": errors,
                "dry_run": dry_run,
                "remaining_orphaned": len(orphaned_files) - len(files_to_clean),
            }

        except Exception as e:
            logger.error(f"Error during orphaned file cleanup: {e}")
            raise ValueError(f"Orphaned file cleanup failed: {e}") from e

    async def cleanup_failed_uploads(self, age_hours: int = 1) -> dict[str, Any]:
        """
        Clean up files from failed upload attempts.

        Args:
            age_hours: Minimum age in hours for files to be considered failed uploads

        Returns:
            dict: Cleanup statistics
        """
        try:
            cutoff_time = datetime.now(UTC) - timedelta(hours=age_hours)

            # Find product image records that might represent failed uploads
            # (files that exist in S3 but products are still in 'uploading' status for too long)
            from modules.product_management.infrastructure.models.product_model import (
                ProductModel,
            )

            stmt = (
                select(ProductImageModel.s3_key, ProductImageModel.file_size_bytes)
                .join(ProductModel, ProductImageModel.product_id == ProductModel.id)
                .where(
                    ProductModel.status == "uploading",
                    ProductModel.created_at < cutoff_time,
                )
            )

            result = await self.session.execute(stmt)
            failed_upload_files = list(result.fetchall())

            cleaned_count = 0
            total_size = 0
            errors: list[str] = []

            for s3_key, file_size in failed_upload_files:
                try:
                    # Verify file exists in S3 before trying to delete
                    if await self.file_storage.file_exists(s3_key):
                        success = await self.file_storage.delete_file(s3_key)
                        if success:
                            cleaned_count += 1
                            total_size += file_size
                        else:
                            errors.append(f"Failed to delete {s3_key}")

                except Exception as e:
                    error_msg = f"Error cleaning failed upload {s3_key}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            logger.info(
                f"Cleaned {cleaned_count} failed upload files, "
                f"{total_size} bytes, {len(errors)} errors"
            )

            return {
                "cleaned": cleaned_count,
                "total_size_bytes": total_size,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Error during failed upload cleanup: {e}")
            raise ValueError(f"Failed upload cleanup failed: {e}") from e

    async def get_storage_statistics(
        self, user_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Get storage usage statistics.

        Args:
            user_id: Optional user ID to get user-specific statistics

        Returns:
            dict: Storage statistics
        """
        try:
            # Get bucket usage
            bucket_stats = await self.file_storage.get_bucket_usage()

            # Get database statistics
            stmt = select(
                ProductImageModel.file_size_bytes,
                ProductImageModel.file_format,
                ProductImageModel.created_at,
            )

            if user_id:
                from modules.product_management.infrastructure.models.product_model import (
                    ProductModel,
                )

                stmt = stmt.join(
                    ProductModel, ProductImageModel.product_id == ProductModel.id
                ).where(ProductModel.user_id == user_id)

            result = await self.session.execute(stmt)
            db_files = list(result.fetchall())

            # Calculate statistics
            total_db_size = sum(row[0] for row in db_files)
            format_counts: dict[str, int] = {}
            for _, file_format, _ in db_files:
                format_counts[file_format] = format_counts.get(file_format, 0) + 1

            # Find orphaned files count
            orphaned_files: list[dict[str, Any]] = await self.find_orphaned_files(
                user_id
            )
            orphaned_size = sum(cast("int", file["size"]) for file in orphaned_files)

            return {
                "bucket_stats": bucket_stats,
                "database_files": len(db_files),
                "database_size_bytes": total_db_size,
                "database_size_mb": round(total_db_size / (1024 * 1024), 2),
                "format_distribution": format_counts,
                "orphaned_files": len(orphaned_files),
                "orphaned_size_bytes": orphaned_size,
                "orphaned_size_mb": round(orphaned_size / (1024 * 1024), 2),
                "user_id": str(user_id) if user_id else "all_users",
            }

        except Exception as e:
            logger.error(f"Error getting storage statistics: {e}")
            raise ValueError(f"Failed to get storage statistics: {e}") from e

    async def validate_file_integrity(
        self, user_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Validate that all database file references have corresponding S3 files.

        Args:
            user_id: Optional user ID to limit validation scope

        Returns:
            dict: Validation results
        """
        try:
            # Get all database file references
            stmt = select(
                ProductImageModel.id,
                ProductImageModel.s3_key,
                ProductImageModel.file_size_bytes,
            )

            if user_id:
                from modules.product_management.infrastructure.models.product_model import (
                    ProductModel,
                )

                stmt = stmt.join(
                    ProductModel, ProductImageModel.product_id == ProductModel.id
                ).where(ProductModel.user_id == user_id)

            result = await self.session.execute(stmt)
            db_files = list(result.fetchall())

            missing_files: list[dict[str, Any]] = []
            size_mismatches: list[dict[str, Any]] = []
            valid_files = 0

            for image_id, s3_key, expected_size in db_files:
                try:
                    file_metadata = await self.file_storage.get_file_metadata(s3_key)

                    if file_metadata is None:
                        missing_files.append(
                            {
                                "image_id": str(image_id),
                                "s3_key": s3_key,
                                "expected_size": expected_size,
                            }
                        )
                    elif file_metadata["size"] != expected_size:
                        size_mismatches.append(
                            {
                                "image_id": str(image_id),
                                "s3_key": s3_key,
                                "expected_size": expected_size,
                                "actual_size": file_metadata["size"],
                            }
                        )
                    else:
                        valid_files += 1

                except Exception as e:
                    logger.error(f"Error validating file {s3_key}: {e}")
                    missing_files.append(
                        {
                            "image_id": str(image_id),
                            "s3_key": s3_key,
                            "expected_size": expected_size,
                            "error": str(e),
                        }
                    )

            logger.info(
                f"File integrity validation completed: {valid_files} valid, "
                f"{len(missing_files)} missing, {len(size_mismatches)} size mismatches"
            )

            return {
                "total_files": len(db_files),
                "valid_files": valid_files,
                "missing_files": missing_files,
                "size_mismatches": size_mismatches,
                "user_id": str(user_id) if user_id else "all_users",
            }

        except Exception as e:
            logger.error(f"Error during file integrity validation: {e}")
            raise ValueError(f"File integrity validation failed: {e}") from e
