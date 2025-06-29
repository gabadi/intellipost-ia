<script lang="ts">
  import { isOffline, networkStatus } from '$stores/network';
  import { fly } from 'svelte/transition';

  let retryCount = 0;
  let isRetrying = false;

  async function handleRetry() {
    if (isRetrying) return;

    isRetrying = true;
    retryCount++;

    try {
      const isConnected = await networkStatus.checkConnection();
      if (!isConnected) {
        // Show feedback that retry failed

        setTimeout(() => {
          isRetrying = false;
        }, 2000);
      } else {
        isRetrying = false;
        retryCount = 0;
      }
    } catch {
      isRetrying = false;
    }
  }

  function getRetryMessage() {
    if (isRetrying) return 'Checking connection...';
    if (retryCount > 0) return `Retry attempt ${retryCount}`;
    return 'Tap to retry';
  }
</script>

{#if $isOffline}
  <div
    class="offline-banner"
    role="alert"
    aria-live="polite"
    transition:fly={{ y: -100, duration: 300 }}
  >
    <div class="banner-content">
      <div class="offline-icon" aria-hidden="true">📡</div>
      <div class="offline-text">
        <div class="offline-title">You're offline</div>
        <div class="offline-description">
          Check your internet connection. Some features may not be available.
        </div>
      </div>
      <button
        class="retry-button"
        class:retrying={isRetrying}
        on:click={handleRetry}
        disabled={isRetrying}
        aria-label="Retry connection"
      >
        <span class="retry-icon" class:spinning={isRetrying}>
          {isRetrying ? '⟳' : '↻'}
        </span>
        <span class="retry-text">{getRetryMessage()}</span>
      </button>
    </div>
  </div>
{/if}

<style>
  .offline-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--color-warning);
    color: white;
    z-index: 9999;
    box-shadow: var(--shadow-md);
  }

  @media (min-width: 768px) {
    .offline-banner {
      margin-left: 280px; /* Account for desktop navigation */
    }
  }

  .banner-content {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    max-width: 100%;
  }

  .offline-icon {
    font-size: var(--text-lg);
    flex-shrink: 0;
  }

  .offline-text {
    flex: 1;
    min-width: 0;
  }

  .offline-title {
    font-weight: 600;
    font-size: var(--text-sm);
    line-height: var(--leading-tight);
    margin-bottom: var(--space-1);
  }

  .offline-description {
    font-size: var(--text-xs);
    line-height: var(--leading-tight);
    opacity: 0.9;
  }

  .retry-button {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: 36px;
    flex-shrink: 0;
  }

  .retry-button:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.3);
  }

  .retry-button:focus {
    outline: 2px solid white;
    outline-offset: 2px;
  }

  .retry-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .retry-button.retrying {
    pointer-events: none;
  }

  .retry-icon {
    font-size: var(--text-base);
    transition: transform 0.3s ease;
  }

  .retry-icon.spinning {
    animation: spin 1s linear infinite;
  }

  .retry-text {
    white-space: nowrap;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  /* Mobile-specific adjustments */
  @media (max-width: 480px) {
    .banner-content {
      padding: var(--space-2) var(--space-3);
    }

    .offline-description {
      display: none; /* Hide description on very small screens */
    }

    .retry-text {
      display: none; /* Show only icon on small screens */
    }

    .retry-button {
      min-width: 36px;
      justify-content: center;
    }
  }

  /* Reduce motion for accessibility */
  @media (prefers-reduced-motion: reduce) {
    .retry-icon.spinning {
      animation: none;
      opacity: 0.7;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .offline-banner {
      background: var(--color-text);
      border-bottom: 3px solid var(--color-warning);
    }

    .retry-button {
      border: 2px solid white;
    }
  }
</style>
