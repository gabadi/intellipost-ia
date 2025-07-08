"""Create products and product_images tables

Revision ID: 004_create_products_tables
Revises: 003_create_ml_credentials
Create Date: 2025-01-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004_create_products_tables"
down_revision: str | None = "003_create_ml_credentials"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=True),
        # Product information
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("category_id", sa.String(length=100), nullable=True),
        # AI-generated content
        sa.Column("ai_title", sa.String(length=255), nullable=True),
        sa.Column("ai_description", sa.Text(), nullable=True),
        sa.Column("ai_tags", sa.JSON(), nullable=True),
        # MercadoLibre integration
        sa.Column("ml_listing_id", sa.String(length=100), nullable=True),
        sa.Column("ml_category_id", sa.String(length=100), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_products_user_id", ondelete="CASCADE"
        ),
    )

    # Create indexes for products table
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_user_id"), "products", ["user_id"], unique=False)
    op.create_index(op.f("ix_products_status"), "products", ["status"], unique=False)
    op.create_index(
        op.f("ix_products_created_at"), "products", ["created_at"], unique=False
    )

    # Create product_images table
    op.create_table(
        "product_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("s3_key", sa.String(length=500), nullable=False),
        sa.Column("s3_url", sa.String(length=1000), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("file_format", sa.String(length=10), nullable=False),
        sa.Column("resolution_width", sa.Integer(), nullable=False),
        sa.Column("resolution_height", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, default=False),
        sa.Column("processing_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_product_images_product_id",
            ondelete="CASCADE",
        ),
    )

    # Create indexes for product_images table
    op.create_index(
        op.f("ix_product_images_id"), "product_images", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_product_images_product_id"),
        "product_images",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_product_images_is_primary"),
        "product_images",
        ["is_primary"],
        unique=False,
    )


def downgrade() -> None:
    # Drop product_images table
    op.drop_index(op.f("ix_product_images_is_primary"), table_name="product_images")
    op.drop_index(op.f("ix_product_images_product_id"), table_name="product_images")
    op.drop_index(op.f("ix_product_images_id"), table_name="product_images")
    op.drop_table("product_images")

    # Drop products table
    op.drop_index(op.f("ix_products_created_at"), table_name="products")
    op.drop_index(op.f("ix_products_status"), table_name="products")
    op.drop_index(op.f("ix_products_user_id"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
