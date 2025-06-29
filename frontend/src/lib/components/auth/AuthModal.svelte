<!--
  Authentication modal component with login/register forms.

  Features:
  - Single-screen auth with smooth transitions
  - Modal overlay with proper focus management
  - Mobile-first responsive design
  - Accessibility support (ARIA, keyboard navigation)
  - Auto-close on successful authentication
-->

<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import type { AuthMode, User } from '$types/auth';
  import LoginForm from './LoginForm.svelte';
  import RegisterForm from './RegisterForm.svelte';

  // Props
  export let isOpen: boolean = false;
  export let initialMode: AuthMode = 'login';
  export let redirectTo: string | undefined = undefined;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    close: void;
    success: { user: User; mode: AuthMode };
    error: { error: string; mode: AuthMode };
  }>();

  // State
  let currentMode: AuthMode = initialMode;
  let modalElement: HTMLElement;
  let previousActiveElement: HTMLElement | null = null;

  // Handle successful authentication
  function handleAuthSuccess(event: CustomEvent<{ user: User }>) {
    const { user } = event.detail;
    dispatch('success', { user, mode: currentMode });
    closeModal();
  }

  // Handle authentication error
  function handleAuthError(event: CustomEvent<{ error: string }>) {
    const { error } = event.detail;
    dispatch('error', { error, mode: currentMode });
  }

  // Switch between login and register modes
  function switchMode() {
    currentMode = currentMode === 'login' ? 'register' : 'login';
  }

  // Close modal
  function closeModal() {
    isOpen = false;
    dispatch('close');
  }

  // Handle backdrop click
  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  }

  // Handle escape key
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      closeModal();
    }
  }

  // Focus management
  function manageFocus() {
    if (isOpen) {
      // Store currently focused element
      previousActiveElement = document.activeElement as HTMLElement;

      // Focus the modal
      setTimeout(() => {
        modalElement?.focus();
      }, 100);
    } else {
      // Restore focus to previously focused element
      if (previousActiveElement) {
        previousActiveElement.focus();
        previousActiveElement = null;
      }
    }
  }

  // Trap focus within modal
  function trapFocus(event: KeyboardEvent) {
    if (!isOpen || event.key !== 'Tab') return;

    const focusableElements = modalElement.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }

  // Reactive effects
  $: if (isOpen !== undefined) {
    manageFocus();
  }

  $: currentMode = initialMode;

  // Prevent body scroll when modal is open
  $: if (typeof document !== 'undefined') {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }

  onMount(() => {
    return () => {
      // Cleanup on component destroy
      if (typeof document !== 'undefined') {
        document.body.style.overflow = '';
      }
    };
  });
</script>

<!-- Modal backdrop -->
{#if isOpen}
  <div
    class="modal-backdrop"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    transition:fade={{ duration: 200 }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="auth-modal-title"
    tabindex="0"
  >
    <!-- Modal content -->
    <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
    <div
      class="modal-content"
      bind:this={modalElement}
      tabindex="-1"
      on:keydown={trapFocus}
      transition:fly={{ y: 20, duration: 300 }}
      role="document"
    >
      <!-- Close button -->
      <button
        type="button"
        class="close-button"
        on:click={closeModal}
        aria-label="Close authentication modal"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>

      <!-- Modal body -->
      <div class="modal-body">
        {#if currentMode === 'login'}
          <LoginForm
            {redirectTo}
            on:success={handleAuthSuccess}
            on:error={handleAuthError}
            on:switchToRegister={switchMode}
          />
        {:else}
          <RegisterForm
            {redirectTo}
            on:success={handleAuthSuccess}
            on:error={handleAuthError}
            on:switchToLogin={switchMode}
          />
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-4);
    overflow-y: auto;
  }

  .modal-content {
    position: relative;
    background: var(--color-background);
    border-radius: var(--border-radius-lg);
    box-shadow:
      0 20px 25px -5px rgba(0, 0, 0, 0.1),
      0 10px 10px -5px rgba(0, 0, 0, 0.04);
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    overflow-y: auto;
    padding: var(--spacing-6);
    margin: auto;
    outline: none;
  }

  .close-button {
    position: absolute;
    top: var(--spacing-4);
    right: var(--spacing-4);
    width: 44px; /* Mobile-optimized touch target */
    height: 44px;
    border: none;
    background: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    border-radius: var(--border-radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    z-index: 1;
  }

  .close-button:hover {
    background: var(--color-background-hover);
    color: var(--color-text);
  }

  .close-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
  }

  .modal-body {
    padding-top: var(--spacing-2);
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .modal-backdrop {
      padding: var(--spacing-2);
      align-items: flex-start;
      padding-top: var(--spacing-8);
    }

    .modal-content {
      padding: var(--spacing-5);
      border-radius: var(--border-radius-md);
      max-height: calc(100vh - var(--spacing-16));
    }

    .close-button {
      top: var(--spacing-3);
      right: var(--spacing-3);
    }
  }

  /* Tablet styles */
  @media (min-width: 768px) and (max-width: 1023px) {
    .modal-content {
      max-width: 520px;
    }
  }

  /* Desktop styles */
  @media (min-width: 1024px) {
    .modal-backdrop {
      padding: var(--spacing-6);
    }

    .modal-content {
      max-width: 480px;
      padding: var(--spacing-8);
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .modal-content {
      border: 2px solid var(--color-border);
    }

    .close-button {
      border: 1px solid var(--color-border);
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .modal-backdrop {
      transition: none;
    }

    .modal-content {
      transition: none;
    }

    .close-button {
      transition: none;
    }
  }

  /* Print styles */
  @media print {
    .modal-backdrop {
      display: none;
    }
  }
</style>
