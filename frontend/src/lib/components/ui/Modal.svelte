<script lang="ts">
  export let open: boolean = false;
  export let title: string = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let closable: boolean = true;
  export let closeOnBackdrop: boolean = true;
  export let closeOnEscape: boolean = true;

  // Event handlers
  export let onClose: (() => void) | undefined = undefined;
  export let onOpen: (() => void) | undefined = undefined;

  let dialogElement: HTMLDialogElement;

  $: sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  };

  $: if (open) {
    if (dialogElement) {
      dialogElement.showModal();
      // eslint-disable-next-line no-undef
      document.body.style.overflow = 'hidden';
      onOpen?.();
    }
  } else {
    if (dialogElement) {
      dialogElement.close();
      // eslint-disable-next-line no-undef
      document.body.style.overflow = '';
    }
  }

  function handleClose() {
    if (closable) {
      open = false;
      onClose?.();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (closeOnBackdrop && event.target === dialogElement) {
      handleClose();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (closeOnEscape && event.key === 'Escape') {
      event.preventDefault();
      handleClose();
    }
  }

  function handleDialogClose() {
    open = false;
    // eslint-disable-next-line no-undef
    document.body.style.overflow = '';
    onClose?.();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<dialog
  bind:this={dialogElement}
  class="modal {sizeClasses[size]}"
  on:click={handleBackdropClick}
  on:close={handleDialogClose}
>
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="modal-content" on:click|stopPropagation>
    <header class="modal-header">
      {#if title}
        <h2 class="modal-title">{title}</h2>
      {:else}
        <slot name="title" />
      {/if}

      {#if closable}
        <button type="button" class="close-button" on:click={handleClose} aria-label="Close modal">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      {/if}
    </header>

    <div class="modal-body">
      <slot />
    </div>

    <footer class="modal-footer">
      <slot name="footer" />
    </footer>
  </div>
</dialog>

<style>
  .modal {
    padding: 0;
    margin: auto;
    border: none;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    background: transparent;
    max-height: calc(100vh - var(--space-8));
    width: calc(100vw - var(--space-8));
  }

  .modal::backdrop {
    background-color: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
  }

  .modal-content {
    background: white;
    border-radius: var(--radius-lg);
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - var(--space-8));
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6);
    border-bottom: 1px solid var(--color-gray-200);
    flex-shrink: 0;
  }

  .modal-title {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-gray-900);
    margin: 0;
    line-height: var(--leading-tight);
  }

  .close-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--touch-target-min);
    height: var(--touch-target-min);
    border: none;
    background: none;
    color: var(--color-gray-400);
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .close-button:hover {
    color: var(--color-gray-600);
    background-color: var(--color-gray-100);
  }

  .close-button:focus {
    outline: none;
    color: var(--color-gray-600);
    background-color: var(--color-gray-100);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .modal-body {
    padding: var(--space-6);
    flex: 1;
    overflow-y: auto;
  }

  .modal-footer {
    padding: var(--space-6);
    border-top: 1px solid var(--color-gray-200);
    flex-shrink: 0;
  }

  .modal-footer:empty {
    display: none;
  }

  /* Size variations */
  .max-w-sm {
    max-width: 384px;
  }

  .max-w-md {
    max-width: 448px;
  }

  .max-w-lg {
    max-width: 512px;
  }

  .max-w-xl {
    max-width: 576px;
  }

  /* Mobile responsiveness */
  @media (max-width: 640px) {
    .modal {
      width: calc(100vw - var(--space-4));
      max-height: calc(100vh - var(--space-4));
    }

    .modal-header,
    .modal-body,
    .modal-footer {
      padding: var(--space-4);
    }

    .modal-title {
      font-size: var(--text-lg);
    }
  }
</style>
