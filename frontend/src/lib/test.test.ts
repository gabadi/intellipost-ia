import { describe, it, expect } from 'vitest';
import { testFunction, testArray, type TestInterface } from './test';

describe('test module', () => {
  it('should format test data correctly', () => {
    const testData: TestInterface = { id: 1, name: 'Sample', active: true };
    const result = testFunction(testData);
    expect(result).toBe('Test item: Sample (active)');
  });

  it('should format inactive test data correctly', () => {
    const testData: TestInterface = { id: 2, name: 'Inactive', active: false };
    const result = testFunction(testData);
    expect(result).toBe('Test item: Inactive (inactive)');
  });

  it('should provide test array with correct structure', () => {
    expect(testArray).toHaveLength(2);
    expect(testArray[0]).toMatchObject({ id: 1, name: 'Test 1', active: true });
    expect(testArray[1]).toMatchObject({ id: 2, name: 'Test 2', active: false });
  });
});
