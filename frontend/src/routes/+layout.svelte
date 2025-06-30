<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import MobileNavigation from '$components/core/MobileNavigation.svelte';
  import DesktopNavigation from '$components/core/DesktopNavigation.svelte';
  import OfflineBanner from '$components/ui/OfflineBanner.svelte';
  import { authStore } from '$stores/auth';
  import { themeStore } from '$stores/theme';
  import '../app.css';

  // Initialize stores on app startup
  onMount(() => {
    authStore.initialize();

    // Initialize theme store (redundant safety check)
    themeStore.initialize();
  });

  // Check if we're on an auth page
  $: isAuthPage = $page.url.pathname.startsWith('/auth');
</script>

<svelte:head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <!-- theme-color meta tag is handled by theme system in app.html -->
</svelte:head>

<!-- Skip Navigation Links for Accessibility -->
<nav class="skip-links" aria-label="Skip navigation">
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <a href="#mobile-navigation" class="skip-link">Skip to navigation</a>
</nav>

<div class="app">
  <!-- Offline Banner -->
  <OfflineBanner />

  <!-- Hidden heading for screen readers -->
  <h1 class="sr-only">IntelliPost AI - Intelligent Social Media Posting Platform</h1>

  <!-- Desktop Navigation - Only show when not on auth pages -->
  {#if !isAuthPage}
    <DesktopNavigation />
  {/if}

  <main class="main-content" class:auth-layout={isAuthPage} id="main-content" tabindex="-1">
    <slot />
  </main>

  <!-- Mobile Navigation - Only show when not on auth pages -->
  {#if !isAuthPage}
    <MobileNavigation />
  {/if}
</div>

<style>
  /* Skip navigation links for accessibility */
  .skip-links {
    position: fixed;
    top: -100px;
    left: 0;
    z-index: 9999;
    display: flex;
    gap: var(--space-2);
    background: white;
    padding: var(--space-2);
    border-radius: 0 0 var(--radius-md) 0;
    box-shadow: var(--shadow-lg);
  }

  .skip-links:focus-within {
    top: 0;
  }

  .skip-link {
    padding: var(--space-2) var(--space-4);
    background: var(--color-primary);
    color: white;
    text-decoration: none;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    min-height: var(--touch-target-min);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .skip-link:hover,
  .skip-link:focus {
    background: var(--color-primary-hover);
    outline: 2px solid var(--color-gray-900);
    outline-offset: 2px;
  }

  /* Screen reader only content */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main-content {
    flex: 1;
    padding-bottom: 70px; /* Space for mobile navigation */
    min-height: 100vh;
    padding: var(--space-4);
  }

  .main-content:focus {
    outline: none;
  }

  @media (min-width: 768px) {
    .main-content {
      margin-left: 280px; /* Space for desktop navigation */
      padding-bottom: 0; /* No space needed for mobile nav on desktop */
      padding: var(--space-6);
    }

    /* Auth pages: full width, centered layout */
    .main-content.auth-layout {
      margin-left: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: var(--space-4);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .skip-link {
      transition: none;
    }
  }
</style>
