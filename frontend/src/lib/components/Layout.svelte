<script lang="ts">
  import { isAuthenticated } from '$lib/stores/auth';
  import UserProfile from './auth/UserProfile.svelte';
  import AuthModal from './auth/AuthModal.svelte';
  import Button from './ui/Button.svelte';

  export let title = 'IntelliPost AI';

  // Auth modal state
  let showAuthModal = false;
  let authModalMode: 'login' | 'register' = 'login';

  // Handle auth actions
  function showLogin() {
    authModalMode = 'login';
    showAuthModal = true;
  }

  function showRegister() {
    authModalMode = 'register';
    showAuthModal = true;
  }

  function handleAuthSuccess() {
    showAuthModal = false;
  }

  function handleAuthModalClose() {
    showAuthModal = false;
  }

  function handleLogout() {
    // Handled by UserProfile component and auth store
  }

  function handleSettings() {
    // TODO: Navigate to settings page
    console.log('Navigate to settings');
  }
</script>

<!-- Skip Navigation Links -->
<div class="skip-links">
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <a href="#navigation" class="skip-link">Skip to navigation</a>
</div>

<div class="focus-within-highlight">
  <header id="navigation" class="landmark header">
    <div class="header__content">
      <h1 class="header__title animate-in">{title}</h1>

      <div class="header__auth">
        {#if $isAuthenticated}
          <UserProfile
            on:logout={handleLogout}
            on:settings={handleSettings}
          />
        {:else}
          <div class="header__auth-buttons">
            <Button
              variant="ghost"
              size="small"
              on:click={showLogin}
            >
              Sign in
            </Button>
            <Button
              variant="primary"
              size="small"
              on:click={showRegister}
            >
              Get started
            </Button>
          </div>
        {/if}
      </div>
    </div>
  </header>

  <main id="main-content" class="landmark focus-group">
    <slot />
  </main>
</div>

<!-- Auth Modal -->
<AuthModal
  isOpen={showAuthModal}
  initialMode={authModalMode}
  on:authSuccess={handleAuthSuccess}
  on:close={handleAuthModalClose}
/>

<style>
  .header {
    border-bottom: 1px solid var(--color-border-secondary);
    background-color: var(--color-surface-primary);
    position: sticky;
    top: 0;
    z-index: 40;
    backdrop-filter: blur(8px);
  }

  .header__content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-4) var(--spacing-6);
    max-width: 1200px;
    margin: 0 auto;
    gap: var(--spacing-4);
  }

  .header__title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary-600);
    margin: 0;
    line-height: 1;
  }

  .header__auth {
    display: flex;
    align-items: center;
  }

  .header__auth-buttons {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .header__content {
      padding: var(--spacing-3) var(--spacing-4);
    }

    .header__title {
      font-size: var(--font-size-lg);
    }

    .header__auth-buttons {
      gap: var(--spacing-2);
    }
  }

  /* Extra small screens */
  @media (max-width: 480px) {
    .header__content {
      padding: var(--spacing-3);
    }

    .header__title {
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-semibold);
    }
  }

  /* Focus enhancement */
  .header__content:focus-within {
    box-shadow: inset 0 0 0 2px var(--color-primary-200);
  }

  /* Animation support */
  .header {
    transition: box-shadow var(--transition-fast);
  }

  .header:has(.header__auth-buttons button:focus-visible),
  .header:has(.user-profile__trigger:focus-visible) {
    box-shadow: inset 0 -2px 0 var(--color-primary-500);
  }
</style>
