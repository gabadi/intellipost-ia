<script lang="ts">
  export let size: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' = 'md';
  export let color: 'primary' | 'secondary' | 'white' | 'current' | 'gray' = 'primary';
  export let label: string = 'Loading...';
  export let showLabel: boolean = false;
  export let variant: 'spin' | 'dots' | 'pulse' | 'bars' = 'spin';
</script>

<div class="spinner-container" class:spinner-container--vertical={showLabel}>
  {#if variant === 'spin'}
    <div class="spinner spinner--{size} spinner--{color}" role="status" aria-label={label}>
      <span class="spinner__sr-text">{label}</span>
    </div>
  {:else if variant === 'dots'}
    <div class="spinner spinner--dots spinner--{color}" role="status" aria-label={label}>
      <div class="spinner--dots-dot"></div>
      <span class="spinner__sr-text">{label}</span>
    </div>
  {:else if variant === 'pulse'}
    <div
      class="spinner spinner--pulse spinner--{size} spinner--{color}"
      role="status"
      aria-label={label}
    >
      <span class="spinner__sr-text">{label}</span>
    </div>
  {:else if variant === 'bars'}
    <div class="spinner spinner--bars spinner--{color}" role="status" aria-label={label}>
      <div class="spinner--bars-bar"></div>
      <span class="spinner__sr-text">{label}</span>
    </div>
  {/if}

  {#if showLabel}
    <span class="spinner__label spinner__label--{size}">{label}</span>
  {/if}
</div>

<!-- No component-specific styles needed - handled by semantic CSS classes -->
