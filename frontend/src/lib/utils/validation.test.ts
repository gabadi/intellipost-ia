import { describe, test, expect } from 'vitest';
import { validatePrompt, formatFileSize } from './validation';

describe('Validation Utilities', () => {
  describe('validatePrompt', () => {
    test('should validate empty prompt', () => {
      const result = validatePrompt('');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toBe('Product description is required');
    });

    test('should validate too short prompt', () => {
      const result = validatePrompt('short', 10);
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toBe('Minimum 10 characters required');
    });

    test('should validate too long prompt', () => {
      const longText = 'x'.repeat(501);
      const result = validatePrompt(longText, 10, 500);
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toBe('Maximum 500 characters allowed');
    });

    test('should show warning near limit', () => {
      const nearLimitText = 'x'.repeat(450); // 90% of 500
      const result = validatePrompt(nearLimitText, 10, 500);
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('warning');
      expect(result.message).toBe('50 characters remaining');
    });

    test('should validate correct prompt', () => {
      const validText = 'This is a valid product description';
      const result = validatePrompt(validText, 10, 500);
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
      expect(result.message).toBe('Valid description');
    });
  });

  describe('formatFileSize', () => {
    test('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    test('should format decimal values', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(1024 * 1024 * 1.5)).toBe('1.5 MB');
    });
  });
});
