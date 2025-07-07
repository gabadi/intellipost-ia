<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { productCreationStore } from '$lib/stores/product-creation';
  import PromptInputComponent from '$lib/components/product/PromptInputComponent.svelte';
  import PhotoCollectionComponent from '$lib/components/product/PhotoCollectionComponent.svelte';
  import type { ValidationState } from '$lib/types/product';

  let isLoading = false;

  // Use store validation states instead of local ones
  $: promptValidation = $productCreationStore.validation.prompt;
  $: imagesValidation = $productCreationStore.validation.images;
  $: isFormValid = $productCreationStore.validation.form.isValid;
  $: canSubmit = isFormValid && !isLoading;

  onMount(() => {
    // Clear any previous form data when mounting
    productCreationStore.clearErrors();
  });

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!canSubmit) return;

    isLoading = true;
    productCreationStore.setUploading(true);

    try {
      // TODO: Implement actual API call to create product
      // For now, simulate form submission
      await simulateProductCreation();

      // Navigate to success page or product list
      await goto('/products');
    } catch {
      // Log error and show user-friendly message
      productCreationStore.addError('Failed to create product. Please try again.');
    } finally {
      isLoading = false;
      productCreationStore.setUploading(false);
    }
  }

  async function simulateProductCreation(): Promise<void> {
    return new Promise(resolve => {
      setTimeout(() => {
        productCreationStore.reset();
        resolve();
      }, 2000);
    });
  }

  function handlePromptChange(text: string) {
    productCreationStore.setPromptText(text);
  }

  function handleCancel() {
    // eslint-disable-next-line no-alert
    if (window.confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
      productCreationStore.reset();
      goto('/products');
    }
  }

  function handleReset() {
    // eslint-disable-next-line no-alert
    if (window.confirm('Are you sure you want to reset the form? All data will be lost.')) {
      productCreationStore.reset();
    }
  }
</script>

