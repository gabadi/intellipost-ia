<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import LoginForm from './LoginForm.svelte';
  import RegisterForm from './RegisterForm.svelte';

  // Props
  export let isOpen = false;
  export let initialMode: 'login' | 'register' = 'login';

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    close: void;
    authSuccess: { mode: 'login' | 'register' };
  }>();

  // Local state
  let currentMode = initialMode;

  // Watch for prop changes
  $: if (isOpen) {
    currentMode = initialMode;
  }

  // Handle successful authentication
  function handleAuthSuccess() {
    dispatch('authSuccess', { mode: currentMode });
    dispatch('close');
  }

  // Handle mode switching
  function handleSwitchToLogin() {
    currentMode = 'login';
  }

  function handleSwitchToRegister() {
    currentMode = 'register';
  }

  // Handle modal close
  function handleClose() {
    dispatch('close');
  }
</script>

<Modal
  {isOpen}
  title={currentMode === 'login' ? 'Sign In' : 'Create Account'}
  on:close={handleClose}
  maxWidth="480px"
  closeOnEscape={true}
  closeOnClickOutside={true}
>
  <div class="auth-modal">
    {#if currentMode === 'login'}
      <LoginForm
        on:success={handleAuthSuccess}
        on:switchToRegister={handleSwitchToRegister}
      />
    {:else}
      <RegisterForm
        on:success={handleAuthSuccess}
        on:switchToLogin={handleSwitchToLogin}
      />
    {/if}
  </div>
</Modal>

<style>
  .auth-modal {
    padding: var(--spacing-6);
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .auth-modal {
      padding: var(--spacing-4);
      min-height: 350px;
    }
  }

  /* Ensure proper focus management */
  .auth-modal :global(.auth-form__form) {
    width: 100%;
  }

  /* Animation for form switching */
  .auth-modal :global(.auth-form) {
    animation: fadeIn 0.2s ease-in-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
