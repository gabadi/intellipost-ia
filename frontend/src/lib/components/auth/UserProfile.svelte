<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { authStore, currentUser, isLoading } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    logout: void;
    settings: void;
  }>();

  // Local state
  let isMenuOpen = false;
  let isLoggingOut = false;

  // Handle logout
  async function handleLogout() {
    isLoggingOut = true;
    try {
      await authStore.logout();
      dispatch('logout');
    } finally {
      isLoggingOut = false;
      isMenuOpen = false;
    }
  }

  // Handle settings
  function handleSettings() {
    dispatch('settings');
    isMenuOpen = false;
  }

  // Toggle menu
  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  // Close menu when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.user-profile')) {
      isMenuOpen = false;
    }
  }

  // Generate user initials for avatar
  function getUserInitials(email: string): string {
    if (!email) return 'U';
    const parts = email.split('@')[0].split('.');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return email[0].toUpperCase();
  }

  // Handle keyboard navigation
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      isMenuOpen = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeydown} />

<div class="user-profile">
  {#if $currentUser}
    <button
      type="button"
      class="user-profile__trigger"
      class:user-profile__trigger--active={isMenuOpen}
      on:click={toggleMenu}
      aria-expanded={isMenuOpen}
      aria-haspopup="menu"
      aria-label="User menu for {$currentUser.email}"
      disabled={$isLoading || isLoggingOut}
    >
      <div class="user-profile__avatar">
        <span class="user-profile__initials">
          {getUserInitials($currentUser.email)}
        </span>
      </div>
      <div class="user-profile__info">
        <span class="user-profile__email">{$currentUser.email}</span>
        <span class="user-profile__status">
          {$isLoading ? 'Loading...' : 'Online'}
        </span>
      </div>
      <svg
        class="user-profile__chevron"
        class:user-profile__chevron--rotated={isMenuOpen}
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M4 6L8 10L12 6"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>

    {#if isMenuOpen}
      <div class="user-profile__menu" role="menu">
        <div class="user-profile__menu-header">
          <div class="user-profile__menu-avatar">
            <span class="user-profile__menu-initials">
              {getUserInitials($currentUser.email)}
            </span>
          </div>
          <div class="user-profile__menu-info">
            <span class="user-profile__menu-email">{$currentUser.email}</span>
            <span class="user-profile__menu-id">ID: {$currentUser.user_id.slice(0, 8)}...</span>
          </div>
        </div>

        <div class="user-profile__menu-divider"></div>

        <div class="user-profile__menu-items">
          <button
            type="button"
            class="user-profile__menu-item"
            role="menuitem"
            on:click={handleSettings}
            disabled={$isLoading || isLoggingOut}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z"
                stroke="currentColor"
                stroke-width="1.5"
              />
              <path
                d="M13.4 8C13.4 8.3 13.1 8.6 12.8 8.7L11.8 9L11.5 9.7L12.2 10.5C12.4 10.8 12.4 11.2 12.2 11.4L11.4 12.2C11.2 12.4 10.8 12.4 10.5 12.2L9.7 11.5L9 11.8L8.7 12.8C8.6 13.1 8.3 13.4 8 13.4H7C6.7 13.4 6.4 13.1 6.3 12.8L6 11.8L5.3 11.5L4.5 12.2C4.2 12.4 3.8 12.4 3.6 12.2L2.8 11.4C2.6 11.2 2.6 10.8 2.8 10.5L3.5 9.7L3.2 9L2.2 8.7C1.9 8.6 1.6 8.3 1.6 8V7C1.6 6.7 1.9 6.4 2.2 6.3L3.2 6L3.5 5.3L2.8 4.5C2.6 4.2 2.6 3.8 2.8 3.6L3.6 2.8C3.8 2.6 4.2 2.6 4.5 2.8L5.3 3.5L6 3.2L6.3 2.2C6.4 1.9 6.7 1.6 7 1.6H8C8.3 1.6 8.6 1.9 8.7 2.2L9 3.2L9.7 3.5L10.5 2.8C10.8 2.6 11.2 2.6 11.4 2.8L12.2 3.6C12.4 3.8 12.4 4.2 12.2 4.5L11.5 5.3L11.8 6L12.8 6.3C13.1 6.4 13.4 6.7 13.4 7V8Z"
                stroke="currentColor"
                stroke-width="1.5"
              />
            </svg>
            <span>Account Settings</span>
          </button>

          <button
            type="button"
            class="user-profile__menu-item user-profile__menu-item--danger"
            role="menuitem"
            on:click={handleLogout}
            disabled={$isLoading || isLoggingOut}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M6 2H3C2.44772 2 2 2.44772 2 3V13C2 13.5523 2.44772 14 3 14H6"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
              <path
                d="M11 5L14 8L11 11"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M14 8H6"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
            <span>{isLoggingOut ? 'Signing out...' : 'Sign out'}</span>
          </button>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .user-profile {
    position: relative;
    display: inline-block;
  }

  .user-profile__trigger {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    padding: var(--spacing-2);
    background: none;
    border: 1px solid var(--color-border-secondary);
    border-radius: var(--border-radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast);
    color: var(--color-text-primary);
    min-width: 0; /* Prevent overflow */
  }

  .user-profile__trigger:hover:not(:disabled) {
    border-color: var(--color-border-primary);
    background-color: var(--color-surface-secondary);
  }

  .user-profile__trigger:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 1px;
  }

  .user-profile__trigger--active {
    border-color: var(--color-primary-500);
    background-color: var(--color-primary-50);
  }

  .user-profile__trigger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .user-profile__avatar {
    width: 32px;
    height: 32px;
    border-radius: var(--border-radius-full);
    background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .user-profile__initials {
    color: white;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    line-height: 1;
  }

  .user-profile__info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    min-width: 0;
    flex: 1;
  }

  .user-profile__email {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }

  .user-profile__status {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    line-height: 1;
  }

  .user-profile__chevron {
    color: var(--color-text-tertiary);
    transition: transform var(--transition-fast);
    flex-shrink: 0;
  }

  .user-profile__chevron--rotated {
    transform: rotate(180deg);
  }

  .user-profile__menu {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: var(--spacing-2);
    background: var(--color-surface-primary);
    border: 1px solid var(--color-border-secondary);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-lg);
    z-index: 50;
    min-width: 280px;
    overflow: hidden;
    animation: slideIn 0.15s ease-out;
  }

  .user-profile__menu-header {
    padding: var(--spacing-4);
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    background-color: var(--color-surface-secondary);
  }

  .user-profile__menu-avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--border-radius-full);
    background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .user-profile__menu-initials {
    color: white;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    line-height: 1;
  }

  .user-profile__menu-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-1);
    min-width: 0;
    flex: 1;
  }

  .user-profile__menu-email {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-profile__menu-id {
    font-size: var(--font-size-xs);
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
  }

  .user-profile__menu-divider {
    height: 1px;
    background-color: var(--color-border-secondary);
  }

  .user-profile__menu-items {
    padding: var(--spacing-2);
  }

  .user-profile__menu-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    padding: var(--spacing-3);
    background: none;
    border: none;
    border-radius: var(--border-radius-md);
    cursor: pointer;
    color: var(--color-text-primary);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    transition: background-color var(--transition-fast);
    text-align: left;
  }

  .user-profile__menu-item:hover:not(:disabled) {
    background-color: var(--color-surface-secondary);
  }

  .user-profile__menu-item:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 1px;
  }

  .user-profile__menu-item:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .user-profile__menu-item--danger {
    color: var(--color-error-600);
  }

  .user-profile__menu-item--danger:hover:not(:disabled) {
    background-color: var(--color-error-50);
  }

  .user-profile__menu-item--danger:focus-visible {
    outline-color: var(--color-error-500);
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .user-profile__trigger {
      padding: var(--spacing-2);
    }

    .user-profile__info {
      display: none; /* Hide email on mobile to save space */
    }

    .user-profile__menu {
      right: -var(--spacing-2);
      min-width: 260px;
    }

    .user-profile__email {
      max-width: 120px;
    }
  }

  /* Animation */
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-8px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .user-profile__menu {
      box-shadow: var(--shadow-lg-dark);
    }
  }
</style>
