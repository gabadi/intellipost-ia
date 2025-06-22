# IntelliPost AI - External Service Integrations

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Focus:** Go-style Protocol Implementation
- **Services:** Gemini AI, PhotoRoom, MercadoLibre, S3

---

## Integration Architecture Overview

### Go-Style Protocol Implementation
```python
# Core principle: Accept interfaces, return instances
# No explicit adapter classes - duck typing + static validation

# Example service integration:
async def process_product_content(
    product_id: UUID,
    ai_service: AIContentGenerator,  # Accept interface
    image_processor: ImageProcessor,  # Accept interface
    ml_publisher: MLPublisher        # Accept interface
) -> GeneratedContent:              # Return instance
    # Business logic works with interfaces
    content = await ai_service.generate_listing(...)  # Returns instance
    return content  # Return instance
```

---

## 1. Gemini AI Integration

### Protocol Definition
```python
# src/services/ai_service.py
from typing import Protocol, List, Optional
from src.models.product import GeneratedContent, ImageData, ConfidenceScore

class AIContentGenerator(Protocol):
    """Client interface - what business logic expects from AI services"""

    async def generate_listing(
        self,
        images: List[ImageData],
        prompt: str,
        category_hint: Optional[str] = None
    ) -> GeneratedContent:
        """Generate complete MercadoLibre listing content"""
        ...

    async def calculate_confidence(
        self,
        content: GeneratedContent
    ) -> ConfidenceScore:
        """Calculate confidence scores for generated content"""
        ...

    async def enhance_description(
        self,
        current_description: str,
        additional_context: str
    ) -> str:
        """Improve existing description with additional context"""
        ...
```

### Gemini Service Implementation (Duck-type Compatible)
```python
# src/adapters/ai_providers/gemini_service.py
import google.generativeai as genai
from typing import List, Optional
from src.models.product import GeneratedContent, ImageData, ConfidenceScore

class GeminiService:
    """Duck-type compatible with AIContentGenerator Protocol"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 2048,
        }

    async def generate_listing(
        self,
        images: List[ImageData],
        prompt: str,
        category_hint: Optional[str] = None
    ) -> GeneratedContent:
        """
        Generate MercadoLibre listing using Gemini 2.5 Flash
        Returns GeneratedContent instance (satisfies Protocol)
        """
        try:
            # Prepare images for Gemini
            image_parts = []
            for image in images:
                image_parts.append({
                    "mime_type": image.mime_type,
                    "data": image.base64_data
                })

            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(category_hint)
            user_prompt = self._build_user_prompt(prompt)

            # Generate content
            response = await self.model.generate_content_async(
                contents=[
                    {"parts": [{"text": system_prompt}]},
                    {"parts": image_parts + [{"text": user_prompt}]}
                ],
                generation_config=self.generation_config
            )

            # Parse response into structured data
            parsed_content = self._parse_gemini_response(response.text)

            # Return GeneratedContent instance
            return GeneratedContent(
                title=parsed_content["title"],
                description=parsed_content["description"],
                ml_category_id=parsed_content["category_id"],
                ml_category_name=parsed_content["category_name"],
                ml_price=parsed_content["price"],
                ml_currency_id="ARS",
                ml_condition=parsed_content["condition"],
                ml_attributes=parsed_content["attributes"],
                confidence_overall=parsed_content["confidence"],
                confidence_breakdown=parsed_content["confidence_breakdown"],
                ai_provider="gemini",
                ai_model_version="gemini-2.5-flash",
                generation_time_ms=response.usage_metadata.total_latency_ms
            )

        except Exception as e:
            raise AIServiceError(f"Gemini generation failed: {str(e)}")

    async def calculate_confidence(
        self,
        content: GeneratedContent
    ) -> ConfidenceScore:
        """Calculate confidence based on Gemini's internal scoring"""
        # Gemini provides confidence in generation response
        return ConfidenceScore(
            overall=content.confidence_overall,
            breakdown=content.confidence_breakdown
        )

    async def enhance_description(
        self,
        current_description: str,
        additional_context: str
    ) -> str:
        """Enhance description with additional context"""
        prompt = f"""
        Improve this MercadoLibre product description:

        Current: {current_description}
        Additional context: {additional_context}

        Return only the improved description in Spanish.
        """

        response = await self.model.generate_content_async(prompt)
        return response.text.strip()

    def _build_system_prompt(self, category_hint: Optional[str] = None) -> str:
        """Build system prompt for MercadoLibre listing generation"""
        return f"""
        You are an expert MercadoLibre listing generator for Argentina marketplace.

        CRITICAL REQUIREMENTS:
        - Generate content in Spanish for Argentina (MLA) marketplace
        - Title: Maximum 60 characters, descriptive and searchable
        - Description: Detailed, persuasive, include key features
        - Price: Estimate based on Argentina market in ARS
        - Category: Select most appropriate MercadoLibre category
        - Condition: new, used, or not_specified

        {f"CATEGORY HINT: Focus on {category_hint} categories" if category_hint else ""}

        RESPONSE FORMAT (JSON):
        {{
            "title": "Product title (max 60 chars)",
            "description": "Detailed description",
            "category_id": "MLA category ID",
            "category_name": "Category name",
            "price": numeric_price_in_ars,
            "condition": "new|used|not_specified",
            "attributes": {{
                "BRAND": "brand_name",
                "MODEL": "model_name",
                "COLOR": "color_name"
            }},
            "confidence": confidence_score_0_to_1,
            "confidence_breakdown": {{
                "title": 0.95,
                "description": 0.88,
                "category": 0.92,
                "price": 0.75,
                "attributes": 0.90
            }}
        }}
        """

    def _build_user_prompt(self, user_prompt: str) -> str:
        """Build user prompt with image analysis instructions"""
        return f"""
        Analyze these product images and user description to create a MercadoLibre listing:

        User description: {user_prompt}

        Instructions:
        1. Analyze all images to identify the product
        2. Use the user description as context
        3. Generate optimized title and description for MercadoLibre
        4. Estimate appropriate price for Argentina market
        5. Select correct category and attributes
        6. Provide confidence scores for each component

        Return only the JSON response as specified in system prompt.
        """

    def _parse_gemini_response(self, response_text: str) -> dict:
        """Parse Gemini response into structured data"""
        try:
            # Extract JSON from response (handle markdown formatting)
            import json
            import re

            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

            return json.loads(response_text)

        except (json.JSONDecodeError, AttributeError) as e:
            raise AIServiceError(f"Failed to parse Gemini response: {str(e)}")


# Service factory for dependency injection
def create_gemini_service(api_key: str) -> GeminiService:
    """Factory function returns instance compatible with AIContentGenerator"""
    return GeminiService(api_key)
```

