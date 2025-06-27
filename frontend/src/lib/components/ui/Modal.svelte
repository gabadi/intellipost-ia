<script lang="ts">
  export let open: boolean = false;
  export let title: string = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | 'full' = 'md';
  export let variant: 'default' | 'danger' | 'success' | 'warning' | 'info' = 'default';
  export let closable: boolean = true;
  export let closeOnBackdrop: boolean = true;
  export let closeOnEscape: boolean = true;

  // Event handlers
  export let onClose: (() => void) | undefined = undefined;
  export let onOpen: (() => void) | undefined = undefined;

  let dialogElement: HTMLDialogElement;

  $: if (open) {
    if (dialogElement) {
      dialogElement.showModal();

      document.body.style.overflow = 'hidden';
      onOpen?.();
    }
  } else {
    if (dialogElement) {
      dialogElement.close();

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

    document.body.style.overflow = '';
    onClose?.();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<dialog
  bind:this={dialogElement}
  class="modal modal--{size}"
  class:modal--danger={variant === 'danger'}
  class:modal--success={variant === 'success'}
  class:modal--warning={variant === 'warning'}
  class:modal--info={variant === 'info'}
  on:click={handleBackdropClick}
  on:close={handleDialogClose}
>
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="modal__content" on:click|stopPropagation>
    <header class="modal__header">
      {#if title}
        <h2 class="modal__title">{title}</h2>
      {:else}
        <slot name="title" />
      {/if}

      {#if closable}
        <button type="button" class="modal__close" on:click={handleClose} aria-label="Close modal">
          <svg
            class="modal__close-icon"
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

    <div class="modal__body">
      <slot />
    </div>

    <footer class="modal__footer">
      <slot name="footer" />
    </footer>
  </div>
</dialog>

<!-- No component-specific styles needed - handled by semantic CSS classes -->
