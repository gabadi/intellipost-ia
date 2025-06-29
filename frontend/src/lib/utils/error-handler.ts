/**
 * Standardized error handling for authentication and API calls
 */

export interface ApiError {
  error: string;
  error_code: string;
  status_code: number;
  request_id?: string;
}

export interface MobileError {
  code: string;
  title: string;
  message: string;
  suggested_action: string;
  recoverable: boolean;
  status_code: number;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export class AuthenticationError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly recoverable: boolean;
  public readonly requestId?: string;

  constructor(
    message: string,
    code: string,
    statusCode: number = 400,
    recoverable: boolean = true,
    requestId?: string
  ) {
    super(message);
    this.name = 'AuthenticationError';
    this.code = code;
    this.statusCode = statusCode;
    this.recoverable = recoverable;
    this.requestId = requestId;
  }

  static fromApiError(apiError: ApiError): AuthenticationError {
    return new AuthenticationError(
      apiError.error,
      apiError.error_code,
      apiError.status_code,
      isRecoverableError(apiError.error_code),
      apiError.request_id
    );
  }

  static fromMobileError(mobileError: { error: MobileError }): AuthenticationError {
    return new AuthenticationError(
      mobileError.error.message,
      mobileError.error.code,
      mobileError.error.status_code,
      mobileError.error.recoverable
    );
  }
}

/**
 * Check if an error code represents a recoverable error
 */
function isRecoverableError(errorCode: string): boolean {
  const nonRecoverableErrors = [
    'USER_INACTIVE',
    'ACCOUNT_SUSPENDED',
    'PERMISSION_DENIED',
    'INTERNAL_SERVER_ERROR',
  ];

  return !nonRecoverableErrors.includes(errorCode);
}

/**
 * Convert API error response to user-friendly error messages
 */
export function createUserFriendlyError(error: ApiError | MobileError | any): {
  title: string;
  message: string;
  action: string;
  recoverable: boolean;
} {
  // Handle mobile-optimized errors from backend
  if (error.error && typeof error.error === 'object') {
    const mobileError = error.error as MobileError;
    return {
      title: mobileError.title,
      message: mobileError.message,
      action: mobileError.suggested_action,
      recoverable: mobileError.recoverable,
    };
  }

  // Handle standard API errors
  const errorCode = error.error_code || error.code || 'UNKNOWN_ERROR';

  const errorMappings: Record<
    string,
    {
      title: string;
      message: string;
      action: string;
      recoverable: boolean;
    }
  > = {
    INVALID_CREDENTIALS: {
      title: 'Login Failed',
      message: 'Check your email and password, then try again.',
      action: 'Try Again',
      recoverable: true,
    },
    EMAIL_ALREADY_EXISTS: {
      title: 'Account Exists',
      message: 'An account with this email already exists. Try logging in instead.',
      action: 'Go to Login',
      recoverable: true,
    },
    WEAK_PASSWORD: {
      title: 'Password Too Weak',
      message: 'Use at least 8 characters with uppercase, lowercase, and numbers.',
      action: 'Try Another Password',
      recoverable: true,
    },
    INVALID_EMAIL_FORMAT: {
      title: 'Invalid Email',
      message: 'Please enter a valid email address.',
      action: 'Check Email',
      recoverable: true,
    },
    INVALID_TOKEN: {
      title: 'Session Expired',
      message: 'Your session has expired. Please log in again.',
      action: 'Log In',
      recoverable: true,
    },
    INVALID_REFRESH_TOKEN: {
      title: 'Session Expired',
      message: 'Your session has expired. Please log in again.',
      action: 'Log In',
      recoverable: true,
    },
    RATE_LIMIT_EXCEEDED: {
      title: 'Too Many Attempts',
      message: 'Please wait a moment before trying again.',
      action: 'Wait',
      recoverable: true,
    },
    USER_INACTIVE: {
      title: 'Account Suspended',
      message: 'Your account is temporarily suspended. Contact support for help.',
      action: 'Contact Support',
      recoverable: false,
    },
    NETWORK_ERROR: {
      title: 'Connection Error',
      message: 'Please check your internet connection and try again.',
      action: 'Retry',
      recoverable: true,
    },
    VALIDATION_ERROR: {
      title: 'Invalid Input',
      message: 'Please check your input and try again.',
      action: 'Fix Input',
      recoverable: true,
    },
    MISSING_AUTHORIZATION: {
      title: 'Login Required',
      message: 'Please log in to continue.',
      action: 'Log In',
      recoverable: true,
    },
  };

  return (
    errorMappings[errorCode] || {
      title: 'Something Went Wrong',
      message: error.error || error.message || 'An unexpected error occurred.',
      action: 'Try Again',
      recoverable: true,
    }
  );
}