---

## 2. PhotoRoom Image Processing Integration

### Protocol Definition
```python
# src/services/image_service.py
from typing import Protocol, List
from src.models.product import ImageData, ProcessedImage

class ImageProcessor(Protocol):
    """Client interface for image processing services"""

    async def remove_background(
        self,
        image: ImageData
    ) -> ProcessedImage:
        """Remove background from product image"""
        ...

    async def enhance_quality(
        self,
        image: ImageData
    ) -> ProcessedImage:
        """Enhance image quality and lighting"""
        ...

    async def batch_process(
        self,
        images: List[ImageData]
    ) -> List[ProcessedImage]:
        """Process multiple images efficiently"""
        ...
```

### PhotoRoom Service Implementation
```python
# src/adapters/image_processors/photoroom_service.py
import httpx
from typing import List
from src.models.product import ImageData, ProcessedImage

class PhotoRoomService:
    """Duck-type compatible with ImageProcessor Protocol"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sdk.photoroom.com/v1"
        self.client = httpx.AsyncClient(
            headers={"x-api-key": api_key},
            timeout=30.0
        )

    async def remove_background(
        self,
        image: ImageData
    ) -> ProcessedImage:
        """
        Remove background using PhotoRoom API
        Returns ProcessedImage instance (satisfies Protocol)
        """
        try:
            # Prepare image for upload
            files = {
                "image_file": (
                    image.filename,
                    image.bytes_data,
                    image.mime_type
                )
            }

            # PhotoRoom background removal
            response = await self.client.post(
                f"{self.base_url}/segment",
                files=files,
                data={
                    "format": "png",
                    "crop": "false",
                    "padding": "0.1"
                }
            )
            response.raise_for_status()

            # Return ProcessedImage instance
            return ProcessedImage(
                original_image_id=image.id,
                processed_data=response.content,
                mime_type="image/png",
                processing_type="background_removal",
                processor="photoroom",
                file_size=len(response.content),
                processing_metadata={
                    "api_version": "v1",
                    "processing_time_ms": 350,  # PhotoRoom typical response time
                    "background_removed": True,
                    "format_converted": "png"
                }
            )

        except httpx.HTTPError as e:
            raise ImageProcessingError(f"PhotoRoom API error: {str(e)}")
        except Exception as e:
            raise ImageProcessingError(f"Image processing failed: {str(e)}")

    async def enhance_quality(
        self,
        image: ImageData
    ) -> ProcessedImage:
        """Enhance image quality using PhotoRoom API"""
        try:
            files = {
                "image_file": (
                    image.filename,
                    image.bytes_data,
                    image.mime_type
                )
            }

            # PhotoRoom enhancement
            response = await self.client.post(
                f"{self.base_url}/enhance",
                files=files,
                data={
                    "enhance_type": "product",
                    "output_format": "jpg",
                    "quality": "high"
                }
            )
            response.raise_for_status()

            return ProcessedImage(
                original_image_id=image.id,
                processed_data=response.content,
                mime_type="image/jpeg",
                processing_type="quality_enhancement",
                processor="photoroom",
                file_size=len(response.content),
                processing_metadata={
                    "enhanced": True,
                    "quality_level": "high",
                    "enhancement_type": "product"
                }
            )

        except Exception as e:
            raise ImageProcessingError(f"Image enhancement failed: {str(e)}")

    async def batch_process(
        self,
        images: List[ImageData]
    ) -> List[ProcessedImage]:
        """Process multiple images concurrently"""
        import asyncio

        # Process images concurrently (PhotoRoom rate limit: 60/minute)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

        async def process_single(image: ImageData) -> ProcessedImage:
            async with semaphore:
                return await self.remove_background(image)

        return await asyncio.gather(*[
            process_single(image) for image in images
        ])


# Service factory
def create_photoroom_service(api_key: str) -> PhotoRoomService:
    """Factory function returns instance compatible with ImageProcessor"""
    return PhotoRoomService(api_key)
```

