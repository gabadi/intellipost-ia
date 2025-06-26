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
    // eslint-disable-next-line no-undef
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
</script>

<svelte:head>
  <title>Products - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="products-page">
    <header class="page-header">
      <h1 class="text-3xl font-bold text-gray-900">Products</h1>
      <p class="text-gray-600 mt-2">Manage your AI-generated product listings</p>
    </header>

    <div class="actions-bar">
      <a href="/products/new" class="btn-primary">
        <span class="btn-icon">➕</span>
        Create New Product
      </a>
    </div>

    {#if isLoading}
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p class="text-gray-500">Loading products...</p>
      </div>
    {:else if products.length === 0}
      <div class="empty-state">
        <div class="empty-icon">📦</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No products yet</h3>
        <p class="text-gray-500 mb-6">
          Create your first AI-powered product listing to get started.
        </p>
        <a href="/products/new" class="btn-primary">
          <span class="btn-icon">➕</span>
          Create Your First Product
        </a>
      </div>
    {:else}
      <div class="products-grid">
        {#each products as product}
          <div class="product-card">
            <div class="product-header">
              <h3 class="font-semibold text-gray-900">{product.id}</h3>
              <span class="status-badge status-{product.status}">
                {product.status}
              </span>
            </div>
            <div class="product-meta">
              <p class="text-sm text-gray-500">
                Created: {new Date(product.created_at).toLocaleDateString()}
              </p>
              {#if product.confidence}
                <p class="text-sm text-gray-500">
                  Confidence: {Math.round(product.confidence * 100)}%
                </p>
              {/if}
            </div>
            <div class="product-actions">
              <a href="/products/{product.id}" class="btn-secondary"> View Details </a>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .products-page {
    padding: var(--space-6) 0;
    min-height: calc(100vh - 70px);
  }

  .page-header {
    margin-bottom: var(--space-6);
  }

  .actions-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: var(--space-6);
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    background-color: var(--color-primary);
    color: white;
    text-decoration: none;
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: var(--text-sm);
    min-height: var(--touch-target-min);
    transition: background-color 0.2s ease;
  }

  .btn-primary:hover {
    background-color: var(--color-primary-hover);
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background-color: white;
    color: var(--color-gray-700);
    text-decoration: none;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: var(--text-sm);
    min-height: var(--touch-target-min);
    transition: all 0.2s ease;
  }

  .btn-secondary:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  .btn-icon {
    font-size: var(--text-base);
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-16) var(--space-4);
    text-align: center;
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-gray-300);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-4);
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-16) var(--space-4);
    text-align: center;
  }

  .empty-icon {
    font-size: 64px;
    margin-bottom: var(--space-6);
    opacity: 0.5;
  }

  .products-grid {
    display: grid;
    gap: var(--space-4);
    grid-template-columns: 1fr;
  }

  @media (min-width: 640px) {
    .products-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1024px) {
    .products-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .product-card {
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
  }

  .product-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }

  .product-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-4);
  }

  .status-badge {
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 500;
    text-transform: capitalize;
  }

  .status-uploading {
    background-color: #fef3c7;
    color: #92400e;
  }

  .status-processing {
    background-color: #dbeafe;
    color: #1e40af;
  }

  .status-ready {
    background-color: #d1fae5;
    color: #065f46;
  }

  .status-publishing {
    background-color: #e0e7ff;
    color: #3730a3;
  }

  .status-published {
    background-color: #dcfce7;
    color: #166534;
  }

  .status-failed {
    background-color: #fee2e2;
    color: #991b1b;
  }

  .product-meta {
    margin-bottom: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .product-actions {
    display: flex;
    justify-content: flex-end;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
