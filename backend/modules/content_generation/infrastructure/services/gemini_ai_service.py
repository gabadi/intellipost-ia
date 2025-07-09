"""
Gemini AI Service implementation.

This module provides integration with Google's Gemini AI API for multimodal content generation,
specifically optimized for MercadoLibre listing creation.
"""

import asyncio
import json
import logging
import time
from decimal import Decimal
from typing import Any
from uuid import uuid4

import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPICallError,
    ServiceUnavailable,
    TooManyRequests,
)
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from modules.content_generation.domain.entities import (
    ConfidenceScore,
    GeneratedContent,
)
from modules.content_generation.domain.exceptions import (
    AIServiceError,
    AIServiceRateLimitError,
    ConfigurationError,
    InvalidContentError,
)
from modules.content_generation.domain.ports.ai_service_protocols import (
    ImageData,
)
from modules.content_generation.infrastructure.config import ai_content_config

logger = logging.getLogger(__name__)


class GeminiAIService:
    """
    Google Gemini AI service implementation for content generation.

    This service provides multimodal content generation capabilities using
    Google's Gemini 2.5 Flash model, optimized for MercadoLibre listings.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize the Gemini AI service.

        Args:
            api_key: Google API key for Gemini
            model_name: Name of the Gemini model to use
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            timeout_seconds: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key or ai_content_config.gemini_api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        if not self.api_key:
            raise ConfigurationError(
                "Gemini API key is required", config_key="gemini_api_key"
            )

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                top_p=0.9,
                top_k=40,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUAL_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        logger.info(f"Initialized Gemini AI service with model: {self.model_name}")

    async def generate_listing(
        self,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: dict[str, float] | None = None,
        target_audience: str | None = None,
    ) -> GeneratedContent:
        """
        Generate complete MercadoLibre listing content using Gemini AI.

        Args:
            images: List of product images
            prompt: User description of the product
            category_hint: Optional category suggestion
            price_range: Optional price range guidance
            target_audience: Optional target audience specification

        Returns:
            GeneratedContent: Complete generated listing content

        Raises:
            AIServiceError: If content generation fails
            AIServiceTimeoutError: If request times out
            AIServiceRateLimitError: If rate limit is exceeded
        """
        start_time = time.time()

        try:
            # Prepare multimodal input
            input_parts = await self._prepare_multimodal_input(
                images, prompt, category_hint, price_range, target_audience
            )

            # Generate content with retry logic
            response = await self._generate_with_retry(input_parts)

            # Parse the response
            generated_data = self._parse_generation_response(response)

            # Calculate generation time
            generation_time_ms = int((time.time() - start_time) * 1000)

            # Create GeneratedContent entity
            content = GeneratedContent(
                id=uuid4(),
                product_id=uuid4(),  # This will be set by the calling use case
                title=generated_data["title"],
                description=generated_data["description"],
                ml_category_id=generated_data["ml_category_id"],
                ml_category_name=generated_data["ml_category_name"],
                ml_title=generated_data["ml_title"],
                ml_price=Decimal(str(generated_data["ml_price"])),
                ml_currency_id=generated_data.get("ml_currency_id", "ARS"),
                ml_available_quantity=generated_data.get("ml_available_quantity", 1),
                ml_buying_mode=generated_data.get("ml_buying_mode", "buy_it_now"),
                ml_condition=generated_data.get("ml_condition", "new"),
                ml_listing_type_id=generated_data.get(
                    "ml_listing_type_id", "gold_special"
                ),
                ml_attributes=generated_data.get("ml_attributes", {}),
                ml_sale_terms=generated_data.get("ml_sale_terms", {}),
                ml_shipping=generated_data.get("ml_shipping", {}),
                confidence_overall=generated_data["confidence_overall"],
                confidence_breakdown=generated_data["confidence_breakdown"],
                ai_provider="gemini",
                ai_model_version=self.model_name,
                generation_time_ms=generation_time_ms,
                version=1,
                generated_at=time.time(),
            )

            logger.info(f"Generated content successfully in {generation_time_ms}ms")
            return content

        except TooManyRequests as e:
            logger.error(f"Gemini API rate limit exceeded: {e}")
            raise AIServiceRateLimitError(
                "Rate limit exceeded for Gemini API",
                provider="gemini",
                model_version=self.model_name,
                retry_after_seconds=60,
            ) from e
        except ServiceUnavailable as e:
            logger.error(f"Gemini API service unavailable: {e}")
            raise AIServiceError(
                "Gemini API service is temporarily unavailable",
                provider="gemini",
                model_version=self.model_name,
            ) from e
        except GoogleAPICallError as e:
            logger.error(f"Gemini API call failed: {e}")
            raise AIServiceError(
                f"Gemini API call failed: {str(e)}",
                provider="gemini",
                model_version=self.model_name,
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in content generation: {e}")
            raise AIServiceError(
                f"Unexpected error in content generation: {str(e)}",
                provider="gemini",
                model_version=self.model_name,
            ) from e

    async def calculate_confidence(
        self,
        content: GeneratedContent,
    ) -> ConfidenceScore:
        """
        Calculate confidence scores for generated content.

        Args:
            content: Generated content to analyze

        Returns:
            ConfidenceScore: Confidence score breakdown
        """
        # For now, return the confidence already calculated during generation
        return ConfidenceScore(
            overall=content.confidence_overall,
            breakdown=content.confidence_breakdown,
        )

    async def validate_content(
        self,
        content: GeneratedContent,
    ) -> dict[str, Any]:
        """
        Validate generated content against quality standards.

        Args:
            content: Generated content to validate

        Returns:
            Dict containing validation results
        """
        validation_errors = []

        # Check title length
        if len(content.ml_title) > 60:
            validation_errors.append("Title exceeds 60 character limit")

        # Check description length
        if len(content.description) < 50:
            validation_errors.append("Description is too short")

        # Check price validity
        if content.ml_price <= 0:
            validation_errors.append("Price must be positive")

        # Check category is set
        if not content.ml_category_id:
            validation_errors.append("Category ID is required")

        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "quality_score": content.confidence_overall,
        }

    async def generate_title_variations(
        self,
        base_title: str,
        product_info: str,
        count: int = 3,
    ) -> list[str]:
        """
        Generate multiple title variations for A/B testing.

        Args:
            base_title: Base title to create variations from
            product_info: Product information for context
            count: Number of variations to generate

        Returns:
            List of title variations
        """
        prompt = self._create_title_variation_prompt(base_title, product_info, count)

        try:
            response = await self._generate_with_retry([prompt])
            variations = self._parse_title_variations(response)
            return variations[:count]
        except Exception as e:
            logger.error(f"Error generating title variations: {e}")
            return [base_title]  # Return original title as fallback

    async def enhance_description(
        self,
        base_description: str,
        product_features: dict[str, Any],
        target_length: int | None = None,
    ) -> str:
        """
        Enhance an existing description with additional features.

        Args:
            base_description: Original description
            product_features: Additional product features
            target_length: Target description length

        Returns:
            Enhanced description
        """
        prompt = self._create_description_enhancement_prompt(
            base_description, product_features, target_length
        )

        try:
            response = await self._generate_with_retry([prompt])
            enhanced_description = self._parse_description_response(response)
            return enhanced_description
        except Exception as e:
            logger.error(f"Error enhancing description: {e}")
            return base_description  # Return original as fallback

    async def extract_product_features(
        self,
        images: list[ImageData],
        prompt: str,
    ) -> dict[str, Any]:
        """
        Extract product features from images and prompt.

        Args:
            images: Product images
            prompt: User description

        Returns:
            Dict of extracted features
        """
        extraction_prompt = self._create_feature_extraction_prompt(prompt)
        input_parts = await self._prepare_multimodal_input(images, extraction_prompt)

        try:
            response = await self._generate_with_retry(input_parts)
            features = self._parse_feature_extraction_response(response)
            return features
        except Exception as e:
            logger.error(f"Error extracting product features: {e}")
            return {}

    async def estimate_price(
        self,
        product_features: dict[str, Any],
        category_id: str,
        condition: str = "new",
    ) -> dict[str, Any]:
        """
        Estimate product price based on features and category.

        Args:
            product_features: Product features
            category_id: MercadoLibre category ID
            condition: Product condition

        Returns:
            Dict with price estimation
        """
        prompt = self._create_price_estimation_prompt(
            product_features, category_id, condition
        )

        try:
            response = await self._generate_with_retry([prompt])
            price_info = self._parse_price_estimation_response(response)
            return price_info
        except Exception as e:
            logger.error(f"Error estimating price: {e}")
            return {"estimated_price": 0.0, "confidence": 0.0}

    async def check_content_quality(
        self,
        content: GeneratedContent,
        quality_threshold: float = 0.7,
    ) -> bool:
        """
        Check if content meets quality standards.

        Args:
            content: Generated content to check
            quality_threshold: Minimum quality threshold

        Returns:
            True if content meets quality standards
        """
        return content.confidence_overall >= quality_threshold

    async def _prepare_multimodal_input(
        self,
        images: list[ImageData],
        prompt: str,
        category_hint: str | None = None,
        price_range: dict[str, float] | None = None,
        target_audience: str | None = None,
    ) -> list[Any]:
        """Prepare multimodal input for Gemini API."""
        input_parts = []

        # Add images
        for image in images:
            # For now, we'll use a placeholder - in production, you'd fetch the image
            # from S3 and convert to the appropriate format
            input_parts.append(
                {
                    "mime_type": f"image/{image.file_format.lower()}",
                    "data": f"placeholder_image_{image.s3_key}",  # This would be actual image data
                }
            )

        # Add the main prompt
        main_prompt = self._create_mercadolibre_prompt(
            prompt, category_hint, price_range, target_audience
        )
        input_parts.append(main_prompt)

        return input_parts

    def _create_mercadolibre_prompt(
        self,
        user_prompt: str,
        category_hint: str | None = None,
        price_range: dict[str, float] | None = None,
        target_audience: str | None = None,
    ) -> str:
        """Create optimized prompt for MercadoLibre content generation."""

        base_prompt = f"""
