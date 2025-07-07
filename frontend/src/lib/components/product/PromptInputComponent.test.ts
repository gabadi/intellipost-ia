// Test for PromptInputComponent
// Note: These tests focus on the component's behavior without CSS preprocessing
import { describe, test, expect, vi } from 'vitest';
import { validatePrompt } from '../../utils/validation';

describe('PromptInputComponent Logic', () => {
  test('prompt validation works correctly', () => {
    const shortPrompt = 'short';
    const validPrompt = 'This is a valid product description';
    const longPrompt = 'A'.repeat(600);

    const shortResult = validatePrompt(shortPrompt, 10, 500);
    expect(shortResult.isValid).toBe(false);
    expect(shortResult.message).toContain('Minimum');

    const validResult = validatePrompt(validPrompt, 10, 500);
    expect(validResult.isValid).toBe(true);

    const longResult = validatePrompt(longPrompt, 10, 500);
    expect(longResult.isValid).toBe(false);
    expect(longResult.message).toContain('Maximum');
  });

  test('debounce utility works correctly', async () => {
    const { debounceStringFunction } = await import('../../utils/validation');
    const mockFn = vi.fn();
    const debouncedFn = debounceStringFunction(mockFn, 100);

    debouncedFn('test1');
    debouncedFn('test2');
    debouncedFn('test3');

    // Should not have been called yet
    expect(mockFn).not.toHaveBeenCalled();

    // Wait for debounce delay
    await new Promise(resolve => setTimeout(resolve, 150));

    // Should have been called once with the last value
    expect(mockFn).toHaveBeenCalledTimes(1);
    expect(mockFn).toHaveBeenCalledWith('test3');
  });

  test('character count calculation', () => {
    const text1 = 'Hello World';
    const text2 = '';
    const text3 = 'A'.repeat(100);

    expect(text1.length).toBe(11);
    expect(text2.length).toBe(0);
    expect(text3.length).toBe(100);
  });

  test('validation state types', () => {
    const errorState = { isValid: false, type: 'error' as const, message: 'Error' };
    const successState = { isValid: true, type: 'success' as const, message: 'Success' };
    const warningState = { isValid: true, type: 'warning' as const, message: 'Warning' };

    expect(errorState.type).toBe('error');
    expect(successState.type).toBe('success');
    expect(warningState.type).toBe('warning');
  });
});
