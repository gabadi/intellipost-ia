"""
AI Generation domain entity.

This module defines the AIGeneration entity which represents
the processing state and metadata of AI content generation.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID


class GenerationStatus(str, Enum):
    """Status of AI content generation process."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStep(str, Enum):
    """Steps in the AI content generation process."""

    IMAGE_ANALYSIS = "image_analysis"
    CONTENT_EXTRACTION = "content_extraction"
    CATEGORY_DETECTION = "category_detection"
    TITLE_GENERATION = "title_generation"
    DESCRIPTION_GENERATION = "description_generation"
    ATTRIBUTE_MAPPING = "attribute_mapping"
    PRICE_ESTIMATION = "price_estimation"
    QUALITY_VALIDATION = "quality_validation"
    CONTENT_FINALIZATION = "content_finalization"


@dataclass
class AIGeneration:
    """
    Domain entity representing the state and metadata of AI content generation.

    This entity tracks the processing state, progress, and results of
    AI content generation for a product.
    """

    id: UUID
    product_id: UUID
    status: GenerationStatus

    # Processing metadata
    current_step: ProcessingStep | None = None
    progress_percentage: float = 0.0
    estimated_completion_seconds: int | None = None

    # Input data
    input_images: list[str] | None = None  # S3 keys
    input_prompt: str | None = None
    category_hint: str | None = None
    price_range: dict[str, float] | None = None
    target_audience: str | None = None

    # Processing results
    generated_content_id: UUID | None = None
    error_message: str | None = None
    error_code: str | None = None

    # AI provider metadata
    ai_provider: str = "gemini"
    ai_model_version: str | None = None
    processing_time_ms: int | None = None

    # Processing steps tracking
    completed_steps: list[ProcessingStep] | None = None
    failed_step: ProcessingStep | None = None

    # Timestamps
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Initialize default values and validate the entity."""
        if self.input_images is None:
            self.input_images = []
        if self.completed_steps is None:
            self.completed_steps = []
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.price_range is None:
            self.price_range = {}

        self._validate_progress()
        self._validate_status()

    def _validate_progress(self):
        """Validate progress percentage."""
        if not (0.0 <= self.progress_percentage <= 100.0):
            raise ValueError("Progress percentage must be between 0.0 and 100.0")

    def _validate_status(self):
        """Validate status consistency."""
        if self.status == GenerationStatus.COMPLETED and not self.generated_content_id:
            raise ValueError("Completed generation must have generated_content_id")

        if self.status == GenerationStatus.FAILED and not self.error_message:
            raise ValueError("Failed generation must have error_message")

    def start_processing(self, ai_model_version: str):
        """Start the processing and update status."""
        self.status = GenerationStatus.PROCESSING
        self.started_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.ai_model_version = ai_model_version
        self.current_step = ProcessingStep.IMAGE_ANALYSIS
        self.progress_percentage = 0.0

    def update_progress(self, step: ProcessingStep, percentage: float):
        """Update the current processing step and progress."""
        self.current_step = step
        self.progress_percentage = percentage
        self.updated_at = datetime.now(UTC)

        # Add to completed steps if not already there
        if self.completed_steps is not None and step not in self.completed_steps:
            # Only mark as completed if we're moving to next step
            if percentage >= 100.0 or step != self.current_step:
                self.completed_steps.append(step)

    def complete_processing(self, generated_content_id: UUID, processing_time_ms: int):
        """Mark the processing as completed."""
        self.status = GenerationStatus.COMPLETED
        self.generated_content_id = generated_content_id
        self.processing_time_ms = processing_time_ms
        self.progress_percentage = 100.0
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.current_step = None

    def fail_processing(
        self,
        error_message: str,
        error_code: str | None = None,
        failed_step: ProcessingStep | None = None,
    ):
        """Mark the processing as failed."""
        self.status = GenerationStatus.FAILED
        self.error_message = error_message
        self.error_code = error_code
        self.failed_step = failed_step or self.current_step
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def cancel_processing(self):
        """Cancel the processing."""
        self.status = GenerationStatus.CANCELLED
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def get_progress_info(self) -> dict[str, Any]:
        """Get progress information for client updates."""
        return {
            "processing_id": str(self.id),
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "progress_percentage": self.progress_percentage,
            "estimated_completion_seconds": self.estimated_completion_seconds,
            "completed_steps": [step.value for step in self.completed_steps]
            if self.completed_steps
            else [],
            "total_steps": len(ProcessingStep),
        }

    def get_processing_summary(self) -> dict[str, Any]:
        """Get a summary of the processing results."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "status": self.status.value,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "processing_time_ms": self.processing_time_ms,
            "generated_content_id": str(self.generated_content_id)
            if self.generated_content_id
            else None,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "failed_step": self.failed_step.value if self.failed_step else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }

    def is_processing(self) -> bool:
        """Check if the generation is currently processing."""
        return self.status == GenerationStatus.PROCESSING

    def is_completed(self) -> bool:
        """Check if the generation is completed."""
        return self.status == GenerationStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if the generation failed."""
        return self.status == GenerationStatus.FAILED

    def get_estimated_remaining_time(self) -> int | None:
        """Get estimated remaining time in seconds."""
        if not self.estimated_completion_seconds:
            return None

        if self.progress_percentage <= 0:
            return self.estimated_completion_seconds

        # Calculate remaining time based on progress
        remaining_percentage = 100.0 - self.progress_percentage
        remaining_time = int(
            (remaining_percentage / 100.0) * self.estimated_completion_seconds
        )
        return max(0, remaining_time)

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary representation."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "progress_percentage": self.progress_percentage,
            "estimated_completion_seconds": self.estimated_completion_seconds,
            "input_images": self.input_images,
            "input_prompt": self.input_prompt,
            "category_hint": self.category_hint,
            "price_range": self.price_range,
            "target_audience": self.target_audience,
            "generated_content_id": str(self.generated_content_id)
            if self.generated_content_id
            else None,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "ai_provider": self.ai_provider,
            "ai_model_version": self.ai_model_version,
            "processing_time_ms": self.processing_time_ms,
            "completed_steps": [step.value for step in self.completed_steps]
            if self.completed_steps
            else [],
            "failed_step": self.failed_step.value if self.failed_step else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