/**
 * Extract validation errors from API response
 */
export function extractValidationErrors(error: any): ValidationError[] {
  const validationErrors: ValidationError[] = [];

  if (error.detail && Array.isArray(error.detail)) {
    // FastAPI validation error format
    for (const validationError of error.detail) {
      const field = validationError.loc?.[validationError.loc.length - 1] || 'unknown';
      validationErrors.push({
        field,
        message: validationError.msg || 'Invalid value',
        code: validationError.type || 'validation_error',
      });
    }
  } else if (error.error_code === 'VALIDATION_ERROR') {
    // Custom validation error format
    validationErrors.push({
      field: 'general',
      message: error.error || 'Validation failed',
      code: 'validation_error',
    });
  }

  return validationErrors;
}

/**
 * Handle network errors and convert them to AuthenticationError
 */
export function handleNetworkError(error: any): AuthenticationError {
  if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
    return new AuthenticationError(
      'Unable to connect to server. Please check your internet connection.',
      'NETWORK_ERROR',
      0,
      true
    );
  }

  if (error.name === 'AbortError') {
    return new AuthenticationError(
      'Request timed out. Please try again.',
      'TIMEOUT_ERROR',
      408,
      true
    );
  }

  return new AuthenticationError(
    'Network error occurred. Please try again.',
    'NETWORK_ERROR',
    0,
    true
  );
}

/**
 * Log authentication errors for debugging and analytics
 */
export function logAuthenticationError(
  error: AuthenticationError,
  context: {
    action: string;
    userId?: string;
    email?: string;
    userAgent?: string;
    url?: string;
  }
): void {
  const logData = {
    timestamp: new Date().toISOString(),
    error_code: error.code,
    message: error.message,
    status_code: error.statusCode,
    recoverable: error.recoverable,
    request_id: error.requestId,
    context: {
      action: context.action,
      user_id: context.userId,
      email: context.email,
      user_agent: context.userAgent || navigator.userAgent,
      url: context.url || window.location.href,
    },
  };

  // Log to console in development
  if (import.meta.env.DEV) {
    console.error('Authentication Error:', logData);
  }

  // In production, you might want to send this to an error tracking service
  // like Sentry, LogRocket, or your own analytics endpoint
  if (import.meta.env.PROD) {
    // Example: Send to error tracking service
    // errorTrackingService.captureException(error, logData);
  }
}

/**
 * Retry logic for recoverable authentication errors
 */
export async function retryAuthenticationAction<T>(
  action: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: AuthenticationError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await action();
    } catch (error) {
      if (error instanceof AuthenticationError) {
        lastError = error;

        // Don't retry non-recoverable errors
        if (!error.recoverable) {
          throw error;
        }

        // Don't retry client errors (4xx), only server errors (5xx) and network errors
        if (error.statusCode >= 400 && error.statusCode < 500) {
          throw error;
        }

        // Wait before retrying
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delayMs * (attempt + 1)));
        }
      } else {
        // Convert unknown errors to AuthenticationError
        lastError = handleNetworkError(error);
        if (!lastError.recoverable) {
          throw lastError;
        }
      }
    }
  }

  throw lastError!;
}

/**
 * Create error message for specific form fields
 */
export function getFieldErrorMessage(
  validationErrors: ValidationError[],
  fieldName: string
): string | null {
  const fieldError = validationErrors.find(error => error.field === fieldName);
  return fieldError ? fieldError.message : null;
}

/**
 * Check if error requires user to log in again
 */
export function requiresReAuthentication(error: AuthenticationError): boolean {
  const reAuthCodes = [
    'INVALID_TOKEN',
    'INVALID_REFRESH_TOKEN',
    'TOKEN_EXPIRED',
    'MISSING_AUTHORIZATION',
  ];

  return reAuthCodes.includes(error.code);
}

/**
 * Get appropriate HTTP status code for client-side routing
 */
export function getRouterStatusCode(error: AuthenticationError): number {
  // Map authentication errors to appropriate status codes for router handling
  const statusMapping: Record<string, number> = {
    INVALID_TOKEN: 401,
    INVALID_REFRESH_TOKEN: 401,
    MISSING_AUTHORIZATION: 401,
    USER_INACTIVE: 403,
    RATE_LIMIT_EXCEEDED: 429,
    NETWORK_ERROR: 503,
  };

  return statusMapping[error.code] || error.statusCode || 400;
}
