"""
SQLAlchemy Content Repository implementation.

This module provides the repository implementation for content generation
using SQLAlchemy ORM.
"""

import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.content_generation.domain.entities import GeneratedContent
from modules.content_generation.domain.exceptions import (
    EntityNotFoundError,
    RepositoryError,
)
from modules.content_generation.infrastructure.models.generated_content_model import (
    GeneratedContentModel,
)
from shared.migration.value_object_migration import (
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
)

logger = logging.getLogger(__name__)


class SQLAlchemyContentRepository:
    """
    SQLAlchemy implementation of the content repository.

    This repository provides persistent storage for generated content
    using PostgreSQL with SQLAlchemy ORM.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def save_generated_content(
        self,
        content: GeneratedContent,
    ) -> GeneratedContent:
        """
        Save generated content to the repository.

        Args:
            content: Generated content to save

        Returns:
            GeneratedContent: Saved content entity

        Raises:
            RepositoryError: If save operation fails
        """
        try:
            # Convert domain entity to model
            content_model = self._domain_to_model(content)

            # Add to session
            self.session.add(content_model)
            await self.session.commit()
            await self.session.refresh(content_model)

            # Convert back to domain entity
            saved_content = self._model_to_domain(content_model)

            logger.info(f"Saved generated content: {saved_content.id}")
            return saved_content

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving generated content: {e}")
            raise RepositoryError(
                f"Failed to save generated content: {str(e)}",
                operation="save",
                entity_type="GeneratedContent",
            ) from e

    async def get_generated_content(
        self,
        content_id: UUID,
    ) -> GeneratedContent | None:
        """
        Get generated content by ID.

        Args:
            content_id: Content ID to retrieve

        Returns:
            GeneratedContent or None if not found

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Query for content
            stmt = select(GeneratedContentModel).where(
                GeneratedContentModel.id == content_id
            )

            result = await self.session.execute(stmt)
            content_model = result.scalar_one_or_none()

            if content_model is None:
                return None

            # Convert to domain entity
            content = self._model_to_domain(content_model)

            logger.debug(f"Retrieved generated content: {content_id}")
            return content

        except Exception as e:
            logger.error(f"Error retrieving generated content {content_id}: {e}")
            raise RepositoryError(
                f"Failed to retrieve generated content: {str(e)}",
                operation="get",
                entity_type="GeneratedContent",
            ) from e

    async def get_content_by_product_id(
        self,
        product_id: UUID,
    ) -> GeneratedContent | None:
        """
        Get generated content by product ID.

        Args:
            product_id: Product ID to search for

        Returns:
            GeneratedContent or None if not found

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Query for latest content version for product
            stmt = (
                select(GeneratedContentModel)
                .where(GeneratedContentModel.product_id == product_id)
                .order_by(desc(GeneratedContentModel.version))
                .limit(1)
            )

            result = await self.session.execute(stmt)
            content_model = result.scalar_one_or_none()

            if content_model is None:
                return None

            # Convert to domain entity
            content = self._model_to_domain(content_model)

            logger.debug(f"Retrieved content for product: {product_id}")
            return content

        except Exception as e:
            logger.error(f"Error retrieving content for product {product_id}: {e}")
            raise RepositoryError(
                f"Failed to retrieve content for product: {str(e)}",
                operation="get_by_product",
                entity_type="GeneratedContent",
            ) from e

    async def update_generated_content(
        self,
        content: GeneratedContent,
    ) -> GeneratedContent:
        """
        Update existing generated content.

        Args:
            content: Updated content entity

        Returns:
            GeneratedContent: Updated content entity

        Raises:
            RepositoryError: If update fails
        """
        try:
            # Find existing content
            stmt = select(GeneratedContentModel).where(
                GeneratedContentModel.id == content.id
            )

            result = await self.session.execute(stmt)
            content_model = result.scalar_one_or_none()

            if content_model is None:
                raise EntityNotFoundError(
                    f"Generated content not found: {content.id}",
                    entity_type="GeneratedContent",
                    entity_id=str(content.id),
                )

            # Update model fields
            self._update_model_from_domain(content_model, content)

            # Commit changes
            await self.session.commit()
            await self.session.refresh(content_model)

            # Convert back to domain entity
            updated_content = self._model_to_domain(content_model)

            logger.info(f"Updated generated content: {updated_content.id}")
            return updated_content

        except EntityNotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating generated content {content.id}: {e}")
            raise RepositoryError(
                f"Failed to update generated content: {str(e)}",
                operation="update",
                entity_type="GeneratedContent",
            ) from e

    async def delete_generated_content(
        self,
        content_id: UUID,
    ) -> bool:
        """
        Delete generated content by ID.

        Args:
            content_id: Content ID to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            # Find and delete content
            stmt = select(GeneratedContentModel).where(
                GeneratedContentModel.id == content_id
            )

            result = await self.session.execute(stmt)
            content_model = result.scalar_one_or_none()

            if content_model is None:
                return False

            # Delete content
            await self.session.delete(content_model)
            await self.session.commit()

            logger.info(f"Deleted generated content: {content_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting generated content {content_id}: {e}")
            raise RepositoryError(
                f"Failed to delete generated content: {str(e)}",
                operation="delete",
                entity_type="GeneratedContent",
            ) from e

    async def get_content_versions(
        self,
        product_id: UUID,
    ) -> list[GeneratedContent]:
        """
        Get all versions of content for a product.

        Args:
            product_id: Product ID to search for

        Returns:
            List of GeneratedContent entities, ordered by version

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Query for all versions of content for product
            stmt = (
                select(GeneratedContentModel)
                .where(GeneratedContentModel.product_id == product_id)
                .order_by(desc(GeneratedContentModel.version))
            )

            result = await self.session.execute(stmt)
            content_models = result.scalars().all()

            # Convert to domain entities
            content_versions = [
                self._model_to_domain(model) for model in content_models
            ]

            logger.debug(
                f"Retrieved {len(content_versions)} content versions for product: {product_id}"
            )
            return content_versions

        except Exception as e:
            logger.error(
                f"Error retrieving content versions for product {product_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to retrieve content versions: {str(e)}",
                operation="get_versions",
                entity_type="GeneratedContent",
            ) from e

    async def get_content_by_confidence_range(
        self,
        min_confidence: float,
        max_confidence: float,
        limit: int = 100,
    ) -> list[GeneratedContent]:
        """
        Get content within a confidence range.

        Args:
            min_confidence: Minimum confidence score
            max_confidence: Maximum confidence score
            limit: Maximum number of results

        Returns:
            List of GeneratedContent entities

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Query for content within confidence range
            stmt = (
                select(GeneratedContentModel)
                .where(
                    and_(
                        GeneratedContentModel.confidence_overall >= min_confidence,
                        GeneratedContentModel.confidence_overall <= max_confidence,
                    )
                )
                .order_by(desc(GeneratedContentModel.confidence_overall))
                .limit(limit)
            )

            result = await self.session.execute(stmt)
            content_models = result.scalars().all()

            # Convert to domain entities
            content_list = [self._model_to_domain(model) for model in content_models]

            logger.debug(
                f"Retrieved {len(content_list)} content items in confidence range {min_confidence}-{max_confidence}"
            )
            return content_list

        except Exception as e:
            logger.error(f"Error retrieving content by confidence range: {e}")
            raise RepositoryError(
                f"Failed to retrieve content by confidence range: {str(e)}",
                operation="get_by_confidence",
                entity_type="GeneratedContent",
            ) from e

    async def get_content_by_category(
        self,
        category_id: str,
        limit: int = 100,
    ) -> list[GeneratedContent]:
        """
        Get content by category.

        Args:
            category_id: MercadoLibre category ID
            limit: Maximum number of results

        Returns:
            List of GeneratedContent entities

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Query for content by category
            stmt = (
                select(GeneratedContentModel)
                .where(GeneratedContentModel.ml_category_id == category_id)
                .order_by(desc(GeneratedContentModel.generated_at))
                .limit(limit)
            )

            result = await self.session.execute(stmt)
            content_models = result.scalars().all()

            # Convert to domain entities
            content_list = [self._model_to_domain(model) for model in content_models]

            logger.debug(
                f"Retrieved {len(content_list)} content items for category: {category_id}"
            )
            return content_list

        except Exception as e:
            logger.error(f"Error retrieving content by category {category_id}: {e}")
            raise RepositoryError(
                f"Failed to retrieve content by category: {str(e)}",
                operation="get_by_category",
                entity_type="GeneratedContent",
            ) from e

    def _domain_to_model(self, content: GeneratedContent) -> GeneratedContentModel:
        """Convert domain entity to SQLAlchemy model."""
        return GeneratedContentModel(
            id=content.id,
            product_id=content.product_id,
            title=content.title,
            description=content.description,
            ml_category_id=content.ml_category_id,
            ml_category_name=content.ml_category_name,
            ml_title=content.ml_title,
            ml_price=content.ml_price,
            ml_currency_id=content.ml_currency_id,
            ml_available_quantity=content.ml_available_quantity,
            ml_buying_mode=content.ml_buying_mode,
            ml_condition=content.ml_condition,
            ml_listing_type_id=content.ml_listing_type_id,
            ml_attributes=content.ml_attributes.to_dict(),
            ml_sale_terms=content.ml_sale_terms.to_dict(),
            ml_shipping=content.ml_shipping.to_dict(),
            confidence_overall=content.confidence_overall,
            confidence_breakdown=content.confidence_breakdown,
            ai_provider=content.ai_provider,
            ai_model_version=content.ai_model_version,
            generation_time_ms=content.generation_time_ms,
            version=content.version,
            generated_at=content.generated_at,
            updated_at=content.updated_at,
        )

    def _model_to_domain(self, model: GeneratedContentModel) -> GeneratedContent:
        """Convert SQLAlchemy model to domain entity."""
        return GeneratedContent(
            id=model.id,
            product_id=model.product_id,
            title=model.title,
            description=model.description,
            ml_category_id=model.ml_category_id,
            ml_category_name=model.ml_category_name,
            ml_title=model.ml_title,
            ml_price=model.ml_price,
            ml_currency_id=model.ml_currency_id,
            ml_available_quantity=model.ml_available_quantity,
            ml_buying_mode=model.ml_buying_mode,
            ml_condition=model.ml_condition,
            ml_listing_type_id=model.ml_listing_type_id,
            ml_attributes=safe_migrate_ml_attributes(model.ml_attributes),
            ml_sale_terms=safe_migrate_ml_sale_terms(model.ml_sale_terms),
            ml_shipping=safe_migrate_ml_shipping(model.ml_shipping),
            confidence_overall=float(model.confidence_overall),
            confidence_breakdown=model.confidence_breakdown,
            ai_provider=model.ai_provider,
            ai_model_version=model.ai_model_version,
            generation_time_ms=model.generation_time_ms or 0,
            version=model.version,
            generated_at=model.generated_at,
            updated_at=model.updated_at,
        )

    def _update_model_from_domain(
        self,
        model: GeneratedContentModel,
        content: GeneratedContent,
    ) -> None:
        """Update SQLAlchemy model from domain entity."""
        model.title = content.title
        model.description = content.description
        model.ml_category_id = content.ml_category_id
        model.ml_category_name = content.ml_category_name
        model.ml_title = content.ml_title
        model.ml_price = content.ml_price
        model.ml_currency_id = content.ml_currency_id
        model.ml_available_quantity = content.ml_available_quantity
        model.ml_buying_mode = content.ml_buying_mode
        model.ml_condition = content.ml_condition
        model.ml_listing_type_id = content.ml_listing_type_id
        model.ml_attributes = content.ml_attributes.to_dict()
        model.ml_sale_terms = content.ml_sale_terms.to_dict()
        model.ml_shipping = content.ml_shipping.to_dict()
        model.confidence_overall = Decimal(str(content.confidence_overall))
        model.confidence_breakdown = content.confidence_breakdown
        model.ai_provider = content.ai_provider
        model.ai_model_version = content.ai_model_version
        model.generation_time_ms = content.generation_time_ms
        model.version = content.version
        model.updated_at = content.updated_at or datetime.now(UTC)
