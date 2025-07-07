import { writable, derived } from 'svelte/store';
import type { ProductCreationState, ProductImageData, ValidationState } from '../types/product';
import { validatePrompt, validateImageBatch } from '../utils/validation';
import { DEFAULT_IMAGE_VALIDATION_RULES } from '../types/product';

const STORAGE_KEY = 'product-creation-autosave';

function createProductCreationStore() {
  const initialState: ProductCreationState = {
    prompt_text: '',
    images: [],
    isUploading: false,
    uploadProgress: {},
    validation: {
      prompt: { isValid: false, type: 'error' },
      images: { isValid: false, type: 'error' },
      form: { isValid: false, type: 'error' },
    },
    errors: [],
    autoSaved: false,
  };

  const { subscribe, set, update } = writable<ProductCreationState>(initialState);

  // Load from localStorage on initialization
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsedState = JSON.parse(saved);
        // Don't restore file objects, just the text
        if (parsedState.prompt_text) {
          update(state => ({
            ...state,
            prompt_text: parsedState.prompt_text,
            autoSaved: true,
          }));
        }
      } catch {
        // Failed to restore autosaved data - continue with empty state
      }
    }
  }

  function setPromptText(text: string) {
    update(state => {
      // Only update if text actually changed to prevent infinite loops
      if (state.prompt_text === text) {
        return state;
      }

      const promptValidation = validatePrompt(text);
      const newState = {
        ...state,
        prompt_text: text,
        validation: {
          ...state.validation,
          prompt: promptValidation,
        },
      };

      // Update form validation
      newState.validation.form = validateForm(newState);

      // Auto-save to localStorage (only if text is not empty)
      if (typeof window !== 'undefined' && text.trim().length > 0) {
        try {
          localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify({
              prompt_text: text,
              timestamp: Date.now(),
            })
          );
          newState.autoSaved = true;
        } catch (error) {
          // Silent fail for localStorage issues
          console.warn('Failed to auto-save:', error);
        }
      }

      return newState;
    });
  }

  function addImages(newImages: ProductImageData[]) {
    update(state => {
      // Prevent adding empty arrays
      if (!newImages || newImages.length === 0) {
        return state;
      }

      const allImages = [...state.images, ...newImages];

      // Set first image as primary if no primary exists
      if (state.images.length === 0 && allImages.length > 0) {
        allImages[0].is_primary = true;
      }

      const imagesValidation = validateImageBatch(
        allImages.map(img => img.file),
        DEFAULT_IMAGE_VALIDATION_RULES
      );

      const newState = {
        ...state,
        images: allImages,
        validation: {
          ...state.validation,
          images: imagesValidation,
        },
      };

      // Update form validation
      newState.validation.form = validateForm(newState);

      return newState;
    });
  }

  function removeImage(imageId: string) {
    update(state => {
      const filteredImages = state.images.filter(img => img.id !== imageId);
      const imagesValidation = validateImageBatch(
        filteredImages.map(img => img.file),
        DEFAULT_IMAGE_VALIDATION_RULES
      );

      // If removing primary image, make first image primary
      if (filteredImages.length > 0 && !filteredImages.some(img => img.is_primary)) {
        filteredImages[0].is_primary = true;
      }

      const newState = {
        ...state,
        images: filteredImages,
        validation: {
          ...state.validation,
          images: imagesValidation,
        },
      };

      // Update form validation
      newState.validation.form = validateForm(newState);

      return newState;
    });
  }

  function setPrimaryImage(imageId: string) {
    update(state => ({
      ...state,
      images: state.images.map(img => ({
        ...img,
        is_primary: img.id === imageId,
      })),
    }));
  }

  function reorderImages(startIndex: number, endIndex: number) {
    update(state => {
      const newImages = [...state.images];
      const [movedImage] = newImages.splice(startIndex, 1);
      newImages.splice(endIndex, 0, movedImage);

      return {
        ...state,
        images: newImages,
      };
    });
  }

  function setUploadProgress(imageId: string, progress: number) {
    update(state => ({
      ...state,
      uploadProgress: {
        ...state.uploadProgress,
        [imageId]: progress,
      },
    }));
  }

  function setUploading(isUploading: boolean) {
    update(state => ({
      ...state,
      isUploading,
    }));
  }

  function addError(error: string) {
    update(state => ({
      ...state,
      errors: [...state.errors, error],
    }));
  }

  function clearErrors() {
    update(state => ({
      ...state,
      errors: [],
    }));
  }

  function reset() {
    set(initialState);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  function validateForm(state: ProductCreationState): ValidationState {
    // Simplified boolean logic - just check the isValid property directly
    const isPromptValid = state.validation.prompt.isValid;
    const isImagesValid = state.validation.images.isValid;

    if (!isPromptValid && !isImagesValid) {
      return {
        isValid: false,
        message: 'Please add a description and at least one image',
        type: 'error',
      };
    }

    if (!isPromptValid) {
      return {
        isValid: false,
        message: 'Please add a valid product description',
        type: 'error',
      };
    }

    if (!isImagesValid) {
      return {
        isValid: false,
        message: 'Please add at least one image',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: 'Ready to create product',
      type: 'success',
    };
  }

  return {
    subscribe,
    setPromptText,
    addImages,
    removeImage,
    setPrimaryImage,
    reorderImages,
    setUploadProgress,
    setUploading,
    addError,
    clearErrors,
    reset,

    // Derived values
    isFormValid: derived({ subscribe }, $state => $state.validation.form.isValid),

    totalImages: derived({ subscribe }, $state => $state.images.length),

    primaryImage: derived({ subscribe }, $state => $state.images.find(img => img.is_primary)),

    uploadProgressPercentage: derived({ subscribe }, $state => {
      const progresses = Object.values($state.uploadProgress);
      if (progresses.length === 0) return 0;
      return progresses.reduce((sum, progress) => sum + progress, 0) / progresses.length;
    }),
  };
}

export const productCreationStore = createProductCreationStore();
