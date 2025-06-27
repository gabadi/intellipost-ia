/**
 * Authentication form validation utilities.
 *
 * Provides validation functions for email, password, and form data
 * with real-time feedback for user experience.
 */

import type { PasswordValidation } from '../types/auth';

/**
 * Validate email format
 */
export function validateEmail(email: string): { isValid: boolean; error?: string } {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  if (email.length > 255) {
    return { isValid: false, error: 'Email must not exceed 255 characters' };
  }

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Please enter a valid email address' };
  }

  return { isValid: true };
}

/**
 * Validate password strength with detailed feedback
 */
export function validatePassword(password: string): PasswordValidation {
  const validation: PasswordValidation = {
    minLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /\d/.test(password),
    isValid: false,
  };

  validation.isValid = validation.minLength &&
                      validation.hasUpperCase &&
                      validation.hasLowerCase &&
                      validation.hasNumber;

  return validation;
}

/**
 * Get password strength level
 */
export function getPasswordStrength(password: string): 'weak' | 'medium' | 'strong' {
  const validation = validatePassword(password);

  if (!validation.minLength) return 'weak';

  const criteriaCount = [
    validation.hasUpperCase,
    validation.hasLowerCase,
    validation.hasNumber,
  ].filter(Boolean).length;

  if (criteriaCount < 2) return 'weak';
  if (criteriaCount === 2) return 'medium';
  return 'strong';
}

/**
 * Validate name field (first_name, last_name)
 */
export function validateName(name: string): { isValid: boolean; error?: string } {
  if (name && name.length > 100) {
    return { isValid: false, error: 'Name must not exceed 100 characters' };
  }

  // Name is optional, so empty is valid
  return { isValid: true };
}

/**
 * Validate login form data
 */
export function validateLoginForm(email: string, password: string): {
  isValid: boolean;
  errors: { email?: string; password?: string };
} {
  const errors: { email?: string; password?: string } = {};

  const emailValidation = validateEmail(email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error;
  }

  if (!password) {
    errors.password = 'Password is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate registration form data
 */
export function validateRegisterForm(
  email: string,
  password: string,
  firstName?: string,
  lastName?: string
): {
  isValid: boolean;
  errors: {
    email?: string;
    password?: string;
    firstName?: string;
    lastName?: string
  };
} {
  const errors: {
    email?: string;
    password?: string;
    firstName?: string;
    lastName?: string
  } = {};

  const emailValidation = validateEmail(email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error;
  }

  const passwordValidation = validatePassword(password);
  if (!passwordValidation.isValid) {
    errors.password = 'Password must be at least 8 characters with uppercase, lowercase, and number';
  }

  if (firstName) {
    const firstNameValidation = validateName(firstName);
    if (!firstNameValidation.isValid) {
      errors.firstName = firstNameValidation.error;
    }
  }

  if (lastName) {
    const lastNameValidation = validateName(lastName);
    if (!lastNameValidation.isValid) {
      errors.lastName = lastNameValidation.error;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Format validation error for display
 */
export function formatValidationError(error: string): string {
  // Make error messages more user-friendly
  return error.charAt(0).toUpperCase() + error.slice(1);
}

/**
 * Check if password meets minimum requirements for real-time feedback
 */
export function getPasswordRequirements(password: string): {
  minLength: { met: boolean; text: string };
  hasUpperCase: { met: boolean; text: string };
  hasLowerCase: { met: boolean; text: string };
  hasNumber: { met: boolean; text: string };
} {
  const validation = validatePassword(password);

  return {
    minLength: {
      met: validation.minLength,
      text: 'At least 8 characters',
    },
    hasUpperCase: {
      met: validation.hasUpperCase,
      text: 'One uppercase letter',
    },
    hasLowerCase: {
      met: validation.hasLowerCase,
      text: 'One lowercase letter',
    },
    hasNumber: {
      met: validation.hasNumber,
      text: 'One number',
    },
  };
}
