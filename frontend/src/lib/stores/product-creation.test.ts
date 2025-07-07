import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { productCreationStore } from './product-creation';
import type { ProductImageData } from '../types/product';

describe('Product Creation Store Validation', () => {
  beforeEach(() => {
    // Reset the store before each test
    productCreationStore.reset();
  });

  it('should properly track form validation state in store', () => {
    // Initially, form should be invalid
    const initialState = get(productCreationStore);
    expect(initialState.validation.form.isValid).toBe(false);
    expect(initialState.validation.prompt.isValid).toBe(false);
    expect(initialState.validation.images.isValid).toBe(false);
  });

  it('should validate form correctly when prompt is added', () => {
    // Add valid prompt
    const validPrompt = 'This is a valid product description with more than 10 characters';
    productCreationStore.setPromptText(validPrompt);

    const state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(false); // Still no images
    expect(state.validation.form.isValid).toBe(false); // Form still invalid because no images
  });

  it('should validate form correctly when images are added', () => {
    // Create mock images
    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
      {
        id: '2',
        file: new File(['mock'], 'test2.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
      {
        id: '3',
        file: new File(['mock'], 'test3.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
    ];

    productCreationStore.addImages(mockImages);

    const state = get(productCreationStore);
    expect(state.validation.prompt.isValid).toBe(false); // Still no prompt
    expect(state.validation.images.isValid).toBe(true); // Images are valid
    expect(state.validation.form.isValid).toBe(false); // Form still invalid because no prompt
  });

  it('should validate form correctly when both prompt and images are added - THIS IS THE KEY TEST', () => {
    // First add valid prompt
    const validPrompt = 'This is a valid product description with more than 10 characters';
    productCreationStore.setPromptText(validPrompt);

    // Then add valid images
    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
      {
        id: '2',
        file: new File(['mock'], 'test2.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
      {
        id: '3',
        file: new File(['mock'], 'test3.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
    ];

    productCreationStore.addImages(mockImages);

    const state = get(productCreationStore);

    // Both individual validations should be valid
    expect(state.validation.prompt.isValid).toBe(true);
    expect(state.validation.images.isValid).toBe(true);

    // The overall form validation should be valid
    expect(state.validation.form.isValid).toBe(true);

    // The derived isFormValid should also be true
    const isFormValid = get(productCreationStore.isFormValid);
    expect(isFormValid).toBe(true);
  });

  it('should show that store validation works but page validation might not', () => {
    // This test demonstrates that the store handles validation correctly
    // but the page component has its own local validation states

    const validPrompt = 'This is a valid product description with more than 10 characters';
    productCreationStore.setPromptText(validPrompt);

    const mockImages: ProductImageData[] = [
      {
        id: '1',
        file: new File(['mock'], 'test1.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: true,
      },
      {
        id: '2',
        file: new File(['mock'], 'test2.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
      {
        id: '3',
        file: new File(['mock'], 'test3.jpg', { type: 'image/jpeg' }),
        file_size_bytes: 1000,
        file_format: 'jpg',
        resolution_width: 1000,
        resolution_height: 800,
        is_primary: false,
      },
    ];

    productCreationStore.addImages(mockImages);

    const state = get(productCreationStore);

    // Store correctly tracks that form is valid
    expect(state.validation.form.isValid).toBe(true);

    // But the page component uses local validation states:
    // let promptValidation: ValidationState = { isValid: false, type: 'error' };
    // let imagesValidation: ValidationState = { isValid: false, type: 'error' };
    // $: isFormValid = promptValidation.isValid && imagesValidation.isValid;
    //
    // These local states are updated by event handlers, not the store!
    // This is the bug - there's a disconnect between store and page validation
  });
});
