/**
 * Test suite for the enhanced error handling system.
 *
 * This module provides tests to validate error processing, categorization,
 * and user-friendly messaging functionality.
 */

import { describe, it, expect } from 'vitest';
import { ErrorHandler, ErrorCategory, ErrorSeverity } from './error-handler';

describe('ErrorHandler', () => {
  describe('Error Processing', () => {
    it('processes authentication error correctly', () => {
      const error = ErrorHandler.processError('Invalid email or password');

      expect(error.details.category).toBe(ErrorCategory.AUTHENTICATION);
      expect(error.details.code).toBe('AUTH_INVALID_CREDENTIALS');
      expect(error.details.severity).toBe(ErrorSeverity.MEDIUM);
      expect(error.details.recoverable).toBe(true);
      expect(error.details.retryable).toBe(true);
      expect(error.details.suggestions).toContain('Double-check your email address for typos');
    });

    it('processes validation error correctly', () => {
      const error = ErrorHandler.processError('User with this email already exists');

      expect(error.details.category).toBe(ErrorCategory.VALIDATION);
      expect(error.details.code).toBe('AUTH_EMAIL_EXISTS');
      expect(error.details.severity).toBe(ErrorSeverity.MEDIUM);
      expect(error.details.recoverable).toBe(true);
      expect(error.details.retryable).toBe(false);
    });

    it('processes network error correctly', () => {
      const error = ErrorHandler.processError('Failed to fetch');

      expect(error.details.category).toBe(ErrorCategory.NETWORK);
      expect(error.details.code).toBe('NETWORK_CONNECTION_ERROR');
      expect(error.details.severity).toBe(ErrorSeverity.HIGH);
      expect(error.details.recoverable).toBe(true);
      expect(error.details.retryable).toBe(true);
    });

    it('processes rate limiting error correctly', () => {
      const error = ErrorHandler.processError('Too many authentication attempts');

      expect(error.details.category).toBe(ErrorCategory.RATE_LIMIT);
      expect(error.details.code).toBe('AUTH_RATE_LIMITED');
      expect(error.details.severity).toBe(ErrorSeverity.MEDIUM);
      expect(error.details.recoverable).toBe(true);
      expect(error.details.retryable).toBe(false);
    });

    it('processes server error correctly', () => {
      const error = ErrorHandler.processError('Internal Server Error');

      expect(error.details.category).toBe(ErrorCategory.SERVER);
      expect(error.details.code).toBe('SERVER_INTERNAL_ERROR');
      expect(error.details.severity).toBe(ErrorSeverity.HIGH);
      expect(error.details.recoverable).toBe(true);
      expect(error.details.retryable).toBe(true);
    });

    it('falls back to status code processing', () => {
      const errorObj = { message: 'Unknown error', status: 401 };
      const error = ErrorHandler.processError(errorObj);

      expect(error.details.category).toBe(ErrorCategory.AUTHENTICATION);
      expect(error.details.code).toBe('UNAUTHORIZED');
      expect(error.details.severity).toBe(ErrorSeverity.HIGH);
    });

    it('handles unknown errors gracefully', () => {
      const error = ErrorHandler.processError('Completely unknown error message');

      expect(error.details.category).toBe(ErrorCategory.UNKNOWN);
      expect(error.details.severity).toBe(ErrorSeverity.MEDIUM);
      expect(error.details.recoverable).toBe(true);
    });

    it('processes object errors correctly', () => {
      const errorObj = {
        detail: 'Invalid credentials provided',
        status: 401,
      };
      const error = ErrorHandler.processError(errorObj);

      expect(error.message).toBe('Invalid credentials provided');
      expect(error.details.category).toBe(ErrorCategory.AUTHENTICATION);
    });
  });

  describe('Retry Logic', () => {
    it('determines retryable errors correctly', () => {
      const networkError = ErrorHandler.processError('Failed to fetch');
      const validationError = ErrorHandler.processError('User with this email already exists');

      expect(ErrorHandler.isRetryable(networkError)).toBe(true);
      expect(ErrorHandler.isRetryable(validationError)).toBe(false);
    });

    it('calculates retry delays correctly', () => {
      const networkError = ErrorHandler.processError('Failed to fetch');
      const rateLimitError = ErrorHandler.processError('Too many authentication attempts');

      const networkDelay = ErrorHandler.getRetryDelay(networkError, 1);
      const rateLimitDelay = ErrorHandler.getRetryDelay(rateLimitError, 1);

      expect(networkDelay).toBeGreaterThan(0);
      expect(networkDelay).toBeLessThanOrEqual(1500); // 1000ms + jitter
      expect(rateLimitDelay).toBe(0); // Rate limit errors are not retryable
    });
  });

  describe('Error Logging', () => {
    it('logs errors without throwing', () => {
      const error = ErrorHandler.processError('Test error');
      // Should not throw
      expect(() => ErrorHandler.logError(error, 'test_context')).not.toThrow();
    });
  });
});
