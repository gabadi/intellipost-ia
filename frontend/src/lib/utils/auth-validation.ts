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
export function validateEmail(email: string): {
  isValid: boolean;
  error?: string;
  suggestion?: string;
} {
  if (!email) {
    return { isValid: false, error: 'Email is required to create your account' };
  }

  if (email.length > 255) {
    return { isValid: false, error: 'Email address is too long (255 characters max)' };
  }

  // Check for missing @ symbol
  if (!email.includes('@')) {
    return { isValid: false, error: 'Email must include an @ symbol (e.g., user@example.com)' };
  }

  // Check for missing domain
  const [, domain] = email.split('@');
  if (!domain || domain.length === 0) {
    return { isValid: false, error: 'Please include a domain (e.g., @gmail.com)' };
  }

  // Check for missing dot in domain
  if (!domain.includes('.')) {
    return { isValid: false, error: 'Domain must include a dot (e.g., gmail.com)' };
  }

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) {
    // Provide specific feedback based on common issues
    if (email.startsWith('@')) {
      return { isValid: false, error: 'Email cannot start with @ symbol' };
    }
    if (email.endsWith('@')) {
      return { isValid: false, error: 'Please add a domain after @ (e.g., @gmail.com)' };
    }
    if (email.includes('..')) {
      return { isValid: false, error: 'Email cannot contain consecutive dots (..)' };
    }
    return { isValid: false, error: 'Please check your email format (e.g., user@example.com)' };
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

  validation.isValid =
    validation.minLength &&
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
export function validateLoginForm(
  email: string,
  password: string
): {
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
    lastName?: string;
  };
} {
  const errors: {
    email?: string;
    password?: string;
    firstName?: string;
    lastName?: string;
  } = {};

  const emailValidation = validateEmail(email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.error;
  }

  const passwordValidation = validatePassword(password);
  if (!passwordValidation.isValid) {
    // Provide specific guidance based on what's missing
    const missing = [];
    if (!passwordValidation.minLength) missing.push('8+ characters');
    if (!passwordValidation.hasUpperCase) missing.push('uppercase letter');
    if (!passwordValidation.hasLowerCase) missing.push('lowercase letter');
    if (!passwordValidation.hasNumber) missing.push('number');

    if (missing.length === 1) {
      errors.password = `Password needs ${missing[0]}`;
    } else if (missing.length === 2) {
      errors.password = `Password needs ${missing[0]} and ${missing[1]}`;
    } else {
      errors.password = 'Check password requirements below';
    }
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
  minLength: { met: boolean; text: string; icon: string };
  hasUpperCase: { met: boolean; text: string; icon: string };
  hasLowerCase: { met: boolean; text: string; icon: string };
  hasNumber: { met: boolean; text: string; icon: string };
  allMet: boolean;
} {
  const validation = validatePassword(password);

  const requirements = {
    minLength: {
      met: validation.minLength,
      text: 'At least 8 characters',
      icon: validation.minLength ? '✓' : '○',
    },
    hasUpperCase: {
      met: validation.hasUpperCase,
      text: 'One uppercase letter',
      icon: validation.hasUpperCase ? '✓' : '○',
    },
    hasLowerCase: {
      met: validation.hasLowerCase,
      text: 'One lowercase letter',
      icon: validation.hasLowerCase ? '✓' : '○',
    },
    hasNumber: {
      met: validation.hasNumber,
      text: 'One number',
      icon: validation.hasNumber ? '✓' : '○',
    },
    allMet: validation.isValid,
  };

  return requirements;
}

/**
 * Enhanced email validation with typo suggestions
 */
const commonEmailDomains = [
  'gmail.com',
  'yahoo.com',
  'hotmail.com',
  'outlook.com',
  'icloud.com',
  'aol.com',
  'live.com',
  'msn.com',
  'protonmail.com',
  'yandex.com',
];

const commonTypos: Record<string, string> = {
  'gmai.com': 'gmail.com',
  'gmial.com': 'gmail.com',
  'gmaill.com': 'gmail.com',
  'gmail.co': 'gmail.com',
  'yahooo.com': 'yahoo.com',
  'yaho.com': 'yahoo.com',
  'yahoo.co': 'yahoo.com',
  'hotmial.com': 'hotmail.com',
  'hotmail.co': 'hotmail.com',
  'outlok.com': 'outlook.com',
  'outlook.co': 'outlook.com',
};

export function getEmailSuggestion(email: string): string | null {
  if (!email || !email.includes('@')) return null;

  const [localPart, domain] = email.split('@');
  if (!domain) return null;

  const lowerDomain = domain.toLowerCase();

  // Check for exact typo matches
  if (commonTypos[lowerDomain]) {
    return `${localPart}@${commonTypos[lowerDomain]}`;
  }

  // Check for similar domains using simple string distance
  for (const commonDomain of commonEmailDomains) {
    if (isTypoLike(lowerDomain, commonDomain)) {
      return `${localPart}@${commonDomain}`;
    }
  }

  return null;
}

function isTypoLike(typed: string, target: string): boolean {
  if (Math.abs(typed.length - target.length) > 2) return false;

  let differences = 0;
  const maxLen = Math.max(typed.length, target.length);

  for (let i = 0; i < maxLen; i++) {
    if (typed[i] !== target[i]) {
      differences++;
      if (differences > 2) return false;
    }
  }

  return differences > 0 && differences <= 2;
}
