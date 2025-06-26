<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled: boolean = false;
  export let loading: boolean = false;
  export let type: 'button' | 'submit' | 'reset' = 'button';
  export let href: string | undefined = undefined;
  export let fullWidth: boolean = false;

  // Event handlers
  export let onClick: ((event: MouseEvent) => void) | undefined = undefined;

  $: isLink = href !== undefined;
  $: isDisabled = disabled || loading;

  $: variantClasses = {
    primary: 'bg-primary text-white hover:bg-primary-hover focus:ring-primary',
    secondary:
      'bg-white text-gray-700 border border-gray-300 hover:border-primary hover:text-primary focus:ring-primary',
    ghost: 'bg-transparent text-primary hover:bg-primary-light focus:ring-primary',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  $: sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  };

  function handleClick(event: MouseEvent) {
    if (isDisabled) {
      event.preventDefault();
      return;
    }
    onClick?.(event);
  }
</script>

{#if isLink}
  <a
    {href}
    class="btn {variantClasses[variant]} {sizeClasses[size]}"
    class:full-width={fullWidth}
    class:disabled={isDisabled}
    aria-disabled={isDisabled}
    on:click={handleClick}
  >
    {#if loading}
      <span class="loading-spinner"></span>
    {/if}
    <slot />
  </a>
{:else}
  <button
    {type}
    class="btn {variantClasses[variant]} {sizeClasses[size]}"
    class:full-width={fullWidth}
    disabled={isDisabled}
    on:click={handleClick}
  >
    {#if loading}
      <span class="loading-spinner"></span>
    {/if}
    <slot />
  </button>
{/if}

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    font-weight: 500;
    border-radius: var(--radius-md);
    text-decoration: none;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: var(--touch-target-min);
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    border: 1px solid transparent;
  }

  .btn:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .btn.full-width {
    width: 100%;
  }

  .btn.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  /* Variant styles */
  .bg-primary {
    background-color: var(--color-primary);
  }

  .bg-primary-hover:hover {
    background-color: var(--color-primary-hover);
  }

  .bg-primary-light {
    background-color: var(--color-primary-light);
  }

  .bg-white {
    background-color: white;
  }

  .bg-transparent {
    background-color: transparent;
  }

  .text-white {
    color: white;
  }

  .text-gray-700 {
    color: var(--color-gray-700);
  }

  .text-primary {
    color: var(--color-primary);
  }

  .border {
    border-width: 1px;
  }

  .border-gray-300 {
    border-color: var(--color-gray-300);
  }

  .hover\:border-primary:hover {
    border-color: var(--color-primary);
  }

  .hover\:text-primary:hover {
    color: var(--color-primary);
  }

  .hover\:bg-primary-light:hover {
    background-color: var(--color-primary-light);
  }

  /* Size styles */
  .px-3 {
    padding-left: var(--space-3);
    padding-right: var(--space-3);
  }
  .py-2 {
    padding-top: var(--space-2);
    padding-bottom: var(--space-2);
  }
  .px-4 {
    padding-left: var(--space-4);
    padding-right: var(--space-4);
  }
  .py-3 {
    padding-top: var(--space-3);
    padding-bottom: var(--space-3);
  }
  .px-6 {
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
  .py-4 {
    padding-top: var(--space-4);
    padding-bottom: var(--space-4);
  }

  .text-sm {
    font-size: var(--text-sm);
  }
  .text-base {
    font-size: var(--text-base);
  }
  .text-lg {
    font-size: var(--text-lg);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
