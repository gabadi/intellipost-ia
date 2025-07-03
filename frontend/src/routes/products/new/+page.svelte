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

    setTimeout(() => {
      isLoading = false;
      // Redirect to products list after creation

      window.location.href = '/products';
    }, 2000);
  }

  function handleCancel() {
    window.history.back();
  }
</script>

<svelte:head>
  <title>Create New Product - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="page-container">
    <header class="page-header">
      <h1 class="page-title">Create New Product</h1>
      <p class="page-subtitle">Let AI help you create compelling product listings</p>
    </header>

    <div class="form-container form-container-split">
      <form on:submit={handleSubmit} class="card card-form">
        <div class="form-section">
          <h2 class="form-section-title">Product Information</h2>

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
            class="btn btn--primary btn--md"
            class:btn--loading={isLoading}
            disabled={isLoading}
          >
            {#if !isLoading}
              <span class="btn-icon">✨</span>
              Create Product
            {/if}
          </button>
        </div>
      </form>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">AI Preview</h3>
        </div>
        <div class="card-content">
          <div class="preview-area">
            <div class="preview-icon">🤖</div>
            <p
              style="color: var(--color-text-muted); font-size: var(--text-sm); text-align: center;"
            >
              AI-powered content generation will appear here as you fill out the form
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .btn-icon {
    font-size: var(--text-base);
  }

  .preview-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8);
    border: 2px dashed var(--color-border-secondary);
    border-radius: var(--radius-lg);
    text-align: center;
  }

  .preview-icon {
    font-size: 48px;
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }
</style>
