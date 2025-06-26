<script lang="ts">
  import { onMount } from 'svelte';
  import type { HealthCheckResponse } from '$types';

  let healthStatus: HealthCheckResponse | null = null;
  let healthError: string | null = null;
  let isLoading = true;

  async function checkBackendHealth() {
    try {
      // eslint-disable-next-line no-undef
      const response = await fetch('http://localhost:8000/health');
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
  <div class="dashboard">
    <header class="dashboard-header">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-2">Welcome to IntelliPost AI Control Panel</p>
    </header>

    <div class="status-section">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">System Status</h2>

      <div class="status-card">
        <div class="status-header">
          <h3 class="font-medium text-gray-900">Backend Connection</h3>
          {#if isLoading}
            <div class="status-indicator loading">
              <span class="loading-spinner"></span>
              <span class="text-sm text-gray-500">Checking...</span>
            </div>
          {:else if healthStatus}
            <div class="status-indicator success">
              <span class="status-dot success"></span>
              <span class="text-sm text-gray-600">Healthy</span>
            </div>
          {:else}
            <div class="status-indicator error">
              <span class="status-dot error"></span>
              <span class="text-sm text-gray-600">Disconnected</span>
            </div>
          {/if}
        </div>

        {#if healthStatus}
          <div class="status-details">
            <div class="detail-row">
              <span class="detail-label">Status:</span>
              <span class="detail-value success">{healthStatus.status}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Version:</span>
              <span class="detail-value">{healthStatus.version}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Last Check:</span>
              <span class="detail-value">{new Date(healthStatus.timestamp).toLocaleString()}</span>
            </div>
          </div>
        {:else if healthError}
          <div class="error-details">
            <p class="text-sm text-gray-600 mb-2">Connection Error:</p>
            <p class="text-sm error">{healthError}</p>
            <button
              class="retry-button"
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

    <div class="quick-actions">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div class="action-grid">
        <a href="/products/new" class="action-card">
          <div class="action-icon">➕</div>
          <h3 class="font-medium text-gray-900">Create Product</h3>
          <p class="text-sm text-gray-500">Start a new AI-powered product listing</p>
        </a>

        <a href="/products" class="action-card">
          <div class="action-icon">📦</div>
          <h3 class="font-medium text-gray-900">View Products</h3>
          <p class="text-sm text-gray-500">Manage your existing product listings</p>
        </a>
      </div>
    </div>
  </div>
</div>

<style>
  .dashboard {
    padding: var(--space-6) 0;
    min-height: calc(100vh - 70px);
  }

  .dashboard-header {
    margin-bottom: var(--space-8);
  }

  .status-section {
    margin-bottom: var(--space-8);
  }

  .status-card {
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
  }

  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-4);
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

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
    animation: spin 1s linear infinite;
  }

  .status-details {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding-top: var(--space-4);
    border-top: 1px solid var(--color-gray-100);
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .detail-label {
    font-size: var(--text-sm);
    color: var(--color-gray-500);
  }

  .detail-value {
    font-size: var(--text-sm);
    color: var(--color-gray-900);
    font-weight: 500;
  }

  .detail-value.success {
    color: var(--color-success);
  }

  .error-details {
    padding-top: var(--space-4);
    border-top: 1px solid var(--color-gray-100);
  }

  .retry-button {
    margin-top: var(--space-3);
    padding: var(--space-2) var(--space-4);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    cursor: pointer;
    min-height: var(--touch-target-min);
    transition: background-color 0.2s ease;
  }

  .retry-button:hover {
    background-color: var(--color-primary-hover);
  }

  .action-grid {
    display: grid;
    gap: var(--space-4);
    grid-template-columns: 1fr;
  }

  @media (min-width: 640px) {
    .action-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .action-card {
    display: block;
    background: white;
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    text-decoration: none;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
    min-height: var(--touch-target-min);
  }

  .action-card:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }

  .action-icon {
    font-size: var(--text-2xl);
    margin-bottom: var(--space-3);
  }

  .action-card h3 {
    margin-bottom: var(--space-2);
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
