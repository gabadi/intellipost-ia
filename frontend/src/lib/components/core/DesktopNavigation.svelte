<script lang="ts">
  import { page } from '$app/stores';
  import type { NavItem } from '$types/navigation.js';

  const navItems: NavItem[] = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/products/new', label: 'Create Product', icon: '➕' },
    { path: '/products', label: 'Products', icon: '📦' },
  ];

  $: currentPath = $page.url.pathname;

  function isActive(path: string): boolean {
    if (path === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(path);
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
    <div class="user-section">
      <div class="user-avatar" aria-hidden="true">👤</div>
      <div class="user-info">
        <div class="user-name">User</div>
        <div class="user-status">Online</div>
      </div>
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
    background: white;
    border-right: 1px solid var(--color-gray-200);
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
    border-bottom: 1px solid var(--color-gray-100);
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
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-gray-900);
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
    color: var(--color-gray-700);
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    min-height: var(--touch-target-min);
    position: relative;
  }

  .nav-item:hover {
    background: var(--color-gray-50);
    color: var(--color-gray-900);
  }

  .nav-item:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .nav-item.active {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: 500;
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
    font-size: var(--text-lg);
    min-width: 24px;
    text-align: center;
  }

  .nav-label {
    font-size: var(--text-base);
    line-height: var(--leading-normal);
  }

  .nav-footer {
    padding: var(--space-4);
    border-top: 1px solid var(--color-gray-100);
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    background: var(--color-gray-50);
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
    font-size: var(--text-base);
  }

  .user-info {
    flex: 1;
    min-width: 0;
  }

  .user-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-900);
    line-height: var(--leading-tight);
  }

  .user-status {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
    line-height: var(--leading-tight);
  }

  /* Dark mode preparation */
  @media (prefers-color-scheme: dark) {
    .desktop-nav {
      background: var(--color-gray-900);
      border-right-color: var(--color-gray-700);
    }

    .nav-header {
      border-bottom-color: var(--color-gray-700);
    }

    .logo-text {
      color: white;
    }

    .nav-item {
      color: var(--color-gray-300);
    }

    .nav-item:hover {
      background: var(--color-gray-800);
      color: white;
    }

    .nav-item.active {
      background: var(--color-primary-transparent);
      color: var(--color-primary-light);
    }

    .nav-footer {
      border-top-color: var(--color-gray-700);
    }

    .user-section {
      background: var(--color-gray-800);
    }

    .user-name {
      color: white;
    }

    .user-status {
      color: var(--color-gray-400);
    }
  }

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
