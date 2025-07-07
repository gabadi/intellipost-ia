import type { ValidationState, ImageValidationRules } from '../types/product';
import { DEFAULT_IMAGE_VALIDATION_RULES } from '../types/product';

export function validatePrompt(prompt: string, minLength = 10, maxLength = 500): ValidationState {
  const trimmedPrompt = prompt.trim();

  if (trimmedPrompt.length === 0) {
    return {
      isValid: false,
      message: 'Product description is required',
      type: 'error',
    };
  }

  if (trimmedPrompt.length < minLength) {
    return {
      isValid: false,
      message: `Minimum ${minLength} characters required`,
      type: 'error',
    };
  }

  if (trimmedPrompt.length > maxLength) {
    return {
      isValid: false,
      message: `Maximum ${maxLength} characters allowed`,
      type: 'error',
    };
  }

  // Warning state for length approaching limit
  if (trimmedPrompt.length > maxLength * 0.8) {
    return {
      isValid: true,
      message: `${maxLength - trimmedPrompt.length} characters remaining`,
      type: 'warning',
    };
  }

  return {
    isValid: true,
    message: 'Valid description',
    type: 'success',
  };
}

export function validateImageFile(
  file: File,
  rules: ImageValidationRules = DEFAULT_IMAGE_VALIDATION_RULES
): Promise<ValidationState> {
  return new Promise(resolve => {
    // Check file type
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !rules.allowedFormats.includes(fileExtension)) {
      resolve({
        isValid: false,
        message: `Invalid file type. Allowed: ${rules.allowedFormats.join(', ')}`,
        type: 'error',
      });
      return;
    }

    // Check file size
    if (file.size > rules.maxFileSize) {
      resolve({
        isValid: false,
        message: `File too large. Maximum ${(rules.maxFileSize / 1024 / 1024).toFixed(1)}MB allowed`,
        type: 'error',
      });
      return;
    }

    // Check image dimensions
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      if (img.width < rules.minResolution.width || img.height < rules.minResolution.height) {
        resolve({
          isValid: false,
          message: `Image too small. Minimum ${rules.minResolution.width}x${rules.minResolution.height}px required`,
          type: 'error',
        });
        return;
      }

      resolve({
        isValid: true,
        message: 'Valid image',
        type: 'success',
      });
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      resolve({
        isValid: false,
        message: 'Invalid image file',
        type: 'error',
      });
    };

    img.src = URL.createObjectURL(file);
  });
}

export function validateImageBatch(
  files: File[],
  rules: ImageValidationRules = DEFAULT_IMAGE_VALIDATION_RULES
): ValidationState {
  if (files.length === 0) {
    return {
      isValid: false,
      message: 'At least 1 image is required',
      type: 'error',
    };
  }

  if (files.length > rules.maxImages) {
    return {
      isValid: false,
      message: `Maximum ${rules.maxImages} images allowed`,
      type: 'error',
    };
  }

  const totalSize = files.reduce((sum, file) => sum + file.size, 0);
  if (totalSize > rules.maxTotalSize) {
    return {
      isValid: false,
      message: `Total file size too large. Maximum ${(rules.maxTotalSize / 1024 / 1024).toFixed(1)}MB allowed`,
      type: 'error',
    };
  }

  return {
    isValid: true,
    message: `${files.length} image${files.length === 1 ? '' : 's'} ready`,
    type: 'success',
  };
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Specialized debounce function for string validation
export function debounceStringFunction(
  func: (text: string) => void,
  delay: number
): (text: string) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (text: string) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(text), delay);
  };
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function getImageMetadata(file: File): Promise<{
  width: number;
  height: number;
  size: number;
  format: string;
}> {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      resolve({
        width: img.width,
        height: img.height,
        size: file.size,
        format: file.type.split('/')[1] || 'unknown',
      });
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      reject(new Error('Failed to load image'));
    };

    img.src = URL.createObjectURL(file);
  });
}
