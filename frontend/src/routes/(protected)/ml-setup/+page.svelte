<script lang="ts">
  /**
   * MercadoLibre Setup Page
   *
   * Main page for managing MercadoLibre integration with connection modal
   * and status display.
   */

  import { onMount } from 'svelte';
  import MLConnectionModal from '$lib/components/ml/MLConnectionModal.svelte';
  import MLConnectionStatus from '$lib/components/ml/MLConnectionStatus.svelte';
  import { mlConnectionStore, isMLConnected } from '$lib/stores/ml-connection';
  import { get } from 'svelte/store';

  // Component state
  let showConnectionModal = false;
  let selectedSiteId = 'MLA';

  // Reactive values
  let isConnected = false;

  // Use get() to avoid $ syntax issues with dependency-cruiser
  $: {
    isConnected = get(isMLConnected);
  }

  // Initialize store on mount
  onMount(() => {
    mlConnectionStore.init();
  });

  /**
   * Handle connect button click
   */
  function handleConnect() {
    showConnectionModal = true;
  }

  /**
   * Handle modal close
   */
  function handleModalClose() {
    showConnectionModal = false;
  }

  /**
   * Handle successful connection
   */
  function handleConnected(_event: CustomEvent) {
    showConnectionModal = false;
    // Connection status will be updated automatically by the store
  }

  /**
   * Handle disconnect
   */
  function handleDisconnect() {
    // Disconnection is handled by the MLConnectionStatus component
    // MercadoLibre account disconnected
  }

  /**
   * Handle status refresh
   */
  function handleRefresh() {
    // MercadoLibre connection status refreshed
  }
</script>

<svelte:head>
  <title>MercadoLibre Setup - IntelliPost AI</title>
  <meta
    name="description"
    content="Connect your MercadoLibre account to automate product listing publishing with AI-generated content."
  />
</svelte:head>

