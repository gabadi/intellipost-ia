<script lang="ts">
  import { page } from '$app/stores';
  import type { NavItem } from '$types/navigation.js';
  import { themeStore, isDarkMode } from '$lib/stores/theme';
  import { config } from '$lib/config';

  const navItems: NavItem[] = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/products/new', label: 'Create Product', icon: '➕' },
    { path: '/products', label: 'Products', icon: '📦' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  $: currentPath = $page.url.pathname;

  function isActive(path: string): boolean {
    // Handle root path exactly
    if (path === '/') {
      return currentPath === '/';
    }

    // For other paths, check for exact match first
    if (currentPath === path) {
      return true;
    }

    // For parent paths, only match if current path starts with the path
    // AND the next character is a slash (to avoid partial matches)
    // AND there's no more specific match available
    if (currentPath.startsWith(`${path}/`)) {
      // Check if there's a more specific navigation item that would match
      const moreSpecificExists = navItems.some(
        item =>
          item.path !== path &&
          item.path.startsWith(path) &&
          (currentPath === item.path || currentPath.startsWith(`${item.path}/`))
      );
      return !moreSpecificExists;
    }

    return false;
  }

  function toggleTheme() {
    themeStore.toggleTheme();

    // Announce theme change for screen readers
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      const announcement = `Theme changed to ${$isDarkMode ? 'light' : 'dark'} mode`;
      const utterance = new SpeechSynthesisUtterance(announcement);
      utterance.volume = 0; // Silent announcement
      window.speechSynthesis.speak(utterance);
    }
  }
</script>

<!-- Fixed bottom navigation for mobile -->
<nav class="mobile-nav" id="mobile-navigation" aria-label="Main navigation">
  {#each navItems as item}
    <a
      href={item.path}
      class="nav-item"
      class:active={isActive(item.path)}
      aria-current={isActive(item.path) ? 'page' : undefined}
    >
      <span class="icon" aria-hidden="true">{item.icon}</span>
      <span class="label">{item.label}</span>
    </a>
  {/each}

  <!-- Mobile Theme Toggle -->
  {#if config.features.DARK_MODE}
    <button
      class="nav-item theme-toggle"
      on:click={toggleTheme}
      aria-label={$isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      title={$isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      type="button"
    >
      <span class="icon" aria-hidden="true">
        {$isDarkMode ? '☀️' : '🌙'}
      </span>
      <span class="label">Theme</span>
    </button>
  {/if}
</nav>

<style>
  .mobile-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    background: var(--color-background);
    border-top: 1px solid var(--color-border);
    min-height: 60px; /* Above 44px touch target requirement */
    z-index: 1000;
    padding: 0;
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  }

  .nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    color: var(--color-text-muted);
    padding: 8px 4px;
    min-height: 44px; /* Touch target minimum */
    transition: all 0.2s ease;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }

  .nav-item:hover,
  .nav-item:focus {
    background-color: var(--color-background-tertiary);
    outline: none;
  }

  .nav-item.active {
    color: var(--color-primary);
    background-color: var(--color-primary-light);
  }

  /* Theme toggle button styles */
  .nav-item.theme-toggle {
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
  }

  .nav-item.theme-toggle:hover,
  .nav-item.theme-toggle:focus {
    background-color: var(--color-background-tertiary);
  }

  .nav-item.theme-toggle:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .nav-item.theme-toggle:active {
    transform: scale(0.95);
    transition: transform 0.1s ease;
  }

  .icon {
    font-size: 20px;
    margin-bottom: 2px;
    line-height: 1;
  }

  .label {
    font-size: 11px;
    font-weight: 500;
    line-height: 1;
    text-align: center;
  }

  /* Responsive adjustments */
  @media (max-width: 360px) {
    .label {
      font-size: 10px;
    }
    .icon {
      font-size: 18px;
    }
  }

  @media (min-width: 768px) {
    .mobile-nav {
      display: none; /* Hide on desktop - will be replaced with desktop nav later */
    }
  }
</style>
