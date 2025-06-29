<!--
  Registration is disabled - redirect to login page.

  This page now redirects users to the login page since registration
  has been disabled in favor of a default user system.
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuthenticated } from '$stores/auth';

  // Reactive redirect logic
  $: redirectTo = $page.url.searchParams.get('redirect') || '/';

  // Redirect to login immediately
  onMount(() => {
    if ($isAuthenticated) {
      goto(redirectTo);
    } else {
      // Redirect to login with the same redirect parameter
      const loginUrl = new URL('/auth/login', window.location.origin);
      if (redirectTo && redirectTo !== '/') {
        loginUrl.searchParams.set('redirect', redirectTo);
      }
      goto(loginUrl.toString());
    }
  });
</script>

<svelte:head>
  <title>Redirecting to Login - IntelliPost AI</title>
  <meta
    name="description"
    content="Redirecting to login page. Registration is disabled - please use the default login credentials."
  />
  <meta name="robots" content="noindex" />
</svelte:head>

<div class="redirect-page">
  <div class="redirect-container">
    <header class="page-header">
      <a href="/" class="logo-link" aria-label="Go to homepage">
        <h1 class="logo">IntelliPost AI</h1>
      </a>
    </header>

    <main class="main-content">
      <div class="redirect-message">
        <h2>Redirecting to Login</h2>
        <p>Registration has been disabled. Please use the login page to access the system.</p>
        <p><strong>Loading...</strong></p>
      </div>
    </main>
  </div>
</div>

<style>
  .redirect-page {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-background) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-4);
  }

  .redirect-container {
    width: 100%;
    max-width: 480px;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-8);
  }

  .page-header {
    text-align: center;
  }

  .logo-link {
    text-decoration: none;
    color: inherit;
    display: inline-block;
    transition: transform 0.2s ease;
  }

  .logo-link:hover {
    transform: scale(1.02);
  }

  .logo-link:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
    border-radius: var(--border-radius-md);
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

  .redirect-message {
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

  .redirect-message h2 {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--color-text);
    margin: 0 0 var(--spacing-4) 0;
    line-height: 1.2;
  }

  .redirect-message p {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-3) 0;
    line-height: 1.4;
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .redirect-page {
      padding: var(--spacing-2);
      align-items: flex-start;
      padding-top: var(--spacing-8);
    }

    .redirect-container {
      gap: var(--spacing-6);
    }

    .redirect-message {
      padding: var(--spacing-6);
      border-radius: var(--border-radius-md);
    }

    .logo {
      font-size: var(--font-size-2xl);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .redirect-page {
      background: linear-gradient(
        135deg,
        var(--color-primary-900) 0%,
        var(--color-background) 100%
      );
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .logo-link {
      transition: none;
    }
  }
</style>
