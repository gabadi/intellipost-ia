<script lang="ts">
  import type { Product } from '$types';

  // Placeholder data - will be replaced with API calls in future stories
  let products: Product[] = [];
  let isLoading = false;

  // Placeholder function for future API integration
  async function loadProducts() {
    isLoading = true;
    // TODO: Implement API call to load products
    // For now, simulate loading

    setTimeout(() => {
      products = [];
      isLoading = false;
    }, 1000);
  }

  // Load products on component mount
  import { onMount } from 'svelte';
  onMount(() => {
    loadProducts();
  });

  // Helper function to map product status to badge classes
  function getStatusClass(status: string): string {
    const statusMap: Record<string, string> = {
      uploading: 'status-badge-warning',
      processing: 'status-badge-info',
      ready: 'status-badge-success',
      publishing: 'status-badge-info',
      published: 'status-badge-success',
      failed: 'status-badge-error',
    };
    return statusMap[status] || 'status-badge-neutral';
  }
</script>

<svelte:head>
  <title>Products - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="page-container">
    <header class="page-header">
      <h1 class="page-title">Products</h1>
      <p class="page-subtitle">Manage your AI-generated product listings</p>
    </header>

    <div class="actions-bar">
      <a href="/products/new" class="btn btn--primary btn--md">
        <span class="btn-icon">➕</span>
        Create New Product
      </a>
    </div>

    {#if isLoading}
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p style="color: var(--color-text-muted)">Loading products...</p>
      </div>
    {:else if products.length === 0}
      <div class="empty-state">
        <div class="empty-state-icon">📦</div>
        <h3 class="empty-state-title">No products yet</h3>
        <p class="empty-state-subtitle">
          Create your first AI-powered product listing to get started.
        </p>
        <a href="/products/new" class="btn btn--primary btn--md">
          <span class="btn-icon">➕</span>
          Create Your First Product
        </a>
      </div>
    {:else}
      <div class="cards-grid">
        {#each products as product}
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">{product.id}</h3>
              <span class="status-badge {getStatusClass(product.status)}">
                {product.status}
              </span>
            </div>
            <div class="card-content">
              <p style="color: var(--color-text-muted); font-size: var(--text-sm);">
                Created: {new Date(product.created_at).toLocaleDateString()}
              </p>
              {#if product.confidence}
                <p style="color: var(--color-text-muted); font-size: var(--text-sm);">
                  Confidence: {Math.round(product.confidence * 100)}%
                </p>
              {/if}
            </div>
            <div class="card-footer">
              <a href="/products/{product.id}" class="btn btn--secondary btn--sm">View Details</a>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .btn-icon {
    font-size: var(--text-base);
  }
</style>