Analiza las imágenes del producto y la descripción del usuario para generar contenido optimizado para MercadoLibre Argentina.

DESCRIPCIÓN DEL USUARIO: {user_prompt}

INSTRUCCIONES:
1. Genera un título optimizado para MercadoLibre (máximo 60 caracteres)
2. Crea una descripción completa en español optimizada para móviles
3. Identifica la categoría más apropiada de MercadoLibre
4. Estima un precio competitivo en pesos argentinos
5. Sugiere atributos específicos para la categoría
6. Proporciona puntuaciones de confianza para cada componente

CONTEXTO ADICIONAL:
"""

        if category_hint:
            base_prompt += f"- Sugerencia de categoría: {category_hint}\n"

        if price_range:
            base_prompt += f"- Rango de precio esperado: ${price_range.get('min', 0)} - ${price_range.get('max', 999999)}\n"

        if target_audience:
            base_prompt += f"- Audiencia objetivo: {target_audience}\n"

        base_prompt += """
FORMATO DE RESPUESTA (JSON):
{
    "title": "Título descriptivo del producto",
    "description": "Descripción completa en español, formato móvil, con características clave, beneficios y especificaciones",
    "ml_category_id": "MLA123456",
    "ml_category_name": "Nombre de la categoría",
    "ml_title": "Título optimizado ≤60 caracteres",
    "ml_price": 12345.67,
    "ml_currency_id": "ARS",
    "ml_available_quantity": 1,
    "ml_buying_mode": "buy_it_now",
    "ml_condition": "new",
    "ml_listing_type_id": "gold_special",
    "ml_attributes": {
        "ATTRIBUTE_ID": "valor",
        "OTRO_ATRIBUTO": "valor"
    },
    "ml_sale_terms": {
        "id": "WARRANTY_TYPE",
        "value_name": "Garantía del vendedor"
    },
    "ml_shipping": {
        "mode": "me2",
        "free_shipping": true
    },
    "confidence_overall": 0.85,
    "confidence_breakdown": {
        "title": 0.90,
        "description": 0.85,
        "category": 0.80,
        "price": 0.75,
        "attributes": 0.88
    }
}

