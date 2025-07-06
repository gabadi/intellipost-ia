<script lang="ts">
  /**
   * Quick Action Card Component
   *
   * Reusable card for dashboard quick actions with support for different
   * action types, status indicators, and navigation.
   */

  import { createEventDispatcher } from 'svelte';

  // Component props
  export let title: string;
  export let description: string;
  export let icon: string;
  export let href: string = '';
  export let status: 'connected' | 'disconnected' | 'warning' | 'info' = 'info';
  export let actionText: string = 'Open';
  export let disabled: boolean = false;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    click: void;
  }>();

  /**
   * Handle card click
   */
  function handleClick() {
    if (disabled) return;

    if (href) {
      window.location.href = href;
    } else {
      dispatch('click');
    }
  }

  /**
   * Get status color class
   */
  function getStatusClass(status: string): string {
    switch (status) {
      case 'connected':
        return 'status-connected';
      case 'disconnected':
        return 'status-disconnected';
      case 'warning':
        return 'status-warning';
      case 'info':
      default:
        return 'status-info';
    }
  }

  /**
   * Get status icon
   */
  function getStatusIcon(status: string): string {
    switch (status) {
      case 'connected':
        return '✅';
      case 'disconnected':
        return '⚫';
      case 'warning':
        return '⚠️';
      case 'info':
      default:
        return 'ℹ️';
    }
  }

  /**
   * Get status text
   */
  function getStatusText(status: string): string {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Not Connected';
      case 'warning':
        return 'Needs Attention';
      case 'info':
      default:
        return 'Available';
    }
  }
</script>

<div
  class="quick-action-card {getStatusClass(status)}"
  class:disabled
  on:click={handleClick}
  on:keydown={e => e.key === 'Enter' && handleClick()}
  role="button"
  tabindex={disabled ? -1 : 0}
  aria-label="{title} - {getStatusText(status)}"
>
  <!-- Card Header -->
  <div class="card-header">
    <div class="card-icon">
      {icon}
    </div>
    <div class="status-indicator">
      <span class="status-icon">{getStatusIcon(status)}</span>
      <span class="status-text">{getStatusText(status)}</span>
    </div>
  </div>

  <!-- Card Content -->
  <div class="card-content">
    <h3 class="card-title">{title}</h3>
    <p class="card-description">{description}</p>
  </div>

  <!-- Card Footer -->
  <div class="card-footer">
    <span class="action-text">{actionText}</span>
    <span class="action-arrow">→</span>
  </div>
</div>

<style>
  .quick-action-card {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 160px;
  }

  .quick-action-card:hover:not(.disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: var(--color-primary-light);
  }

  .quick-action-card:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .quick-action-card.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .card-icon {
    font-size: 2rem;
    flex-shrink: 0;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 12px;
    white-space: nowrap;
  }

  .status-icon {
    font-size: 0.875rem;
  }

  /* Status color variants */
  .status-connected .status-indicator {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  .status-disconnected .status-indicator {
    background: var(--color-background-tertiary);
    color: var(--color-text-muted);
  }

  .status-warning .status-indicator {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  .status-info .status-indicator {
    background: var(--color-primary-light);
    color: var(--color-primary-dark);
  }

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
    line-height: 1.3;
  }

  .card-description {
    color: var(--color-text-secondary);
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.5;
    flex: 1;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
    padding-top: 8px;
    border-top: 1px solid var(--color-border-muted);
  }

  .action-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-primary);
  }

  .action-arrow {
    font-size: 1rem;
    color: var(--color-text-muted);
    transition: transform 0.2s ease;
  }

  .quick-action-card:hover:not(.disabled) .action-arrow {
    transform: translateX(4px);
    color: var(--color-primary);
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .quick-action-card {
      padding: 16px;
      min-height: 140px;
    }

    .card-icon {
      font-size: 1.75rem;
    }

    .card-title {
      font-size: 1rem;
    }

    .card-description {
      font-size: 0.8rem;
    }

    .status-indicator {
      font-size: 0.7rem;
      padding: 3px 6px;
    }
  }

  /* High contrast support */
  @media (prefers-contrast: high) {
    .quick-action-card {
      border-width: 2px;
    }

    .quick-action-card:focus {
      outline-width: 3px;
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .quick-action-card {
      transition: none;
    }

    .action-arrow {
      transition: none;
    }
  }
</style>
