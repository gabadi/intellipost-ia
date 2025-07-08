"""
Create product use case.

This module contains the business logic for creating a new product with images.
"""

import contextlib
from typing import Any
from uuid import UUID, uuid4

from fastapi import UploadFile

from infrastructure.config.logging import get_logger
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_status import ProductStatus
from modules.product_management.domain.ports.product_repository_protocol import (
    ProductRepositoryProtocol,
)
from modules.product_management.infrastructure.services.file_storage_service import (
    FileStorageService,
)

logger = get_logger(__name__)


class CreateProductUseCase:
    """Use case for creating a new product with images."""

    def __init__(
        self,
        product_repository: ProductRepositoryProtocol,
        file_storage_service: FileStorageService,
    ):
        self.product_repository = product_repository
        self.file_storage_service = file_storage_service

    async def execute(
        self,
        user_id: UUID,
        prompt_text: str,
        images: list[UploadFile],
    ) -> dict[str, Any]:
        """
        Execute the create product use case.

        Args:
            user_id: ID of the user creating the product
            prompt_text: Product description prompt
            images: List of uploaded image files

        Returns:
            Dict containing the created product details and upload results
        """
        logger.info(f"Creating product for user {user_id} with {len(images)} images")

        # Validate inputs
        if not prompt_text.strip():
            raise ValueError("Product description cannot be empty")

        if not images:
            raise ValueError("At least one image is required")

        if len(images) > 8:  # Match frontend validation
            raise ValueError("Maximum 8 images allowed")

        # Create product entity
        product_id = uuid4()
        product = Product(
            id=product_id,
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text.strip(),
        )

        try:
            # Save product to database
            created_product = await self.product_repository.create(product)
            logger.info(f"Created product entity: {created_product.id}")

            # Process and upload images
            upload_results = []
            upload_errors = []
            images_uploaded = 0

            for i, image_file in enumerate(images):
                try:
                    # Read file content
                    file_content = await image_file.read()

                    # Validate image
                    validation_result = self.file_storage_service.validate_image_file(
                        file_content, image_file.filename or "unknown.jpg"
                    )

                    if not validation_result["is_valid"]:
                        upload_errors.append(
                            {
                                "filename": image_file.filename,
                                "error_message": validation_result["error_message"],
                            }
                        )
                        continue

                    # Upload to storage
                    upload_metadata = (
                        await self.file_storage_service.upload_product_image(
                            user_id=user_id,
                            product_id=product_id,
                            file_content=file_content,
                            filename=image_file.filename or "unknown.jpg",
                            content_type=image_file.content_type,
                        )
                    )

                    # Create product image record in database
                    image_record = await self.product_repository.create_product_image(
                        product_id=product_id,
                        original_filename=image_file.filename or "unknown.jpg",
                        s3_key=upload_metadata["s3_key"],
                        s3_url=upload_metadata["s3_url"],
                        file_size_bytes=upload_metadata["file_size_bytes"],
                        file_format=upload_metadata["file_format"],
                        resolution_width=upload_metadata["resolution_width"],
                        resolution_height=upload_metadata["resolution_height"],
                        is_primary=(i == 0),  # First image is primary
                    )

                    upload_results.append(
                        {
                            "filename": image_file.filename,
                            "image_id": str(image_record.id),
                            "s3_url": upload_metadata["s3_url"],
                            "is_primary": (i == 0),
                        }
                    )

                    images_uploaded += 1
                    logger.info(f"Successfully uploaded image: {image_file.filename}")

                except Exception as e:
                    logger.error(f"Failed to upload image {image_file.filename}: {e}")
                    upload_errors.append(
                        {
                            "filename": image_file.filename,
                            "error_message": str(e),
                        }
                    )

            # Check if any images were successfully uploaded
            if images_uploaded == 0:
                # If no images were uploaded, we should clean up the product
                await self.product_repository.delete(product_id)
                raise ValueError(
                    "Failed to upload any images. Product creation cancelled."
                )

            # Update product status if partially successful
            if upload_errors and images_uploaded > 0:
                logger.warning(
                    f"Product {product_id} created with {len(upload_errors)} upload errors"
                )

            return {
                "product_id": str(created_product.id),
                "user_id": str(created_product.user_id),
                "status": created_product.status.value,
                "prompt_text": prompt_text,
                "images_uploaded": images_uploaded,
                "upload_results": upload_results,
                "upload_errors": upload_errors,
                "created_at": created_product.created_at.isoformat()
                if created_product.created_at
                else None,
            }

        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            # Attempt to clean up if product was created
            with contextlib.suppress(Exception):
                await self.product_repository.delete(product_id)

            raise e


class GetProductsUseCase:
    """Use case for retrieving user's products."""

    def __init__(self, product_repository: ProductRepositoryProtocol):
        self.product_repository = product_repository

    async def execute(self, user_id: UUID) -> list[dict[str, Any]]:
        """
        Get all products for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of product dictionaries
        """
        logger.info(f"Retrieving products for user {user_id}")

        products = await self.product_repository.get_by_user_id(user_id)

        result = []
        for product in products:
            # Get images for each product
            product_images = await self.product_repository.get_product_images(
                product.id
            )

            product_dict = {
                "id": str(product.id),
                "user_id": str(product.user_id),
                "status": product.status.value,
                "confidence": str(product.confidence.score)
                if product.confidence
                else None,
                "prompt_text": product.prompt_text,
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "category_id": product.category_id,
                "ai_title": product.ai_title,
                "ai_description": product.ai_description,
                "ai_tags": product.ai_tags,
                "ml_listing_id": product.ml_listing_id,
                "ml_category_id": product.ml_category_id,
                "processing_started_at": product.processing_started_at.isoformat()
                if product.processing_started_at
                else None,
                "processing_completed_at": product.processing_completed_at.isoformat()
                if product.processing_completed_at
                else None,
                "processing_error": product.processing_error,
                "created_at": product.created_at.isoformat()
                if product.created_at
                else None,
                "updated_at": product.updated_at.isoformat()
                if product.updated_at
                else None,
                "published_at": product.published_at.isoformat()
                if product.published_at
                else None,
                "images": [image.to_dict() for image in product_images],
            }
            result.append(product_dict)

        logger.info(f"Retrieved {len(result)} products for user {user_id}")
        return result
