"""
Validation result value objects for content generation.

This module contains value objects for content validation and ML compliance results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class ContentValidationResult(BaseValueObject):
    """
    Value object for content validation results.
    
    Encapsulates validation results from content analysis including
    quality metrics, compliance checks, and validation errors.
    """
    
    # Validation status
    valid: bool
    validation_score: float
    content_quality_score: float
    
    # Quality metrics
    readability_score: float | None = None
    grammar_score: float | None = None
    
    # Validation details
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    validation_suggestions: list[str] = field(default_factory=list)
    
    # Content analysis
    word_count: int | None = None
    character_count: int | None = None
    sentence_count: int | None = None
    
    # SEO analysis
    seo_score: float | None = None
    keyword_density: float | None = None
    title_optimization: float | None = None
    
    # Validation metadata - with default values
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now())
    validation_engine: str = field(default="default")
    validation_version: str = field(default="1.0")
    
    # Business rule constants
    MIN_VALIDATION_SCORE = 0.0
    MAX_VALIDATION_SCORE = 1.0
    MIN_QUALITY_SCORE = 0.0
    MAX_QUALITY_SCORE = 1.0
    MAX_ERRORS = 100
    MAX_WARNINGS = 100
    MAX_SUGGESTIONS = 100
    
    def validate(self) -> None:
        """
        Validate content validation result according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate scores
        score_fields = [
            ("validation_score", self.validation_score),
            ("content_quality_score", self.content_quality_score),
            ("readability_score", self.readability_score),
            ("grammar_score", self.grammar_score),
            ("seo_score", self.seo_score),
            ("keyword_density", self.keyword_density),
            ("title_optimization", self.title_optimization),
        ]
        
        for field_name, score in score_fields:
            if score is not None:
                if not isinstance(score, (int, float)):
                    errors.append(f"{field_name} must be a number, got {type(score).__name__}")
                elif not (self.MIN_VALIDATION_SCORE <= score <= self.MAX_VALIDATION_SCORE):
                    errors.append(
                        f"{field_name} {score} must be between "
                        f"{self.MIN_VALIDATION_SCORE} and {self.MAX_VALIDATION_SCORE}"
                    )
        
        # Validate counts
        count_fields = [
            ("word_count", self.word_count),
            ("character_count", self.character_count),
            ("sentence_count", self.sentence_count),
        ]
        
        for field_name, count in count_fields:
            if count is not None:
                if not isinstance(count, int):
                    errors.append(f"{field_name} must be an integer, got {type(count).__name__}")
                elif count < 0:
                    errors.append(f"{field_name} must be non-negative, got {count}")
        
        # Validate list sizes
        if len(self.validation_errors) > self.MAX_ERRORS:
            errors.append(f"Too many validation errors: {len(self.validation_errors)} (max: {self.MAX_ERRORS})")
        
        if len(self.validation_warnings) > self.MAX_WARNINGS:
            errors.append(f"Too many validation warnings: {len(self.validation_warnings)} (max: {self.MAX_WARNINGS})")
        
        if len(self.validation_suggestions) > self.MAX_SUGGESTIONS:
            errors.append(f"Too many validation suggestions: {len(self.validation_suggestions)} (max: {self.MAX_SUGGESTIONS})")
        
        # Validate list contents
        for i, error in enumerate(self.validation_errors):
            if not isinstance(error, str):
                errors.append(f"validation_errors[{i}] must be a string, got {type(error).__name__}")
        
        for i, warning in enumerate(self.validation_warnings):
            if not isinstance(warning, str):
                errors.append(f"validation_warnings[{i}] must be a string, got {type(warning).__name__}")
        
        for i, suggestion in enumerate(self.validation_suggestions):
            if not isinstance(suggestion, str):
                errors.append(f"validation_suggestions[{i}] must be a string, got {type(suggestion).__name__}")
        
        # Validate engine and version
        if not isinstance(self.validation_engine, str) or not self.validation_engine:
            errors.append("validation_engine must be a non-empty string")
        
        if not isinstance(self.validation_version, str) or not self.validation_version:
            errors.append("validation_version must be a non-empty string")
        
        # Business logic validation
        if not self.valid and len(self.validation_errors) == 0:
            errors.append("Content marked as invalid must have validation errors")
        
        if self.valid and self.validation_score < 0.5:
            errors.append("Valid content should have validation score >= 0.5")
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Content validation result validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
            )
    
    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.
        
        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.
            
        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        if field_name in ("validation_score", "content_quality_score", "readability_score", "grammar_score", "seo_score"):
            if field_value is not None:
                if not isinstance(field_value, (int, float)):
                    raise ValueObjectValidationError(
                        f"{field_name} must be a number, got {type(field_value).__name__}"
                    )
                if not (self.MIN_VALIDATION_SCORE <= field_value <= self.MAX_VALIDATION_SCORE):
                    raise ValueObjectValidationError(
                        f"{field_name} {field_value} must be between "
                        f"{self.MIN_VALIDATION_SCORE} and {self.MAX_VALIDATION_SCORE}"
                    )
        
        elif field_name in ("word_count", "character_count", "sentence_count"):
            if field_value is not None:
                if not isinstance(field_value, int):
                    raise ValueObjectValidationError(
                        f"{field_name} must be an integer, got {type(field_value).__name__}"
                    )
                if field_value < 0:
                    raise ValueObjectValidationError(
                        f"{field_name} must be non-negative, got {field_value}"
                    )
        
        elif field_name == "valid":
            if not isinstance(field_value, bool):
                raise ValueObjectValidationError(
                    f"valid must be a boolean, got {type(field_value).__name__}"
                )
    
    @property
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.validation_errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.validation_warnings) > 0
    
    @property
    def has_suggestions(self) -> bool:
        """Check if there are validation suggestions."""
        return len(self.validation_suggestions) > 0
    
    @property
    def overall_quality(self) -> str:
        """Get overall quality assessment."""
        if self.validation_score >= 0.9:
            return "excellent"
        elif self.validation_score >= 0.7:
            return "good"
        elif self.validation_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    @property
    def is_valid(self) -> bool:
        """Check if content is valid (backwards compatibility property)."""
        return self.valid
    
    @property
    def is_production_ready(self) -> bool:
        """Check if content is ready for production."""
        return self.valid and self.validation_score >= 0.7 and not self.has_errors
    
    def add_error(self, error_message: str) -> "ContentValidationResult":
        """
        Add a validation error to the result.
        
        Args:
            error_message: Error message to add.
            
        Returns:
            New ContentValidationResult with added error.
        """
        new_errors = list(self.validation_errors) + [error_message]
        
        if len(new_errors) > self.MAX_ERRORS:
            new_errors = new_errors[-self.MAX_ERRORS:]
        
        return self.__class__(
            valid=False,  # Adding an error makes content invalid
            validation_score=min(self.validation_score - 0.1, 0.0),  # Reduce score
            content_quality_score=self.content_quality_score,
            readability_score=self.readability_score,
            grammar_score=self.grammar_score,
            validation_errors=new_errors,
            validation_warnings=self.validation_warnings,
            validation_suggestions=self.validation_suggestions,
            word_count=self.word_count,
            character_count=self.character_count,
            sentence_count=self.sentence_count,
            seo_score=self.seo_score,
            keyword_density=self.keyword_density,
            title_optimization=self.title_optimization,
            validation_timestamp=self.validation_timestamp,
            validation_engine=self.validation_engine,
            validation_version=self.validation_version,
        )
    
    def add_warning(self, warning_message: str) -> "ContentValidationResult":
        """
        Add a validation warning to the result.
        
        Args:
            warning_message: Warning message to add.
            
        Returns:
            New ContentValidationResult with added warning.
        """
        new_warnings = list(self.validation_warnings) + [warning_message]
        
        if len(new_warnings) > self.MAX_WARNINGS:
            new_warnings = new_warnings[-self.MAX_WARNINGS:]
        
        return self.__class__(
            valid=self.valid,
            validation_score=self.validation_score,
            content_quality_score=self.content_quality_score,
            readability_score=self.readability_score,
            grammar_score=self.grammar_score,
            validation_errors=self.validation_errors,
            validation_warnings=new_warnings,
            validation_suggestions=self.validation_suggestions,
            word_count=self.word_count,
            character_count=self.character_count,
            sentence_count=self.sentence_count,
            seo_score=self.seo_score,
            keyword_density=self.keyword_density,
            title_optimization=self.title_optimization,
            validation_timestamp=self.validation_timestamp,
            validation_engine=self.validation_engine,
            validation_version=self.validation_version,
        )


