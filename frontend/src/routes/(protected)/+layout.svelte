<!--
  Protected layout for authenticated routes

  Automatically redirects to login if user is not authenticated
  and initializes auth store on mount
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';

  let isInitialized = false;

  $: authState = $authStore;

  onMount(async () => {
    // Initialize auth store from localStorage
    authStore.init();

    // Small delay to allow store initialization
    await new Promise(resolve => setTimeout(resolve, 100));

    isInitialized = true;

    // If not authenticated, redirect to login
    if (!authState.isAuthenticated) {
      const currentPath = $page.url.pathname;
      const loginUrl = `/auth/login${currentPath !== '/' ? `?redirect=${encodeURIComponent(currentPath)}` : ''}`;
      goto(loginUrl);
    }
  });

  // Watch for auth state changes
  $: {
    if (isInitialized && !authState.isAuthenticated) {
      const currentPath = $page.url.pathname;
      const loginUrl = `/auth/login${currentPath !== '/' ? `?redirect=${encodeURIComponent(currentPath)}` : ''}`;
      goto(loginUrl);
    }
  }
</script>

{#if !isInitialized || (isInitialized && authState.isLoading)}
  <!-- Loading state while checking authentication -->
  <div class="auth-loading">
    <LoadingSpinner size="lg" />
    <p>Checking authentication...</p>
  </div>
{:else if authState.isAuthenticated}
  <!-- Render protected content -->
  <slot />
{:else}
  <!-- This should not be visible due to redirect, but just in case -->
  <div class="auth-loading">
    <p>Redirecting to login...</p>
  </div>
{/if}

<style>
  .auth-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1rem;
    padding: 2rem;
  }

  .auth-loading p {
    color: #6b7280;
    margin: 0;
    font-size: 0.875rem;
  }
</style>
