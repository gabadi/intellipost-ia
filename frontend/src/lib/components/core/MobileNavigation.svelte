<script lang="ts">
  import { page } from '$app/stores';
  import type { NavItem } from '$types/navigation.js';
  import { theme, type Theme } from '$stores/theme.js';
  import { authStore } from '$lib/stores/auth';

  const navItems: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { path: '/products/new', label: 'New Product', icon: '➕' },
    { path: '/products', label: 'Products', icon: '📦' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

  $: currentPath = $page.url.pathname;

  function isActive(path: string): boolean {
    if (path === '/dashboard') {
      return currentPath === '/dashboard' || currentPath === '/';
    }
    // Exact match for specific paths to avoid conflicts
    if (path === '/products/new') {
      return currentPath === '/products/new';
    }
    if (path === '/products') {
      return (
        currentPath === '/products' ||
        (currentPath.startsWith('/products/') && currentPath !== '/products/new')
      );
    }
    // For other paths, use startsWith but exclude more specific matches
    return currentPath.startsWith(path) && currentPath !== '/products/new';
  }

  async function handleLogout() {
    await authStore.logout();
  }

  // Theme management
  let currentTheme: Theme;
  $: currentTheme = $theme;

  const themeOptions: Array<{ value: Theme; label: string; icon: string }> = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'auto', label: 'Auto', icon: '🔄' },
  ];

  function getNextTheme(current: Theme): Theme {
    const currentIndex = themeOptions.findIndex(t => t.value === current);
    const nextIndex = (currentIndex + 1) % themeOptions.length;
    return themeOptions[nextIndex].value;
  }

  function handleThemeToggle() {
    const nextTheme = getNextTheme(currentTheme);
    theme.setTheme(nextTheme);
  }

  $: currentThemeInfo = themeOptions.find(t => t.value === currentTheme) || themeOptions[0];
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

  <!-- Theme toggle button -->
  <button
    class="nav-item theme-toggle"
    on:click={handleThemeToggle}
    aria-label="Toggle theme: {currentThemeInfo.label}"
    type="button"
  >
    <span class="icon" aria-hidden="true">{currentThemeInfo.icon}</span>
    <span class="label">{currentThemeInfo.label}</span>
  </button>

  <!-- Logout button -->
  <button class="nav-item logout-btn" on:click={handleLogout} aria-label="Logout" type="button">
    <span class="icon" aria-hidden="true">🚪</span>
    <span class="label">Logout</span>
  </button>
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
    box-shadow: var(--shadow-lg);
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
    transition: all var(--duration-200) var(--ease-out);
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }

  .nav-item:hover,
  .nav-item:focus {
    background-color: var(--color-background-secondary);
    outline: none;
  }

  .nav-item.active {
    color: var(--color-primary);
    background-color: var(--color-primary-light);
  }

  .nav-item.theme-toggle,
  .nav-item.logout-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
  }

  .nav-item.theme-toggle:hover,
  .nav-item.theme-toggle:focus,
  .nav-item.logout-btn:hover,
  .nav-item.logout-btn:focus {
    background-color: var(--color-background-secondary);
    outline: none;
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
