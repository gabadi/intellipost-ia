"""
ProductImageResolution value object for product image dimensions.

This module contains the ProductImageResolution value object that encapsulates
image dimensions with proper validation and business rules.
"""

from dataclasses import dataclass
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import ValueObjectValidationError


@dataclass(frozen=True)
class ProductImageResolution(BaseValueObject):
    """
    Value object for product image resolution.
    
    Encapsulates image width and height with validation rules for
    acceptable image dimensions according to business requirements.
    """
    
    width: int
    height: int
    
    # Business rules constants
    MIN_WIDTH = 200
    MIN_HEIGHT = 200
    MAX_WIDTH = 8000
    MAX_HEIGHT = 8000
    MIN_ASPECT_RATIO = 0.2  # Minimum aspect ratio (height/width or width/height)
    MAX_MEGAPIXELS = 50    # Maximum image size in megapixels
    
    def validate(self) -> None:
        """
        Validate image resolution according to business rules.
        
        Raises:
            ValueObjectValidationError: If validation fails.
        """
        errors = []
        
        # Validate dimensions are positive
        if self.width <= 0:
            errors.append(f"Width must be positive, got {self.width}")
        if self.height <= 0:
            errors.append(f"Height must be positive, got {self.height}")
            
        # If basic validation fails, don't continue
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Invalid image dimensions",
                errors=[ValueObjectValidationError(msg) for msg in errors]
            )
        
        # Validate minimum dimensions
        if self.width < self.MIN_WIDTH:
            errors.append(f"Width {self.width} is below minimum {self.MIN_WIDTH}")
        if self.height < self.MIN_HEIGHT:
            errors.append(f"Height {self.height} is below minimum {self.MIN_HEIGHT}")
            
        # Validate maximum dimensions
        if self.width > self.MAX_WIDTH:
            errors.append(f"Width {self.width} exceeds maximum {self.MAX_WIDTH}")
        if self.height > self.MAX_HEIGHT:
            errors.append(f"Height {self.height} exceeds maximum {self.MAX_HEIGHT}")
            
        # Validate aspect ratio
        aspect_ratio = min(self.width, self.height) / max(self.width, self.height)
        if aspect_ratio < self.MIN_ASPECT_RATIO:
            errors.append(
                f"Aspect ratio {aspect_ratio:.3f} is too extreme "
                f"(minimum: {self.MIN_ASPECT_RATIO})"
            )
            
        # Validate megapixels
        megapixels = (self.width * self.height) / 1_000_000
        if megapixels > self.MAX_MEGAPIXELS:
            errors.append(
                f"Image size {megapixels:.1f}MP exceeds maximum {self.MAX_MEGAPIXELS}MP"
            )
        
        if errors:
            from shared.value_objects.exceptions import MultipleValidationError
            raise MultipleValidationError(
                "Image resolution validation failed",
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
        if field_name in ("width", "height"):
            if not isinstance(field_value, int):
                raise ValueObjectValidationError(
                    f"{field_name} must be an integer, got {type(field_value).__name__}"
                )
            if field_value <= 0:
                raise ValueObjectValidationError(
                    f"{field_name} must be positive, got {field_value}"
                )
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio as width/height."""
        return self.width / self.height
    
    @property
    def megapixels(self) -> float:
        """Calculate image size in megapixels."""
        return (self.width * self.height) / 1_000_000
    
    @property
    def total_pixels(self) -> int:
        """Calculate total number of pixels."""
        return self.width * self.height
    
    def is_square(self, tolerance: float = 0.01) -> bool:
        """
        Check if the image is approximately square.
        
        Args:
            tolerance: Allowed deviation from perfect square (1.0 aspect ratio).
            
        Returns:
            True if the image is square within tolerance.
        """
        return abs(self.aspect_ratio - 1.0) <= tolerance
    
    def is_landscape(self) -> bool:
        """Check if the image is in landscape orientation."""
        return self.width > self.height
    
    def is_portrait(self) -> bool:
        """Check if the image is in portrait orientation."""
        return self.height > self.width
    
    def get_orientation(self) -> str:
        """
        Get image orientation as string.
        
        Returns:
            "square", "landscape", or "portrait"
        """
        if self.is_square():
            return "square"
        elif self.is_landscape():
            return "landscape"
        else:
            return "portrait"
    
    def scale_to_fit(self, max_width: int, max_height: int) -> "ProductImageResolution":
        """
        Scale resolution to fit within given bounds while maintaining aspect ratio.
        
        Args:
            max_width: Maximum allowed width.
            max_height: Maximum allowed height.
            
        Returns:
            New ProductImageResolution scaled to fit.
        """
        # Calculate scaling factors
        width_scale = max_width / self.width
        height_scale = max_height / self.height
        
        # Use the smaller scaling factor to maintain aspect ratio
        scale = min(width_scale, height_scale)
        
        # If image is already smaller, return as-is
        if scale >= 1.0:
            return self
        
        # Calculate new dimensions
        new_width = int(self.width * scale)
        new_height = int(self.height * scale)
        
        return ProductImageResolution(width=new_width, height=new_height)
    
    def __str__(self) -> str:
        """String representation showing dimensions and orientation."""
        return f"{self.width}x{self.height} ({self.get_orientation()})"