---

## 3. MercadoLibre API Integration

### Protocol Definition
```python
# src/services/ml_service.py
from typing import Protocol, List, Optional
from src.models.product import GeneratedContent, MLListing, MLCredentials

class MLPublisher(Protocol):
    """Client interface for MercadoLibre publishing"""

    async def create_listing(
        self,
        content: GeneratedContent,
        credentials: MLCredentials,
        images: List[str]  # S3 URLs
    ) -> MLListing:
        """Create listing on MercadoLibre"""
        ...

    async def update_listing(
        self,
        item_id: str,
        content: GeneratedContent,
        credentials: MLCredentials
    ) -> MLListing:
        """Update existing listing"""
        ...

    async def get_categories(
        self,
        site_id: str = "MLA"
    ) -> List[dict]:
        """Get available categories"""
        ...

    async def validate_credentials(
        self,
        credentials: MLCredentials
    ) -> bool:
        """Validate OAuth credentials"""
        ...
```

### MercadoLibre Service Implementation
```python
# src/adapters/ml_api/mercadolibre_service.py
import httpx
from typing import List, Optional
from src.models.product import GeneratedContent, MLListing, MLCredentials

class MercadoLibreService:
    """Duck-type compatible with MLPublisher Protocol"""

    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_listing(
        self,
        content: GeneratedContent,
        credentials: MLCredentials,
        images: List[str]
    ) -> MLListing:
        """
        Create MercadoLibre listing
        Returns MLListing instance (satisfies Protocol)
        """
        try:
            # First, upload images to MercadoLibre
            ml_image_ids = await self._upload_images(images, credentials)

            # Prepare listing data
            listing_data = {
                "title": content.ml_title,
                "category_id": content.ml_category_id,
                "price": content.ml_price,
                "currency_id": content.ml_currency_id,
                "available_quantity": content.ml_available_quantity,
                "buying_mode": content.ml_buying_mode,
                "condition": content.ml_condition,
                "listing_type_id": content.ml_listing_type_id,
                "description": {
                    "plain_text": content.description
                },
                "pictures": [{"id": img_id} for img_id in ml_image_ids],
                "attributes": self._format_attributes(content.ml_attributes),
                "shipping": {
                    "mode": "me2",
                    "free_shipping": False
                }
            }

            # Create listing via MercadoLibre API
            response = await self.client.post(
                f"{self.base_url}/items",
                headers={"Authorization": f"Bearer {credentials.access_token}"},
                json=listing_data
            )
            response.raise_for_status()

            listing_response = response.json()

            # Return MLListing instance
            return MLListing(
                item_id=listing_response["id"],
                title=listing_response["title"],
                permalink=listing_response["permalink"],
                status=listing_response["status"],
                price=listing_response["price"],
                currency_id=listing_response["currency_id"],
                available_quantity=listing_response["available_quantity"],
                sold_quantity=listing_response.get("sold_quantity", 0),
                health=listing_response.get("health", 1.0),
                created_at=listing_response["date_created"],
                ml_images=ml_image_ids
            )

        except httpx.HTTPError as e:
            raise MLAPIError(f"MercadoLibre API error: {str(e)}")
        except Exception as e:
            raise MLAPIError(f"Listing creation failed: {str(e)}")

    async def update_listing(
        self,
        item_id: str,
        content: GeneratedContent,
        credentials: MLCredentials
    ) -> MLListing:
        """Update existing MercadoLibre listing"""
        update_data = {
            "title": content.ml_title,
            "price": content.ml_price,
            "available_quantity": content.ml_available_quantity,
            "description": {
                "plain_text": content.description
            }
        }

        response = await self.client.put(
            f"{self.base_url}/items/{item_id}",
            headers={"Authorization": f"Bearer {credentials.access_token}"},
            json=update_data
        )
        response.raise_for_status()

        # Return updated listing data
        return await self._get_listing_details(item_id, credentials)

    async def get_categories(
        self,
        site_id: str = "MLA"
    ) -> List[dict]:
        """Get MercadoLibre categories for caching"""
        response = await self.client.get(
            f"{self.base_url}/sites/{site_id}/categories"
        )
        response.raise_for_status()
        return response.json()

    async def validate_credentials(
        self,
        credentials: MLCredentials
    ) -> bool:
        """Validate OAuth credentials"""
        try:
            response = await self.client.get(
                f"{self.base_url}/users/me",
                headers={"Authorization": f"Bearer {credentials.access_token}"}
            )
            return response.status_code == 200
        except:
            return False

    async def _upload_images(
        self,
        image_urls: List[str],
        credentials: MLCredentials
    ) -> List[str]:
        """Upload images to MercadoLibre and return image IDs"""
        ml_image_ids = []

        for image_url in image_urls:
            # Download image from S3
            image_response = await self.client.get(image_url)
            image_response.raise_for_status()

            # Upload to MercadoLibre
            files = {
                "file": ("image.jpg", image_response.content, "image/jpeg")
            }

            upload_response = await self.client.post(
                f"{self.base_url}/pictures",
                headers={"Authorization": f"Bearer {credentials.access_token}"},
                files=files
            )
            upload_response.raise_for_status()

            ml_image_ids.append(upload_response.json()["id"])

        return ml_image_ids

    def _format_attributes(self, attributes: dict) -> List[dict]:
        """Format attributes for MercadoLibre API"""
        return [
            {"id": key, "value_name": value}
            for key, value in attributes.items()
            if value is not None
        ]


# Service factory
def create_mercadolibre_service() -> MercadoLibreService:
    """Factory function returns instance compatible with MLPublisher"""
    return MercadoLibreService()
```