<div class="ml-setup-page">
  <!-- Header -->
  <div class="page-header">
    <div class="header-content">
      <div class="header-text">
        <h1>MercadoLibre Integration</h1>
        <p class="header-description">
          Connect your MercadoLibre account to automatically publish AI-generated product listings
          and synchronize your inventory across platforms.
        </p>
      </div>
      <div class="header-logo">
        <span class="ml-logo">🛒</span>
      </div>
    </div>
  </div>

  <!-- Main content -->
  <div class="page-content">
    {#if isConnected}
      <!-- Connected state -->
      <div class="connected-section">
        <div class="status-card">
          <MLConnectionStatus
            variant="full"
            showActions={true}
            showRefresh={true}
            on:connect={handleConnect}
            on:disconnect={handleDisconnect}
            on:refresh={handleRefresh}
          />
        </div>

        <!-- Features available when connected -->
        <div class="features-section">
          <h2>Available Features</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">🚀</div>
              <h3>Automated Publishing</h3>
              <p>
                Publish AI-generated product listings directly to your MercadoLibre store with
                optimized titles and descriptions.
              </p>
              <div class="feature-status enabled">
                <span class="status-indicator">✅</span>
                <span>Active</span>
              </div>
            </div>

            <div class="feature-card">
              <div class="feature-icon">⚡</div>
              <h3>Real-time Sync</h3>
              <p>
                Keep your product inventory synchronized between IntelliPost AI and MercadoLibre
                automatically.
              </p>
              <div class="feature-status enabled">
                <span class="status-indicator">✅</span>
                <span>Active</span>
              </div>
            </div>

            <div class="feature-card">
              <div class="feature-icon">🎯</div>
              <h3>Smart Optimization</h3>
              <p>
                AI-powered optimization for better visibility and conversion rates in MercadoLibre
                search results.
              </p>
              <div class="feature-status enabled">
                <span class="status-indicator">✅</span>
                <span>Active</span>
              </div>
            </div>

            <div class="feature-card">
              <div class="feature-icon">📊</div>
              <h3>Performance Analytics</h3>
              <p>
                Track listing performance and get insights on how to improve your product
                visibility.
              </p>
              <div class="feature-status coming-soon">
                <span class="status-indicator">🔄</span>
                <span>Coming Soon</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick actions -->
        <div class="actions-section">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            <a href="/products/new" class="action-card">
              <div class="action-icon">➕</div>
              <div class="action-content">
                <h3>Create New Product</h3>
                <p>Generate and publish a new product listing with AI assistance</p>
              </div>
              <div class="action-arrow">→</div>
            </a>

            <a href="/products" class="action-card">
              <div class="action-icon">📋</div>
              <div class="action-content">
                <h3>Manage Products</h3>
                <p>View and manage your existing product listings</p>
              </div>
              <div class="action-arrow">→</div>
            </a>

            <button class="action-card button" on:click={() => mlConnectionStore.checkStatus()}>
              <div class="action-icon">🔄</div>
              <div class="action-content">
                <h3>Refresh Connection</h3>
                <p>Check connection status and refresh tokens if needed</p>
              </div>
              <div class="action-arrow">↻</div>
            </button>
          </div>
        </div>
      </div>
    {:else}
      <!-- Not connected state -->
      <div class="not-connected-section">
        <!-- Benefits showcase -->
        <div class="benefits-card">
          <h2>Why Connect MercadoLibre?</h2>
          <div class="benefits-list">
            <div class="benefit-item">
              <div class="benefit-icon">🤖</div>
              <div class="benefit-content">
                <h3>AI-Powered Listings</h3>
                <p>
                  Generate high-quality product titles, descriptions, and categories optimized for
                  MercadoLibre's search algorithm.
                </p>
              </div>
            </div>

            <div class="benefit-item">
              <div class="benefit-icon">⏱️</div>
              <div class="benefit-content">
                <h3>Save Time</h3>
                <p>
                  Automate the tedious process of creating and formatting product listings. Focus on
                  growing your business instead.
                </p>
              </div>
            </div>

            <div class="benefit-item">
              <div class="benefit-icon">📈</div>
              <div class="benefit-content">
                <h3>Increase Visibility</h3>
                <p>
                  AI-optimized content helps your products rank higher in search results and attract
                  more buyers.
                </p>
              </div>
            </div>

            <div class="benefit-item">
              <div class="benefit-icon">🔄</div>
              <div class="benefit-content">
                <h3>Stay Synchronized</h3>
                <p>
                  Keep your inventory up-to-date across all platforms with automatic
                  synchronization.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Connection CTA -->
        <div class="connection-cta">
          <h2>Ready to Get Started?</h2>
          <p>
            Connect your MercadoLibre account now and start publishing AI-generated listings in
            minutes.
          </p>

          <!-- Important notice -->
          <div class="manager-notice">
            <div class="notice-icon">⚠️</div>
            <div class="notice-content">
              <p>
                <strong>Manager Account Required:</strong> Only MercadoLibre manager accounts can connect
                to IntelliPost AI. Collaborator accounts cannot authorize applications.
              </p>
            </div>
          </div>

          <button class="connect-button" on:click={handleConnect}>
            <span class="button-icon">🔗</span>
            Connect MercadoLibre Account
          </button>

          <!-- Security note -->
          <div class="security-note">
            <p>
              🔒 This connection uses OAuth 2.0 with PKCE security. Your MercadoLibre credentials
              are never stored by IntelliPost AI.
            </p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Connection Modal -->
<MLConnectionModal
  bind:isOpen={showConnectionModal}
  bind:selectedSiteId
  on:close={handleModalClose}
  on:connected={handleConnected}
/>

<style>
  .ml-setup-page {
    min-height: 100vh;
    background-color: #f9fafb;
  }

  .page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 20px;
  }

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
  }

  .header-text h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 12px 0;
  }

  .header-description {
    font-size: 1.125rem;
    margin: 0;
    opacity: 0.9;
    line-height: 1.6;
    max-width: 600px;
  }

  .header-logo .ml-logo {
    font-size: 4rem;
    opacity: 0.8;
  }

  .page-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
  }

  /* Connected state styles */
  .connected-section {
    display: flex;
    flex-direction: column;
    gap: 40px;
  }

  .status-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .features-section h2,
  .actions-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 24px 0;
    color: #111827;
  }

  .features-grid,
  .actions-grid {
    display: grid;
    gap: 20px;
  }

  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }

  .actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }

  .feature-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
  }

  .feature-icon {
    font-size: 2rem;
    margin-bottom: 16px;
  }

  .feature-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #111827;
  }

  .feature-card p {
    color: #6b7280;
    line-height: 1.6;
    margin: 0 0 16px 0;
  }

  .feature-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }

  .feature-status.enabled {
    color: #059669;
  }

  .feature-status.coming-soon {
    color: #d97706;
  }

  .action-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 16px;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
    cursor: pointer;
  }

  .action-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .action-card.button {
    border: none;
    text-align: left;
    width: 100%;
  }

  .action-icon {
    font-size: 2rem;
    flex-shrink: 0;
  }

  .action-content {
    flex: 1;
  }

  .action-content h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0 0 4px 0;
    color: #111827;
  }

  .action-content p {
    color: #6b7280;
    margin: 0;
    font-size: 0.875rem;
  }

  .action-arrow {
    font-size: 1.25rem;
    color: #6b7280;
    flex-shrink: 0;
  }

  /* Not connected state styles */
  .not-connected-section {
    display: flex;
    flex-direction: column;
    gap: 40px;
  }

  .benefits-card {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
  }

  .benefits-card h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 24px 0;
    color: #111827;
    text-align: center;
  }

  .benefits-list {
    display: grid;
    gap: 24px;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }

  .benefit-item {
    display: flex;
    gap: 16px;
    align-items: flex-start;
  }

  .benefit-icon {
    font-size: 2rem;
    flex-shrink: 0;
  }

  .benefit-content h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #111827;
  }

  .benefit-content p {
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
  }

  .connection-cta {
    background: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    text-align: center;
  }

  .connection-cta h2 {
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0 0 12px 0;
    color: #111827;
  }

  .connection-cta > p {
    font-size: 1.125rem;
    color: #6b7280;
    margin: 0 0 32px 0;
    line-height: 1.6;
  }

  .manager-notice {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    background-color: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 16px;
    margin: 24px 0;
    text-align: left;
  }

  .notice-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
  }

  .notice-content p {
    margin: 0;
    color: #92400e;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .connect-button {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 16px 32px;
    font-size: 1.125rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    margin: 0 0 24px 0;
  }

  .connect-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  }

  .button-icon {
    font-size: 1.25rem;
  }

  .security-note {
    margin-top: 16px;
  }

  .security-note p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .header-content {
      flex-direction: column;
      text-align: center;
    }

    .header-text h1 {
      font-size: 2rem;
    }

    .header-description {
      font-size: 1rem;
    }

    .page-content {
      padding: 20px 10px;
    }

    .benefits-list {
      grid-template-columns: 1fr;
    }

    .features-grid,
    .actions-grid {
      grid-template-columns: 1fr;
    }

    .benefit-item,
    .action-card {
      flex-direction: column;
      text-align: center;
      gap: 12px;
    }

    .action-content {
      text-align: center;
    }

    .benefits-card,
    .connection-cta {
      padding: 24px;
    }

    .manager-notice {
      flex-direction: column;
      text-align: center;
    }
  }
</style>