RESPONDE SOLO CON JSON VÁLIDO:
"""

        return base_prompt

    def _create_title_variation_prompt(
        self,
        base_title: str,
        product_info: str,
        count: int,
    ) -> str:
        """Create prompt for generating title variations."""
        return f"""
Genera {count} variaciones del título para MercadoLibre Argentina.

TÍTULO BASE: {base_title}
INFORMACIÓN DEL PRODUCTO: {product_info}

REQUISITOS:
- Máximo 60 caracteres cada título
- Optimizado para búsqueda en MercadoLibre
- Diferentes enfoques (beneficios, características, palabras clave)
- Mantener la información esencial

FORMATO DE RESPUESTA:
{{
    "variations": [
        "Título variación 1",
        "Título variación 2",
        "Título variación 3"
    ]
}}

RESPONDE SOLO CON JSON VÁLIDO:
"""

    def _create_description_enhancement_prompt(
        self,
        base_description: str,
        product_features: dict[str, Any],
        target_length: int | None = None,
    ) -> str:
        """Create prompt for enhancing descriptions."""
        length_instruction = (
            f"Longitud objetivo: {target_length} caracteres" if target_length else ""
        )

        return f"""
Mejora la descripción del producto para MercadoLibre Argentina.

DESCRIPCIÓN ACTUAL: {base_description}
CARACTERÍSTICAS ADICIONALES: {json.dumps(product_features, ensure_ascii=False)}
{length_instruction}

