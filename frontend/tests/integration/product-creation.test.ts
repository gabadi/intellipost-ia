import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { productCreationStore } from '../../src/lib/stores/product-creation';
import type { ProductImageData } from '../../src/lib/types/product';

describe('Product Creation Form Integration Test - FIXED BUG', () => {
  beforeEach(() => {
    // Reset store before each test
    productCreationStore.reset();
  });

  it('should demonstrate the fix: form validation follows store state correctly', () => {
    // Initial state - everything should be invalid
    let state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(false);
    expect(state.validation.images.isValid).toBe(false);
    expect(state.validation.form.isValid).toBe(false);

    // Add a valid prompt
    const validPrompt = 'This is a valid product description with more than 10 characters';
    productCreationStore.setPromptText(validPrompt);

    state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(false); // Still no images
    expect(state.validation.form.isValid).toBe(false); // Form invalid because no images

    // Add valid images
    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock content'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
      {
        id: '2',
        file: new File(['mock content'], 'test2.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
      {
        id: '3',
        file: new File(['mock content'], 'test3.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
    ];

    productCreationStore.addImages(mockImages);

    // After adding images, everything should be valid
    state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(true);
    expect(state.validation.form.isValid).toBe(true);

    // The page component now uses these reactive statements:
    // $: promptValidation = $productCreationStore.validation.prompt;
    // $: imagesValidation = $productCreationStore.validation.images;
    // $: isFormValid = $productCreationStore.validation.form.isValid;
    // $: canSubmit = isFormValid && !isLoading;

    // So when the store state changes, the page will automatically update
    // and the Create Product button will be enabled!

    // Verify the store derived values
    const isFormValid = get(productCreationStore.isFormValid);
    expect(isFormValid).toBe(true);
  });

  it('should work correctly when adding images first, then prompt', () => {
    // Add images first
    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock content'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
      {
        id: '2',
        file: new File(['mock content'], 'test2.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
      {
        id: '3',
        file: new File(['mock content'], 'test3.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
    ];

    productCreationStore.addImages(mockImages);

    let state = get(productCreationStore);
    expect(state.validation.images.isValid).toBe(true);
    expect(state.validation.prompt.isValid).toBe(false); // No prompt yet
    expect(state.validation.form.isValid).toBe(false); // Form invalid because no prompt

    // Then add prompt
    const validPrompt = 'This is a valid product description with more than 10 characters';
    productCreationStore.setPromptText(validPrompt);

    state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(true);
    expect(state.validation.form.isValid).toBe(true); // Now form is valid!
  });

  it('should correctly handle edge cases', () => {
    // Test with minimum valid prompt length
    const minValidPrompt = 'a'.repeat(10); // Exactly 10 characters
    productCreationStore.setPromptText(minValidPrompt);

    // Add minimum valid images (1 image)
    const singleImage: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock content'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
    ];

    productCreationStore.addImages(singleImage);

    const state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(true);
    expect(state.validation.form.isValid).toBe(true);
  });

  it('should handle invalid states correctly', () => {
    // Test with invalid prompt (too short)
    const invalidPrompt = 'Short'; // Less than 10 characters
    productCreationStore.setPromptText(invalidPrompt);

    // Add valid images
    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock content'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
    ];

    productCreationStore.addImages(mockImages);

    const state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(false); // Invalid prompt
    expect(state.validation.images.isValid).toBe(true); // Valid images
    expect(state.validation.form.isValid).toBe(false); // Form invalid due to prompt
  });
});
