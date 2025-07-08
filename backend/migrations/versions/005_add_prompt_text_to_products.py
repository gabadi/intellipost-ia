"""Add prompt_text field to products table

Revision ID: 005_add_prompt_text_to_products
Revises: 004_create_products_tables
Create Date: 2025-07-08 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_add_prompt_text_to_products"
down_revision: str | None = "004_create_products_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add prompt_text field to products table
    op.add_column(
        "products",
        sa.Column("prompt_text", sa.Text(), nullable=False, default=""),
    )

    # Add check constraint for prompt_text length (10-500 characters as per story spec)
    op.create_check_constraint(
        "ck_products_prompt_text_length",
        "products",
        "char_length(prompt_text) >= 10 AND char_length(prompt_text) <= 500",
    )

    # Add processing fields that are missing from the story spec
    op.add_column(
        "products",
        sa.Column("processing_started_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column(
            "processing_completed_at", sa.TIMESTAMP(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "products",
        sa.Column("processing_error", sa.Text(), nullable=True),
    )

    # Update products table to use product_status enum
    op.execute("""
        CREATE TYPE product_status AS ENUM (
            'uploading',
            'processing',
            'ready',
            'publishing',
            'published',
            'failed'
        );
    """)

    # Update status column to use the enum
    op.execute(
        "ALTER TABLE products ALTER COLUMN status TYPE product_status USING status::product_status;"
    )

    # Set default status to 'uploading'
    op.execute("ALTER TABLE products ALTER COLUMN status SET DEFAULT 'uploading';")

    # Update product_images table to align with story spec
    op.add_column(
        "product_images",
        sa.Column("original_s3_url", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "product_images",
        sa.Column("processed_s3_url", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "product_images",
        sa.Column("uploaded_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "product_images",
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # Copy existing s3_url to original_s3_url for existing records
    op.execute(
        "UPDATE product_images SET original_s3_url = s3_url, uploaded_at = created_at;"
    )

    # Add check constraints for file_size_bytes and resolution
    op.create_check_constraint(
        "ck_product_images_file_size_bytes",
        "product_images",
        "file_size_bytes > 0",
    )
    op.create_check_constraint(
        "ck_product_images_resolution_width",
        "product_images",
        "resolution_width > 0",
    )
    op.create_check_constraint(
        "ck_product_images_resolution_height",
        "product_images",
        "resolution_height > 0",
    )
    op.create_check_constraint(
        "ck_product_images_file_format",
        "product_images",
        "file_format IN ('jpg', 'jpeg', 'png', 'webp')",
    )


def downgrade() -> None:
    # Remove check constraints from product_images
    op.drop_constraint("ck_product_images_file_format", "product_images")
    op.drop_constraint("ck_product_images_resolution_height", "product_images")
    op.drop_constraint("ck_product_images_resolution_width", "product_images")
    op.drop_constraint("ck_product_images_file_size_bytes", "product_images")

    # Remove new columns from product_images
    op.drop_column("product_images", "processed_at")
    op.drop_column("product_images", "uploaded_at")
    op.drop_column("product_images", "processed_s3_url")
    op.drop_column("product_images", "original_s3_url")

    # Revert status column back to varchar
    op.execute("ALTER TABLE products ALTER COLUMN status TYPE VARCHAR(50);")
    op.execute("DROP TYPE product_status;")

    # Remove processing fields from products
    op.drop_column("products", "processing_error")
    op.drop_column("products", "processing_completed_at")
    op.drop_column("products", "processing_started_at")

    # Remove prompt_text field
    op.drop_constraint("ck_products_prompt_text_length", "products")
    op.drop_column("products", "prompt_text")
