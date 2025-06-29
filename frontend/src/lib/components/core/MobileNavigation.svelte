<script lang="ts">
  import { page } from '$app/stores';
  import type { NavItem } from '$types/navigation.js';

  const navItems: NavItem[] = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/products/new', label: 'New Product', icon: '➕' },
    { path: '/products', label: 'Products', icon: '📦' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  $: currentPath = $page.url.pathname;

  function isActive(path: string): boolean {
    if (path === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(path);
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
