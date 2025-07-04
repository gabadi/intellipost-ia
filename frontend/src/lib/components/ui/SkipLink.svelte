<script lang="ts">
  export let href: string = '#main-content';
  export let text: string = 'Skip to main content';
</script>

<a {href} class="skip-link">
  {text}
</a>

<style>
  .skip-link {
    position: absolute;
    top: -40px;
    left: 6px;
    background: var(--primary-600);
    color: var(--surface-primary);
    padding: 8px 12px;
    text-decoration: none;
    border-radius: var(--radius-sm);
    font-weight: var(--font-medium);
    font-size: var(--text-sm);
    z-index: 9999;
    transition: top 0.3s;
  }

  .skip-link:focus {
    top: 6px;
    outline: 2px solid var(--surface-primary);
    outline-offset: 2px;
  }
</style>
