<script lang="ts">
  // Placeholder for new product creation
  let isLoading = false;
  const formData = {
    name: '',
    description: '',
    category: '',
  };

  async function handleSubmit(event: Event) {
    event.preventDefault();
    isLoading = true;

    // TODO: Implement API call to create product
    // For now, simulate form submission
    // eslint-disable-next-line no-undef
    setTimeout(() => {
      isLoading = false;
      // Redirect to products list after creation
      // eslint-disable-next-line no-undef
      window.location.href = '/products';
    }, 2000);
  }

  function handleCancel() {
    // eslint-disable-next-line no-undef
    window.history.back();
  }
</script>

<svelte:head>
  <title>Create New Product - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="new-product-page">
    <header class="page-header">
      <h1 class="text-3xl font-bold text-gray-900">Create New Product</h1>
      <p class="text-gray-600 mt-2">Let AI help you create compelling product listings</p>
    </header>

    <div class="form-container">
      <form on:submit={handleSubmit} class="product-form">
        <div class="form-section">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Product Information</h2>

          <div class="form-group">
            <label for="name" class="form-label">Product Name</label>
            <input
              type="text"
              id="name"
              bind:value={formData.name}
              class="form-input"
              placeholder="Enter product name"
              required
              disabled={isLoading}
            />
          </div>

          <div class="form-group">
            <label for="description" class="form-label">Description</label>
            <textarea
              id="description"
              bind:value={formData.description}
              class="form-textarea"
              placeholder="Describe your product..."
              rows="4"
              required
              disabled={isLoading}
            ></textarea>
          </div>

          <div class="form-group">
            <label for="category" class="form-label">Category</label>
            <select
              id="category"
              bind:value={formData.category}
              class="form-select"
              required
              disabled={isLoading}
            >
              <option value="">Select a category</option>
              <option value="electronics">Electronics</option>
              <option value="clothing">Clothing</option>
              <option value="home">Home & Garden</option>
              <option value="books">Books</option>
              <option value="sports">Sports & Outdoors</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={handleCancel} disabled={isLoading}>
            Cancel
          </button>

          <button type="submit" class="btn-primary" disabled={isLoading}>
            {#if isLoading}
              <span class="loading-spinner"></span>
              Creating...
            {:else}
              <span class="btn-icon">✨</span>
              Create Product
            {/if}
          </button>
        </div>
      </form>

      <div class="ai-preview">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">AI Preview</h3>
        <div class="preview-card">
          <div class="preview-icon">🤖</div>
          <p class="text-sm text-gray-500 text-center">
            AI-powered content generation will appear here as you fill out the form
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .new-product-page {
    padding: var(--space-6) 0;
    min-height: calc(100vh - 70px);
  }

  .page-header {
    margin-bottom: var(--space-8);
  }

  .form-container {
    display: grid;
    gap: var(--space-8);
    grid-template-columns: 1fr;
  }

  @media (min-width: 1024px) {
    .form-container {
      grid-template-columns: 2fr 1fr;
    }
  }

  .product-form {
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
  }

  .form-section {
    margin-bottom: var(--space-6);
  }

  .form-group {
    margin-bottom: var(--space-4);
  }

  .form-label {
    display: block;
    font-weight: 500;
    color: var(--color-gray-700);
    margin-bottom: var(--space-2);
    font-size: var(--text-sm);
  }

  .form-input,
  .form-textarea,
  .form-select {
    width: 100%;
    padding: var(--space-3);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    transition: border-color 0.2s ease;
    min-height: var(--touch-target-min);
  }

  .form-input:focus,
  .form-textarea:focus,
  .form-select:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
  }

  .form-input:disabled,
  .form-textarea:disabled,
  .form-select:disabled {
    background-color: var(--color-gray-100);
    cursor: not-allowed;
  }

  .form-textarea {
    resize: vertical;
    min-height: 100px;
  }

  .form-actions {
    display: flex;
    gap: var(--space-4);
    justify-content: flex-end;
    padding-top: var(--space-6);
    border-top: 1px solid var(--color-gray-200);
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: var(--text-base);
    min-height: var(--touch-target-min);
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--color-primary-hover);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background-color: white;
    color: var(--color-gray-700);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: var(--text-base);
    min-height: var(--touch-target-min);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-secondary:hover:not(:disabled) {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  .btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-icon {
    font-size: var(--text-base);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .ai-preview {
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
    height: fit-content;
  }

  .preview-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8);
    border: 2px dashed var(--color-gray-300);
    border-radius: var(--radius-lg);
    text-align: center;
  }

  .preview-icon {
    font-size: 48px;
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
