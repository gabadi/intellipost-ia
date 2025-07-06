<script lang="ts">
  import { onMount } from 'svelte';
  import type { HealthCheckResponse } from '$types';

  let healthStatus: HealthCheckResponse | null = null;
  let healthError: string | null = null;
  let isLoading = true;

  async function checkBackendHealth() {
    try {
      // Import API client dynamically for browser compatibility
      const { checkBackendHealth: healthCheck } = await import('$lib/api/client');
      healthStatus = await healthCheck();
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
  <div class="page-container">
    <header class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Welcome to IntelliPost AI Control Panel</p>
    </header>

    <div class="section">
      <div class="section-header">
        <h2 class="section-title">System Status</h2>
      </div>

      <div class="card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-medium" style="color: var(--color-text-primary)">Backend Connection</h3>
          {#if isLoading}
            <div class="flex items-center gap-2">
              <span class="loading-spinner"></span>
              <span class="text-sm" style="color: var(--color-text-muted)">Checking...</span>
            </div>
          {:else if healthStatus}
            <div class="flex items-center gap-2">
              <span class="status-dot success"></span>
              <span class="text-sm" style="color: var(--color-text-secondary)">Healthy</span>
            </div>
          {:else}
            <div class="flex items-center gap-2">
              <span class="status-dot error"></span>
              <span class="text-sm" style="color: var(--color-text-secondary)">Disconnected</span>
            </div>
          {/if}
        </div>

        {#if healthStatus}
          <div
            class="flex flex-col gap-2 pt-4 border-t"
            style="border-color: var(--color-border-muted)"
          >
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted)">Status:</span>
              <span class="text-sm text-green-600 font-medium">{healthStatus.status}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted)">Version:</span>
              <span class="text-sm font-medium" style="color: var(--color-text-primary)"
                >{healthStatus.version}</span
              >
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm" style="color: var(--color-text-muted)">Last Check:</span>
              <span class="text-sm font-medium" style="color: var(--color-text-primary)"
                >{new Date(healthStatus.timestamp).toLocaleString()}</span
              >
            </div>
          </div>
        {:else if healthError}
          <div class="pt-4 border-t" style="border-color: var(--color-border-muted)">
            <p class="text-sm mb-2" style="color: var(--color-text-secondary)">Connection Error:</p>
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

    <div class="section">
      <div class="section-header">
        <h2 class="section-title">Quick Actions</h2>
      </div>
      <div class="grid-responsive grid-responsive-sm-2">
        <a href="/products/new" class="card card-action">
          <div style="font-size: var(--text-2xl); margin-bottom: var(--space-3);">➕</div>
          <h3 class="card-title">Create Product</h3>
          <p class="card-subtitle">Start a new AI-powered product listing</p>
        </a>

        <a href="/products" class="card card-action">
          <div style="font-size: var(--text-2xl); margin-bottom: var(--space-3);">📦</div>
          <h3 class="card-title">View Products</h3>
          <p class="card-subtitle">Manage your existing product listings</p>
        </a>
      </div>
    </div>
  </div>
</div>

<style>
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
</style>