@dataclass(frozen=True)
class MLComplianceResult(BaseValueObject):
    """
    Value object for ML compliance analysis results.
    
    Encapsulates compliance checking results from machine learning
    analysis including policy violations, risk assessments, and regulatory compliance.
    """
    
    # Compliance status
    compliant: bool
    compliance_score: float
    risk_level: str  # low, medium, high, critical
    
    # Policy violations
    policy_violations: list[dict[str, Any]] = field(default_factory=list)
    regulatory_flags: list[str] = field(default_factory=list)
    
    # Risk analysis
    content_risk_score: float | None = None
    brand_safety_score: float | None = None
    legal_risk_score: float | None = None
    
    # Detected issues
    detected_toxicity: float | None = None
    detected_bias: float | None = None
    detected_misinformation: float | None = None
    
    # Compliance details
    checked_policies: list[str] = field(default_factory=list)
    skipped_policies: list[str] = field(default_factory=list)
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now())
    analysis_engine: str = "ml_compliance"
    analysis_version: str = "1.0"
    confidence_level: float = 0.95
    
    # Business rule constants
    MIN_COMPLIANCE_SCORE = 0.0
    MAX_COMPLIANCE_SCORE = 1.0
    VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
    MAX_VIOLATIONS = 50
    MAX_FLAGS = 50
    MAX_POLICIES = 100
    
    def validate(self) -> None:
        """
        Validate ML compliance result according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate scores
        score_fields = [
            ("compliance_score", self.compliance_score),
            ("content_risk_score", self.content_risk_score),
            ("brand_safety_score", self.brand_safety_score),
            ("legal_risk_score", self.legal_risk_score),
            ("detected_toxicity", self.detected_toxicity),
            ("detected_bias", self.detected_bias),
            ("detected_misinformation", self.detected_misinformation),
            ("confidence_level", self.confidence_level),
        ]
        
        for field_name, score in score_fields:
            if score is not None:
                if not isinstance(score, (int, float)):
                    errors.append(f"{field_name} must be a number, got {type(score).__name__}")
                elif not (self.MIN_COMPLIANCE_SCORE <= score <= self.MAX_COMPLIANCE_SCORE):
                    errors.append(
                        f"{field_name} {score} must be between "
                        f"{self.MIN_COMPLIANCE_SCORE} and {self.MAX_COMPLIANCE_SCORE}"
                    )
        
        # Validate risk level
        if self.risk_level not in self.VALID_RISK_LEVELS:
            errors.append(f"risk_level must be one of {self.VALID_RISK_LEVELS}, got {self.risk_level}")
        
        # Validate list sizes
        if len(self.policy_violations) > self.MAX_VIOLATIONS:
            errors.append(f"Too many policy violations: {len(self.policy_violations)} (max: {self.MAX_VIOLATIONS})")
        
        if len(self.regulatory_flags) > self.MAX_FLAGS:
            errors.append(f"Too many regulatory flags: {len(self.regulatory_flags)} (max: {self.MAX_FLAGS})")
        
        if len(self.checked_policies) > self.MAX_POLICIES:
            errors.append(f"Too many checked policies: {len(self.checked_policies)} (max: {self.MAX_POLICIES})")
        
        if len(self.skipped_policies) > self.MAX_POLICIES:
            errors.append(f"Too many skipped policies: {len(self.skipped_policies)} (max: {self.MAX_POLICIES})")
        
        # Validate policy violations structure
        for i, violation in enumerate(self.policy_violations):
            if not isinstance(violation, dict):
                errors.append(f"policy_violations[{i}] must be a dict, got {type(violation).__name__}")
                continue
            
            required_fields = ["policy_id", "violation_type", "severity", "description"]
            for field_name in required_fields:
                if field_name not in violation:
                    errors.append(f"policy_violations[{i}] missing required field: {field_name}")
        
        # Validate string lists
        for i, flag in enumerate(self.regulatory_flags):
            if not isinstance(flag, str):
                errors.append(f"regulatory_flags[{i}] must be a string, got {type(flag).__name__}")
        
        for i, policy in enumerate(self.checked_policies):
            if not isinstance(policy, str):
                errors.append(f"checked_policies[{i}] must be a string, got {type(policy).__name__}")
        
        for i, policy in enumerate(self.skipped_policies):
            if not isinstance(policy, str):
                errors.append(f"skipped_policies[{i}] must be a string, got {type(policy).__name__}")
        
        # Validate engine and version
        if not isinstance(self.analysis_engine, str) or not self.analysis_engine:
            errors.append("analysis_engine must be a non-empty string")
        
        if not isinstance(self.analysis_version, str) or not self.analysis_version:
            errors.append("analysis_version must be a non-empty string")
        
        # Business logic validation
        if not self.compliant and len(self.policy_violations) == 0:
            errors.append("Non-compliant content must have policy violations")
        
        if self.compliant and self.risk_level == "critical":
            errors.append("Compliant content cannot have critical risk level")
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "ML compliance result validation failed",
                errors=[ValueObjectValidationError(msg) for msg in errors]
            )
    
    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.
        
        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.
            
        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        if field_name in ("compliance_score", "content_risk_score", "brand_safety_score", "legal_risk_score"):
            if field_value is not None:
                if not isinstance(field_value, (int, float)):
                    raise ValueObjectValidationError(
                        f"{field_name} must be a number, got {type(field_value).__name__}"
                    )
                if not (self.MIN_COMPLIANCE_SCORE <= field_value <= self.MAX_COMPLIANCE_SCORE):
                    raise ValueObjectValidationError(
                        f"{field_name} {field_value} must be between "
                        f"{self.MIN_COMPLIANCE_SCORE} and {self.MAX_COMPLIANCE_SCORE}"
                    )
        
        elif field_name == "risk_level":
            if field_value not in self.VALID_RISK_LEVELS:
                raise ValueObjectValidationError(
                    f"risk_level must be one of {self.VALID_RISK_LEVELS}, got {field_value}"
                )
        
        elif field_name == "compliant":
            if not isinstance(field_value, bool):
                raise ValueObjectValidationError(
                    f"compliant must be a boolean, got {type(field_value).__name__}"
                )
    
    @property
    def has_violations(self) -> bool:
        """Check if there are policy violations."""
        return len(self.policy_violations) > 0
    
    @property
    def has_regulatory_flags(self) -> bool:
        """Check if there are regulatory flags."""
        return len(self.regulatory_flags) > 0
    
    @property
    def is_high_risk(self) -> bool:
        """Check if content is high risk."""
        return self.risk_level in ("high", "critical")
    
    @property
    def is_compliant(self) -> bool:
        """Check if content is compliant (backwards compatibility property)."""
        return self.compliant
    
    @property
    def requires_human_review(self) -> bool:
        """Check if content requires human review."""
        return (
            not self.compliant or 
            self.is_high_risk or 
            self.compliance_score < 0.8 or
            len(self.policy_violations) > 0
        )
    
    @property
    def overall_risk_assessment(self) -> str:
        """Get overall risk assessment."""
        if self.compliance_score >= 0.9 and self.risk_level == "low":
            return "minimal_risk"
        elif self.compliance_score >= 0.7 and self.risk_level in ("low", "medium"):
            return "acceptable_risk"
        elif self.compliance_score >= 0.5:
            return "elevated_risk"
        else:
            return "high_risk"
    
    def add_violation(self, policy_id: str, violation_type: str, severity: str, description: str) -> "MLComplianceResult":
        """
        Add a policy violation to the result.
        
        Args:
            policy_id: ID of the violated policy.
            violation_type: Type of violation.
            severity: Severity level.
            description: Description of the violation.
            
        Returns:
            New MLComplianceResult with added violation.
        """
        new_violation = {
            "policy_id": policy_id,
            "violation_type": violation_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        
        new_violations = list(self.policy_violations) + [new_violation]
        
        if len(new_violations) > self.MAX_VIOLATIONS:
            new_violations = new_violations[-self.MAX_VIOLATIONS:]
        
        # Adjust risk level based on severity
        new_risk_level = self.risk_level
        if severity == "critical" and self.risk_level != "critical":
            new_risk_level = "critical"
        elif severity == "high" and self.risk_level in ("low", "medium"):
            new_risk_level = "high"
        
        return self.__class__(
            compliant=False,  # Adding a violation makes content non-compliant
            compliance_score=max(self.compliance_score - 0.2, 0.0),  # Reduce score
            risk_level=new_risk_level,
            policy_violations=new_violations,
            regulatory_flags=self.regulatory_flags,
            content_risk_score=self.content_risk_score,
            brand_safety_score=self.brand_safety_score,
            legal_risk_score=self.legal_risk_score,
            detected_toxicity=self.detected_toxicity,
            detected_bias=self.detected_bias,
            detected_misinformation=self.detected_misinformation,
            checked_policies=self.checked_policies,
            skipped_policies=self.skipped_policies,
            analysis_timestamp=self.analysis_timestamp,
            analysis_engine=self.analysis_engine,
            analysis_version=self.analysis_version,
            confidence_level=self.confidence_level,
        )