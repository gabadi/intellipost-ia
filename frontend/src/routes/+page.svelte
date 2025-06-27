<script lang="ts">
  import { onMount } from 'svelte';
  import type { HealthCheckResponse } from '$types';

  let healthStatus: HealthCheckResponse | null = null;
  let healthError: string | null = null;
  let isLoading = true;

  async function checkBackendHealth() {
    try {
      // For browser-side requests, always use localhost (host machine)
      const response = await fetch('http://localhost:8080/health');
      if (!response.ok) {
        throw new Error(`Backend health check failed: ${response.status}`);
      }
      healthStatus = await response.json();
      healthError = null;
    } catch (error) {
      healthError = error instanceof Error ? error.message : 'Unknown error occurred';
      healthStatus = null;
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    checkBackendHealth();
  });
</script>

<svelte:head>
  <title>Dashboard - IntelliPost AI</title>
</svelte:head>

<div class="container">
  <div class="py-6" style="min-height: calc(100vh - 70px);">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-2">Welcome to IntelliPost AI Control Panel</p>
    </header>

    <div class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">System Status</h2>

      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium text-gray-900">Backend Connection</h3>
          {#if isLoading}
            <div class="flex items-center gap-2">
              <span class="loading-spinner"></span>
              <span class="text-sm text-gray-500">Checking...</span>
            </div>
          {:else if healthStatus}
            <div class="flex items-center gap-2">
              <span class="status-dot success"></span>
              <span class="text-sm text-gray-600">Healthy</span>
            </div>
          {:else}
            <div class="flex items-center gap-2">
              <span class="status-dot error"></span>
              <span class="text-sm text-gray-600">Disconnected</span>
            </div>
          {/if}
        </div>

        {#if healthStatus}
          <div class="flex flex-col gap-2 pt-4 border-t border-gray-100">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Status:</span>
              <span class="text-sm text-green-600 font-medium">{healthStatus.status}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Version:</span>
              <span class="text-sm text-gray-900 font-medium">{healthStatus.version}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">Last Check:</span>
              <span class="text-sm text-gray-900 font-medium">{new Date(healthStatus.timestamp).toLocaleString()}</span>
            </div>
          </div>
        {:else if healthError}
          <div class="pt-4 border-t border-gray-100">
            <p class="text-sm text-gray-600 mb-2">Connection Error:</p>
            <p class="text-sm text-red-600 mb-3">{healthError}</p>
            <button
              class="btn btn--primary btn--sm"
              on:click={() => {
                isLoading = true;
                checkBackendHealth();
              }}
            >
              Retry Connection
            </button>
          </div>
        {/if}
      </div>
    </div>

    <div>
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div class="grid gap-4 grid-cols-1 sm:grid-cols-2">
        <a href="/products/new" class="action-card">
          <div class="text-2xl mb-3">➕</div>
          <h3 class="font-medium text-gray-900 mb-2">Create Product</h3>
          <p class="text-sm text-gray-500">Start a new AI-powered product listing</p>
        </a>

        <a href="/products" class="action-card">
          <div class="text-2xl mb-3">📦</div>
          <h3 class="font-medium text-gray-900 mb-2">View Products</h3>
          <p class="text-sm text-gray-500">Manage your existing product listings</p>
        </a>
      </div>
    </div>
  </div>
</div>

<style>
  /* Minimal component-specific styles using design tokens */
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-dot.success {
    background-color: var(--color-success);
  }

  .status-dot.error {
    background-color: var(--color-error);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid var(--color-gray-300);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin var(--duration-1000) linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Action Card Component */
  .action-card {
    display: block;
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    text-decoration: none;
    transition: all var(--duration-200) var(--ease-out);
    box-shadow: var(--shadow-sm);
    min-height: var(--touch-target-min);
  }

  .action-card:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
</style>
