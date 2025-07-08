"""
Integration tests for ProductRepository.

This module tests the SQLAlchemy repository implementation with test database.
"""

from uuid import uuid4

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

from modules.product_management.domain.entities.confidence_score import ConfidenceScore
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.product_status import ProductStatus
from modules.product_management.infrastructure.repositories.product_repository import (
    SQLAlchemyProductRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyProductRepository:
    """Test cases for SQLAlchemy Product Repository."""

    async def test_create_product(self, async_session):
        """Test creating a product in the database."""
        repository = SQLAlchemyProductRepository(async_session)

        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="iPhone 13 Pro usado, excelente estado, 128GB",
        )

        created_product = await repository.create(product)

        assert created_product.id == product.id
        assert created_product.user_id == product.user_id
        assert created_product.status == ProductStatus.UPLOADING
        assert created_product.prompt_text == product.prompt_text
        assert created_product.created_at is not None

    async def test_get_product_by_id(self, async_session):
        """Test retrieving a product by ID."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.READY,
            prompt_text="Test product description",
            title="Test Product",
            price=99.99,
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Retrieve product
        retrieved_product = await repository.get_by_id(created_product.id)

        assert retrieved_product is not None
        assert retrieved_product.id == created_product.id
        assert retrieved_product.title == "Test Product"
        assert retrieved_product.price == 99.99

    async def test_get_product_by_id_not_found(self, async_session):
        """Test retrieving a non-existent product returns None."""
        repository = SQLAlchemyProductRepository(async_session)

        non_existent_id = uuid4()
        result = await repository.get_by_id(non_existent_id)

        assert result is None

    async def test_get_products_by_user_id(self, async_session):
        """Test retrieving all products for a user."""
        repository = SQLAlchemyProductRepository(async_session)
        user_id = uuid4()

        # Create multiple products for the user
        products = []
        for i in range(3):
            product = Product(
                id=uuid4(),
                user_id=user_id,
                status=ProductStatus.UPLOADING,
                prompt_text=f"Product {i} description",
                title=f"Product {i}",
            )
            created_product = await repository.create(product)
            products.append(created_product)

        # Create product for different user
        other_product = Product(
            id=uuid4(),
            user_id=uuid4(),  # Different user
            status=ProductStatus.UPLOADING,
            prompt_text="Other user product",
        )
        await repository.create(other_product)
        await async_session.commit()

        # Retrieve products for original user
        user_products = await repository.get_by_user_id(user_id)

        assert len(user_products) == 3
        assert all(p.user_id == user_id for p in user_products)
        # Should be ordered by created_at desc
        assert user_products[0].title == "Product 2"
        assert user_products[1].title == "Product 1"
        assert user_products[2].title == "Product 0"

    async def test_update_product(self, async_session):
        """Test updating a product."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Original description",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Update product
        created_product.status = ProductStatus.READY
        created_product.title = "Updated Title"
        created_product.confidence = ConfidenceScore(0.85)

        updated_product = await repository.update(created_product)

        assert updated_product.status == ProductStatus.READY
        assert updated_product.title == "Updated Title"
        assert updated_product.confidence is not None
        assert updated_product.confidence.score == 0.85

    async def test_delete_product(self, async_session):
        """Test deleting a product."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="To be deleted",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Delete product
        result = await repository.delete(created_product.id)
        await async_session.commit()

        assert result is True

        # Verify deletion
        deleted_product = await repository.get_by_id(created_product.id)
        assert deleted_product is None

    async def test_delete_nonexistent_product(self, async_session):
        """Test deleting a non-existent product returns False."""
        repository = SQLAlchemyProductRepository(async_session)

        non_existent_id = uuid4()
        result = await repository.delete(non_existent_id)

        assert result is False

    async def test_create_product_image(self, async_session):
        """Test creating a product image."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product first
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Product with image",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Create product image
        image = await repository.create_product_image(
            product_id=created_product.id,
            original_filename="test.jpg",
            s3_key="products/user/product/test.jpg",
            s3_url="https://bucket.s3.amazonaws.com/products/user/product/test.jpg",
            file_size_bytes=1024,
            file_format="jpg",
            resolution_width=1920,
            resolution_height=1080,
            is_primary=True,
        )

        assert image.product_id == created_product.id
        assert image.original_filename == "test.jpg"
        assert image.is_primary is True
        assert image.file_size_bytes == 1024

    async def test_get_product_images(self, async_session):
        """Test retrieving images for a product."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Product with multiple images",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Create multiple images
        images = []
        for i in range(3):
            image = await repository.create_product_image(
                product_id=created_product.id,
                original_filename=f"image{i}.jpg",
                s3_key=f"products/user/product/image{i}.jpg",
                s3_url=f"https://bucket.s3.amazonaws.com/products/user/product/image{i}.jpg",
                file_size_bytes=1024 * (i + 1),
                file_format="jpg",
                resolution_width=1920,
                resolution_height=1080,
                is_primary=(i == 0),  # First image is primary
            )
            images.append(image)

        await async_session.commit()

        # Retrieve images
        product_images = await repository.get_product_images(created_product.id)

        assert len(product_images) == 3
        # Should be ordered by is_primary desc, created_at asc
        assert product_images[0].is_primary is True
        assert product_images[0].original_filename == "image0.jpg"

    async def test_set_primary_image(self, async_session):
        """Test setting a specific image as primary."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product and images
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Product for primary image test",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Create multiple images
        images = []
        for i in range(3):
            image = await repository.create_product_image(
                product_id=created_product.id,
                original_filename=f"image{i}.jpg",
                s3_key=f"products/user/product/image{i}.jpg",
                s3_url=f"https://bucket.s3.amazonaws.com/products/user/product/image{i}.jpg",
                file_size_bytes=1024,
                file_format="jpg",
                resolution_width=1920,
                resolution_height=1080,
                is_primary=(i == 0),
            )
            images.append(image)

        await async_session.commit()

        # Set second image as primary
        result = await repository.set_primary_image(created_product.id, images[1].id)
        await async_session.commit()

        assert result is True

        # Verify primary image changed
        product_images = await repository.get_product_images(created_product.id)
        primary_images = [img for img in product_images if img.is_primary]

        assert len(primary_images) == 1
        assert primary_images[0].id == images[1].id

    async def test_delete_product_image(self, async_session):
        """Test deleting a product image."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product and image
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Product for image deletion test",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        image = await repository.create_product_image(
            product_id=created_product.id,
            original_filename="to_delete.jpg",
            s3_key="products/user/product/to_delete.jpg",
            s3_url="https://bucket.s3.amazonaws.com/products/user/product/to_delete.jpg",
            file_size_bytes=1024,
            file_format="jpg",
            resolution_width=1920,
            resolution_height=1080,
        )
        await async_session.commit()

        # Delete image
        result = await repository.delete_product_image(image.id)
        await async_session.commit()

        assert result is True

        # Verify deletion
        product_images = await repository.get_product_images(created_product.id)
        assert len(product_images) == 0

    async def test_get_products_by_status(self, async_session):
        """Test retrieving products by status."""
        repository = SQLAlchemyProductRepository(async_session)
        user_id = uuid4()

        # Create products with different statuses
        statuses = [
            ProductStatus.UPLOADING,
            ProductStatus.PROCESSING,
            ProductStatus.READY,
        ]
        products = []

        for status in statuses:
            product = Product(
                id=uuid4(),
                user_id=user_id,
                status=status,
                prompt_text=f"Product with status {status.value}",
            )
            created_product = await repository.create(product)
            products.append(created_product)

        await async_session.commit()

        # Get products by specific status
        ready_products = await repository.get_products_by_status("ready", user_id)

        assert len(ready_products) == 1
        assert ready_products[0].status == ProductStatus.READY

    async def test_count_products_by_user(self, async_session):
        """Test counting products for a user."""
        repository = SQLAlchemyProductRepository(async_session)
        user_id = uuid4()

        # Create products
        for i in range(5):
            product = Product(
                id=uuid4(),
                user_id=user_id,
                status=ProductStatus.UPLOADING,
                prompt_text=f"Product {i}",
            )
            await repository.create(product)

        await async_session.commit()

        # Count products
        count = await repository.count_products_by_user(user_id)

        assert count == 5

    async def test_get_products_with_pagination(self, async_session):
        """Test paginated product retrieval."""
        repository = SQLAlchemyProductRepository(async_session)
        user_id = uuid4()

        # Create 10 products
        for i in range(10):
            product = Product(
                id=uuid4(),
                user_id=user_id,
                status=ProductStatus.UPLOADING,
                prompt_text=f"Product {i}",
                title=f"Product {i}",
            )
            await repository.create(product)

        await async_session.commit()

        # Get first page
        products, total_count = await repository.get_products_with_pagination(
            user_id, page=1, page_size=3
        )

        assert len(products) == 3
        assert total_count == 10
        assert products[0].title == "Product 9"  # Most recent first

    async def test_update_product_status(self, async_session):
        """Test updating product status with processing tracking."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Status update test",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Update to processing
        updated_product = await repository.update_product_status(
            created_product.id, "processing"
        )
        await async_session.commit()

        assert updated_product is not None
        assert updated_product.status == ProductStatus.PROCESSING
        assert updated_product.processing_started_at is not None

        # Update to failed with error
        failed_product = await repository.update_product_status(
            created_product.id, "failed", "Processing failed due to invalid image"
        )
        await async_session.commit()

        assert failed_product is not None
        assert failed_product.status == ProductStatus.FAILED
        assert (
            failed_product.processing_error == "Processing failed due to invalid image"
        )
        assert failed_product.processing_completed_at is not None

    async def test_bulk_update_image_metadata(self, async_session):
        """Test bulk updating image metadata."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product and images
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Bulk update test",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Create images
        images = []
        for i in range(3):
            image = await repository.create_product_image(
                product_id=created_product.id,
                original_filename=f"image{i}.jpg",
                s3_key=f"products/user/product/image{i}.jpg",
                s3_url=f"https://bucket.s3.amazonaws.com/products/user/product/image{i}.jpg",
                file_size_bytes=1024,
                file_format="jpg",
                resolution_width=1920,
                resolution_height=1080,
            )
            images.append(image)

        await async_session.commit()

        # Bulk update
        updates = [
            {
                "image_id": images[0].id,
                "processing_metadata": {"ai_tags": ["phone", "electronics"]},
                "processed_s3_url": "https://bucket.s3.amazonaws.com/processed/image0.jpg",
            },
            {
                "image_id": images[1].id,
                "is_primary": True,
            },
        ]

        updated_images = await repository.bulk_update_image_metadata(
            created_product.id, updates
        )
        await async_session.commit()

        assert len(updated_images) == 2
        assert updated_images[0].processing_metadata == {
            "ai_tags": ["phone", "electronics"]
        }
        assert updated_images[0].processed_s3_url is not None
        assert updated_images[1].is_primary is True

    async def test_get_product_with_images_for_update(self, async_session):
        """Test getting product with row-level lock."""
        repository = SQLAlchemyProductRepository(async_session)

        # Create product with images
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.UPLOADING,
            prompt_text="Lock test product",
        )

        created_product = await repository.create(product)
        await async_session.commit()

        # Create image
        await repository.create_product_image(
            product_id=created_product.id,
            original_filename="test.jpg",
            s3_key="products/user/product/test.jpg",
            s3_url="https://bucket.s3.amazonaws.com/products/user/product/test.jpg",
            file_size_bytes=1024,
            file_format="jpg",
            resolution_width=1920,
            resolution_height=1080,
        )
        await async_session.commit()

        # Get product for update (with lock)
        locked_product = await repository.get_product_with_images_for_update(
            created_product.id
        )

        assert locked_product is not None
        assert locked_product.id == created_product.id
        # Images should be loaded due to selectinload
        # Note: In actual test, you'd verify the lock behavior with concurrent transactions
