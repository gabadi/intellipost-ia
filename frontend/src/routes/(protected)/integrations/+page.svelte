<script lang="ts">
  /**
   * Integrations Landing Page
   *
   * Central hub for managing all third-party integrations including
   * MercadoLibre, with clear connection status and management options.
   */

  import { onMount } from 'svelte';
  import { mlConnectionStore, isMLConnected } from '$lib/stores/ml-connection';
  import MLConnectionStatus from '$lib/components/ml/MLConnectionStatus.svelte';
  import { get } from 'svelte/store';

  // Reactive values
  let connectedToML = false;

  // Use get() to avoid $ syntax issues with dependency-cruiser
  $: {
    connectedToML = get(isMLConnected);
  }

  // Initialize ML connection store on mount
  onMount(() => {
    mlConnectionStore.init();
  });

  /**
   * Handle ML connection action
   */
  function handleMLConnect() {
    // Navigate to ML setup page for full setup experience
    window.location.href = '/ml-setup';
  }

  /**
   * Handle ML disconnection
   */
  function handleMLDisconnect() {
    // Handled by the MLConnectionStatus component
    // MercadoLibre disconnected from integrations page
  }

  /**
   * Handle ML connection refresh
   */
  function handleMLRefresh() {
    // MercadoLibre connection refreshed from integrations page
  }
</script>

<svelte:head>
  <title>Integrations - IntelliPost AI</title>
  <meta
    name="description"
    content="Manage your third-party integrations and connect with marketplaces like MercadoLibre."
  />
</svelte:head>

