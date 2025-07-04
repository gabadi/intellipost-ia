<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success' | 'warning' =
    'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled: boolean = false;
  export let loading: boolean = false;
  export let type: 'button' | 'submit' | 'reset' = 'button';
  export let href: string | undefined = undefined;
  export let fullWidth: boolean = false;

  // Additional classes
  let className: string = '';
  export { className as class };

  // Event handlers
  export let onClick: ((event: MouseEvent) => void) | undefined = undefined;

  $: isLink = href !== undefined;
  $: isDisabled = disabled || loading;

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
    class="btn btn--{variant} btn--{size} hover-lift active-press smooth-state focus-ring-enhanced {className}"
    class:btn--full-width={fullWidth}
    class:btn--loading={loading}
    class:loading-state={loading}
    aria-disabled={isDisabled}
    on:click={handleClick}
  >
    <slot />
  </a>
{:else}
  <button
    {type}
    class="btn btn--{variant} btn--{size} hover-lift active-press smooth-state focus-ring-enhanced {className}"
    class:btn--full-width={fullWidth}
    class:btn--loading={loading}
    class:loading-state={loading}
    disabled={isDisabled}
    on:click={handleClick}
  >
    <slot />
  </button>
{/if}

<!-- No component-specific styles needed - handled by semantic CSS classes -->