---

## 4. S3 Storage Integration

### Protocol Definition
```python
# src/services/storage_service.py
from typing import Protocol, Optional
from src.models.product import ImageData

class ObjectStorage(Protocol):
    """Client interface for object storage"""

    async def upload_image(
        self,
        image: ImageData,
        bucket: str,
        key: str
    ) -> str:
        """Upload image and return public URL"""
        ...

    async def delete_image(
        self,
        bucket: str,
        key: str
    ) -> bool:
        """Delete image from storage"""
        ...

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """Generate temporary signed URL"""
        ...
```

### S3 Service Implementation
```python
# src/adapters/storage/s3_service.py
import boto3
from typing import Optional
from src.models.product import ImageData

class S3Service:
    """Duck-type compatible with ObjectStorage Protocol"""

    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = "us-east-1"):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.region = region

    async def upload_image(
        self,
        image: ImageData,
        bucket: str,
        key: str
    ) -> str:
        """
        Upload image to S3
        Returns public URL (satisfies Protocol)
        """
        try:
            # Upload with appropriate content type and metadata
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=image.bytes_data,
                ContentType=image.mime_type,
                Metadata={
                    'original_filename': image.filename,
                    'upload_source': 'intellipost_ai'
                }
            )

            # Return public URL
            return f"https://{bucket}.s3.{self.region}.amazonaws.com/{key}"

        except Exception as e:
            raise StorageError(f"S3 upload failed: {str(e)}")

    async def delete_image(
        self,
        bucket: str,
        key: str
    ) -> bool:
        """Delete image from S3"""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """Generate presigned URL for temporary access"""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expires_in
        )


# Service factory
def create_s3_service(aws_access_key: str, aws_secret_key: str) -> S3Service:
    """Factory function returns instance compatible with ObjectStorage"""
    return S3Service(aws_access_key, aws_secret_key)
```