MEJORAS REQUERIDAS:
- Formato optimizado para móviles
- Estructura clara con bullets o párrafos cortos
- Beneficios destacados
- Especificaciones técnicas
- Llamada a la acción

RESPONDE SOLO CON LA DESCRIPCIÓN MEJORADA:
"""

    def _create_feature_extraction_prompt(self, prompt: str) -> str:
        """Create prompt for extracting product features."""
        return f"""
Extrae las características del producto de las imágenes y descripción.

DESCRIPCIÓN: {prompt}

EXTRAE:
- Marca y modelo
- Categoría de producto
- Características físicas (color, tamaño, material)
- Especificaciones técnicas
- Condición del producto
- Accesorios incluidos

FORMATO DE RESPUESTA:
{{
    "brand": "nombre de marca",
    "model": "modelo específico",
    "category": "categoría del producto",
    "color": "color principal",
    "size": "dimensiones o talla",
    "material": "material principal",
    "condition": "nuevo/usado/reacondicionado",
    "technical_specs": {{}},
    "accessories": []
}}

RESPONDE SOLO CON JSON VÁLIDO:
"""

    def _create_price_estimation_prompt(
        self,
        product_features: dict[str, Any],
        category_id: str,
        condition: str,
    ) -> str:
        """Create prompt for price estimation."""
        return f"""
Estima el precio del producto para MercadoLibre Argentina.

CARACTERÍSTICAS: {json.dumps(product_features, ensure_ascii=False)}
CATEGORÍA: {category_id}
CONDICIÓN: {condition}

CONSIDERA:
- Precios actuales del mercado argentino
- Condición del producto
- Características y calidad
- Competencia en MercadoLibre

FORMATO DE RESPUESTA:
{{
    "estimated_price": 12345.67,
    "confidence": 0.85,
    "price_range": {{
        "min": 10000.00,
        "max": 15000.00
    }},
    "reasoning": "Explicación breve del precio estimado"
}}

