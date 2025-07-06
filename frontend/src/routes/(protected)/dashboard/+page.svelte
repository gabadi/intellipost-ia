<script lang="ts">
  import { onMount } from 'svelte';
  import type { HealthCheckResponse } from '$types';
  import QuickActionCard from '$lib/components/dashboard/QuickActionCard.svelte';
  import { mlConnectionStore, isMLConnected, mlConnectionHealth } from '$lib/stores/ml-connection';

  let healthStatus: HealthCheckResponse | null = null;
  let healthError: string | null = null;
  let isLoading = true;

  // ML Connection reactive values
  $: connectedToML = $isMLConnected;
  $: mlHealth = $mlConnectionHealth;

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
    // Initialize ML connection store
    mlConnectionStore.init();
  });

  /**
   * Get ML connection status for dashboard display
   */
  function getMLConnectionStatus(): 'connected' | 'disconnected' | 'warning' {
    if (!connectedToML) return 'disconnected';
    if (mlHealth === 'healthy') return 'connected';
    if (mlHealth === 'expired' || mlHealth === 'invalid') return 'warning';
    return 'disconnected';
  }

  /**
   * Get ML connection description based on status
   */
  function getMLConnectionDescription(): string {
    if (!connectedToML) {
      return 'Connect your MercadoLibre account to start publishing AI-generated listings automatically.';
    }
    if (mlHealth === 'healthy') {
      return 'Your MercadoLibre integration is active and ready for automated publishing.';
    }
    if (mlHealth === 'expired') {
      return 'Your MercadoLibre connection has expired. Please reconnect to continue publishing.';
    }
    if (mlHealth === 'invalid') {
      return 'There is an issue with your MercadoLibre connection. Please check the integration settings.';
    }
    return 'MercadoLibre integration status is being checked...';
  }

  /**
   * Get ML action text based on connection status
   */
  function getMLActionText(): string {
    if (!connectedToML) return 'Connect Account';
    if (mlHealth === 'healthy') return 'Manage Integration';
    return 'Fix Connection';
  }
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
      <div class="grid-responsive grid-responsive-md-3">
        <!-- MercadoLibre Integration Card -->
        <QuickActionCard
          title="MercadoLibre Integration"
          description={getMLConnectionDescription()}
          icon="🛒"
          href="/ml-setup"
          status={getMLConnectionStatus()}
          actionText={getMLActionText()}
        />

        <!-- Create Product Card -->
        <QuickActionCard
          title="Create Product"
          description="Start a new AI-powered product listing with smart content generation."
          icon="➕"
          href="/products/new"
          status="info"
          actionText="Create New"
        />

        <!-- View Products Card -->
        <QuickActionCard
          title="Manage Products"
          description="View, edit, and organize your existing product listings and inventory."
          icon="📦"
          href="/products"
          status="info"
          actionText="View All"
        />
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