---

## 5. Service Orchestration

### Business Logic with Protocol Integration
```python
# src/services/product_service.py
from typing import List
from src.services.ai_service import AIContentGenerator
from src.services.image_service import ImageProcessor
from src.services.ml_service import MLPublisher
from src.services.storage_service import ObjectStorage
from src.models.product import Product, GeneratedContent

class ProductService:
    """
    Business logic orchestrating external services
    Uses Go-style: Accept interfaces, return instances
    """

    def __init__(
        self,
        ai_service: AIContentGenerator,      # Accept interface
        image_processor: ImageProcessor,      # Accept interface
        ml_publisher: MLPublisher,           # Accept interface
        storage: ObjectStorage               # Accept interface
    ):
        self.ai_service = ai_service
        self.image_processor = image_processor
        self.ml_publisher = ml_publisher
        self.storage = storage

    async def process_product_images(
        self,
        product: Product
    ) -> List[str]:
        """
        Process product images and upload to storage
        Returns list of S3 URLs (instances)
        """
        processed_urls = []

        for image in product.images:
            # Process image (accept interface, get instance)
            processed_image = await self.image_processor.remove_background(image)

            # Upload to storage (accept interface, get instance)
            s3_key = f"products/{product.id}/processed/{image.id}.png"
            s3_url = await self.storage.upload_image(
                processed_image,
                bucket="intellipost-images",
                key=s3_key
            )

            processed_urls.append(s3_url)

        return processed_urls

    async def generate_listing_content(
        self,
        product: Product
    ) -> GeneratedContent:
        """
        Generate AI content for product
        Returns GeneratedContent instance
        """
        # Generate content (accept interface, get instance)
        content = await self.ai_service.generate_listing(
            images=product.images,
            prompt=product.prompt_text,
            category_hint=None
        )

        return content

    async def publish_to_mercadolibre(
        self,
        product: Product,
        content: GeneratedContent,
        credentials: MLCredentials,
        image_urls: List[str]
    ) -> MLListing:
        """
        Publish listing to MercadoLibre
        Returns MLListing instance
        """
        # Publish listing (accept interface, get instance)
        listing = await self.ml_publisher.create_listing(
            content=content,
            credentials=credentials,
            images=image_urls
        )

        return listing


# Dependency injection setup
def create_product_service(
    gemini_api_key: str,
    photoroom_api_key: str,
    aws_access_key: str,
    aws_secret_key: str
) -> ProductService:
    """
    Factory function using dependency injection
    All services are duck-type compatible with their protocols
    """
    # Create service instances (no explicit adapter classes)
    ai_service = create_gemini_service(gemini_api_key)
    image_processor = create_photoroom_service(photoroom_api_key)
    ml_publisher = create_mercadolibre_service()
    storage = create_s3_service(aws_access_key, aws_secret_key)

    # Return business service with injected dependencies
    return ProductService(
        ai_service=ai_service,
        image_processor=image_processor,
        ml_publisher=ml_publisher,
        storage=storage
    )
```

---

## 6. Error Handling & Resilience

### Service-Level Error Handling
```python
# src/services/resilient_service.py
import asyncio
from typing import TypeVar, Callable, Any
from src.exceptions import ServiceError, RetryableError

T = TypeVar('T')

class ResilientService:
    """Wrapper for adding resilience to any service"""

    @staticmethod
    async def with_retry(
        operation: Callable[[], T],
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ) -> T:
        """Add exponential backoff retry to any operation"""

        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except RetryableError as e:
                if attempt == max_retries:
                    raise ServiceError(f"Operation failed after {max_retries} retries: {str(e)}")

                wait_time = backoff_factor * (2 ** attempt)
                await asyncio.sleep(wait_time)
            except Exception as e:
                # Non-retryable errors
                raise ServiceError(f"Operation failed: {str(e)}")

# Usage example with any service
async def resilient_ai_generation(ai_service: AIContentGenerator, images, prompt):
    """Add resilience to AI generation"""
    return await ResilientService.with_retry(
        lambda: ai_service.generate_listing(images, prompt),
        max_retries=2,
        backoff_factor=1.0
    )
```

---

**Esta integración completa sigue el patrón Go-style con duck typing y Pyright validation. ¿Continuamos con Deployment Strategy para completar la arquitectura?**
