"""
Content Validation Service implementation.

This module provides comprehensive validation for generated content,
ensuring MercadoLibre compliance and quality standards.
"""

import logging
import re
from decimal import Decimal
from typing import Any, TypedDict

from modules.content_generation.domain.entities import GeneratedContent
from modules.content_generation.domain.exceptions import (
    ContentValidationError,
)
from modules.content_generation.domain.ports.ai_service_protocols import (
    ContentValidationServiceProtocol,
)

logger = logging.getLogger(__name__)


class ValidationResult(TypedDict):
    """Type definition for validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


class ContentValidationResult(TypedDict):
    """Type definition for content validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    quality_score: float
    validation_details: dict[str, Any]


class ComplianceResult(TypedDict):
    """Type definition for compliance results."""

    is_compliant: bool
    issues: list[str]
    warnings: list[str]
    policy_violations: list[str]


class ProhibitedContentResult(TypedDict):
    """Type definition for prohibited content check results."""

    violations: list[str]


class ContactInfoResult(TypedDict):
    """Type definition for contact information check results."""

    has_contact_info: bool


class ExternalLinksResult(TypedDict):
    """Type definition for external links check results."""

    has_external_links: bool


class PromotionalLanguageResult(TypedDict):
    """Type definition for promotional language check results."""

    is_excessive: bool
    promotional_count: int


class MisleadingClaimsResult(TypedDict):
    """Type definition for misleading claims check results."""

    has_misleading_claims: bool


class PriceComplianceResult(TypedDict):
    """Type definition for price compliance check results."""

    is_compliant: bool
    violations: list[str]


