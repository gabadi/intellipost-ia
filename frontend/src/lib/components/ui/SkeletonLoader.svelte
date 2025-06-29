<!--
  Skeleton Loader Component
  Provides smooth loading state placeholders for enhanced UX
-->

<script lang="ts">
  export let width: string = '100%';
  export let height: string = '20px';
  export let variant: 'text' | 'rect' | 'circle' | 'button' = 'text';
  export let animation: boolean = true;
  export let lines: number = 1;
  export let spacing: string = 'var(--spacing-2)';
</script>

<div class="skeleton-container" style="gap: {spacing}">
  {#each Array(lines) as _}
    <div
      class="skeleton skeleton-{variant}"
      class:animated={animation}
      style="width: {width}; height: {height}"
      aria-hidden="true"
    ></div>
  {/each}
</div>

<style>
  .skeleton-container {
    display: flex;
    flex-direction: column;
  }

  .skeleton {
    background: linear-gradient(
      90deg,
      var(--color-background-muted) 0%,
      var(--color-background-secondary) 50%,
      var(--color-background-muted) 100%
    );
    background-size: 200% 100%;
  }

  .skeleton.animated {
    animation: skeleton-loading 1.5s ease-in-out infinite;
  }

  .skeleton-text {
    border-radius: var(--border-radius-sm);
  }

  .skeleton-rect {
    border-radius: var(--border-radius-md);
  }

  .skeleton-circle {
    border-radius: 50%;
  }

  .skeleton-button {
    border-radius: var(--border-radius-md);
    height: 44px;
  }

  @keyframes skeleton-loading {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }

  /* Dark mode adjustments */
  :root[data-theme='dark'] .skeleton {
    background: linear-gradient(
      90deg,
      var(--color-secondary-800) 0%,
      var(--color-secondary-700) 50%,
      var(--color-secondary-800) 100%
    );
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme]) .skeleton {
      background: linear-gradient(
        90deg,
        var(--color-secondary-800) 0%,
        var(--color-secondary-700) 50%,
        var(--color-secondary-800) 100%
      );
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .skeleton.animated {
      animation: none;
      background: var(--color-background-muted);
    }
  }
</style>
