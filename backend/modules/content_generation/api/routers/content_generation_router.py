"""
Content Generation API router.

This module provides the FastAPI router for content generation endpoints.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import HTTPBearer

from modules.content_generation.api.schemas import (
    CompletionMessage,
    ConnectionMessage,
    ContentEnhancementRequest,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentValidationSchema,
    ContentVersionsSchema,
    ErrorMessage,
    ErrorResponseSchema,
    GeneratedContentSchema,
    ProcessingStatusSchema,
    ProgressUpdateMessage,
)
from modules.content_generation.application.use_cases import GenerateContentUseCase
from modules.content_generation.domain.exceptions import (
    AIServiceError,
    CategoryDetectionError,
    ContentGenerationError,
    EntityNotFoundError,
    InvalidContentError,
    QualityThresholdError,
)
from modules.user_management.domain.entities.user import User

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/content-generation",
    tags=["Content Generation"],
    responses={
        400: {"model": ErrorResponseSchema},
        401: {"model": ErrorResponseSchema},
        403: {"model": ErrorResponseSchema},
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
        500: {"model": ErrorResponseSchema},
    },
)

# Security
security = HTTPBearer()


# WebSocket connection manager
class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: dict[UUID, list[WebSocket]] = {}
        self.connection_tasks: dict[UUID, asyncio.Task[Any]] = {}

    async def connect(self, websocket: WebSocket, processing_id: UUID):
        """Connect a WebSocket client."""
        await websocket.accept()

        if processing_id not in self.active_connections:
            self.active_connections[processing_id] = []

        self.active_connections[processing_id].append(websocket)

        # Send connection confirmation
        await self.send_personal_message(
            processing_id,
            websocket,
            {
                "type": "connect",
                "processing_id": str(processing_id),
                "message": "Connected to content generation updates",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        logger.info(f"WebSocket connected for processing: {processing_id}")

    def disconnect(self, websocket: WebSocket, processing_id: UUID):
        """Disconnect a WebSocket client."""
        if processing_id in self.active_connections:
            if websocket in self.active_connections[processing_id]:
                self.active_connections[processing_id].remove(websocket)

            # Clean up empty connections
            if not self.active_connections[processing_id]:
                del self.active_connections[processing_id]

        logger.info(f"WebSocket disconnected for processing: {processing_id}")

    async def send_personal_message(
        self, processing_id: UUID, websocket: WebSocket, message: dict[str, Any]
    ) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket, processing_id)

    async def broadcast_to_processing(
        self, processing_id: UUID, message: dict[str, Any]
    ) -> None:
        """Broadcast a message to all connections for a processing ID."""
        if processing_id not in self.active_connections:
            return

        disconnected_connections: list[WebSocket] = []

        for websocket in self.active_connections[processing_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected_connections.append(websocket)

        # Clean up disconnected connections
        for websocket in disconnected_connections:
            self.disconnect(websocket, processing_id)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


def create_content_generation_router(
    generate_content_use_case_factory: Callable[[], GenerateContentUseCase],
    current_user_provider: Callable[[], User] | None = None,
) -> APIRouter:
    """Create content generation router with dependency injection."""

    # Create new router instance
    content_router = APIRouter(
        prefix="/content-generation",
        tags=["Content Generation"],
        responses={
            400: {"model": ErrorResponseSchema},
            401: {"model": ErrorResponseSchema},
            403: {"model": ErrorResponseSchema},
            404: {"model": ErrorResponseSchema},
            422: {"model": ErrorResponseSchema},
            500: {"model": ErrorResponseSchema},
        },
    )

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

    # Create use case dependency
    use_case_dep = Depends(generate_content_use_case_factory)

    # Mock ImageData for testing
    class MockImageData:
        """Mock image data for testing."""

        def __init__(
            self, s3_key: str, s3_url: str, file_format: str, width: int, height: int
        ):
            self.s3_key = s3_key
            self.s3_url = s3_url
            self.file_format = file_format
            self.resolution_width = width
            self.resolution_height = height

    # API Endpoints

    @content_router.post(
        "/products/{product_id}/generate",
        response_model=ContentGenerationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        summary="Generate content for a product",
        description="Generate AI-optimized content for a MercadoLibre product listing",
    )
    async def generate_content(
        product_id: UUID,
        request: ContentGenerationRequest,
        use_case: GenerateContentUseCase = use_case_dep,
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """
        Generate AI-optimized content for a product listing.

        This endpoint initiates the content generation process and returns
        a processing ID for tracking progress via WebSocket.
        """
        try:
            # Mock images for testing (in production, these would be fetched from database)
            mock_images = [
                MockImageData(
                    s3_key=f"products/{product_id}/image1.jpg",
                    s3_url=f"https://s3.amazonaws.com/bucket/products/{product_id}/image1.jpg",
                    file_format="jpeg",
                    width=800,
                    height=600,
                )
            ]

            # Execute content generation
            ai_generation = await use_case.execute(
                product_id=product_id,
                images=mock_images,
                prompt="Sample product description",  # This would come from product data
                category_hint=request.category_hint,
                price_range=request.price_range,
                target_audience=request.target_audience,
                regenerate=request.regenerate,
            )

            # Start WebSocket updates task
            if ai_generation.is_processing():
                task = asyncio.create_task(
                    _monitor_processing_progress(ai_generation.id, use_case)
                )
                websocket_manager.connection_tasks[ai_generation.id] = task

            # Return processing information
            return ContentGenerationResponse(
                processing_id=ai_generation.id,
                status=ai_generation.status.value,
                estimated_completion_seconds=ai_generation.estimated_completion_seconds,
                progress={
                    "current_step": ai_generation.current_step.value
                    if ai_generation.current_step
                    else None,
                    "total_steps": 9,
                    "percentage": ai_generation.progress_percentage,
                },
            )

        except QualityThresholdError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Generated content quality below threshold: {str(e)}",
            ) from e
        except InvalidContentError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Generated content validation failed: {str(e)}",
            ) from e
        except AIServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service error: {str(e)}",
            ) from e
        except CategoryDetectionError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Category detection failed: {str(e)}",
            ) from e
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content generation failed: {str(e)}",
            ) from e

    @content_router.get(
        "/processing/{processing_id}/status",
        response_model=ProcessingStatusSchema,
        summary="Get processing status",
        description="Get the current status of a content generation process",
    )
    async def get_processing_status(
        processing_id: UUID,
        use_case: GenerateContentUseCase = use_case_dep,  # noqa: ARG001
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """Get the current status of a content generation process."""
        try:
            # This would need to be implemented in the use case
            # For now, return a mock status
            return ProcessingStatusSchema(
                processing_id=processing_id,
                product_id=UUID("12345678-1234-5678-9012-123456789012"),
                status="processing",
                current_step="title_generation",
                progress_percentage=45.0,
                estimated_completion_seconds=15,
                estimated_remaining_seconds=8,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Processing not found: {processing_id}",
            ) from e

    @content_router.get(
        "/content/{content_id}",
        response_model=GeneratedContentSchema,
        summary="Get generated content",
        description="Get generated content by ID",
    )
    async def get_generated_content(
        content_id: UUID,
        use_case: GenerateContentUseCase = use_case_dep,  # noqa: ARG001
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """Get generated content by ID."""
        try:
            # Get content using the use case
            content = await use_case.get_generated_content(content_id)

            # Convert to response schema
            return GeneratedContentSchema(
                id=content.id,
                product_id=content.product_id,
                title=content.title,
                description=content.description,
                ml_category_id=content.ml_category_id,
                ml_category_name=content.ml_category_name,
                ml_title=content.ml_title,
                ml_price=float(content.ml_price),
                ml_currency_id=content.ml_currency_id,
                ml_available_quantity=content.ml_available_quantity,
                ml_buying_mode=content.ml_buying_mode,
                ml_condition=content.ml_condition,
                ml_listing_type_id=content.ml_listing_type_id,
                ml_attributes=content.ml_attributes,
                ml_sale_terms=content.ml_sale_terms,
                ml_shipping=content.ml_shipping,
                confidence_overall=content.confidence_overall,
                confidence_breakdown=content.confidence_breakdown,
                ai_provider=content.ai_provider,
                ai_model_version=content.ai_model_version,
                generation_time_ms=content.generation_time_ms,
                version=content.version,
                generated_at=content.generated_at,
                updated_at=content.updated_at,
            )

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generated content not found: {content_id}",
            ) from e

    @content_router.post(
        "/content/{content_id}/validate",
        response_model=ContentValidationSchema,
        summary="Validate generated content",
        description="Validate generated content against quality standards",
    )
    async def validate_generated_content(
        content_id: UUID,
        use_case: GenerateContentUseCase = use_case_dep,
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """Validate generated content against quality standards."""
        try:
            validation_results = await use_case.validate_generated_content(content_id)

            return ContentValidationSchema(
                content_id=content_id,
                is_valid=validation_results["is_valid"],
                validation_errors=validation_results["validation_errors"],
                validation_warnings=validation_results["validation_warnings"],
                is_compliant=validation_results["is_compliant"],
                compliance_issues=validation_results["compliance_issues"],
                quality_score=validation_results["quality_score"],
                meets_threshold=validation_results["meets_threshold"],
                improvement_suggestions=validation_results["improvement_suggestions"],
                quality_indicators=validation_results["quality_indicators"],
            )

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generated content not found: {content_id}",
            ) from e

    @content_router.post(
        "/content/{content_id}/enhance",
        response_model=GeneratedContentSchema,
        summary="Enhance generated content",
        description="Enhance existing generated content with additional data",
    )
    async def enhance_generated_content(
        content_id: UUID,
        request: ContentEnhancementRequest,
        use_case: GenerateContentUseCase = use_case_dep,
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """Enhance existing generated content."""
        try:
            enhanced_content = await use_case.enhance_content(
                content_id=content_id,
                enhancement_type=request.enhancement_type,
                additional_data=request.additional_data,
            )

            return GeneratedContentSchema(
                id=enhanced_content.id,
                product_id=enhanced_content.product_id,
                title=enhanced_content.title,
                description=enhanced_content.description,
                ml_category_id=enhanced_content.ml_category_id,
                ml_category_name=enhanced_content.ml_category_name,
                ml_title=enhanced_content.ml_title,
                ml_price=float(enhanced_content.ml_price),
                ml_currency_id=enhanced_content.ml_currency_id,
                ml_available_quantity=enhanced_content.ml_available_quantity,
                ml_buying_mode=enhanced_content.ml_buying_mode,
                ml_condition=enhanced_content.ml_condition,
                ml_listing_type_id=enhanced_content.ml_listing_type_id,
                ml_attributes=enhanced_content.ml_attributes,
                ml_sale_terms=enhanced_content.ml_sale_terms,
                ml_shipping=enhanced_content.ml_shipping,
                confidence_overall=enhanced_content.confidence_overall,
                confidence_breakdown=enhanced_content.confidence_breakdown,
                ai_provider=enhanced_content.ai_provider,
                ai_model_version=enhanced_content.ai_model_version,
                generation_time_ms=enhanced_content.generation_time_ms,
                version=enhanced_content.version,
                generated_at=enhanced_content.generated_at,
                updated_at=enhanced_content.updated_at,
            )

        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generated content not found: {content_id}",
            ) from e

    @content_router.get(
        "/products/{product_id}/versions",
        response_model=ContentVersionsSchema,
        summary="Get content versions",
        description="Get all versions of generated content for a product",
    )
    async def get_content_versions(
        product_id: UUID,
        use_case: GenerateContentUseCase = use_case_dep,
        current_user: User = current_user_dep,  # noqa: ARG001
    ):
        """Get all versions of generated content for a product."""
        try:
            versions = await use_case.get_content_versions(product_id)

            return ContentVersionsSchema(
                product_id=product_id,
                versions=[
                    GeneratedContentSchema(
                        id=version.id,
                        product_id=version.product_id,
                        title=version.title,
                        description=version.description,
                        ml_category_id=version.ml_category_id,
                        ml_category_name=version.ml_category_name,
                        ml_title=version.ml_title,
                        ml_price=float(version.ml_price),
                        ml_currency_id=version.ml_currency_id,
                        ml_available_quantity=version.ml_available_quantity,
                        ml_buying_mode=version.ml_buying_mode,
                        ml_condition=version.ml_condition,
                        ml_listing_type_id=version.ml_listing_type_id,
                        ml_attributes=version.ml_attributes,
                        ml_sale_terms=version.ml_sale_terms,
                        ml_shipping=version.ml_shipping,
                        confidence_overall=version.confidence_overall,
                        confidence_breakdown=version.confidence_breakdown,
                        ai_provider=version.ai_provider,
                        ai_model_version=version.ai_model_version,
                        generation_time_ms=version.generation_time_ms,
                        version=version.version,
                        generated_at=version.generated_at,
                        updated_at=version.updated_at,
                    )
                    for version in versions
                ],
                total_versions=len(versions),
                latest_version=max(version.version for version in versions)
                if versions
                else 0,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving content versions: {str(e)}",
            ) from e

    @content_router.post(
        "/products/{product_id}/regenerate",
        response_model=ContentGenerationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        summary="Regenerate content",
        description="Regenerate content for a product (creates new version)",
    )
    async def regenerate_content(
        product_id: UUID,
        request: ContentGenerationRequest,
        use_case: GenerateContentUseCase = use_case_dep,
        current_user: User = current_user_dep,
    ):
        """Regenerate content for a product (creates new version)."""
        # Force regeneration
        request.regenerate = True

        # Use the same logic as generate_content
        return await generate_content(product_id, request, use_case, current_user)

    # WebSocket endpoint for real-time updates
    @content_router.websocket("/ws/processing/{processing_id}")
    async def websocket_endpoint(
        websocket: WebSocket,
        processing_id: UUID,
    ):
        """WebSocket endpoint for real-time content generation updates."""
        await websocket_manager.connect(websocket, processing_id)

        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()

                # Handle client messages (heartbeat, etc.)
                try:
                    message = ConnectionMessage.model_validate_json(data)

                    if message.type == "heartbeat":
                        await websocket_manager.send_personal_message(
                            processing_id,
                            websocket,
                            {
                                "type": "heartbeat",
                                "timestamp": datetime.now(UTC).isoformat(),
                                "server_time": datetime.now(UTC).isoformat(),
                            },
                        )

                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")

        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, processing_id)
            logger.info(f"WebSocket disconnected for processing: {processing_id}")

    # Helper function to monitor processing progress
    async def _monitor_processing_progress(
        processing_id: UUID,
        use_case: GenerateContentUseCase,  # noqa: ARG001
    ):
        """Monitor processing progress and send WebSocket updates."""
        try:
            # This would poll the processing status and send updates
            # For now, we'll simulate progress updates

            steps = [
                ("image_analysis", 15),
                ("content_extraction", 25),
                ("category_detection", 40),
                ("title_generation", 55),
                ("description_generation", 70),
                ("attribute_mapping", 80),
                ("price_estimation", 85),
                ("quality_validation", 95),
                ("content_finalization", 100),
            ]

            for step_name, progress in steps:
                # Simulate processing time
                await asyncio.sleep(2)

                # Send progress update
                await websocket_manager.broadcast_to_processing(
                    processing_id,
                    ProgressUpdateMessage(
                        type="progress_update",
                        processing_id=processing_id,
                        timestamp=datetime.now(UTC),
                        data={
                            "processing_id": str(processing_id),
                            "status": "processing",
                            "current_step": step_name,
                            "progress_percentage": progress,
                            "estimated_remaining_seconds": max(
                                0, (100 - progress) * 0.3
                            ),
                        },
                    ).model_dump(),
                )

            # Send completion message
            await websocket_manager.broadcast_to_processing(
                processing_id,
                CompletionMessage(
                    type="completion",
                    processing_id=processing_id,
                    timestamp=datetime.now(UTC),
                    data={
                        "processing_id": str(processing_id),
                        "status": "completed",
                        "generated_content": {
                            "id": "mock_content_id",
                            "title": "iPhone 13 Pro 128GB Usado Excelente Estado",
                            "description": "iPhone 13 Pro de 128GB en excelente estado...",
                            "confidence_overall": 0.87,
                            "confidence_breakdown": {
                                "title": 0.92,
                                "description": 0.85,
                                "category": 0.88,
                                "price": 0.75,
                                "attributes": 0.90,
                            },
                        },
                    },
                ).model_dump(),
            )

        except Exception as e:
            logger.error(f"Error in processing monitor: {e}")

            # Send error message
            await websocket_manager.broadcast_to_processing(
                processing_id,
                ErrorMessage(
                    type="error",
                    processing_id=processing_id,
                    timestamp=datetime.now(UTC),
                    data={
                        "processing_id": str(processing_id),
                        "status": "failed",
                        "error_message": str(e),
                        "error_code": "PROCESSING_ERROR",
                    },
                ).model_dump(),
            )

        finally:
            # Clean up task
            if processing_id in websocket_manager.connection_tasks:
                del websocket_manager.connection_tasks[processing_id]

    return content_router
