<script lang="ts">
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let color: 'primary' | 'secondary' | 'white' = 'primary';
  export let label: string = 'Loading...';
  export let showLabel: boolean = false;

  $: sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  $: colorClasses = {
    primary: 'border-primary border-t-transparent',
    secondary: 'border-gray-300 border-t-primary',
    white: 'border-white border-t-transparent',
  };
</script>

<div class="loading-container" class:with-label={showLabel}>
  <div
    class="loading-spinner {sizeClasses[size]} {colorClasses[color]}"
    role="status"
    aria-label={label}
  ></div>
  {#if showLabel}
    <span class="loading-label">{label}</span>
  {/if}
</div>

<style>
  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .loading-container.with-label {
    gap: var(--space-2);
  }

  .loading-spinner {
    border: 2px solid;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .w-4 {
    width: 16px;
  }
  .h-4 {
    height: 16px;
  }
  .w-6 {
    width: 24px;
  }
  .h-6 {
    height: 24px;
  }
  .w-8 {
    width: 32px;
  }
  .h-8 {
    height: 32px;
  }

  .border-primary {
    border-color: var(--color-primary);
  }

  .border-t-transparent {
    border-top-color: transparent;
  }

  .border-t-primary {
    border-top-color: var(--color-primary);
  }

  .border-gray-300 {
    border-color: var(--color-gray-300);
  }

  .border-white {
    border-color: white;
  }

  .loading-label {
    font-size: var(--text-sm);
    color: var(--color-gray-600);
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
