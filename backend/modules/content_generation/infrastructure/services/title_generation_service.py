"""
Title Generation Service implementation.

This module provides specialized title generation for MercadoLibre listings,
optimized for SEO and search algorithm performance.
"""

import logging
import re
from typing import Any

from modules.content_generation.domain.exceptions import (
    TitleGenerationError,
)
from modules.content_generation.domain.ports.ai_service_protocols import (
    TitleGenerationServiceProtocol,
)

logger = logging.getLogger(__name__)


class TitleGenerationService(TitleGenerationServiceProtocol):
    """
    Title generation service for MercadoLibre optimization.

    This service creates SEO-optimized titles that maximize
    discoverability on MercadoLibre Argentina.
    """

    def __init__(
        self,
        max_title_length: int = 60,
        min_title_length: int = 10,
    ):
        """
        Initialize the title generation service.

        Args:
            max_title_length: Maximum title length (MercadoLibre limit)
            min_title_length: Minimum title length
        """
        self.max_title_length = max_title_length
        self.min_title_length = min_title_length

        # Common Spanish stop words to avoid in titles
        self.stop_words = {
            "el",
            "la",
            "de",
            "que",
            "y",
            "a",
            "en",
            "un",
            "es",
            "se",
            "no",
            "te",
            "lo",
            "le",
            "da",
            "su",
            "por",
            "son",
            "con",
            "para",
            "al",
            "del",
            "las",
            "los",
            "una",
            "está",
            "muy",
            "todo",
            "más",
            "como",
            "pero",
            "sus",
            "fue",
            "ser",
            "han",
            "hay",
            "era",
        }

        # MercadoLibre SEO keywords for different categories
        self.seo_keywords = {
            "electronics": ["original", "nuevo", "garantía", "envío"],
            "clothing": ["talla", "color", "marca", "temporada"],
            "home": ["hogar", "cocina", "decoración", "calidad"],
            "sports": ["deportes", "fitness", "entrenamiento", "profesional"],
            "automotive": ["auto", "repuesto", "original", "compatible"],
            "books": ["libro", "editorial", "autor", "nuevo"],
            "beauty": ["belleza", "cuidado", "natural", "piel"],
            "toys": ["juguete", "niños", "educativo", "seguro"],
        }

        # MercadoLibre title optimization patterns
        self.title_patterns = {
            "brand_model": "{brand} {model}",
            "brand_model_specs": "{brand} {model} {specs}",
            "brand_category": "{brand} {category}",
            "category_brand": "{category} {brand}",
            "product_condition": "{product} {condition}",
            "product_features": "{product} {features}",
        }

        logger.info("Initialized Title Generation Service")

    async def generate_optimized_title(
        self,
        product_features: dict[str, Any],
        category_id: str,
        max_length: int = 60,
    ) -> str:
        """
        Generate MercadoLibre-optimized title.

        Args:
            product_features: Product features and attributes
            category_id: MercadoLibre category ID
            max_length: Maximum title length

        Returns:
            Optimized title string

        Raises:
            TitleGenerationError: If title generation fails
        """
        try:
            # Generate title components
            title_components = self._extract_title_components(product_features)

            # Create multiple title variants
            title_variants = self._generate_title_variants(
                title_components, category_id, max_length
            )

            # Score and select best title
            best_title = self._select_best_title(title_variants, product_features)

            # Validate and clean title
            final_title = self._validate_and_clean_title(best_title, max_length)

            logger.info(f"Generated optimized title: {final_title}")
            return final_title

        except Exception as e:
            logger.error(f"Error generating optimized title: {e}")
            raise TitleGenerationError(
                f"Failed to generate optimized title: {str(e)}",
                error_code="TITLE_GENERATION_FAILED",
            ) from e

    async def validate_title(
        self,
        title: str,
        category_id: str,
    ) -> dict[str, Any]:
        """
        Validate title against MercadoLibre requirements.

        Args:
            title: Title to validate
            category_id: MercadoLibre category ID

        Returns:
            Dict containing validation results
        """
        validation_errors: list[str] = []
        warnings: list[str] = []

        # Length validation
        if len(title) > self.max_title_length:
            validation_errors.append(
                f"Title exceeds maximum length ({self.max_title_length})"
            )

        if len(title) < self.min_title_length:
            validation_errors.append(
                f"Title below minimum length ({self.min_title_length})"
            )

        # Character validation
        if not self._has_valid_characters(title):
            validation_errors.append("Title contains invalid characters")

        # Content validation
        if self._has_excessive_capitalization(title):
            warnings.append("Title has excessive capitalization")

        if self._has_repetitive_words(title):
            warnings.append("Title has repetitive words")

        if self._lacks_brand_or_model(title):
            warnings.append("Title lacks brand or model information")

        # SEO validation
        seo_score = self._calculate_seo_score(title, category_id)

        return {
            "is_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "warnings": warnings,
            "seo_score": seo_score,
            "title_length": len(title),
            "optimization_suggestions": self._get_optimization_suggestions(
                title, category_id
            ),
        }

    async def generate_title_variations(
        self,
        base_title: str,
        product_features: dict[str, Any],
        count: int = 3,
    ) -> list[str]:
        """
        Generate multiple title variations.

        Args:
            base_title: Base title to create variations from
            product_features: Product features
            count: Number of variations to generate

        Returns:
            List of title variations
        """
        try:
            variations: list[str] = []

            # Extract components from base title and features
            title_components = self._extract_title_components(product_features)

            # Generate variations using different patterns
            for i in range(count):
                if i == 0:
                    # Rearrange existing components
                    variation = self._rearrange_title_components(
                        base_title, title_components
                    )
                elif i == 1:
                    # Add SEO keywords
                    variation = self._add_seo_keywords(base_title, product_features)
                else:
                    # Emphasize different aspects
                    variation = self._emphasize_different_aspects(
                        base_title, title_components, i
                    )

                # Validate and clean variation
                if variation and len(variation) <= self.max_title_length:
                    variations.append(
                        self._validate_and_clean_title(variation, self.max_title_length)
                    )

            # Remove duplicates and return unique variations
            unique_variations = list(dict.fromkeys(variations))

            return unique_variations[:count]

        except Exception as e:
            logger.error(f"Error generating title variations: {e}")
            return [base_title]  # Return original title as fallback

    async def calculate_title_confidence(
        self,
        title: str,
        product_features: dict[str, Any],
    ) -> float:
        """
        Calculate confidence score for generated title.

        Args:
            title: Title to evaluate
            product_features: Product features

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.0

        # Length score (optimal length is 40-60 characters)
        length_score = self._calculate_length_score(title)
        confidence += length_score * 0.2

        # Content completeness score
        completeness_score = self._calculate_completeness_score(title, product_features)
        confidence += completeness_score * 0.3

        # SEO score
        seo_score = self._calculate_seo_score(
            title, product_features.get("category", "")
        )
        confidence += seo_score * 0.2

        # Readability score
        readability_score = self._calculate_readability_score(title)
        confidence += readability_score * 0.15

        # Uniqueness score
        uniqueness_score = self._calculate_uniqueness_score(title)
        confidence += uniqueness_score * 0.15

        return min(confidence, 1.0)

    def _extract_title_components(
        self, product_features: dict[str, Any]
    ) -> dict[str, str]:
        """Extract title components from product features."""
        components: dict[str, str] = {}

        # Core components
        components["brand"] = product_features.get("brand", "")
        components["model"] = product_features.get("model", "")
        components["category"] = product_features.get("category", "")
        components["condition"] = product_features.get("condition", "")

        # Additional components
        components["color"] = product_features.get("color", "")
        components["size"] = product_features.get("size", "")
        components["material"] = product_features.get("material", "")

        # Technical specs
        specs = product_features.get("technical_specs", {})
        if specs:
            # Extract key specs that should appear in title
            important_specs = ["capacity", "memory", "storage", "resolution", "power"]
            for spec in important_specs:
                if spec in specs:
                    components[spec] = str(specs[spec])

        return components

    def _generate_title_variants(
        self,
        components: dict[str, str],
        category_id: str,
        max_length: int,
    ) -> list[str]:
        """Generate multiple title variants using different patterns."""
        variants: list[str] = []

        brand = components.get("brand", "")
        model = components.get("model", "")
        category = components.get("category", "")
        condition = components.get("condition", "")
        color = components.get("color", "")

        # Pattern 1: Brand + Model + Key Features
        if brand and model:
            title = f"{brand} {model}"
            if color:
                title += f" {color}"
            if condition and condition != "nuevo":
                title += f" {condition}"
            variants.append(title)

        # Pattern 2: Category + Brand + Model
        if category and brand:
            title = f"{category} {brand}"
            if model:
                title += f" {model}"
            variants.append(title)

        # Pattern 3: Brand + Category + Condition
        if brand and category:
            title = f"{brand} {category}"
            if condition:
                title += f" {condition}"
            variants.append(title)

        # Pattern 4: Full descriptive title
        if brand and model and category:
            title = f"{brand} {model} {category}"
            if color:
                title += f" {color}"
            variants.append(title)

        # Filter by length and return
        valid_variants: list[str] = [
            v
            for v in variants
            if len(v) <= max_length and len(v) >= self.min_title_length
        ]

        return valid_variants

    def _select_best_title(
        self,
        title_variants: list[str],
        product_features: dict[str, Any],
    ) -> str:
        """Select the best title from variants."""
        if not title_variants:
            # Generate fallback title
            brand = product_features.get("brand", "")
            model = product_features.get("model", "")
            category = product_features.get("category", "Producto")

            if brand and model:
                return f"{brand} {model}"
            elif brand:
                return f"{brand} {category}"
            else:
                return category

        # Score each variant
        scored_variants: list[tuple[str, float]] = []
        for variant in title_variants:
            score = self._score_title_variant(variant, product_features)
            scored_variants.append((variant, score))

        # Return highest scoring variant
        best_variant: tuple[str, float] = max(scored_variants, key=lambda x: x[1])
        return best_variant[0]

    def _score_title_variant(
        self, title: str, product_features: dict[str, Any]
    ) -> float:
        """Score a title variant for selection."""
        score = 0.0

        # Length score (prefer 40-60 characters)
        length = len(title)
        if 40 <= length <= 60:
            score += 0.3
        elif 30 <= length <= 40:
            score += 0.2
        elif 20 <= length <= 30:
            score += 0.1

        # Brand presence
        brand = product_features.get("brand", "")
        if brand and brand.lower() in title.lower():
            score += 0.25

        # Model presence
        model = product_features.get("model", "")
        if model and model.lower() in title.lower():
            score += 0.25

        # Category presence
        category = product_features.get("category", "")
        if category and category.lower() in title.lower():
            score += 0.1

        # Condition presence (if not new)
        condition = product_features.get("condition", "")
        if condition and condition != "nuevo" and condition.lower() in title.lower():
            score += 0.1

        return score

    def _validate_and_clean_title(self, title: str, max_length: int) -> str:
        """Validate and clean title."""
        # Remove extra whitespace
        title = " ".join(title.split())

        # Capitalize properly
        title = self._capitalize_title(title)

        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length].rsplit(" ", 1)[0]

        # Remove trailing punctuation
        title = title.rstrip(".,;:-")

        return title

    def _capitalize_title(self, title: str) -> str:
        """Capitalize title properly."""
        words = title.split()
        capitalized_words: list[str] = []

        for word in words:
            # Don't capitalize common stop words unless they're the first word
            if word.lower() in self.stop_words and len(capitalized_words) > 0:
                capitalized_words.append(word.lower())
            else:
                capitalized_words.append(word.capitalize())

        return " ".join(capitalized_words)

    def _has_valid_characters(self, title: str) -> bool:
        """Check if title contains valid characters."""
        # Allow letters, numbers, spaces, and basic punctuation
        allowed_pattern = r"^[a-zA-ZáéíóúñÑ0-9\s\-\(\)\/\+\&\.\,]+$"
        return bool(re.match(allowed_pattern, title))

    def _has_excessive_capitalization(self, title: str) -> bool:
        """Check if title has excessive capitalization."""
        upper_count = sum(1 for c in title if c.isupper())
        total_letters = sum(1 for c in title if c.isalpha())

        if total_letters == 0:
            return False

        # More than 60% uppercase is excessive
        return (upper_count / total_letters) > 0.6

    def _has_repetitive_words(self, title: str) -> bool:
        """Check if title has repetitive words."""
        words = title.lower().split()
        return len(words) != len(set(words))

    def _lacks_brand_or_model(self, title: str) -> bool:
        """Check if title lacks brand or model information."""
        # This is a simplified check - in production you'd have a database of brands
        common_brands = [
            "apple",
            "samsung",
            "sony",
            "lg",
            "nike",
            "adidas",
            "hp",
            "dell",
        ]
        title_lower = title.lower()

        return not any(brand in title_lower for brand in common_brands)

    def _calculate_seo_score(self, title: str, category_id: str) -> float:
        """Calculate SEO score for title."""
        score = 0.0

        # Check for relevant keywords
        category_keywords = self.seo_keywords.get(
            "electronics", []
        )  # Default to electronics

        for keyword in category_keywords:
            if keyword in title.lower():
                score += 0.25

        # Check title length optimization
        length = len(title)
        if 40 <= length <= 60:
            score += 0.3
        elif 30 <= length <= 40:
            score += 0.2

        # Check for numbers (specs are good for SEO)
        if any(char.isdigit() for char in title):
            score += 0.1

        return min(score, 1.0)

    def _calculate_length_score(self, title: str) -> float:
        """Calculate score based on title length."""
        length = len(title)

        if 40 <= length <= 60:
            return 1.0
        elif 30 <= length <= 40:
            return 0.8
        elif 20 <= length <= 30:
            return 0.6
        elif 10 <= length <= 20:
            return 0.4
        else:
            return 0.2

    def _calculate_completeness_score(
        self, title: str, product_features: dict[str, Any]
    ) -> float:
        """Calculate completeness score based on included information."""
        score = 0.0

        # Brand
        if (
            product_features.get("brand", "")
            and product_features["brand"].lower() in title.lower()
        ):
            score += 0.4

        # Model
        if (
            product_features.get("model", "")
            and product_features["model"].lower() in title.lower()
        ):
            score += 0.3

        # Category
        if (
            product_features.get("category", "")
            and product_features["category"].lower() in title.lower()
        ):
            score += 0.2

        # Condition (if not new)
        condition = product_features.get("condition", "")
        if condition and condition != "nuevo" and condition.lower() in title.lower():
            score += 0.1

        return score

    def _calculate_readability_score(self, title: str) -> float:
        """Calculate readability score."""
        words = title.split()

        # Prefer 3-8 words
        word_count = len(words)
        if 3 <= word_count <= 8:
            return 1.0
        elif 2 <= word_count <= 10:
            return 0.8
        else:
            return 0.5

    def _calculate_uniqueness_score(self, title: str) -> float:
        """Calculate uniqueness score."""
        # Simple uniqueness check - in production you'd check against database
        words = title.lower().split()
        unique_words = len(set(words))
        total_words = len(words)

        if total_words == 0:
            return 0.0

        return unique_words / total_words

    def _rearrange_title_components(
        self, base_title: str, components: dict[str, str]
    ) -> str:
        """Rearrange title components for variation."""
        # Simple rearrangement - swap brand and model if both present
        words = base_title.split()
        if len(words) >= 2:
            words[0], words[1] = words[1], words[0]
            return " ".join(words)
        return base_title

    def _add_seo_keywords(
        self, base_title: str, product_features: dict[str, Any]
    ) -> str:
        """Add SEO keywords to title."""
        # Add condition if not present and product is not new
        condition = product_features.get("condition", "")
        if (
            condition
            and condition != "nuevo"
            and condition.lower() not in base_title.lower()
        ):
            if len(base_title) + len(condition) + 1 <= self.max_title_length:
                return f"{base_title} {condition}"

        return base_title

    def _emphasize_different_aspects(
        self, base_title: str, components: dict[str, str], variant_index: int
    ) -> str:
        """Emphasize different aspects for variation."""
        # Emphasize color, size, or material based on variant index
        emphasis_options = ["color", "size", "material"]

        if variant_index < len(emphasis_options):
            emphasis = emphasis_options[variant_index]
            value = components.get(emphasis, "")

            if value and value.lower() not in base_title.lower():
                if len(base_title) + len(value) + 1 <= self.max_title_length:
                    return f"{base_title} {value}"

        return base_title

    def _get_optimization_suggestions(self, title: str, category_id: str) -> list[str]:
        """Get optimization suggestions for title."""
        suggestions: list[str] = []

        # Length suggestions
        if len(title) < 30:
            suggestions.append("Consider adding more descriptive keywords")
        elif len(title) > 55:
            suggestions.append("Consider shortening to improve readability")

        # SEO suggestions
        if not any(char.isdigit() for char in title):
            suggestions.append("Consider adding model numbers or specifications")

        # Content suggestions
        if title.isupper():
            suggestions.append("Use proper capitalization instead of all caps")

        return suggestions
