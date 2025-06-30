<!--
  Logout page that handles user logout and redirects to login
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$stores/auth';

  let logoutError = '';

  onMount(async () => {
    try {
      // Perform logout
      await authStore.logout();

      // Small delay to show the logout message
      setTimeout(() => {
        goto('/auth/login');
      }, 1500);
    } catch {
      // Logout error, but still continue to redirect
      logoutError = 'Logout failed. Redirecting to login...';

      // Still redirect to login even if logout fails
      setTimeout(() => {
        goto('/auth/login');
      }, 2000);
    }
  });
</script>

<svelte:head>
  <title>Signing Out - IntelliPost AI</title>
  <meta name="robots" content="noindex" />
</svelte:head>

<div class="logout-page">
  <div class="logout-container">
    <header class="page-header">
      <h1 class="logo">IntelliPost AI</h1>
    </header>

    <main class="main-content">
      <div class="logout-message">
        {#if logoutError}
          <div class="error-icon" aria-hidden="true">⚠️</div>
          <h2>Logout Issue</h2>
          <p class="error-text">{logoutError}</p>
        {:else}
          <div class="loading-icon" aria-hidden="true">👋</div>
          <h2>Signing Out</h2>
          <p>Thank you for using IntelliPost AI. You are being signed out...</p>
        {/if}

        <div class="loading-spinner" aria-hidden="true"></div>
      </div>
    </main>
  </div>
</div>

<style>
  .logout-page {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-background) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-4);
  }

  .logout-container {
    width: 100%;
    max-width: 480px;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-8);
  }

  .page-header {
    text-align: center;
  }

  .logo {
    font-size: var(--font-size-3xl);
    font-weight: 800;
    color: var(--color-primary);
    margin: 0;
    letter-spacing: -0.02em;
  }

  .main-content {
    display: flex;
    justify-content: center;
  }

  .logout-message {
    width: 100%;
    background: var(--color-background);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-8);
    box-shadow:
      0 10px 25px -5px rgba(0, 0, 0, 0.1),
      0 8px 10px -6px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--color-border-light);
    text-align: center;
  }

  .loading-icon,
  .error-icon {
    font-size: var(--font-size-4xl);
    margin-bottom: var(--spacing-4);
  }

  .logout-message h2 {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--color-text);
    margin: 0 0 var(--spacing-3) 0;
    line-height: 1.2;
  }

  .logout-message p {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-4) 0;
    line-height: 1.4;
  }

  .error-text {
    color: var(--color-error) !important;
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-border);
    border-top: 3px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .logout-page {
      padding: var(--spacing-2);
      align-items: flex-start;
      padding-top: var(--spacing-8);
    }

    .logout-container {
      gap: var(--spacing-6);
    }

    .logout-message {
      padding: var(--spacing-6);
      border-radius: var(--border-radius-md);
    }

    .logo {
      font-size: var(--font-size-2xl);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .logout-page {
      background: linear-gradient(
        135deg,
        var(--color-primary-900) 0%,
        var(--color-background) 100%
      );
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .loading-spinner {
      animation: none;
    }
  }
</style>