RESPONDE SOLO CON JSON VÁLIDO:
"""

    async def _generate_with_retry(self, input_parts: list[Any]) -> Any:
        """Generate content with retry logic and exponential backoff."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # For now, simulate the API call
                # In production, this would be:
                # response = await self.model.generate_content_async(input_parts)

                # Simulate API response
                await asyncio.sleep(0.1)  # Simulate network delay

                # Return a mock response for now
                return self._create_mock_response()

            except TooManyRequests as e:
                wait_time = (2**attempt) + (attempt * 0.1)
                logger.warning(
                    f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1})"
                )
                await asyncio.sleep(wait_time)
                last_exception = e
            except (ServiceUnavailable, GoogleAPICallError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = (2**attempt) + (attempt * 0.1)
                    logger.warning(
                        f"API error, retrying in {wait_time}s (attempt {attempt + 1})"
                    )
                    await asyncio.sleep(wait_time)
                last_exception = e
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                last_exception = e
                break

        if last_exception:
            raise last_exception

        raise AIServiceError(
            f"Max retries ({self.max_retries}) exceeded",
            provider="gemini",
            model_version=self.model_name,
        )

    def _create_mock_response(self) -> dict[str, Any]:
        """Create a mock response for testing purposes."""
        return {
            "text": json.dumps(
                {
                    "title": "iPhone 13 Pro 128GB Azul Excelente Estado",
                    "description": "iPhone 13 Pro de 128GB en excelente estado. Incluye cargador original y caja. Batería al 95%. Sin rayones ni golpes. Ideal para uso diario y profesional.",
                    "ml_category_id": "MLA1055",
                    "ml_category_name": "Celulares y Teléfonos",
                    "ml_title": "iPhone 13 Pro 128GB Azul Excelente Estado",
                    "ml_price": 450000.00,
                    "ml_currency_id": "ARS",
                    "ml_available_quantity": 1,
                    "ml_buying_mode": "buy_it_now",
                    "ml_condition": "used",
                    "ml_listing_type_id": "gold_special",
                    "ml_attributes": {
                        "BRAND": "Apple",
                        "MODEL": "iPhone 13 Pro",
                        "STORAGE_CAPACITY": "128 GB",
                        "COLOR": "Azul",
                    },
                    "ml_sale_terms": {
                        "id": "WARRANTY_TYPE",
                        "value_name": "Garantía del vendedor",
                    },
                    "ml_shipping": {"mode": "me2", "free_shipping": True},
                    "confidence_overall": 0.85,
                    "confidence_breakdown": {
                        "title": 0.90,
                        "description": 0.85,
                        "category": 0.80,
                        "price": 0.75,
                        "attributes": 0.88,
                    },
                },
                ensure_ascii=False,
            )
        }

    def _parse_generation_response(self, response: Any) -> dict[str, Any]:
        """Parse the generation response from Gemini."""
        try:
            # Extract JSON from response
            response_text = response.get("text", "")

            # Parse JSON
            parsed_data = json.loads(response_text)

            # Validate required fields
            required_fields = [
                "title",
                "description",
                "ml_category_id",
                "ml_category_name",
                "ml_title",
                "ml_price",
                "confidence_overall",
                "confidence_breakdown",
            ]

            for field in required_fields:
                if field not in parsed_data:
                    raise InvalidContentError(f"Missing required field: {field}")

            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise InvalidContentError(
                "Invalid JSON response from Gemini API",
                content_type="api_response",
                validation_errors={"json_error": str(e)},
            ) from e
        except Exception as e:
            logger.error(f"Error parsing generation response: {e}")
            raise InvalidContentError(
                f"Error parsing generation response: {str(e)}",
                content_type="api_response",
            ) from e

    def _parse_title_variations(self, response: Any) -> list[str]:
        """Parse title variations from response."""
        try:
            response_text = response.get("text", "")
            parsed_data = json.loads(response_text)
            return parsed_data.get("variations", [])
        except Exception as e:
            logger.error(f"Error parsing title variations: {e}")
            return []

    def _parse_description_response(self, response: Any) -> str:
        """Parse description enhancement response."""
        try:
            return response.get("text", "").strip()
        except Exception as e:
            logger.error(f"Error parsing description response: {e}")
            return ""

    def _parse_feature_extraction_response(self, response: Any) -> dict[str, Any]:
        """Parse feature extraction response."""
        try:
            response_text = response.get("text", "")
            parsed_data = json.loads(response_text)
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing feature extraction response: {e}")
            return {}

    def _parse_price_estimation_response(self, response: Any) -> dict[str, Any]:
        """Parse price estimation response."""
        try:
            response_text = response.get("text", "")
            parsed_data = json.loads(response_text)
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing price estimation response: {e}")
            return {"estimated_price": 0.0, "confidence": 0.0}
