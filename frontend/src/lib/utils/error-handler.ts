/**
 * Enhanced error handling utilities for better user experience.
 *
 * This module provides comprehensive error handling with user-friendly messages,
 * error categorization, and recovery suggestions.
 */

export interface ErrorDetails {
  code: string;
  message: string;
  userMessage: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  recoverable: boolean;
  retryable: boolean;
  suggestions?: string[];
}

export enum ErrorCategory {
  AUTHENTICATION = 'authentication',
  VALIDATION = 'validation',
  NETWORK = 'network',
  SERVER = 'server',
  RATE_LIMIT = 'rate_limit',
  PERMISSION = 'permission',
  UNKNOWN = 'unknown',
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Enhanced authentication error handling.
 */
export class AuthError extends Error {
  readonly details: ErrorDetails;

  constructor(details: ErrorDetails) {
    super(details.message);
    this.name = 'AuthError';
    this.details = details;
  }
}

/**
 * Error message mappings for user-friendly feedback.
 */
const ERROR_MESSAGES: Record<string, Partial<ErrorDetails>> = {
  // Authentication errors
  'Invalid email or password': {
    code: 'AUTH_INVALID_CREDENTIALS',
    userMessage:
      'The email or password you entered is incorrect. Please check your credentials and try again.',
    category: ErrorCategory.AUTHENTICATION,
    severity: ErrorSeverity.MEDIUM,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Double-check your email address for typos',
      'Make sure your password is correct',
      'Try using the password reset feature if needed',
    ],
  },
  'Account is inactive': {
    code: 'AUTH_ACCOUNT_INACTIVE',
    userMessage: 'Your account is currently inactive. Please contact support for assistance.',
    category: ErrorCategory.AUTHENTICATION,
    severity: ErrorSeverity.HIGH,
    recoverable: false,
    retryable: false,
    suggestions: [
      'Contact customer support',
      'Check your email for account activation instructions',
    ],
  },
  'Account locked': {
    code: 'AUTH_ACCOUNT_LOCKED',
    userMessage:
      'Your account has been temporarily locked due to too many failed login attempts. Please try again later.',
    category: ErrorCategory.AUTHENTICATION,
    severity: ErrorSeverity.HIGH,
    recoverable: true,
    retryable: false,
    suggestions: [
      'Wait 15 minutes and try again',
      'Use the password reset feature',
      'Contact support if you continue having issues',
    ],
  },
  'User with this email already exists': {
    code: 'AUTH_EMAIL_EXISTS',
    userMessage:
      'An account with this email address already exists. Please use a different email or try logging in.',
    category: ErrorCategory.VALIDATION,
    severity: ErrorSeverity.MEDIUM,
    recoverable: true,
    retryable: false,
    suggestions: [
      'Try logging in with this email instead',
      'Use a different email address',
      'Use the password reset feature if you forgot your password',
    ],
  },
  'Password does not meet security requirements': {
    code: 'AUTH_WEAK_PASSWORD',
    userMessage:
      "Your password doesn't meet our security requirements. Please create a stronger password.",
    category: ErrorCategory.VALIDATION,
    severity: ErrorSeverity.MEDIUM,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Use at least 8 characters',
      'Include uppercase and lowercase letters',
      'Add numbers and special characters',
      'Avoid common words or personal information',
    ],
  },
  'Too many authentication attempts': {
    code: 'AUTH_RATE_LIMITED',
    userMessage: "You've made too many login attempts. Please wait a moment and try again.",
    category: ErrorCategory.RATE_LIMIT,
    severity: ErrorSeverity.MEDIUM,
    recoverable: true,
    retryable: false,
    suggestions: [
      'Wait 1 minute before trying again',
      'Check your internet connection',
      "Make sure you're using the correct credentials",
    ],
  },
  // Network errors
  'Failed to fetch': {
    code: 'NETWORK_CONNECTION_ERROR',
    userMessage:
      'Unable to connect to the server. Please check your internet connection and try again.',
    category: ErrorCategory.NETWORK,
    severity: ErrorSeverity.HIGH,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Check your internet connection',
      'Try refreshing the page',
      'Wait a moment and try again',
    ],
  },
  'Network request failed': {
    code: 'NETWORK_REQUEST_FAILED',
    userMessage: 'Network request failed. Please check your connection and try again.',
    category: ErrorCategory.NETWORK,
    severity: ErrorSeverity.HIGH,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Check your internet connection',
      'Try refreshing the page',
      'Contact support if the problem persists',
    ],
  },
  // Server errors
  'Internal Server Error': {
    code: 'SERVER_INTERNAL_ERROR',
    userMessage: 'Something went wrong on our end. Please try again in a moment.',
    category: ErrorCategory.SERVER,
    severity: ErrorSeverity.HIGH,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Try again in a few minutes',
      'Refresh the page',
      'Contact support if the problem continues',
    ],
  },
  'Service Unavailable': {
    code: 'SERVER_UNAVAILABLE',
    userMessage: 'The service is temporarily unavailable. Please try again later.',
    category: ErrorCategory.SERVER,
    severity: ErrorSeverity.HIGH,
    recoverable: true,
    retryable: true,
    suggestions: [
      'Try again in a few minutes',
      'Check our status page for updates',
      'Contact support if needed',
    ],
  },
};

/**
 * Enhanced error handler that categorizes errors and provides user-friendly messages.
 */
export class ErrorHandler {
  /**
   * Process and enhance an error with user-friendly details.
   */
  static processError(error: unknown): AuthError {
    let errorMessage = 'An unexpected error occurred';
    let statusCode = 0;

    // Extract error details from different error types
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      const errorObj = error as any;
      errorMessage = errorObj.detail || errorObj.message || errorMessage;
      statusCode = errorObj.status || 0;
    }

