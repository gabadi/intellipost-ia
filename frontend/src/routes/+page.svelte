<script lang="ts">
  import { onMount } from 'svelte';
  import type { HealthCheckResponse } from '$types';
  import { config } from '$lib/config';

  let healthStatus: HealthCheckResponse | null = null;
  let healthError: string | null = null;
  let isLoading = true;

  async function checkBackendHealth() {
    try {
      // Use centralized configuration for API endpoint
      const response = await fetch(config.getApiUrl(config.api.HEALTH_ENDPOINT));
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
  <div class="py-6" style="min-height: var(--layout-main-min-height);">
    <header class="mb-8">
      <h1 class="text-3xl font-bold" style="color: var(--color-text);">Dashboard</h1>
      <p class="mt-2" style="color: var(--color-text-secondary);">
        Welcome to IntelliPost AI Control Panel
      </p>
    </header>

    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4" style="color: var(--color-text);">System Status</h2>

      <div class="status-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium" style="color: var(--color-text);">Backend Connection</h3>
          {#if isLoading}
            <div class="flex items-center gap-2">
              <span class="loading-spinner"></span>
              <span class="text-sm" style="color: var(--color-text-muted);">Checking...</span>
            </div>
          {:else if healthStatus}
            <div class="flex items-center gap-2">
              <span class="status-dot success"></span>
              <span class="text-sm" style="color: var(--color-text-secondary);">Healthy</span>
            </div>
          {:else}
            <div class="flex items-center gap-2">
              <span class="status-dot error"></span>
              <span class="text-sm" style="color: var(--color-text-secondary);">Disconnected</span>
            </div>
          {/if}
        </div>

        {#if healthStatus}
          <div
            class="flex flex-col gap-2 pt-4 border-t"
            style="border-color: var(--color-border-muted);"
          >
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted);">Status:</span>
              <span class="text-sm font-medium" style="color: var(--color-success);"
                >{healthStatus.status}</span
              >
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted);">Version:</span>
              <span class="text-sm font-medium" style="color: var(--color-text);"
                >{healthStatus.version}</span
              >
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted);">Last Check:</span>
              <span class="text-sm font-medium" style="color: var(--color-text);"
                >{new Date(healthStatus.timestamp).toLocaleString()}</span
              >
            </div>
          </div>
        {:else if healthError}
          <div class="pt-4 border-t" style="border-color: var(--color-border-muted);">
            <p class="text-sm mb-2" style="color: var(--color-text-secondary);">
              Connection Error:
            </p>
            <p class="text-sm mb-3" style="color: var(--color-error);">{healthError}</p>
            <button class="btn btn--primary btn--sm" on:click={checkBackendHealth}>
              Retry Connection
            </button>
          </div>
        {/if}
      </div>
    </div>

    <div>
      <h2 class="text-xl font-semibold mb-4" style="color: var(--color-text);">Quick Actions</h2>
      <div class="grid gap-4 grid-cols-1 sm:grid-cols-2">
        <a href="/products/new" class="action-card">
          <div class="text-2xl mb-3">➕</div>
          <h3 class="font-medium mb-2" style="color: var(--color-text);">Create Product</h3>
          <p class="text-sm" style="color: var(--color-text-muted);">
            Start a new AI-powered product listing
          </p>
        </a>

        <a href="/products" class="action-card">
          <div class="text-2xl mb-3">📦</div>
          <h3 class="font-medium mb-2" style="color: var(--color-text);">View Products</h3>
          <p class="text-sm" style="color: var(--color-text-muted);">
            Manage your existing product listings
          </p>
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

  /* Status Card Component */
  .status-card {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
  }

  /* Action Card Component */
  .action-card {
    display: block;
    background: var(--color-background);
    border: 1px solid var(--color-border);
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
