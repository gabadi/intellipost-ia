<script lang="ts">
  import { onMount } from 'svelte';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import AuthModal from './AuthModal.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';

  // Props
  export let requireAuth = false;
  export let fallbackMode: 'login' | 'register' = 'login';
  export let showSpinner = true;

  // Local state
  let isInitialized = false;
  let showAuthModal = false;

  onMount(() => {
    // Initialize auth state
    authStore.init();
    isInitialized = true;

    // Show auth modal if authentication is required and user is not authenticated
    if (requireAuth && !$isAuthenticated) {
      showAuthModal = true;
    }
  });

  // Reactive statement to handle auth state changes
  $: if (isInitialized && requireAuth && !$isAuthenticated) {
    showAuthModal = true;
  }

  // Handle successful authentication
  function handleAuthSuccess() {
    showAuthModal = false;
  }

  // Handle auth modal close
  function handleAuthModalClose() {
    if (requireAuth && !$isAuthenticated) {
      // If auth is required and user is not authenticated, keep modal open
      return;
    }
    showAuthModal = false;
  }
</script>

{#if !isInitialized && showSpinner}
  <div class="auth-guard__loading">
    <LoadingSpinner size="large" />
    <p class="auth-guard__loading-text">Initializing authentication...</p>
  </div>
{:else if requireAuth && !$isAuthenticated}
  <!-- Show auth modal for required authentication -->
  <AuthModal
    isOpen={showAuthModal}
    initialMode={fallbackMode}
    on:authSuccess={handleAuthSuccess}
    on:close={handleAuthModalClose}
  />

  <!-- Optional: Show a message while auth modal is open -->
  <div class="auth-guard__required">
    <div class="auth-guard__required-content">
      <h2 class="auth-guard__required-title">Authentication Required</h2>
      <p class="auth-guard__required-message">
        Please sign in to access this content.
      </p>
    </div>
  </div>
{:else}
  <!-- Render children when authenticated or auth not required -->
  <slot />

  <!-- Show auth modal when explicitly requested -->
  {#if showAuthModal}
    <AuthModal
      isOpen={showAuthModal}
      initialMode={fallbackMode}
      on:authSuccess={handleAuthSuccess}
      on:close={handleAuthModalClose}
    />
  {/if}
{/if}

<style>
  .auth-guard__loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    gap: var(--spacing-4);
    padding: var(--spacing-8);
  }

  .auth-guard__loading-text {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    margin: 0;
  }

  .auth-guard__required {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    padding: var(--spacing-8);
  }

  .auth-guard__required-content {
    text-align: center;
    max-width: 400px;
  }

  .auth-guard__required-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-3) 0;
  }

  .auth-guard__required-message {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    line-height: var(--line-height-relaxed);
    margin: 0;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .auth-guard__loading {
      min-height: 150px;
      padding: var(--spacing-6);
    }

    .auth-guard__required {
      min-height: 300px;
      padding: var(--spacing-6);
    }

    .auth-guard__required-title {
      font-size: var(--font-size-lg);
    }

    .auth-guard__required-message {
      font-size: var(--font-size-sm);
    }
  }
</style>
