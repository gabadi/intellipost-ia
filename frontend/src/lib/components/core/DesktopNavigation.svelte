<script lang="ts">
  import { page } from '$app/stores';
  import type { NavItem } from '$types/navigation.js';
  import ThemeToggle from '$components/ui/ThemeToggle.svelte';

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
</script>

<!-- Desktop sidebar navigation -->
<nav class="desktop-nav" aria-label="Main navigation">
  <div class="nav-header">
    <div class="logo">
      <span class="logo-icon">🚀</span>
      <span class="logo-text">IntelliPost AI</span>
    </div>
  </div>

  <div class="nav-content">
    <ul class="nav-list" role="list">
      {#each navItems as item}
        <li class="nav-item-wrapper">
          <a
            href={item.path}
            class="nav-item"
            class:active={isActive(item.path)}
            aria-current={isActive(item.path) ? 'page' : undefined}
          >
            <span class="nav-icon" aria-hidden="true">{item.icon}</span>
            <span class="nav-label">{item.label}</span>
          </a>
        </li>
      {/each}
    </ul>
  </div>

  <div class="nav-footer">
    <!-- Theme Toggle -->
    <div class="theme-section">
      <ThemeToggle />
    </div>

    <div class="user-section">
      <div class="user-avatar" aria-hidden="true">👤</div>
      <div class="user-info">
        <div class="user-name">Admin User</div>
        <div class="user-status">Online</div>
      </div>
      <button
        class="logout-button"
        on:click={() => (window.location.href = '/auth/logout')}
        aria-label="Logout"
        title="Logout"
      >
        🚪
      </button>
    </div>
  </div>
</nav>

<style>
  .desktop-nav {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 280px;
    height: 100vh;
    background: var(--color-background);
    border-right: 1px solid var(--color-border);
    flex-direction: column;
    z-index: 1000;
    overflow-y: auto;
  }

  @media (min-width: 768px) {
    .desktop-nav {
      display: flex;
    }
  }

  .nav-header {
    padding: var(--space-6) var(--space-4);
    border-bottom: 1px solid var(--color-border-muted);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .logo-icon {
    font-size: var(--text-2xl);
  }

  .logo-text {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
  }

  .nav-content {
    flex: 1;
    padding: var(--space-4) 0;
  }

  .nav-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .nav-item-wrapper {
    margin-bottom: var(--space-1);
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    margin: 0 var(--space-2);
    text-decoration: none;
    color: var(--color-text-secondary);
    border-radius: var(--radius-md);
    transition: all var(--duration-200) var(--ease-out);
    min-height: var(--touch-target-min);
    position: relative;
    white-space: nowrap;
  }

  .nav-item:hover {
    background: var(--color-background-secondary);
    color: var(--color-text);
  }

  .nav-item:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .nav-item.active {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: var(--font-weight-medium);
  }

  .nav-item.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 20px;
    background: var(--color-primary);
    border-radius: 0 2px 2px 0;
  }

  .nav-icon {
    font-size: var(--font-size-lg);
    min-width: 24px;
    text-align: center;
  }

  .nav-label {
    font-size: var(--font-size-base);
    line-height: var(--line-height-normal);
  }

  .nav-footer {
    padding: var(--space-4);
    border-top: 1px solid var(--color-border-muted);
  }

  .theme-section {
    margin-bottom: var(--space-3);
    display: flex;
    justify-content: center;
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    background: var(--color-background-secondary);
    border-radius: var(--radius-md);
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    background: var(--color-primary-light);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--font-size-base);
  }

  .user-info {
    flex: 1;
    min-width: 0;
  }

  .user-name {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text);
    line-height: var(--line-height-tight);
  }

  .user-status {
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    line-height: var(--line-height-tight);
  }

  .logout-button {
    background: none;
    border: none;
    font-size: var(--font-size-lg);
    cursor: pointer;
    padding: var(--space-2);
    border-radius: var(--radius-md);
    transition: background-color var(--duration-200) var(--ease-out);
    color: var(--color-text-tertiary);
  }

  .logout-button:hover {
    background: var(--color-background-tertiary);
    color: var(--color-text);
  }

  .logout-button:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  /* Dark mode styles are now handled automatically by design tokens */
  /* Removed hardcoded @media (prefers-color-scheme: dark) styles */

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .nav-item {
      transition: none;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .nav-item.active {
      background: var(--color-primary);
      color: white;
    }

    .nav-item:focus {
      outline: 3px solid var(--color-primary);
    }
  }
</style>