    // Look for matching error pattern
    const errorDetails = this.findErrorDetails(errorMessage, statusCode);

    return new AuthError({
      code: errorDetails.code || 'UNKNOWN_ERROR',
      message: errorMessage,
      userMessage: errorDetails.userMessage || this.getGenericUserMessage(statusCode),
      category: errorDetails.category || ErrorCategory.UNKNOWN,
      severity: errorDetails.severity || ErrorSeverity.MEDIUM,
      recoverable: errorDetails.recoverable ?? true,
      retryable: errorDetails.retryable ?? false,
      suggestions: errorDetails.suggestions || this.getGenericSuggestions(statusCode),
    });
  }

  /**
   * Find matching error details from the error message.
   */
  private static findErrorDetails(message: string, statusCode: number): Partial<ErrorDetails> {
    // Direct message match
    if (ERROR_MESSAGES[message]) {
      return ERROR_MESSAGES[message];
    }

    // Pattern matching for similar messages
    for (const [pattern, details] of Object.entries(ERROR_MESSAGES)) {
      if (message.toLowerCase().includes(pattern.toLowerCase())) {
        return details;
      }
    }

    // Status code-based fallback
    return this.getStatusCodeDetails(statusCode);
  }

  /**
   * Get error details based on HTTP status code.
   */
  private static getStatusCodeDetails(statusCode: number): Partial<ErrorDetails> {
    switch (statusCode) {
      case 400:
        return {
          code: 'BAD_REQUEST',
          category: ErrorCategory.VALIDATION,
          severity: ErrorSeverity.MEDIUM,
          recoverable: true,
          retryable: false,
        };
      case 401:
        return {
          code: 'UNAUTHORIZED',
          category: ErrorCategory.AUTHENTICATION,
          severity: ErrorSeverity.HIGH,
          recoverable: true,
          retryable: false,
        };
      case 403:
        return {
          code: 'FORBIDDEN',
          category: ErrorCategory.PERMISSION,
          severity: ErrorSeverity.HIGH,
          recoverable: false,
          retryable: false,
        };
      case 404:
        return {
          code: 'NOT_FOUND',
          category: ErrorCategory.SERVER,
          severity: ErrorSeverity.MEDIUM,
          recoverable: true,
          retryable: false,
        };
      case 429:
        return {
          code: 'RATE_LIMITED',
          category: ErrorCategory.RATE_LIMIT,
          severity: ErrorSeverity.MEDIUM,
          recoverable: true,
          retryable: false,
        };
      case 500:
      case 502:
      case 503:
      case 504:
        return {
          code: 'SERVER_ERROR',
          category: ErrorCategory.SERVER,
          severity: ErrorSeverity.HIGH,
          recoverable: true,
          retryable: true,
        };
      default:
        return {
          code: 'UNKNOWN_ERROR',
          category: ErrorCategory.UNKNOWN,
          severity: ErrorSeverity.MEDIUM,
          recoverable: true,
          retryable: false,
        };
    }
  }

  /**
   * Get generic user-friendly message based on status code.
   */
  private static getGenericUserMessage(statusCode: number): string {
    switch (Math.floor(statusCode / 100)) {
      case 4:
        return 'There was a problem with your request. Please check your input and try again.';
      case 5:
        return "We're experiencing technical difficulties. Please try again in a moment.";
      default:
        return 'Something unexpected happened. Please try again.';
    }
  }

  /**
   * Get generic suggestions based on status code.
   */
  private static getGenericSuggestions(statusCode: number): string[] {
    switch (Math.floor(statusCode / 100)) {
      case 4:
        return [
          'Check your input for errors',
          'Make sure all required fields are filled',
          'Try refreshing the page',
        ];
      case 5:
        return [
          'Try again in a few minutes',
          'Refresh the page',
          'Contact support if the problem persists',
        ];
      default:
        return ['Try again', 'Refresh the page', 'Contact support if needed'];
    }
  }

  /**
   * Check if an error is retryable.
   */
  static isRetryable(error: AuthError): boolean {
    return (
      error.details.retryable &&
      error.details.category !== ErrorCategory.VALIDATION &&
      error.details.category !== ErrorCategory.PERMISSION
    );
  }

  /**
   * Get retry delay based on error type.
   */
  static getRetryDelay(error: AuthError, attempt: number = 1): number {
    if (!this.isRetryable(error)) return 0;

    // Exponential backoff with jitter
    const baseDelay = error.details.category === ErrorCategory.RATE_LIMIT ? 5000 : 1000;
    const delay = baseDelay * Math.pow(2, attempt - 1);
    const jitter = Math.random() * 0.1 * delay;

    return Math.min(delay + jitter, 30000); // Max 30 seconds
  }

  /**
   * Log error for debugging and analytics.
   */
  static logError(error: AuthError, context: string = ''): void {
    const logData = {
      timestamp: new Date().toISOString(),
      context,
      code: error.details.code,
      message: error.message,
      category: error.details.category,
      severity: error.details.severity,
      recoverable: error.details.recoverable,
      retryable: error.details.retryable,
    };

    if (error.details.severity === ErrorSeverity.CRITICAL) {
      console.error('Critical authentication error:', logData);
    } else if (error.details.severity === ErrorSeverity.HIGH) {
      console.error('High severity authentication error:', logData);
    } else {
      console.warn('Authentication error:', logData);
    }

    // In production, send to error tracking service
    if (import.meta.env.PROD) {
      // Example: Send to Sentry, LogRocket, etc.
      // errorTrackingService.captureError(error, logData);
    }
  }
}
