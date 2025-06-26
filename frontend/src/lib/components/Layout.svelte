<script lang="ts">
  export let title = 'IntelliPost AI';
</script>

<!-- Skip Navigation Links -->
<div class="skip-links">
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <a href="#navigation" class="skip-link">Skip to navigation</a>
</div>

<div class="focus-within-highlight">
  <header id="navigation" class="landmark">
    <h1 class="animate-in">{title}</h1>
  </header>

  <main id="main-content" class="landmark focus-group">
    <slot />
  </main>
</div>