<div class="integrations-page">
  <!-- Header -->
  <div class="page-header">
    <h1>Integrations</h1>
    <p class="header-description">
      Connect your favorite marketplaces and services to streamline your product management
      workflow.
    </p>
  </div>

  <!-- Available Integrations -->
  <div class="integrations-section">
    <h2>Available Integrations</h2>
    <div class="integrations-grid">
      <!-- MercadoLibre Integration Card -->
      <div class="integration-card">
        <div class="integration-header">
          <div class="integration-info">
            <div class="integration-icon">🛒</div>
            <div class="integration-details">
              <h3>MercadoLibre</h3>
              <p>Latin America's leading e-commerce platform</p>
            </div>
          </div>
          <div class="integration-status">
            {#if connectedToML}
              <span class="status-badge connected">Connected</span>
            {:else}
              <span class="status-badge disconnected">Not Connected</span>
            {/if}
          </div>
        </div>

        <div class="integration-content">
          <!-- Connection Status Component -->
          <MLConnectionStatus
            variant="compact"
            showActions={true}
            showRefresh={true}
            on:connect={handleMLConnect}
            on:disconnect={handleMLDisconnect}
            on:refresh={handleMLRefresh}
          />

          <!-- Features List -->
          <div class="features-list">
            <h4>Features</h4>
            <ul>
              <li>
                <span class="feature-icon">🚀</span>
                <span>Automated product publishing</span>
              </li>
              <li>
                <span class="feature-icon">⚡</span>
                <span>Real-time inventory sync</span>
              </li>
              <li>
                <span class="feature-icon">🎯</span>
                <span>AI-optimized listings</span>
              </li>
              <li>
                <span class="feature-icon">📊</span>
                <span>Performance analytics</span>
              </li>
            </ul>
          </div>

          <!-- Action Buttons -->
          <div class="integration-actions">
            {#if connectedToML}
              <a href="/ml-setup" class="action-button secondary"> Manage Settings </a>
            {:else}
              <button class="action-button primary" on:click={handleMLConnect}>
                Connect Account
              </button>
            {/if}
          </div>
        </div>
      </div>

      <!-- Future Integrations Placeholder -->
      <div class="integration-card coming-soon">
        <div class="integration-header">
          <div class="integration-info">
            <div class="integration-icon">🔮</div>
            <div class="integration-details">
              <h3>More Coming Soon</h3>
              <p>Additional marketplace integrations</p>
            </div>
          </div>
          <div class="integration-status">
            <span class="status-badge coming-soon">Coming Soon</span>
          </div>
        </div>

        <div class="integration-content">
          <p class="coming-soon-text">
            We're working on integrations with more marketplaces and services. Stay tuned for
            updates!
          </p>

          <div class="upcoming-features">
            <h4>Planned Integrations</h4>
            <ul>
              <li>
                <span class="feature-icon">🛍️</span>
                <span>Amazon Marketplace</span>
              </li>
              <li>
                <span class="feature-icon">📱</span>
                <span>Social Media Platforms</span>
              </li>
              <li>
                <span class="feature-icon">📧</span>
                <span>Email Marketing Tools</span>
              </li>
              <li>
                <span class="feature-icon">📈</span>
                <span>Analytics Platforms</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Integration Tips -->
  <div class="tips-section">
    <h2>Integration Tips</h2>
    <div class="tips-grid">
      <div class="tip-card">
        <div class="tip-icon">🔐</div>
        <h3>Secure Connections</h3>
        <p>
          All integrations use OAuth 2.0 with PKCE security. Your credentials are never stored by
          IntelliPost AI.
        </p>
      </div>
      <div class="tip-card">
        <div class="tip-icon">🔄</div>
        <h3>Automatic Sync</h3>
        <p>
          Once connected, your data syncs automatically. You can always refresh manually if needed.
        </p>
      </div>
      <div class="tip-card">
        <div class="tip-icon">⚙️</div>
        <h3>Manage Settings</h3>
        <p>
          Each integration has detailed settings pages where you can customize behavior and
          preferences.
        </p>
      </div>
    </div>
  </div>
</div>

<style>
  .integrations-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .page-header {
    margin-bottom: 40px;
  }

  .page-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 12px 0;
  }

  .header-description {
    font-size: 1.125rem;
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.6;
  }

  .integrations-section {
    margin-bottom: 48px;
  }

  .integrations-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 24px 0;
  }

  .integrations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
  }

  .integration-card {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s;
  }

  .integration-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .integration-card.coming-soon {
    background: var(--color-background-secondary);
    border-color: var(--color-border-muted);
  }

  .integration-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
  }

  .integration-info {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .integration-icon {
    font-size: 2.5rem;
    flex-shrink: 0;
  }

  .integration-details h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 4px 0;
  }

  .integration-details p {
    color: var(--color-text-secondary);
    margin: 0;
    font-size: 0.875rem;
  }

  .integration-status {
    flex-shrink: 0;
  }

  .status-badge {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .status-badge.connected {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  .status-badge.disconnected {
    background: var(--color-background-tertiary);
    color: var(--color-text-muted);
  }

  .status-badge.coming-soon {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  .integration-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .features-list h4,
  .upcoming-features h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 12px 0;
  }

  .features-list ul,
  .upcoming-features ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .features-list li,
  .upcoming-features li {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
  }

  .feature-icon {
    font-size: 1rem;
    flex-shrink: 0;
  }

  .coming-soon-text {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    line-height: 1.6;
    margin: 0;
  }

  .integration-actions {
    display: flex;
    gap: 12px;
    margin-top: auto;
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

  .action-button.primary {
    background: var(--color-primary);
    color: white;
  }

  .action-button.primary:hover {
    background: var(--color-primary-hover);
  }

  .action-button.secondary {
    background: var(--color-background-secondary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
  }

  .action-button.secondary:hover {
    background: var(--color-background-tertiary);
  }

  .tips-section {
    margin-bottom: 48px;
  }

  .tips-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 24px 0;
  }

  .tips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }

  .tip-card {
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border-muted);
    border-radius: 8px;
    padding: 20px;
  }

  .tip-icon {
    font-size: 2rem;
    margin-bottom: 12px;
  }

  .tip-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 8px 0;
  }

  .tip-card p {
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.6;
    font-size: 0.875rem;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .integrations-page {
      padding: 16px;
    }

    .page-header h1 {
      font-size: 2rem;
    }

    .header-description {
      font-size: 1rem;
    }

    .integrations-grid {
      grid-template-columns: 1fr;
    }

    .integration-header {
      flex-direction: column;
      gap: 16px;
      align-items: flex-start;
    }

    .integration-info {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .tips-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
