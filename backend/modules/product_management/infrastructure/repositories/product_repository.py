"""
SQLAlchemy implementation of ProductRepositoryProtocol.

This module provides PostgreSQL persistence for Product entities using SQLAlchemy.
"""

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_image import ProductImage
from modules.product_management.domain.value_objects.product_image_metadata import (
    ProductImageMetadata,
)
from modules.product_management.domain.value_objects.product_image_resolution import (
    ProductImageResolution,
)
from modules.product_management.infrastructure.models.product_model import (
    ProductImageModel,
    ProductModel,
)


class SQLAlchemyProductRepository:
    """SQLAlchemy implementation of ProductRepositoryProtocol."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product: Product) -> Product:
        """Create a new product."""
        product_model = ProductModel.from_domain(product)
        self.session.add(product_model)
        await self.session.flush()
        await self.session.refresh(product_model)
        return product_model.to_domain()

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.images))
        )
        result = await self.session.execute(stmt)
        product_model = result.scalar_one_or_none()
        return product_model.to_domain() if product_model else None

    async def get_by_user_id(self, user_id: UUID) -> list[Product]:
        """Get all products for a user."""
        stmt = (
            select(ProductModel)
            .where(ProductModel.user_id == user_id)
            .options(selectinload(ProductModel.images))
            .order_by(ProductModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        product_models = result.scalars().all()
        return [product_model.to_domain() for product_model in product_models]

    async def update(self, product: Product) -> Product:
        """Update an existing product."""
        stmt = select(ProductModel).where(ProductModel.id == product.id)
        result = await self.session.execute(stmt)
        product_model = result.scalar_one()

        product_model.update_from_domain(product)
        await self.session.flush()
        await self.session.refresh(product_model)
        return product_model.to_domain()

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.session.execute(stmt)
        product_model = result.scalar_one_or_none()

        if product_model:
            await self.session.delete(product_model)
            await self.session.flush()
            return True
        return False

    async def create_product_image(
        self,
        product_id: UUID,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        file_size_bytes: int,
        file_format: str,
        resolution: ProductImageResolution,
        is_primary: bool = False,
        metadata: ProductImageMetadata | None = None,
    ) -> ProductImage:
        """Create a new product image."""
        # Create domain entity first
        image_id = uuid4()
        image = ProductImage.create_from_upload(
            id=image_id,
            product_id=product_id,
            original_filename=original_filename,
            s3_key=s3_key,
            s3_url=s3_url,
            file_size_bytes=file_size_bytes,
            file_format=file_format,
            resolution=resolution,
            is_primary=is_primary,
            metadata=metadata,
        )

        # Convert to model and persist
        image_model = ProductImageModel.from_domain(image)
        self.session.add(image_model)
        await self.session.flush()
        await self.session.refresh(image_model)
        
        # Return domain entity
        return image_model.to_domain()

    async def get_product_images(self, product_id: UUID) -> list[ProductImage]:
        """Get all images for a product."""
        stmt = (
            select(ProductImageModel)
            .where(ProductImageModel.product_id == product_id)
            .order_by(
                ProductImageModel.is_primary.desc(), ProductImageModel.created_at.asc()
            )
        )
        result = await self.session.execute(stmt)
        image_models = result.scalars().all()
        return [image_model.to_domain() for image_model in image_models]

    async def get_product_image_by_id(self, image_id: UUID) -> ProductImage | None:
        """Get a specific product image by ID."""
        stmt = select(ProductImageModel).where(ProductImageModel.id == image_id)
        result = await self.session.execute(stmt)
        image_model = result.scalar_one_or_none()
        return image_model.to_domain() if image_model else None

    async def update_product_image(self, image: ProductImage) -> ProductImage:
        """Update an existing product image."""
        stmt = select(ProductImageModel).where(ProductImageModel.id == image.id)
        result = await self.session.execute(stmt)
        image_model = result.scalar_one()

        # Update model from domain entity
        updated_model = ProductImageModel.from_domain(image)
        image_model.original_filename = updated_model.original_filename
        image_model.s3_key = updated_model.s3_key
        image_model.s3_url = updated_model.s3_url
        image_model.original_s3_url = updated_model.original_s3_url
        image_model.processed_s3_url = updated_model.processed_s3_url
        image_model.file_size_bytes = updated_model.file_size_bytes
        image_model.file_format = updated_model.file_format
        image_model.resolution_width = updated_model.resolution_width
        image_model.resolution_height = updated_model.resolution_height
        image_model.is_primary = updated_model.is_primary
        image_model.processing_metadata = updated_model.processing_metadata
        image_model.updated_at = updated_model.updated_at
        image_model.processed_at = updated_model.processed_at

        await self.session.flush()
        await self.session.refresh(image_model)
        return image_model.to_domain()

    async def set_primary_image(self, product_id: UUID, image_id: UUID) -> bool:
        """Set a specific image as primary for a product."""
        try:
            # Start transaction
            async with self.session.begin():
                # First, unset all primary flags for this product
                stmt_unset = (
                    select(ProductImageModel)
                    .where(ProductImageModel.product_id == product_id)
                    .with_for_update()
                )
                result = await self.session.execute(stmt_unset)
                images = result.scalars().all()

                for image in images:
                    image.is_primary = False

                # Set the specific image as primary
                stmt_set = (
                    select(ProductImageModel)
                    .where(
                        ProductImageModel.product_id == product_id,
                        ProductImageModel.id == image_id,
                    )
                    .with_for_update()
                )
                result = await self.session.execute(stmt_set)
                target_image = result.scalar_one_or_none()

                if target_image:
                    target_image.is_primary = True
                    await self.session.flush()
                    return True
                return False

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to set primary image: {e}") from e

    async def delete_product_image(self, image_id: UUID) -> bool:
        """Delete a product image by ID."""
        try:
            stmt = select(ProductImageModel).where(ProductImageModel.id == image_id)
            result = await self.session.execute(stmt)
            image = result.scalar_one_or_none()

            if image:
                await self.session.delete(image)
                await self.session.flush()
                return True
            return False

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to delete product image: {e}") from e

    async def get_products_by_status(
        self,
        status: str,
        user_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Product]:
        """Get products by status with optional user filter."""
        stmt = (
            select(ProductModel)
            .where(ProductModel.status == status)
            .options(selectinload(ProductModel.images))
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if user_id:
            stmt = stmt.where(ProductModel.user_id == user_id)

        result = await self.session.execute(stmt)
        product_models = result.scalars().all()
        return [product_model.to_domain() for product_model in product_models]

    async def count_products_by_user(self, user_id: UUID) -> int:
        """Count total products for a user."""
        from sqlalchemy import func

        stmt = select(func.count(ProductModel.id)).where(
            ProductModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_products_with_pagination(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
    ) -> tuple[list[Product], int]:
        """Get products with pagination and optional status filter."""
        offset = (page - 1) * page_size

        # Build base query
        stmt = (
            select(ProductModel)
            .where(ProductModel.user_id == user_id)
            .options(selectinload(ProductModel.images))
            .order_by(ProductModel.created_at.desc())
        )

        # Add status filter if provided
        if status_filter:
            stmt = stmt.where(ProductModel.status == status_filter)

        # Get total count
        count_stmt = select(func.count(ProductModel.id)).where(
            ProductModel.user_id == user_id
        )
        if status_filter:
            count_stmt = count_stmt.where(ProductModel.status == status_filter)

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Get paginated results
        paginated_stmt = stmt.limit(page_size).offset(offset)
        result = await self.session.execute(paginated_stmt)
        product_models = result.scalars().all()
        products = [product_model.to_domain() for product_model in product_models]

        return products, total_count

    async def update_product_status(
        self, product_id: UUID, new_status: str, processing_error: str | None = None
    ) -> Product | None:
        """Update product status with optional error message."""
        try:
            async with self.session.begin():
                stmt = (
                    select(ProductModel)
                    .where(ProductModel.id == product_id)
                    .with_for_update()
                )
                result = await self.session.execute(stmt)
                product_model = result.scalar_one_or_none()

                if product_model:
                    from datetime import UTC, datetime

                    product_model.status = new_status
                    product_model.updated_at = datetime.now(UTC)

                    # Update processing timestamps based on status
                    if new_status == "processing":
                        product_model.processing_started_at = datetime.now(UTC)
                        product_model.processing_error = None
                    elif new_status in ["ready", "published"]:
                        product_model.processing_completed_at = datetime.now(UTC)
                        product_model.processing_error = None
                    elif new_status == "failed":
                        product_model.processing_completed_at = datetime.now(UTC)
                        product_model.processing_error = processing_error

                    await self.session.flush()
                    await self.session.refresh(product_model)
                    return product_model.to_domain()
                return None

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to update product status: {e}") from e

    async def bulk_update_image_metadata(
        self, product_id: UUID, image_updates: list[dict]
    ) -> list[ProductImageModel]:
        """Bulk update image metadata for a product."""
        try:
            async with self.session.begin():
                updated_images = []

                for update in image_updates:
                    image_id = update.get("image_id")
                    if not image_id:
                        continue

                    stmt = (
                        select(ProductImageModel)
                        .where(
                            ProductImageModel.id == image_id,
                            ProductImageModel.product_id == product_id,
                        )
                        .with_for_update()
                    )
                    result = await self.session.execute(stmt)
                    image = result.scalar_one_or_none()

                    if image:
                        # Update allowed fields
                        if "is_primary" in update:
                            image.is_primary = update["is_primary"]
                        if "processing_metadata" in update:
                            image.processing_metadata = update["processing_metadata"]
                        if "processed_s3_url" in update:
                            image.processed_s3_url = update["processed_s3_url"]
                            from datetime import UTC, datetime

                            image.processed_at = datetime.now(UTC)

                        updated_images.append(image)

                await self.session.flush()
                return updated_images

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to bulk update image metadata: {e}") from e

    async def get_product_with_images_for_update(
        self, product_id: UUID
    ) -> Product | None:
        """Get product with row-level lock for safe concurrent updates."""
        try:
            stmt = (
                select(ProductModel)
                .where(ProductModel.id == product_id)
                .options(selectinload(ProductModel.images))
                .with_for_update()
            )
            result = await self.session.execute(stmt)
            product_model = result.scalar_one_or_none()
            return product_model.to_domain() if product_model else None

        except Exception as e:
            raise ValueError(f"Failed to get product for update: {e}") from e
