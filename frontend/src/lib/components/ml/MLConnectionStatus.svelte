<script lang="ts">
  /**
   * MercadoLibre Connection Status Component
   *
   * Displays current ML connection status with actions for dashboard and publishing screens.
   */

  import { onMount, createEventDispatcher } from 'svelte';
  import { get } from 'svelte/store';
  import {
    mlConnectionStore,
    isMLConnected,
    mlConnectionHealth,
    mlUserInfo,
  } from '$lib/stores/ml-connection';
  import {
    CONNECTION_HEALTH_LABELS,
    CONNECTION_HEALTH_COLORS,
    ML_SITES,
  } from '$lib/types/ml-connection';

  // Component props
  export let variant: 'full' | 'compact' | 'badge' = 'full';
  export let showActions = true;
  export let showRefresh = true;
  export let autoRefresh = true;
  export let refreshInterval = 300000; // 5 minutes

  // Component state
  let refreshTimer: ReturnType<typeof setInterval> | null = null;
  let isRefreshing = false;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    connect: void;
    disconnect: void;
    refresh: void;
  }>();

  // Reactive values
  $: connectionState = $mlConnectionStore;
  let isConnected: boolean;
  let health: any;
  let userInfo: any;

  // Use get() to avoid $ syntax issues with dependency-cruiser
  $: {
    isConnected = get(isMLConnected);
    health = get(mlConnectionHealth);
    userInfo = get(mlUserInfo);
  }
  $: site = connectionState.mlSiteId ? ML_SITES[connectionState.mlSiteId] : null;
  $: healthLabel = CONNECTION_HEALTH_LABELS[health] || 'Unknown';
  $: healthColor = CONNECTION_HEALTH_COLORS[health] || 'neutral';
  $: needsAttention = ['expired', 'invalid'].includes(health);
  $: canRefresh = isConnected && !connectionState.isLoading && !isRefreshing;

  // Auto-refresh setup
  onMount(() => {
    if (autoRefresh && refreshInterval > 0) {
      refreshTimer = setInterval(async () => {
        if (!connectionState.isLoading && !isRefreshing) {
          await refreshStatus();
        }
      }, refreshInterval);
    }

    return () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
      }
    };
  });

  /**
   * Refresh connection status
   */
  async function refreshStatus() {
    if (isRefreshing) return;

    isRefreshing = true;
    try {
      await mlConnectionStore.checkStatus();
      dispatch('refresh');
    } catch {
      // Failed to refresh ML connection status
    } finally {
      isRefreshing = false;
    }
  }

  /**
   * Handle connect action
   */
  function handleConnect() {
    dispatch('connect');
  }

  /**
   * Handle disconnect action
   */
  async function handleDisconnect() {
    // Note: In production, replace with a proper modal confirmation
    // eslint-disable-next-line no-alert
    if (window.confirm('Are you sure you want to disconnect your MercadoLibre account?')) {
      try {
        await mlConnectionStore.disconnect();
        dispatch('disconnect');
      } catch {
        // Failed to disconnect
      }
    }
  }

  /**
   * Handle token refresh
   */
  async function handleRefreshTokens() {
    try {
      await mlConnectionStore.refreshTokens();
    } catch {
      // Failed to refresh tokens
    }
  }

  /**
   * Format time until refresh
   */
  function formatTimeUntilRefresh(seconds: number | null): string {
    if (!seconds || seconds <= 0) return 'Soon';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  /**
   * Get status icon
   */
  function getStatusIcon(health: string): string {
    switch (health) {
      case 'healthy':
        return '✅';
      case 'expired':
        return '⏰';
      case 'invalid':
        return '❌';
      case 'disconnected':
        return '🔌';
      default:
        return '❓';
    }
  }
</script>

{#if variant === 'badge'}
  <!-- Badge variant - minimal display -->
  <div class="ml-status-badge {healthColor}" title={healthLabel}>
    <span class="status-icon">{getStatusIcon(health)}</span>
    {#if isConnected && userInfo.nickname}
      <span class="status-text">{userInfo.nickname}</span>
    {:else}
      <span class="status-text">{healthLabel}</span>
    {/if}
  </div>
{:else if variant === 'compact'}
  <!-- Compact variant - single line with essential info -->
  <div class="ml-status-compact">
    <div class="status-indicator {healthColor}">
      <span class="status-icon">{getStatusIcon(health)}</span>
      <span class="status-label">MercadoLibre: {healthLabel}</span>
    </div>

    {#if showActions && !connectionState.isLoading}
      <div class="compact-actions">
        {#if isConnected}
          {#if needsAttention}
            <button class="action-button warning" on:click={handleConnect}> Reconnect </button>
          {:else if showRefresh && canRefresh}
            <button
              class="action-button secondary"
              on:click={refreshStatus}
              disabled={isRefreshing}
            >
              {isRefreshing ? '⟳' : '↻'}
            </button>
          {/if}
        {:else}
          <button class="action-button primary" on:click={handleConnect}> Connect </button>
        {/if}
      </div>
    {/if}
  </div>
{:else}
  <!-- Full variant - complete status display -->
  <div class="ml-status-full">
    <!-- Header -->
    <div class="status-header">
      <div class="status-title">
        <span class="ml-logo">🛒</span>
        <h3>MercadoLibre Connection</h3>
      </div>

      {#if showRefresh && !connectionState.isLoading}
        <button
          class="refresh-button"
          on:click={refreshStatus}
          disabled={isRefreshing}
          title="Refresh status"
        >
          <span class="refresh-icon {isRefreshing ? 'spinning' : ''}">↻</span>
        </button>
      {/if}
    </div>

    <!-- Status content -->
    <div class="status-content">
      {#if connectionState.isLoading}
        <!-- Loading state -->
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <p>Checking connection...</p>
        </div>
      {:else if isConnected}
        <!-- Connected state -->
        <div class="connected-state">
          <div class="connection-info">
            <div class="status-indicator {healthColor}">
              <span class="status-icon">{getStatusIcon(health)}</span>
              <span class="status-label">{healthLabel}</span>
            </div>

            {#if userInfo.nickname || userInfo.email}
              <div class="user-info">
                {#if userInfo.nickname}
                  <p class="user-nickname">
                    <strong>{userInfo.nickname}</strong>
                  </p>
                {/if}
                {#if userInfo.email}
                  <p class="user-email">{userInfo.email}</p>
                {/if}
              </div>
            {/if}

            {#if site}
              <div class="site-info">
                <span class="site-flag">{site.flag}</span>
                <span class="site-name">{site.name}</span>
              </div>
            {/if}
          </div>

          <!-- Health details -->
          {#if health === 'healthy'}
            <div class="health-details success">
              <p>✅ Connection is healthy and active</p>
              {#if connectionState.expiresAt}
                <p class="expiry-info">
                  Token expires: {new Date(connectionState.expiresAt).toLocaleString()}
                </p>
              {/if}
              {#if connectionState.shouldRefresh && connectionState.timeUntilRefresh}
                <p class="refresh-info">
                  Auto-refresh in: {formatTimeUntilRefresh(connectionState.timeUntilRefresh)}
                </p>
              {/if}
            </div>
          {:else if health === 'expired'}
            <div class="health-details warning">
              <p>⏰ Your connection has expired</p>
              <p>Please reconnect to continue publishing to MercadoLibre</p>
            </div>
          {:else if health === 'invalid'}
            <div class="health-details error">
              <p>❌ Connection is invalid</p>
              {#if connectionState.error}
                <p class="error-message">{connectionState.error}</p>
              {/if}
              <p>Please reconnect to restore functionality</p>
            </div>
          {/if}

          <!-- Actions for connected state -->
          {#if showActions}
            <div class="status-actions">
              {#if needsAttention}
                <button class="action-button primary" on:click={handleConnect}>
                  Reconnect Account
                </button>
              {:else if connectionState.shouldRefresh}
                <button
                  class="action-button secondary"
                  on:click={handleRefreshTokens}
                  disabled={connectionState.isLoading}
                >
                  Refresh Tokens
                </button>
              {/if}

              <button
                class="action-button danger outline"
                on:click={handleDisconnect}
                disabled={connectionState.isLoading}
              >
                Disconnect
              </button>
            </div>
          {/if}
        </div>
      {:else}
        <!-- Disconnected state -->
        <div class="disconnected-state">
          <div class="status-indicator neutral">
            <span class="status-icon">🔌</span>
            <span class="status-label">Not Connected</span>
          </div>

          <div class="disconnect-info">
            <p>Connect your MercadoLibre account to start publishing listings automatically.</p>

            <div class="benefits-preview">
              <ul>
                <li>🚀 Automated publishing</li>
                <li>⚡ Real-time synchronization</li>
                <li>🎯 AI-optimized listings</li>
              </ul>
            </div>
          </div>

          {#if showActions}
            <div class="status-actions">
              <button class="action-button primary large" on:click={handleConnect}>
                Connect MercadoLibre Account
              </button>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Error display -->
      {#if connectionState.error && !isConnected}
        <div class="error-display">
          <span class="error-icon">❌</span>
          <p class="error-text">{connectionState.error}</p>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Badge variant styles */
  .ml-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .ml-status-badge.success {
    background-color: #dcfce7;
    color: #166534;
  }

  .ml-status-badge.warning {
    background-color: #fef3c7;
    color: #92400e;
  }

  .ml-status-badge.error {
    background-color: #fecaca;
    color: #991b1b;
  }

  .ml-status-badge.neutral {
    background-color: #f3f4f6;
    color: #374151;
  }

  /* Compact variant styles */
  .ml-status-compact {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background-color: #fafafa;
  }

  .compact-actions {
    display: flex;
    gap: 8px;
  }

  /* Full variant styles */
  .ml-status-full {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background-color: white;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .status-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
    background-color: #f9fafb;
  }

  .status-title {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .ml-logo {
    font-size: 1.5rem;
  }

  .status-title h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
  }

  .refresh-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    color: #6b7280;
    transition: all 0.2s;
  }

  .refresh-button:hover {
    color: #374151;
    background-color: #f3f4f6;
  }

  .refresh-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .refresh-icon {
    font-size: 1.125rem;
    transition: transform 0.6s ease;
  }

  .refresh-icon.spinning {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .status-content {
    padding: 20px;
  }

  /* Status indicators */
  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .status-indicator.success {
    color: #059669;
  }

  .status-indicator.warning {
    color: #d97706;
  }

  .status-indicator.error {
    color: #dc2626;
  }

  .status-indicator.neutral {
    color: #6b7280;
  }

  .status-icon {
    font-size: 1.25rem;
  }

  .status-label {
    font-weight: 600;
  }

  /* Loading state */
  .loading-state {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #6b7280;
  }

  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #e5e7eb;
    border-left: 2px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  /* Connection info */
  .connection-info {
    margin-bottom: 16px;
  }

  .user-info {
    margin: 8px 0;
  }

  .user-nickname {
    margin: 0 0 4px 0;
    color: #111827;
  }

  .user-email {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .site-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    padding: 8px 12px;
    background-color: #f3f4f6;
    border-radius: 6px;
  }

  .site-flag {
    font-size: 1.25rem;
  }

  .site-name {
    font-weight: 500;
    color: #374151;
  }

  /* Health details */
  .health-details {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .health-details.success {
    background-color: #dcfce7;
    border: 1px solid #bbf7d0;
  }

  .health-details.warning {
    background-color: #fef3c7;
    border: 1px solid #fde68a;
  }

  .health-details.error {
    background-color: #fecaca;
    border: 1px solid #fca5a5;
  }

  .health-details p {
    margin: 0 0 4px 0;
    font-size: 0.875rem;
  }

  .expiry-info,
  .refresh-info {
    color: #6b7280;
    font-size: 0.75rem !important;
  }

  .error-message {
    color: #991b1b;
    font-weight: 500;
  }

  /* Disconnected state */
  .disconnect-info {
    margin: 16px 0;
  }

  .disconnect-info p {
    color: #6b7280;
    margin-bottom: 12px;
  }

  .benefits-preview ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .benefits-preview li {
    padding: 4px 0;
    font-size: 0.875rem;
    color: #6b7280;
  }

  /* Error display */
  .error-display {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    background-color: #fecaca;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    margin-top: 16px;
  }

  .error-icon {
    flex-shrink: 0;
  }

  .error-text {
    margin: 0;
    font-size: 0.875rem;
    color: #991b1b;
  }

  /* Action buttons */
  .status-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 16px;
  }

  .action-button {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
  }

  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-button.primary {
    background-color: #3b82f6;
    color: white;
  }

  .action-button.primary:hover:not(:disabled) {
    background-color: #2563eb;
  }

  .action-button.secondary {
    background-color: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
  }

  .action-button.secondary:hover:not(:disabled) {
    background-color: #e5e7eb;
  }

  .action-button.warning {
    background-color: #f59e0b;
    color: white;
  }

  .action-button.warning:hover:not(:disabled) {
    background-color: #d97706;
  }

  .action-button.danger {
    background-color: #ef4444;
    color: white;
  }

  .action-button.danger:hover:not(:disabled) {
    background-color: #dc2626;
  }

  .action-button.outline {
    background-color: transparent;
    border: 1px solid currentColor;
  }

  .action-button.outline:hover:not(:disabled) {
    background-color: currentColor;
    color: white;
  }

  .action-button.large {
    padding: 12px 24px;
    font-size: 1rem;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .ml-status-compact {
      flex-direction: column;
      align-items: stretch;
    }

    .compact-actions {
      justify-content: center;
    }

    .status-actions {
      flex-direction: column;
    }

    .action-button {
      width: 100%;
    }
  }
</style>
