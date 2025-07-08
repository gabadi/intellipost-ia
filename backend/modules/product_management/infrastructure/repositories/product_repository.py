"""
SQLAlchemy implementation of ProductRepositoryProtocol.

This module provides PostgreSQL persistence for Product entities using SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.ports.product_repository_protocol import (
    ProductRepositoryProtocol,
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
        resolution_width: int,
        resolution_height: int,
        is_primary: bool = False,
        processing_metadata: dict | None = None,
    ) -> ProductImageModel:
        """Create a new product image."""
        image_model = ProductImageModel.from_upload_data(
            product_id=product_id,
            original_filename=original_filename,
            s3_key=s3_key,
            s3_url=s3_url,
            file_size_bytes=file_size_bytes,
            file_format=file_format,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            is_primary=is_primary,
            processing_metadata=processing_metadata,
        )

        self.session.add(image_model)
        await self.session.flush()
        await self.session.refresh(image_model)
        return image_model

    async def get_product_images(self, product_id: UUID) -> list[ProductImageModel]:
        """Get all images for a product."""
        stmt = (
            select(ProductImageModel)
            .where(ProductImageModel.product_id == product_id)
            .order_by(
                ProductImageModel.is_primary.desc(), ProductImageModel.created_at.asc()
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