<svelte:head>
  <title>Create New Product - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="page-container">
    <header class="page-header">
      <h1 class="page-title">Create New Product</h1>
      <p class="page-subtitle">
        Upload photos and describe your product to generate AI-powered listings
      </p>
    </header>

    <form on:submit={handleSubmit} class="product-creation-form">
      <div class="form-content">
        <!-- Photo Collection Section -->
        <section class="form-section" class:form-section--valid={imagesValidation.isValid} class:form-section--invalid={!imagesValidation.isValid && $productCreationStore.images.length > 0}>
          <PhotoCollectionComponent
            images={$productCreationStore.images}
            disabled={isLoading}
          />
          {#if imagesValidation.message}
            <div class="section-validation-message section-validation-message--{imagesValidation.type}">
              {#if imagesValidation.type === 'success'}✓{/if}
              {#if imagesValidation.type === 'warning'}⚠{/if}
              {#if imagesValidation.type === 'error'}✕{/if}
              {imagesValidation.message}
            </div>
          {/if}
        </section>

        <!-- Prompt Input Section -->
        <section class="form-section" class:form-section--valid={promptValidation.isValid} class:form-section--invalid={!promptValidation.isValid && $productCreationStore.prompt_text.trim().length > 0}>
          <PromptInputComponent
            value={$productCreationStore.prompt_text}
            onChange={handlePromptChange}
            validation={promptValidation}
            disabled={isLoading}
          />
        </section>

        <!-- Form Status -->
        {#if $productCreationStore.errors.length > 0}
          <section class="error-section">
            {#each $productCreationStore.errors as error}
              <div class="error-message">
                <span class="error-icon">⚠</span>
                {error}
              </div>
            {/each}
          </section>
        {/if}

        {#if $productCreationStore.autoSaved}
          <div class="autosave-indicator">
            <span class="autosave-icon">💾</span>
            Your progress has been automatically saved
          </div>
        {/if}
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <div class="form-actions-secondary">
          <button
            type="button"
            class="btn btn--ghost btn--md"
            on:click={handleReset}
            disabled={isLoading}
          >
            Reset Form
          </button>
        </div>

        <div class="form-actions-primary">
          <button
            type="button"
            class="btn btn--secondary btn--md"
            on:click={handleCancel}
            disabled={isLoading}
          >
            Cancel
          </button>

          <button
            type="submit"
            class="btn btn--primary btn--lg"
            class:btn--loading={isLoading}
            disabled={!canSubmit}
          >
            {#if isLoading}
              <span class="btn-spinner"></span>
              Creating...
            {:else}
              <span class="btn-icon">✨</span>
              Create Product
            {/if}
          </button>
        </div>
      </div>

      <!-- Form Validation Summary -->
      <div class="validation-summary">
        <div class="validation-item" class:validation-item--valid={imagesValidation.isValid}>
          <span class="validation-icon">
            {imagesValidation.isValid ? '✓' : '○'}
          </span>
          <span class="validation-text">
            {imagesValidation.isValid ? 'Images ready' : 'Add product photos'}
          </span>
        </div>

        <div class="validation-item" class:validation-item--valid={promptValidation.isValid}>
          <span class="validation-icon">
            {promptValidation.isValid ? '✓' : '○'}
          </span>
          <span class="validation-text">
            {promptValidation.isValid ? 'Description ready' : 'Add product description'}
          </span>
        </div>

        {#if isFormValid}
          <div class="validation-item validation-item--success">
            <span class="validation-icon">🚀</span>
            <span class="validation-text">Ready to create your product!</span>
          </div>
        {/if}
      </div>
    </form>
  </div>
</div>

<style>
  .product-creation-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
  }

  .form-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }

  .form-section {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    transition: all 0.2s ease;
  }

  .form-section:focus-within {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-light);
  }

  .form-section--valid {
    border-color: var(--color-success);
  }

  .form-section--invalid {
    border-color: var(--color-error);
  }

  .section-validation-message {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    margin-top: var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
  }

  .section-validation-message--success {
    background: var(--color-success-light);
    border: 1px solid var(--color-success);
    color: var(--color-success-dark);
  }

  .section-validation-message--warning {
    background: var(--color-warning-light);
    border: 1px solid var(--color-warning);
    color: var(--color-warning-dark);
  }

  .section-validation-message--error {
    background: var(--color-error-light);
    border: 1px solid var(--color-error);
    color: var(--color-error-dark);
  }

  .error-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--color-error-light);
    border: 1px solid var(--color-error);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    color: var(--color-error-dark);
  }

  .error-icon {
    font-size: var(--text-base);
    flex-shrink: 0;
  }

  .autosave-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--color-success-light);
    border: 1px solid var(--color-success);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    color: var(--color-success-dark);
    animation: fadeInOut 0.3s ease;
  }

  .autosave-icon {
    font-size: var(--text-base);
  }

  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-6);
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    flex-wrap: wrap;
  }

  .form-actions-secondary {
    display: flex;
    gap: var(--space-2);
  }

  .form-actions-primary {
    display: flex;
    gap: var(--space-3);
    align-items: center;
  }

  .btn-icon {
    font-size: var(--text-base);
    margin-right: var(--space-1);
  }

  .btn-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: var(--space-2);
  }

  .validation-summary {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
  }

  .validation-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    transition: all 0.2s ease;
  }

  .validation-item--valid {
    color: var(--color-success);
  }

  .validation-item--success {
    color: var(--color-primary);
    font-weight: 600;
  }

  .validation-icon {
    font-size: var(--text-base);
    width: 20px;
    text-align: center;
    flex-shrink: 0;
  }

  .validation-text {
    flex: 1;
  }

  /* Mobile-first responsive design */
  @media (max-width: 768px) {
    .product-creation-form {
      gap: var(--space-4);
    }

    .form-section {
      padding: var(--space-4);
      border-radius: var(--radius-lg);
    }

    .form-actions {
      flex-direction: column;
      align-items: stretch;
      gap: var(--space-3);
      padding: var(--space-4);
    }

    .form-actions-secondary,
    .form-actions-primary {
      justify-content: stretch;
      width: 100%;
    }

    .form-actions-primary {
      flex-direction: column;
    }

    .form-actions-primary .btn {
      width: 100%;
    }

    .btn--lg {
      min-height: 52px;
      font-size: var(--text-base);
    }

    .validation-summary {
      padding: var(--space-3);
    }
  }

  /* Desktop enhancements */
  @media (min-width: 1024px) {
    .product-creation-form {
      max-width: 1000px;
    }

    .form-content {
      gap: var(--space-8);
    }

    .form-section {
      padding: var(--space-8);
    }

    .form-actions {
      padding: var(--space-8);
    }
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  @keyframes fadeInOut {
    0% {
      opacity: 0;
      transform: translateY(-10px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
