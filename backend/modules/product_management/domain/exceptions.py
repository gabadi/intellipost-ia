"""
Product domain exceptions.

This module contains exceptions specific to product domain business rules.
Following YAGNI principle - only exceptions with clear use cases are defined.
"""


class ProductDomainError(Exception):
    """Base exception for product domain errors."""

    def __init__(self, message: str, product_id: str | None = None) -> None:
        super().__init__(message)
        self.product_id = product_id


class InvalidConfidenceScoreError(ProductDomainError):
    """Raised when confidence score is invalid or out of range."""

    def __init__(self, score: float, product_id: str | None = None) -> None:
        message = f"Invalid confidence score: {score}. Must be between 0.0 and 1.0"
        super().__init__(message, product_id)
        self.score = score


class ProductStatusTransitionError(ProductDomainError):
    """Raised when an invalid product status transition is attempted."""

    def __init__(
        self, current_status: str, target_status: str, product_id: str | None = None
    ) -> None:
        message = (
            f"Invalid status transition from '{current_status}' to '{target_status}'"
        )
        super().__init__(message, product_id)
        self.current_status = current_status
        self.target_status = target_status
