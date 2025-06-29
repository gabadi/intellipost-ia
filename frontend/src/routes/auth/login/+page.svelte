<!--
  Login page route.

  Features:
  - Standalone login page
  - Redirect handling
  - Mobile-first responsive design
  - SEO optimization
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import type { User } from '$types/auth';
  import { isAuthenticated } from '$stores/auth';
  import LoginForm from '$lib/components/auth/LoginForm.svelte';

  // Reactive redirect logic
  $: redirectTo = $page.url.searchParams.get('redirect') || '/';

  // Handle successful login
  function handleLoginSuccess(_event: CustomEvent<{ user: User }>) {
    // Redirect to intended page or dashboard
    goto(redirectTo);
  }

  // Handle login error
  function handleLoginError(_event: CustomEvent<{ error: string }>) {
    // Error is already displayed in the form
  }

  // Switch to register page
  function switchToRegister() {
    const registerUrl = new URL('/auth/register', window.location.origin);
    if (redirectTo && redirectTo !== '/') {
      registerUrl.searchParams.set('redirect', redirectTo);
    }
    goto(registerUrl.toString());
  }

  // Redirect if already authenticated
  onMount(() => {
    if ($isAuthenticated) {
      goto(redirectTo);
    }
  });
</script>

<svelte:head>
  <title>Sign In - IntelliPost AI</title>
  <meta
    name="description"
    content="Sign in to your IntelliPost AI account to access intelligent social media posting with AI content generation."
  />
  <meta name="robots" content="noindex" />
</svelte:head>

<div class="login-page">
  <div class="login-container">
    <!-- Header -->
    <header class="page-header">
      <a href="/" class="logo-link" aria-label="Go to homepage">
        <h1 class="logo">IntelliPost AI</h1>
      </a>
    </header>

    <!-- Main content -->
    <main class="main-content">
      <div class="form-container">
        <LoginForm
          {redirectTo}
          on:success={handleLoginSuccess}
          on:error={handleLoginError}
          on:switchToRegister={switchToRegister}
        />
      </div>
    </main>

    <!-- Footer -->
    <footer class="page-footer">
      <p class="footer-text">
        By signing in, you agree to our
        <a href="/terms" class="footer-link">Terms of Service</a>
        and
        <a href="/privacy" class="footer-link">Privacy Policy</a>
      </p>
    </footer>
  </div>
</div>

<style>
  .login-page {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-background) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-4);
  }

  .login-container {
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

  .form-container {
    width: 100%;
    background: var(--color-background);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-8);
    box-shadow:
      0 10px 25px -5px rgba(0, 0, 0, 0.1),
      0 8px 10px -6px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--color-border-light);
  }

  .page-footer {
    text-align: center;
  }

  .footer-text {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .footer-link {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
  }

  .footer-link:hover {
    color: var(--color-primary-hover);
    text-decoration: underline;
  }

  .footer-link:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
    border-radius: var(--border-radius-sm);
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .login-page {
      padding: var(--spacing-2);
      align-items: flex-start;
      padding-top: var(--spacing-8);
    }

    .login-container {
      gap: var(--spacing-6);
    }

    .form-container {
      padding: var(--spacing-6);
      border-radius: var(--border-radius-md);
    }

    .logo {
      font-size: var(--font-size-2xl);
    }
  }

  /* Tablet styles */
  @media (min-width: 768px) and (max-width: 1023px) {
    .login-container {
      max-width: 520px;
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .login-page {
      background: linear-gradient(
        135deg,
        var(--color-primary-900) 0%,
        var(--color-background) 100%
      );
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .form-container {
      border: 2px solid var(--color-border);
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .logo-link {
      transition: none;
    }

    .footer-link {
      transition: none;
    }
  }

  /* Print styles */
  @media print {
    .login-page {
      background: none;
      min-height: auto;
    }

    .form-container {
      box-shadow: none;
      border: 1px solid var(--color-border);
    }
  }
</style>
