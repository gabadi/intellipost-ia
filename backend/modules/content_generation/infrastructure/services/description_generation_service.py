"""
Description Generation Service implementation.

This module provides specialized description generation for MercadoLibre listings,
optimized for mobile-first experience and conversion.
"""

from typing import Any

from modules.content_generation.domain.exceptions import (
    DescriptionGenerationError,
)
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)


class DescriptionGenerationService:
    """
    Description generation service for MercadoLibre optimization.

    This service creates mobile-optimized descriptions that maximize
    engagement and conversion on MercadoLibre Argentina.
    """

    def __init__(
        self,
        logger: ContentLoggerProtocol,
        min_description_length: int = 50,
        max_description_length: int = 2000,
        target_description_length: int = 500,
    ):
        """
        Initialize the description generation service.

        Args:
            logger: Logger protocol for logging operations
            min_description_length: Minimum description length
            max_description_length: Maximum description length
            target_description_length: Target description length
        """
        self.logger = logger
        self.min_description_length = min_description_length
        self.max_description_length = max_description_length
        self.target_description_length = target_description_length

        # Description templates for different categories
        self.description_templates = {
            "electronics": {
                "intro": "📱 {brand} {model} - {condition_description}",
                "features": "✨ Características principales:\n{features_list}",
                "specs": "📋 Especificaciones:\n{specs_list}",
                "benefits": "🎯 Beneficios:\n{benefits_list}",
                "warranty": "🛡️ Garantía: {warranty_info}",
                "shipping": "🚚 Envío: {shipping_info}",
                "cta": "¡Comprá ahora y recibilo rápido! 🛒",
            },
            "clothing": {
                "intro": "👕 {brand} {model} - {condition_description}",
                "features": "✨ Detalles:\n{features_list}",
                "sizes": "📏 Talles disponibles: {sizes_list}",
                "materials": "🧵 Materiales: {materials_list}",
                "care": "🧼 Cuidado: {care_instructions}",
                "shipping": "🚚 Envío: {shipping_info}",
                "cta": "¡Agregá estilo a tu guardarropa! 👗",
            },
            "home": {
                "intro": "🏠 {brand} {model} - {condition_description}",
                "features": "✨ Características:\n{features_list}",
                "dimensions": "📐 Dimensiones: {dimensions_info}",
                "materials": "🔨 Materiales: {materials_list}",
                "benefits": "🎯 Ventajas:\n{benefits_list}",
                "shipping": "🚚 Envío: {shipping_info}",
                "cta": "¡Mejorá tu hogar hoy mismo! 🏡",
            },
            "default": {
                "intro": "{brand} {model} - {condition_description}",
                "features": "Características principales:\n{features_list}",
                "specs": "Especificaciones:\n{specs_list}",
                "benefits": "Beneficios:\n{benefits_list}",
                "shipping": "Envío: {shipping_info}",
                "cta": "¡Comprá ahora!",
            },
        }

        # Mobile-first formatting rules
        self.mobile_formatting: dict[str, Any] = {
            "max_line_length": 50,
            "paragraph_separator": "\n\n",
            "bullet_point": "• ",
            "emoji_spacing": " ",
            "section_spacing": "\n\n",
        }

        # SEO keywords for different categories
        self.seo_keywords = {
            "electronics": [
                "original",
                "garantía",
                "nuevo",
                "calidad",
                "marca",
                "tecnología",
            ],
            "clothing": [
                "moda",
                "estilo",
                "cómodo",
                "elegante",
                "temporada",
                "tendencia",
            ],
            "home": [
                "hogar",
                "decoración",
                "funcional",
                "durável",
                "práctico",
                "diseño",
            ],
            "sports": [
                "deporte",
                "fitness",
                "rendimiento",
                "resistente",
                "cómodo",
                "profesional",
            ],
            "automotive": [
                "auto",
                "vehículo",
                "repuesto",
                "compatible",
                "original",
                "calidad",
            ],
            "books": [
                "libro",
                "lectura",
                "conocimiento",
                "educativo",
                "información",
                "cultura",
            ],
            "beauty": ["belleza", "cuidado", "natural", "piel", "salud", "bienestar"],
            "toys": [
                "juguete",
                "diversión",
                "educativo",
                "seguro",
                "desarrollo",
                "entretenimiento",
            ],
        }

        # Condition descriptions in Spanish
        self.condition_descriptions = {
            "new": "Producto nuevo en excelente estado",
            "used": "Producto usado en buen estado",
            "refurbished": "Producto reacondicionado con garantía",
            "like_new": "Producto como nuevo, sin uso",
            "good": "Producto en buen estado general",
            "fair": "Producto con signos de uso normal",
        }

        self.logger.info("Initialized Description Generation Service")

    async def generate_description(
        self,
        product_features: dict[str, Any],
        category_id: str,
        target_length: int | None = None,
    ) -> str:
        """
        Generate comprehensive product description.

        Args:
            product_features: Product features and attributes
            category_id: MercadoLibre category ID
            target_length: Target description length

        Returns:
            Generated description string

        Raises:
            DescriptionGenerationError: If description generation fails
        """
        try:
            # Determine target length
            if target_length is None:
                target_length = self.target_description_length

            # Identify category type
            category_type = self._identify_category_type(category_id)

            # Generate description sections
            sections = self._generate_description_sections(
                product_features, category_type, target_length
            )

            # Combine sections into full description
            description = self._combine_sections(sections, category_type)

            # Apply mobile formatting
            description = self._apply_mobile_formatting(description)

            # Validate and optimize length
            description = self._optimize_length(description, target_length)

            # Final validation
            if len(description) < self.min_description_length:
                raise DescriptionGenerationError(
                    f"Generated description too short: {len(description)} characters",
                    generated_description=description,
                )

            self.logger.info(f"Generated description: {len(description)} characters")
            return description

        except Exception as e:
            self.logger.error(f"Error generating description: {e}")
            raise DescriptionGenerationError(
                f"Failed to generate description: {str(e)}",
                error_code="DESCRIPTION_GENERATION_FAILED",
            ) from e

    async def validate_description(
        self,
        description: str,
        category_id: str,
    ) -> dict[str, Any]:
        """
        Validate description against quality standards.

        Args:
            description: Description to validate
            category_id: MercadoLibre category ID

        Returns:
            Dict containing validation results
        """
        validation_errors: list[str] = []
        warnings: list[str] = []

        # Length validation
        if len(description) < self.min_description_length:
            validation_errors.append(
                f"Description too short (minimum {self.min_description_length})"
            )

        if len(description) > self.max_description_length:
            validation_errors.append(
                f"Description too long (maximum {self.max_description_length})"
            )

        # Content validation
        if not self._has_product_benefits(description):
            warnings.append("Description lacks clear product benefits")

        if not self._has_call_to_action(description):
            warnings.append("Description lacks call to action")

        if self._has_excessive_emojis(description):
            warnings.append("Description has excessive emojis")

        # Mobile formatting validation
        if not self._is_mobile_friendly(description):
            warnings.append("Description may not be mobile-friendly")

        # SEO validation
        seo_score = self._calculate_seo_score(description, category_id)

        # Readability validation
        readability_score = self._calculate_readability_score(description)

        return {
            "is_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "warnings": warnings,
            "seo_score": seo_score,
            "readability_score": readability_score,
            "description_length": len(description),
            "mobile_friendly": self._is_mobile_friendly(description),
            "has_call_to_action": self._has_call_to_action(description),
            "optimization_suggestions": self._get_optimization_suggestions(
                description, category_id
            ),
        }

    async def enhance_description(
        self,
        base_description: str,
        additional_features: dict[str, Any],
    ) -> str:
        """
        Enhance existing description with additional features.

        Args:
            base_description: Original description
            additional_features: Additional features to include

        Returns:
            Enhanced description
        """
        try:
            # Parse existing description structure
            sections = self._parse_description_sections(base_description)

            # Add new features to appropriate sections
            enhanced_sections = self._enhance_sections(sections, additional_features)

            # Rebuild description
            enhanced_description = self._rebuild_description(enhanced_sections)

            # Apply mobile formatting
            enhanced_description = self._apply_mobile_formatting(enhanced_description)

            # Optimize length
            enhanced_description = self._optimize_length(
                enhanced_description, self.target_description_length
            )

            return enhanced_description

        except Exception as e:
            self.logger.error(f"Error enhancing description: {e}")
            return base_description  # Return original as fallback

    async def calculate_description_confidence(
        self,
        description: str,
        product_features: dict[str, Any],
    ) -> float:
        """
        Calculate confidence score for generated description.

        Args:
            description: Description to evaluate
            product_features: Product features

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.0

        # Length score
        length_score = self._calculate_length_score(description)
        confidence += length_score * 0.2

        # Content completeness score
        completeness_score = self._calculate_completeness_score(
            description, product_features
        )
        confidence += completeness_score * 0.3

        # Structure score
        structure_score = self._calculate_structure_score(description)
        confidence += structure_score * 0.2

        # Mobile friendliness score
        mobile_score = 1.0 if self._is_mobile_friendly(description) else 0.5
        confidence += mobile_score * 0.15

        # SEO score
        seo_score = self._calculate_seo_score(
            description, product_features.get("category", "")
        )
        confidence += seo_score * 0.15

        return min(confidence, 1.0)

    def _identify_category_type(self, category_id: str) -> str:
        """Identify category type from MercadoLibre category ID."""
        # Map category IDs to types (simplified mapping)
        category_mappings = {
            "MLA1055": "electronics",  # Celulares
            "MLA1144": "electronics",  # Cámaras
            "MLA1000": "electronics",  # Electrónicos
            "MLA1430": "clothing",  # Ropa
            "MLA1276": "home",  # Hogar
            "MLA1168": "sports",  # Deportes
            "MLA1744": "automotive",  # Autos
            "MLA1196": "books",  # Libros
            "MLA1246": "beauty",  # Belleza
            "MLA1132": "toys",  # Juguetes
        }

        return category_mappings.get(category_id, "default")

    def _generate_description_sections(
        self,
        product_features: dict[str, Any],
        category_type: str,
        target_length: int,
    ) -> dict[str, str]:
        """Generate individual description sections."""
        sections: dict[str, str] = {}

        # Get template for category
        template = self.description_templates.get(
            category_type, self.description_templates["default"]
        )

        # Introduction section
        sections["intro"] = self._generate_intro_section(product_features, template)

        # Features section
        sections["features"] = self._generate_features_section(
            product_features, template
        )

        # Specifications section (if applicable)
        if "specs" in template:
            sections["specs"] = self._generate_specs_section(product_features, template)

        # Benefits section
        sections["benefits"] = self._generate_benefits_section(
            product_features, template
        )

        # Warranty section (if applicable)
        if "warranty" in template:
            sections["warranty"] = self._generate_warranty_section(
                product_features, template
            )

        # Shipping section
        sections["shipping"] = self._generate_shipping_section(
            product_features, template
        )

        # Call to action
        sections["cta"] = template.get("cta", "¡Comprá ahora!")

        return sections

    def _generate_intro_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate introduction section."""
        brand = product_features.get("brand", "")
        model = product_features.get("model", "")
        condition = product_features.get("condition", "new")

        condition_description = self.condition_descriptions.get(
            condition, "en excelente estado"
        )

        intro_template = template.get(
            "intro", "{brand} {model} - {condition_description}"
        )

        return intro_template.format(
            brand=brand,
            model=model,
            condition_description=condition_description,
        )

    def _generate_features_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate features section."""
        features: list[str] = []

        # Extract key features
        if product_features.get("color"):
            features.append(f"Color: {product_features['color']}")

        if product_features.get("size"):
            features.append(f"Tamaño: {product_features['size']}")

        if product_features.get("material"):
            features.append(f"Material: {product_features['material']}")

        # Add technical specs as features
        specs = product_features.get("technical_specs", {})
        for spec_name, spec_value in specs.items():
            if spec_value:
                features.append(f"{spec_name.title()}: {spec_value}")

        if not features:
            features.append("Producto de alta calidad")

        features_list = "\n".join(f"• {feature}" for feature in features)

        features_template = template.get(
            "features", "Características:\n{features_list}"
        )

        return features_template.format(features_list=features_list)

    def _generate_specs_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate specifications section."""
        specs = product_features.get("technical_specs", {})

        if not specs:
            return ""

        specs_list = "\n".join(
            f"• {name.title()}: {value}" for name, value in specs.items() if value
        )

        if not specs_list:
            return ""

        specs_template = template.get("specs", "Especificaciones:\n{specs_list}")

        return specs_template.format(specs_list=specs_list)

    def _generate_benefits_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate benefits section."""
        benefits: list[str] = []

        # Generate benefits based on features
        if product_features.get("condition") == "new":
            benefits.append("Producto completamente nuevo")

        if product_features.get("brand"):
            benefits.append(f"Marca {product_features['brand']} de confianza")

        # Add category-specific benefits
        category = product_features.get("category", "")
        if "electrónicos" in category.lower():
            benefits.append("Tecnología de última generación")
        elif "ropa" in category.lower():
            benefits.append("Estilo y comodidad garantizados")
        elif "hogar" in category.lower():
            benefits.append("Mejora tu espacio personal")

        # Default benefit
        if not benefits:
            benefits.append("Excelente relación calidad-precio")

        benefits_list = "\n".join(f"• {benefit}" for benefit in benefits)

        benefits_template = template.get("benefits", "Beneficios:\n{benefits_list}")

        return benefits_template.format(benefits_list=benefits_list)

    def _generate_warranty_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate warranty section."""
        warranty_info = "Garantía del vendedor incluida"

        # Customize based on condition
        condition = product_features.get("condition", "new")
        if condition == "new":
            warranty_info = "Garantía oficial + garantía del vendedor"
        elif condition == "refurbished":
            warranty_info = "Garantía de reacondicionamiento incluida"

        warranty_template = template.get("warranty", "Garantía: {warranty_info}")

        return warranty_template.format(warranty_info=warranty_info)

    def _generate_shipping_section(
        self, product_features: dict[str, Any], template: dict[str, str]
    ) -> str:
        """Generate shipping section."""
        shipping_info = "Envío rápido y seguro"

        # Customize based on product type
        if product_features.get("category"):
            shipping_info = "Envío gratis a todo el país"

        shipping_template = template.get("shipping", "Envío: {shipping_info}")

        return shipping_template.format(shipping_info=shipping_info)

    def _combine_sections(self, sections: dict[str, str], category_type: str) -> str:
        """Combine sections into full description."""
        combined_sections: list[str] = []

        # Order sections appropriately
        section_order = [
            "intro",
            "features",
            "specs",
            "benefits",
            "warranty",
            "shipping",
            "cta",
        ]

        for section_name in section_order:
            if section_name in sections and sections[section_name]:
                combined_sections.append(sections[section_name])

        return self.mobile_formatting["section_spacing"].join(combined_sections)

    def _apply_mobile_formatting(self, description: str) -> str:
        """Apply mobile-first formatting to description."""
        # Split into paragraphs
        paragraphs = description.split("\n\n")

        formatted_paragraphs: list[str] = []
        for paragraph in paragraphs:
            # Format individual paragraph
            formatted_paragraph = self._format_paragraph_for_mobile(paragraph)
            formatted_paragraphs.append(formatted_paragraph)

        return self.mobile_formatting["paragraph_separator"].join(formatted_paragraphs)

    def _format_paragraph_for_mobile(self, paragraph: str) -> str:
        """Format individual paragraph for mobile viewing."""
        # Break long lines
        lines = paragraph.split("\n")
        formatted_lines: list[str] = []

        for line in lines:
            if len(line) <= self.mobile_formatting["max_line_length"]:
                formatted_lines.append(line)
            else:
                # Break long line into multiple lines
                words = line.split()
                current_line = ""

                for word in words:
                    if (
                        len(current_line + " " + word)
                        <= self.mobile_formatting["max_line_length"]
                    ):
                        current_line += " " + word if current_line else word
                    else:
                        if current_line:
                            formatted_lines.append(current_line)
                        current_line = word

                if current_line:
                    formatted_lines.append(current_line)

        return "\n".join(formatted_lines)

    def _optimize_length(self, description: str, target_length: int) -> str:
        """Optimize description length."""
        if len(description) <= target_length:
            return description

        # Truncate at sentence boundary
        sentences = description.split(". ")
        truncated_sentences: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence) + 2  # +2 for ". "
            if current_length + sentence_length <= target_length:
                truncated_sentences.append(sentence)
                current_length += sentence_length
            else:
                break

        if truncated_sentences:
            result = ". ".join(truncated_sentences)
            if not result.endswith("."):
                result += "."
            return result

        # If no complete sentences fit, truncate at word boundary
        words = description.split()
        truncated_words: list[str] = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length <= target_length:
                truncated_words.append(word)
                current_length += word_length
            else:
                break

        return " ".join(truncated_words)

    def _has_product_benefits(self, description: str) -> bool:
        """Check if description contains product benefits."""
        benefit_keywords = ["beneficio", "ventaja", "garantía", "calidad", "confianza"]
        return any(keyword in description.lower() for keyword in benefit_keywords)

    def _has_call_to_action(self, description: str) -> bool:
        """Check if description contains call to action."""
        cta_keywords = ["comprá", "comprar", "pedí", "contactá", "consultá", "agregá"]
        return any(keyword in description.lower() for keyword in cta_keywords)

    def _has_excessive_emojis(self, description: str) -> bool:
        """Check if description has excessive emojis."""
        emoji_count = sum(1 for char in description if ord(char) > 127)
        return emoji_count > len(description) * 0.05  # More than 5% emojis

    def _is_mobile_friendly(self, description: str) -> bool:
        """Check if description is mobile-friendly."""
        lines = description.split("\n")

        # Check line length
        long_lines = [line for line in lines if len(line) > 80]
        if len(long_lines) > len(lines) * 0.3:  # More than 30% long lines
            return False

        # Check paragraph length
        paragraphs = description.split("\n\n")
        long_paragraphs = [p for p in paragraphs if len(p) > 300]
        return not (len(long_paragraphs) > len(paragraphs) * 0.5)

    def _calculate_seo_score(self, description: str, category_id: str) -> float:
        """Calculate SEO score for description."""
        score = 0.0

        # Get relevant keywords for category
        category_type = self._identify_category_type(category_id)
        keywords = self.seo_keywords.get(category_type, [])

        # Check keyword presence
        description_lower = description.lower()
        keyword_count = sum(1 for keyword in keywords if keyword in description_lower)

        if keywords:
            score += (keyword_count / len(keywords)) * 0.4

        # Check description length
        if (
            self.min_description_length
            <= len(description)
            <= self.max_description_length
        ):
            score += 0.3

        # Check structure
        if self._has_product_benefits(description):
            score += 0.15

        if self._has_call_to_action(description):
            score += 0.15

        return min(score, 1.0)

    def _calculate_readability_score(self, description: str) -> float:
        """Calculate readability score."""
        score = 0.0

        # Sentence length
        sentences = description.split(". ")
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )

        if 10 <= avg_sentence_length <= 20:
            score += 0.3
        elif 5 <= avg_sentence_length <= 30:
            score += 0.2

        # Paragraph structure
        paragraphs = description.split("\n\n")
        if 3 <= len(paragraphs) <= 8:
            score += 0.3

        # Mobile formatting
        if self._is_mobile_friendly(description):
            score += 0.4

        return min(score, 1.0)

    def _calculate_length_score(self, description: str) -> float:
        """Calculate score based on description length."""
        length = len(description)

        if (
            self.target_description_length * 0.8
            <= length
            <= self.target_description_length * 1.2
        ):
            return 1.0
        elif self.min_description_length <= length <= self.max_description_length:
            return 0.8
        else:
            return 0.4

    def _calculate_completeness_score(
        self, description: str, product_features: dict[str, Any]
    ) -> float:
        """Calculate completeness score."""
        score = 0.0

        # Check for brand mention
        brand = product_features.get("brand", "")
        if brand and brand.lower() in description.lower():
            score += 0.2

        # Check for model mention
        model = product_features.get("model", "")
        if model and model.lower() in description.lower():
            score += 0.2

        # Check for features
        if (
            "características" in description.lower()
            or "features" in description.lower()
        ):
            score += 0.2

        # Check for benefits
        if self._has_product_benefits(description):
            score += 0.2

        # Check for call to action
        if self._has_call_to_action(description):
            score += 0.2

        return score

    def _calculate_structure_score(self, description: str) -> float:
        """Calculate structure score."""
        score = 0.0

        # Check for bullet points
        if "•" in description or "- " in description:
            score += 0.3

        # Check for sections
        sections = description.split("\n\n")
        if 3 <= len(sections) <= 8:
            score += 0.3

        # Check for emojis (moderate use)
        emoji_count = sum(1 for char in description if ord(char) > 127)
        if 0 < emoji_count <= len(description) * 0.03:  # 0-3% emojis
            score += 0.2

        # Check for proper formatting
        if self._is_mobile_friendly(description):
            score += 0.2

        return min(score, 1.0)

    def _parse_description_sections(self, description: str) -> dict[str, str]:
        """Parse existing description into sections."""
        # Simple parsing - in production this would be more sophisticated
        sections: dict[str, str] = {}

        paragraphs = description.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if i == 0:
                sections["intro"] = paragraph
            elif "características" in paragraph.lower():
                sections["features"] = paragraph
            elif "especificaciones" in paragraph.lower():
                sections["specs"] = paragraph
            elif "beneficios" in paragraph.lower() or "ventajas" in paragraph.lower():
                sections["benefits"] = paragraph
            elif "garantía" in paragraph.lower():
                sections["warranty"] = paragraph
            elif "envío" in paragraph.lower():
                sections["shipping"] = paragraph
            elif i == len(paragraphs) - 1:
                sections["cta"] = paragraph

        return sections

    def _enhance_sections(
        self, sections: dict[str, str], additional_features: dict[str, Any]
    ) -> dict[str, str]:
        """Enhance sections with additional features."""
        enhanced_sections = sections.copy()

        # Add new features to features section
        if "features" in sections and additional_features:
            current_features = sections["features"]
            new_features: list[str] = []

            for feature_name, feature_value in additional_features.items():
                if feature_value:
                    new_features.append(f"• {feature_name.title()}: {feature_value}")

            if new_features:
                enhanced_sections["features"] = (
                    current_features + "\n" + "\n".join(new_features)
                )

        return enhanced_sections

    def _rebuild_description(self, sections: dict[str, str]) -> str:
        """Rebuild description from enhanced sections."""
        section_order = [
            "intro",
            "features",
            "specs",
            "benefits",
            "warranty",
            "shipping",
            "cta",
        ]

        rebuild_sections: list[str] = []
        for section_name in section_order:
            if section_name in sections and sections[section_name]:
                rebuild_sections.append(sections[section_name])

        return self.mobile_formatting["section_spacing"].join(rebuild_sections)

    def _get_optimization_suggestions(
        self, description: str, category_id: str
    ) -> list[str]:
        """Get optimization suggestions for description."""
        suggestions: list[str] = []

        # Length suggestions
        if len(description) < 100:
            suggestions.append("Consider adding more product details and benefits")
        elif len(description) > 1000:
            suggestions.append("Consider shortening for better mobile readability")

        # Content suggestions
        if not self._has_product_benefits(description):
            suggestions.append("Add clear product benefits and advantages")

        if not self._has_call_to_action(description):
            suggestions.append("Include a compelling call to action")

        # Mobile suggestions
        if not self._is_mobile_friendly(description):
            suggestions.append("Optimize formatting for mobile viewing")

        # SEO suggestions
        category_type = self._identify_category_type(category_id)
        keywords = self.seo_keywords.get(category_type, [])

        if keywords:
            missing_keywords = [kw for kw in keywords if kw not in description.lower()]
            if missing_keywords:
                suggestions.append(
                    f"Consider adding keywords: {', '.join(missing_keywords[:3])}"
                )

        return suggestions
