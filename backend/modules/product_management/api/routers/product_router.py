"""
Product API router for product management module.

This module contains FastAPI routes for product operations.
"""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer

from infrastructure.config.logging import get_logger
from modules.product_management.api.schemas.product_schemas import (
    CreateProductResponse,
    ErrorResponse,
    ProductListResponse,
    ProductResponse,
    ValidationErrorResponse,
)
from modules.product_management.application.use_cases.create_product import (
    CreateProductUseCase,
    GetProductsUseCase,
)
from modules.user_management.domain.entities.user import User

logger = get_logger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/products", tags=["products"])


def create_product_router(
    create_product_use_case_factory: Callable[[], CreateProductUseCase],
    get_products_use_case_factory: Callable[[], GetProductsUseCase],
    current_user_provider: Callable[[], User] | None = None,
) -> APIRouter:
    """Create product router with dependency injection."""

    # Use the provided current_user_provider or create a dummy one
    if current_user_provider:
        current_user_dep = Depends(current_user_provider)
    else:
        # Fallback - this will be replaced when the router is properly wired
        def dummy_current_user() -> User:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Current user provider not configured",
            )

        current_user_dep = Depends(dummy_current_user)

    @router.post(
        "/",
        response_model=CreateProductResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            400: {"model": ValidationErrorResponse, "description": "Validation error"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            413: {"model": ErrorResponse, "description": "File too large"},
            422: {
                "model": ValidationErrorResponse,
                "description": "Unprocessable entity",
            },
        },
    )
    async def create_product(  # pyright: ignore[reportUnusedFunction]
        prompt_text: Annotated[
            str,
            Form(
                description="Product description prompt", min_length=10, max_length=1000
            ),
        ],
        images: Annotated[
            list[UploadFile], File(description="Product images (1-8 files)")
        ],
        current_user: Annotated[User, current_user_dep],
        create_use_case: Annotated[
            CreateProductUseCase, Depends(create_product_use_case_factory)
        ],
    ) -> CreateProductResponse:
        """Create a new product with images."""
        try:
            logger.info(f"Creating product for user {current_user.id}")

            # Validate inputs
            if not prompt_text or not prompt_text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "INVALID_PROMPT",
                        "message": "Product description cannot be empty",
                    },
                )

            if not images:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "NO_IMAGES",
                        "message": "At least one image is required",
                    },
                )

            if len(images) > 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "TOO_MANY_IMAGES",
                        "message": "Maximum 8 images allowed",
                    },
                )

            # Validate each image file
            for image in images:
                if not image.filename:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error_code": "INVALID_FILENAME",
                            "message": "All image files must have valid filenames",
                        },
                    )

                if not image.content_type or not image.content_type.startswith(
                    "image/"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error_code": "INVALID_FILE_TYPE",
                            "message": f"File {image.filename} is not a valid image",
                        },
                    )

            # Execute use case
            result = await create_use_case.execute(
                user_id=current_user.id,
                prompt_text=prompt_text.strip(),
                images=images,
            )

            # Check for upload errors
            if result.get("upload_errors"):
                logger.warning(
                    f"Product created with upload errors: {result['upload_errors']}"
                )

            return CreateProductResponse(
                id=result["product_id"],
                user_id=result["user_id"],
                status=result["status"],
                prompt_text=result["prompt_text"],
                images_uploaded=result["images_uploaded"],
                created_at=result["created_at"],
                message=f"Product created successfully with {result['images_uploaded']} images"
                + (
                    f" ({len(result['upload_errors'])} errors)"
                    if result.get("upload_errors")
                    else ""
                ),
            )

        except ValueError as e:
            logger.error(f"Validation error creating product: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error creating product: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while creating the product",
                },
            ) from e

    @router.get(
        "/",
        response_model=ProductListResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
        },
    )
    async def get_products(  # pyright: ignore[reportUnusedFunction]
        current_user: Annotated[User, current_user_dep],
        get_use_case: Annotated[
            GetProductsUseCase, Depends(get_products_use_case_factory)
        ],
    ) -> ProductListResponse:
        """Get all products for the current user."""
        try:
            logger.info(f"Retrieving products for user {current_user.id}")

            products_data = await get_use_case.execute(user_id=current_user.id)

            products = []
            for product_data in products_data:
                # Convert images to response format
                images = [
                    {
                        "id": img["id"],
                        "product_id": img["product_id"],
                        "original_filename": img["original_filename"],
                        "s3_url": img["s3_url"],
                        "file_size_bytes": img["file_size_bytes"],
                        "file_format": img["file_format"],
                        "resolution_width": img["resolution_width"],
                        "resolution_height": img["resolution_height"],
                        "is_primary": img["is_primary"],
                        "processing_metadata": img["processing_metadata"],
                        "created_at": img["created_at"],
                        "updated_at": img["updated_at"],
                    }
                    for img in product_data["images"]
                ]

                product = ProductResponse(
                    id=product_data["id"],
                    user_id=product_data["user_id"],
                    status=product_data["status"],
                    confidence=product_data["confidence"],
                    title=product_data["title"],
                    description=product_data["description"],
                    price=product_data["price"],
                    category_id=product_data["category_id"],
                    ai_title=product_data["ai_title"],
                    ai_description=product_data["ai_description"],
                    ai_tags=product_data["ai_tags"],
                    ml_listing_id=product_data["ml_listing_id"],
                    ml_category_id=product_data["ml_category_id"],
                    created_at=product_data["created_at"],
                    updated_at=product_data["updated_at"],
                    published_at=product_data["published_at"],
                    images=images,
                )
                products.append(product)

            return ProductListResponse(
                products=products,
                total=len(products),
                page=1,
                page_size=len(products),
            )

        except Exception as e:
            logger.error(f"Error retrieving products for user {current_user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while retrieving products",
                },
            ) from e

    @router.get(
        "/{product_id}",
        response_model=ProductResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            404: {"model": ErrorResponse, "description": "Product not found"},
        },
    )
    async def get_product(  # pyright: ignore[reportUnusedFunction]
        product_id: UUID,
        current_user: Annotated[User, current_user_dep],
        get_use_case: Annotated[
            GetProductsUseCase, Depends(get_products_use_case_factory)
        ],
    ) -> ProductResponse:
        """Get a specific product by ID."""
        try:
            logger.info(f"Retrieving product {product_id} for user {current_user.id}")

            # Get all user products and find the specific one
            # TODO: Optimize this with a get_by_id method in the use case
            products_data = await get_use_case.execute(user_id=current_user.id)

            product_data = next(
                (p for p in products_data if p["id"] == str(product_id)), None
            )

            if not product_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "PRODUCT_NOT_FOUND",
                        "message": f"Product {product_id} not found",
                    },
                )

            # Convert images to response format
            images = [
                {
                    "id": img["id"],
                    "product_id": img["product_id"],
                    "original_filename": img["original_filename"],
                    "s3_url": img["s3_url"],
                    "file_size_bytes": img["file_size_bytes"],
                    "file_format": img["file_format"],
                    "resolution_width": img["resolution_width"],
                    "resolution_height": img["resolution_height"],
                    "is_primary": img["is_primary"],
                    "processing_metadata": img["processing_metadata"],
                    "created_at": img["created_at"],
                    "updated_at": img["updated_at"],
                }
                for img in product_data["images"]
            ]

            return ProductResponse(
                id=product_data["id"],
                user_id=product_data["user_id"],
                status=product_data["status"],
                confidence=product_data["confidence"],
                title=product_data["title"],
                description=product_data["description"],
                price=product_data["price"],
                category_id=product_data["category_id"],
                ai_title=product_data["ai_title"],
                ai_description=product_data["ai_description"],
                ai_tags=product_data["ai_tags"],
                ml_listing_id=product_data["ml_listing_id"],
                ml_category_id=product_data["ml_category_id"],
                created_at=product_data["created_at"],
                updated_at=product_data["updated_at"],
                published_at=product_data["published_at"],
                images=images,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred while retrieving product {product_id}",
                },
            ) from e

    return router