class ContentValidationService(ContentValidationServiceProtocol):
    """
    Content validation service for MercadoLibre compliance.

    This service validates generated content against MercadoLibre policies,
    quality standards, and technical requirements.
    """

    def __init__(
        self,
        quality_threshold: float = 0.7,
        enable_strict_validation: bool = True,
    ):
        """
        Initialize the content validation service.

        Args:
            quality_threshold: Minimum quality threshold
            enable_strict_validation: Enable strict validation rules
        """
        self.quality_threshold = quality_threshold
        self.enable_strict_validation = enable_strict_validation

        # MercadoLibre prohibited words and phrases
        self.prohibited_words = {
            "spam_keywords": [
                "100% original",
                "garantizado",
                "súper barato",
                "oferta única",
                "aprovecha ahora",
                "último día",
                "stock limitado",
                "no te lo pierdas",
                "compra ya",
                "urgente",
                "increíble",
                "espectacular",
                "fantástico",
                "excelente oportunidad",
                "precio de loco",
                "regalado",
                "liquidación",
            ],
            "promotional_excess": [
                "!!!",
                "???",
                "GRATIS",
                "FREE",
                "PROMO",
                "DESCUENTO",
                "OFERTA",
                "LIQUIDACIÓN",
                "OPORTUNIDAD",
                "APROVECHA",
            ],
            "misleading_claims": [
                "mejor del mercado",
                "único en su tipo",
                "sin competencia",
                "el más barato",
                "precio más bajo",
                "garantía de por vida",
                "nunca vas a encontrar",
                "imposible de conseguir",
            ],
            "contact_info": [
                "whatsapp",
                "telefono",
                "email",
                "contacto",
                "llamar",
                "escribir",
                "mensaje",
                "chat",
                "comunicarse",
            ],
        }

        # MercadoLibre content policies
        self.content_policies = {
            "title_max_length": 60,
            "description_min_length": 50,
            "description_max_length": 2000,
            "max_capitalization_ratio": 0.3,
            "max_punctuation_ratio": 0.1,
            "max_emoji_ratio": 0.05,
            "required_sections": ["features", "benefits"],
            "prohibited_html": ["<script>", "<iframe>", "<embed>", "<object>"],
        }

        # Quality assessment criteria
        self.quality_criteria = {
            "completeness": {
                "weight": 0.25,
                "factors": ["has_brand", "has_model", "has_category", "has_price"],
            },
            "readability": {
                "weight": 0.20,
                "factors": [
                    "sentence_length",
                    "paragraph_structure",
                    "word_complexity",
                ],
            },
            "compliance": {
                "weight": 0.25,
                "factors": ["title_length", "description_length", "prohibited_content"],
            },
            "seo_optimization": {
                "weight": 0.15,
                "factors": ["keyword_density", "meta_information", "structure"],
            },
            "mobile_friendliness": {
                "weight": 0.15,
                "factors": ["line_length", "paragraph_length", "formatting"],
            },
        }

        # Common validation patterns
        self.validation_patterns = {
            "phone_number": r"(\+?[0-9]{1,3})?[-.\s]?(\([0-9]{1,4}\))?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "url": r"https?://[^\s]+",
            "excessive_caps": r"[A-Z]{4,}",
            "excessive_punctuation": r"[!?]{3,}",
            "currency": r"[\$\€\£\¥]",
        }

        logger.info("Initialized Content Validation Service")

    async def validate_content(
        self,
        content: GeneratedContent,
    ) -> ContentValidationResult:
        """
        Validate generated content comprehensively.

        Args:
            content: Generated content to validate

        Returns:
            Dict containing validation results

        Raises:
            ContentValidationError: If validation fails
        """
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "quality_score": 0.0,
                "validation_details": {},
            }

            # Validate title
            title_validation = self._validate_title(content.ml_title)
            validation_results["validation_details"]["title"] = title_validation

            if not title_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(title_validation["errors"])

            validation_results["warnings"].extend(title_validation["warnings"])

            # Validate description
            description_validation = self._validate_description(content.description)
            validation_results["validation_details"]["description"] = (
                description_validation
            )

            if not description_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(description_validation["errors"])

            validation_results["warnings"].extend(description_validation["warnings"])

            # Validate price
            price_validation = self._validate_price(content.ml_price)
            validation_results["validation_details"]["price"] = price_validation

            if not price_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(price_validation["errors"])

            # Validate attributes
            attributes_validation = self._validate_attributes(content.ml_attributes)
            validation_results["validation_details"]["attributes"] = (
                attributes_validation
            )

            if not attributes_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(attributes_validation["errors"])

            # Validate overall structure
            structure_validation = self._validate_structure(content)
            validation_results["validation_details"]["structure"] = structure_validation

            if not structure_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(structure_validation["errors"])

            # Calculate quality score
            quality_score = await self.calculate_quality_score(content)
            validation_results["quality_score"] = quality_score

            if quality_score < self.quality_threshold:
                validation_results["warnings"].append(
                    f"Quality score ({quality_score:.2f}) below threshold ({self.quality_threshold})"
                )

            logger.info(
                f"Content validation completed: {'PASS' if validation_results['is_valid'] else 'FAIL'}"
            )

            return validation_results

        except Exception as e:
            logger.error(f"Error validating content: {e}")
            raise ContentValidationError(
                f"Content validation failed: {str(e)}",
                error_code="VALIDATION_FAILED",
            ) from e

    async def check_ml_compliance(
        self,
        content: GeneratedContent,
    ) -> ComplianceResult:
        """
        Check if content complies with MercadoLibre policies.

        Args:
            content: Generated content to check

        Returns:
            Dict containing compliance results
        """
        compliance_results = {
            "is_compliant": True,
            "issues": [],
            "warnings": [],
            "policy_violations": [],
        }

        # Check for prohibited content
        prohibited_check = self._check_prohibited_content(
            content.ml_title + " " + content.description
        )
        if prohibited_check["violations"]:
            compliance_results["is_compliant"] = False
            compliance_results["policy_violations"].extend(
                prohibited_check["violations"]
            )

        # Check for contact information
        contact_check = self._check_contact_information(content.description)
        if contact_check["has_contact_info"]:
            compliance_results["is_compliant"] = False
            compliance_results["policy_violations"].append(
                "Contains contact information"
            )

        # Check for external links
        links_check = self._check_external_links(content.description)
        if links_check["has_external_links"]:
            compliance_results["is_compliant"] = False
            compliance_results["policy_violations"].append("Contains external links")

        # Check for excessive promotional language
        promotional_check = self._check_promotional_language(
            content.ml_title + " " + content.description
        )
        if promotional_check["is_excessive"]:
            compliance_results["warnings"].append("Excessive promotional language")

        # Check for misleading claims
        misleading_check = self._check_misleading_claims(content.description)
        if misleading_check["has_misleading_claims"]:
            compliance_results["is_compliant"] = False
            compliance_results["policy_violations"].append("Contains misleading claims")

        # Check price compliance
        price_compliance = self._check_price_compliance(content.ml_price)
        if not price_compliance["is_compliant"]:
            compliance_results["is_compliant"] = False
            compliance_results["policy_violations"].extend(
                price_compliance["violations"]
            )

        return compliance_results

    async def calculate_quality_score(
        self,
        content: GeneratedContent,
    ) -> float:
        """
        Calculate overall quality score for content.

        Args:
            content: Generated content to evaluate

        Returns:
            Quality score (0.0 to 1.0)
        """
        total_score = 0.0

        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(content)
        total_score += (
            completeness_score * self.quality_criteria["completeness"]["weight"]
        )

        # Calculate readability score
        readability_score = self._calculate_readability_score(content.description)
        total_score += (
            readability_score * self.quality_criteria["readability"]["weight"]
        )

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(content)
        total_score += compliance_score * self.quality_criteria["compliance"]["weight"]

        # Calculate SEO score
        seo_score = self._calculate_seo_score(content)
        total_score += seo_score * self.quality_criteria["seo_optimization"]["weight"]

        # Calculate mobile friendliness score
        mobile_score = self._calculate_mobile_friendliness_score(content.description)
        total_score += (
            mobile_score * self.quality_criteria["mobile_friendliness"]["weight"]
        )

        return min(total_score, 1.0)

    async def get_improvement_suggestions(
        self,
        content: GeneratedContent,
    ) -> list[str]:
        """
        Get suggestions for improving content quality.

        Args:
            content: Generated content to analyze

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Title suggestions
        if len(content.ml_title) < 30:
            suggestions.append("Consider adding more descriptive keywords to the title")
        elif len(content.ml_title) > 55:
            suggestions.append("Consider shortening the title for better readability")

        # Description suggestions
        if len(content.description) < 150:
            suggestions.append("Add more detailed product information and benefits")
        elif len(content.description) > 1000:
            suggestions.append(
                "Consider breaking the description into shorter paragraphs"
            )

        # Content structure suggestions
        if "•" not in content.description and "-" not in content.description:
            suggestions.append("Use bullet points to improve readability")

        # SEO suggestions
        if not any(char.isdigit() for char in content.ml_title):
            suggestions.append(
                "Consider adding model numbers or specifications to the title"
            )

        # Mobile suggestions
        if not self._is_mobile_friendly(content.description):
            suggestions.append("Optimize formatting for mobile viewing")

        # Attribute suggestions
        if len(content.ml_attributes) < 3:
            suggestions.append("Add more product attributes to improve discoverability")

        # Price suggestions
        if content.ml_price % 100 == 0:
            suggestions.append(
                "Consider psychological pricing (e.g., $199 instead of $200)"
            )

        return suggestions

    def _validate_title(self, title: str) -> ValidationResult:
        """Validate title content."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        # Length validation
        if len(title) > self.content_policies["title_max_length"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Title exceeds maximum length ({self.content_policies['title_max_length']})"
            )

        if len(title) < 10:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                "Title too short (minimum 10 characters)"
            )

        # Capitalization validation
        if self._has_excessive_capitalization(title):
            validation_result["warnings"].append("Title has excessive capitalization")

        # Punctuation validation
        if self._has_excessive_punctuation(title):
            validation_result["warnings"].append("Title has excessive punctuation")

        # Prohibited content validation
        prohibited_check = self._check_prohibited_content(title)
        if prohibited_check["violations"]:
            validation_result["is_valid"] = False
            validation_result["errors"].extend(prohibited_check["violations"])

        return validation_result

    def _validate_description(self, description: str) -> ValidationResult:
        """Validate description content."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        # Length validation
        if len(description) < self.content_policies["description_min_length"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Description too short (minimum {self.content_policies['description_min_length']})"
            )

        if len(description) > self.content_policies["description_max_length"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Description too long (maximum {self.content_policies['description_max_length']})"
            )

        # HTML validation
        for html_tag in self.content_policies["prohibited_html"]:
            if html_tag in description:
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Contains prohibited HTML: {html_tag}"
                )

        # Contact information validation
        contact_check = self._check_contact_information(description)
        if contact_check["has_contact_info"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Contains contact information")

        # External links validation
        links_check = self._check_external_links(description)
        if links_check["has_external_links"]:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Contains external links")

        return validation_result

    def _validate_price(self, price: Decimal | float) -> ValidationResult:
        """Validate price."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        if price <= 0:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Price must be greater than 0")

        if price > 10000000:  # 10 million ARS
            validation_result["warnings"].append("Price seems unusually high")

        if price < 1:
            validation_result["warnings"].append("Price seems unusually low")

        return validation_result

    def _validate_attributes(self, attributes: dict[str, Any]) -> ValidationResult:
        """Validate attributes."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        if not attributes:
            validation_result["warnings"].append("No attributes provided")
            return validation_result

        # Check for required attributes
        if "BRAND" not in attributes:
            validation_result["warnings"].append("Missing brand attribute")

        # Validate attribute values
        for attr_key, attr_value in attributes.items():
            if not attr_value or (
                isinstance(attr_value, str) and not attr_value.strip()
            ):
                validation_result["warnings"].append(
                    f"Empty attribute value: {attr_key}"
                )

        return validation_result

    def _validate_structure(self, content: GeneratedContent) -> ValidationResult:
        """Validate content structure."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check for required fields
        if not content.ml_category_id:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Missing category ID")

        if not content.ml_category_name:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Missing category name")

        # Check confidence scores
        if content.confidence_overall < 0.5:
            validation_result["warnings"].append("Low overall confidence score")

        return validation_result

    def _check_prohibited_content(self, text: str) -> ProhibitedContentResult:
        """Check for prohibited content."""
        violations = []
        text_lower = text.lower()

        # Check for spam keywords
        for keyword in self.prohibited_words["spam_keywords"]:
            if keyword in text_lower:
                violations.append(f"Contains spam keyword: {keyword}")

        # Check for misleading claims
        for claim in self.prohibited_words["misleading_claims"]:
            if claim in text_lower:
                violations.append(f"Contains misleading claim: {claim}")

        return {"violations": violations}

    def _check_contact_information(self, text: str) -> ContactInfoResult:
        """Check for contact information."""
        has_contact_info = False

        # Check for phone numbers
        if re.search(self.validation_patterns["phone_number"], text):
            has_contact_info = True

        # Check for email addresses
        if re.search(self.validation_patterns["email"], text):
            has_contact_info = True

        # Check for contact keywords
        text_lower = text.lower()
        for keyword in self.prohibited_words["contact_info"]:
            if keyword in text_lower:
                has_contact_info = True
                break

        return {"has_contact_info": has_contact_info}

    def _check_external_links(self, text: str) -> ExternalLinksResult:
        """Check for external links."""
        has_external_links = bool(re.search(self.validation_patterns["url"], text))

        return {"has_external_links": has_external_links}

    def _check_promotional_language(self, text: str) -> PromotionalLanguageResult:
        """Check for excessive promotional language."""
        promotional_count = 0
        text_lower = text.lower()

        for keyword in self.prohibited_words["promotional_excess"]:
            promotional_count += text_lower.count(keyword.lower())

        # Check for excessive punctuation
        excessive_punctuation = len(
            re.findall(self.validation_patterns["excessive_punctuation"], text)
        )

        is_excessive = promotional_count > 3 or excessive_punctuation > 2

        return {"is_excessive": is_excessive, "promotional_count": promotional_count}

    def _check_misleading_claims(self, text: str) -> MisleadingClaimsResult:
        """Check for misleading claims."""
        text_lower = text.lower()

        for claim in self.prohibited_words["misleading_claims"]:
            if claim in text_lower:
                return {"has_misleading_claims": True}

        return {"has_misleading_claims": False}

    def _check_price_compliance(self, price: float) -> PriceComplianceResult:
        """Check price compliance."""
        violations = []

        if price <= 0:
            violations.append("Price must be positive")

        if price != round(price, 2):
            violations.append("Price has more than 2 decimal places")

        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
        }

    def _has_excessive_capitalization(self, text: str) -> bool:
        """Check for excessive capitalization."""
        if not text:
            return False

        uppercase_count = sum(1 for c in text if c.isupper())
        total_letters = sum(1 for c in text if c.isalpha())

        if total_letters == 0:
            return False

        return (uppercase_count / total_letters) > self.content_policies[
            "max_capitalization_ratio"
        ]

    def _has_excessive_punctuation(self, text: str) -> bool:
        """Check for excessive punctuation."""
        if not text:
            return False

        punctuation_count = sum(1 for c in text if c in "!?.,;:")

        return (punctuation_count / len(text)) > self.content_policies[
            "max_punctuation_ratio"
        ]

    def _calculate_completeness_score(self, content: GeneratedContent) -> float:
        """Calculate completeness score."""
        score = 0.0

        # Check for required fields
        if content.ml_title:
            score += 0.25

        if content.description:
            score += 0.25

        if content.ml_category_id:
            score += 0.25

        if content.ml_price > 0:
            score += 0.25

        return score

    def _calculate_readability_score(self, description: str) -> float:
        """Calculate readability score."""
        if not description:
            return 0.0

        score = 0.0

        # Sentence length
        sentences = description.split(". ")
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(
                sentences
            )
            if 10 <= avg_sentence_length <= 20:
                score += 0.4
            elif 5 <= avg_sentence_length <= 30:
                score += 0.2

        # Paragraph structure
        paragraphs = description.split("\n\n")
        if 2 <= len(paragraphs) <= 6:
            score += 0.3

        # Mobile friendliness
        if self._is_mobile_friendly(description):
            score += 0.3

        return score

    def _calculate_compliance_score(self, content: GeneratedContent) -> float:
        """Calculate compliance score."""
        score = 0.0

        # Title compliance
        if 10 <= len(content.ml_title) <= 60:
            score += 0.3

        # Description compliance
        if 50 <= len(content.description) <= 2000:
            score += 0.3

        # Prohibited content check
        prohibited_check = self._check_prohibited_content(
            content.ml_title + " " + content.description
        )
        if not prohibited_check["violations"]:
            score += 0.4

        return score

    def _calculate_seo_score(self, content: GeneratedContent) -> float:
        """Calculate SEO score."""
        score = 0.0

        # Title optimization
        if any(char.isdigit() for char in content.ml_title):
            score += 0.3

        # Description structure
        if "•" in content.description or "-" in content.description:
            score += 0.3

        # Attribute presence
        if len(content.ml_attributes) >= 3:
            score += 0.4

        return score

    def _calculate_mobile_friendliness_score(self, description: str) -> float:
        """Calculate mobile friendliness score."""
        if self._is_mobile_friendly(description):
            return 1.0
        else:
            return 0.5

    def _is_mobile_friendly(self, description: str) -> bool:
        """Check if description is mobile-friendly."""
        lines = description.split("\n")

        # Check line length
        long_lines = [line for line in lines if len(line) > 80]
        if len(long_lines) > len(lines) * 0.3:
            return False

        # Check paragraph length
        paragraphs = description.split("\n\n")
        long_paragraphs = [p for p in paragraphs if len(p) > 300]
        return not len(long_paragraphs) > len(paragraphs) * 0.5
