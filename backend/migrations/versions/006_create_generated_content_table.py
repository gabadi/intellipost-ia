"""Create generated_content table for AI-generated content

Revision ID: 006_create_generated_content_table
Revises: 005_add_prompt_text_to_products
Create Date: 2025-07-09 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006_create_generated_content_table"
down_revision: str | None = "005_add_prompt_text_to_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create generated_content table
    op.create_table(
        "generated_content",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        # AI Generated content
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        # MercadoLibre specific fields
        sa.Column("ml_category_id", sa.String(length=50), nullable=False),
        sa.Column("ml_category_name", sa.String(length=200), nullable=False),
        sa.Column("ml_title", sa.String(length=60), nullable=False),
        sa.Column("ml_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("ml_currency_id", sa.String(length=3), nullable=False, default="ARS"),
        sa.Column("ml_available_quantity", sa.Integer(), nullable=False, default=1),
        sa.Column(
            "ml_buying_mode", sa.String(length=20), nullable=False, default="buy_it_now"
        ),
        sa.Column("ml_condition", sa.String(length=20), nullable=False, default="new"),
        sa.Column(
            "ml_listing_type_id",
            sa.String(length=50),
            nullable=False,
            default="gold_special",
        ),
        # MercadoLibre flexible attributes and terms
        sa.Column("ml_attributes", sa.JSON(), nullable=False, default={}),
        sa.Column("ml_sale_terms", sa.JSON(), nullable=False, default={}),
        sa.Column("ml_shipping", sa.JSON(), nullable=False, default={}),
        # AI confidence scoring
        sa.Column(
            "confidence_overall", sa.Numeric(precision=3, scale=2), nullable=False
        ),
        sa.Column("confidence_breakdown", sa.JSON(), nullable=False, default={}),
        # AI provider metadata
        sa.Column(
            "ai_provider", sa.String(length=50), nullable=False, default="gemini"
        ),
        sa.Column("ai_model_version", sa.String(length=100), nullable=False),
        sa.Column("generation_time_ms", sa.Integer(), nullable=True),
        # Version control for regeneration
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        # Timestamps
        sa.Column("generated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_generated_content_product_id",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "char_length(trim(title)) >= 10",
            name="ck_generated_content_title_min_length",
        ),
        sa.CheckConstraint(
            "char_length(trim(description)) >= 50",
            name="ck_generated_content_description_min_length",
        ),
        sa.CheckConstraint("ml_price > 0", name="ck_generated_content_price_positive"),
        sa.CheckConstraint(
            "confidence_overall BETWEEN 0.00 AND 1.00",
            name="ck_generated_content_confidence_range",
        ),
        sa.CheckConstraint(
            "generation_time_ms > 0 OR generation_time_ms IS NULL",
            name="ck_generated_content_generation_time_positive",
        ),
        sa.CheckConstraint("version > 0", name="ck_generated_content_version_positive"),
    )

    # Create indexes for generated_content table
    op.create_index(
        op.f("ix_generated_content_id"), "generated_content", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_generated_content_product_id"),
        "generated_content",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_content_ml_category_id"),
        "generated_content",
        ["ml_category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_content_ai_provider"),
        "generated_content",
        ["ai_provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_content_version"),
        "generated_content",
        ["version"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_content_generated_at"),
        "generated_content",
        ["generated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_content_confidence_overall"),
        "generated_content",
        ["confidence_overall"],
        unique=False,
    )

    # Create composite index for product_id and version (for getting latest version)
    op.create_index(
        "ix_generated_content_product_version",
        "generated_content",
        ["product_id", "version"],
        unique=False,
    )

    # Create ai_generation table for tracking processing status
    op.create_table(
        "ai_generation",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        # Processing metadata
        sa.Column("current_step", sa.String(length=50), nullable=True),
        sa.Column("progress_percentage", sa.Float(), nullable=False, default=0.0),
        sa.Column("estimated_completion_seconds", sa.Integer(), nullable=True),
        # Input data
        sa.Column("input_images", sa.JSON(), nullable=False, default=[]),
        sa.Column("input_prompt", sa.Text(), nullable=True),
        sa.Column("category_hint", sa.String(length=100), nullable=True),
        sa.Column("price_range", sa.JSON(), nullable=False, default={}),
        sa.Column("target_audience", sa.String(length=100), nullable=True),
        # Processing results
        sa.Column("generated_content_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        # AI provider metadata
        sa.Column(
            "ai_provider", sa.String(length=50), nullable=False, default="gemini"
        ),
        sa.Column("ai_model_version", sa.String(length=100), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        # Processing steps tracking
        sa.Column("completed_steps", sa.JSON(), nullable=False, default=[]),
        sa.Column("failed_step", sa.String(length=50), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_ai_generation_product_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["generated_content_id"],
            ["generated_content.id"],
            name="fk_ai_generation_generated_content_id",
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "progress_percentage BETWEEN 0.0 AND 100.0",
            name="ck_ai_generation_progress_range",
        ),
        sa.CheckConstraint(
            "processing_time_ms > 0 OR processing_time_ms IS NULL",
            name="ck_ai_generation_processing_time_positive",
        ),
        sa.CheckConstraint(
            "estimated_completion_seconds > 0 OR estimated_completion_seconds IS NULL",
            name="ck_ai_generation_estimated_completion_positive",
        ),
    )

    # Create indexes for ai_generation table
    op.create_index(op.f("ix_ai_generation_id"), "ai_generation", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_generation_product_id"),
        "ai_generation",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_generation_status"), "ai_generation", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_ai_generation_ai_provider"),
        "ai_generation",
        ["ai_provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_generation_created_at"),
        "ai_generation",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_generation_updated_at"),
        "ai_generation",
        ["updated_at"],
        unique=False,
    )

    # Create composite index for product_id and status (for finding active generations)
    op.create_index(
        "ix_ai_generation_product_status",
        "ai_generation",
        ["product_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    # Drop ai_generation table
    op.drop_index("ix_ai_generation_product_status", table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_updated_at"), table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_created_at"), table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_ai_provider"), table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_status"), table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_product_id"), table_name="ai_generation")
    op.drop_index(op.f("ix_ai_generation_id"), table_name="ai_generation")
    op.drop_table("ai_generation")

    # Drop generated_content table
    op.drop_index(
        "ix_generated_content_product_version", table_name="generated_content"
    )
    op.drop_index(
        op.f("ix_generated_content_confidence_overall"), table_name="generated_content"
    )
    op.drop_index(
        op.f("ix_generated_content_generated_at"), table_name="generated_content"
    )
    op.drop_index(op.f("ix_generated_content_version"), table_name="generated_content")
    op.drop_index(
        op.f("ix_generated_content_ai_provider"), table_name="generated_content"
    )
    op.drop_index(
        op.f("ix_generated_content_ml_category_id"), table_name="generated_content"
    )
    op.drop_index(
        op.f("ix_generated_content_product_id"), table_name="generated_content"
    )
    op.drop_index(op.f("ix_generated_content_id"), table_name="generated_content")
    op.drop_table("generated_content")
