<script lang="ts">
  import { onMount } from 'svelte';
  import { config } from '$lib/config';
  import {
    themeStore,
    isDarkMode,
    themeMode,
    isAutoMode,
    isThemeInitialized,
    announceThemeChange,
    type ThemeMode,
  } from '$lib/stores/theme';

  let isLoading = true;
  let showModeSelector = false;
  let buttonRef: HTMLButtonElement;

  // Handle theme toggle
  function toggleTheme() {
    themeStore.toggleTheme();
    announceThemeChange($isDarkMode ? 'light' : 'dark');
  }

  // Handle specific theme mode selection
  function setThemeMode(mode: ThemeMode) {
    themeStore.setTheme(mode);
    showModeSelector = false;
    if (mode === 'auto') {
      announceThemeChange($isDarkMode ? 'dark' : 'light');
    } else {
      announceThemeChange(mode);
    }
  }

  // Handle keyboard navigation
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      showModeSelector = false;
      buttonRef?.focus();
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      showModeSelector = !showModeSelector;
    }
  }

  // Handle outside clicks
  function handleOutsideClick(event: MouseEvent) {
    if (showModeSelector && buttonRef && !buttonRef.contains(event.target as Node)) {
      showModeSelector = false;
    }
  }

  onMount(() => {
    if (!config.features.DARK_MODE) {
      isLoading = false;
      return;
    }

    // Subscribe to theme store initialization
    const unsubscribe = isThemeInitialized.subscribe(initialized => {
      isLoading = !initialized;
    });

    // Add global click listener for outside clicks
    document.addEventListener('click', handleOutsideClick);

    return () => {
      unsubscribe();
      document.removeEventListener('click', handleOutsideClick);
    };
  });

  // Reactive label for accessibility
  $: accessibilityLabel = isLoading
    ? 'Theme toggle loading'
    : $isAutoMode
      ? `Auto theme mode (currently ${$isDarkMode ? 'Dark' : 'Light'}), click to toggle theme`
      : `Switch to ${$isDarkMode ? 'Light' : 'Dark'} mode`;

  $: themeIcon = isLoading ? '⏳' : $isDarkMode ? '☀️' : '🌙';

  $: themeLabel = isLoading
    ? 'Loading...'
    : $isAutoMode
      ? 'Auto'
      : $isDarkMode
        ? 'Light' // When in dark mode, show "Light" to indicate it will switch to light
        : 'Dark'; // When in light mode, show "Dark" to indicate it will switch to dark
</script>

{#if config.features.DARK_MODE}
  <div class="theme-toggle-container">
    <button
      bind:this={buttonRef}
      class="theme-toggle"
      class:loading={isLoading}
      class:expanded={showModeSelector}
      on:click={toggleTheme}
      on:contextmenu|preventDefault={() => (showModeSelector = !showModeSelector)}
      on:keydown={handleKeydown}
      disabled={isLoading}
      aria-label={accessibilityLabel}
      aria-expanded={showModeSelector}
      aria-haspopup="menu"
      title={accessibilityLabel}
    >
      {#if isLoading}
        <span class="theme-icon loading-spinner" aria-hidden="true"></span>
      {:else}
        <span class="theme-icon" aria-hidden="true">{themeIcon}</span>
      {/if}

      <span class="theme-label">{themeLabel}</span>

      {#if !isLoading}
        <span class="expand-indicator" aria-hidden="true">
          {showModeSelector ? '▲' : '▼'}
        </span>
      {/if}
    </button>

    {#if showModeSelector && !isLoading}
      <div class="theme-selector" role="menu" aria-label="Theme options">
        <button
          class="theme-option"
          class:active={$themeMode === 'light'}
          role="menuitem"
          on:click={() => setThemeMode('light')}
        >
          <span class="option-icon" aria-hidden="true">☀️</span>
          <span class="option-label">Light</span>
          {#if $themeMode === 'light'}
            <span class="option-check" aria-hidden="true">✓</span>
          {/if}
        </button>

        <button
          class="theme-option"
          class:active={$themeMode === 'dark'}
          role="menuitem"
          on:click={() => setThemeMode('dark')}
        >
          <span class="option-icon" aria-hidden="true">🌙</span>
          <span class="option-label">Dark</span>
          {#if $themeMode === 'dark'}
            <span class="option-check" aria-hidden="true">✓</span>
          {/if}
        </button>

        <button
          class="theme-option"
          class:active={$themeMode === 'auto'}
          role="menuitem"
          on:click={() => setThemeMode('auto')}
        >
          <span class="option-icon" aria-hidden="true">🔄</span>
          <span class="option-label">Auto</span>
          {#if $themeMode === 'auto'}
            <span class="option-check" aria-hidden="true">✓</span>
          {/if}
        </button>
      </div>
    {/if}
  </div>
{/if}

<style>
  .theme-toggle-container {
    position: relative;
    display: inline-block;
  }

  .theme-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-2);

    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--space-2) var(--space-3);

    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text);

    cursor: pointer;
    transition: all var(--duration-200) var(--ease-out);

    min-height: var(--touch-target-min);
    min-width: var(--touch-target-min);

    position: relative;
    z-index: 1;
  }

  .theme-toggle:hover:not(:disabled) {
    background: var(--color-background-secondary);
    border-color: var(--color-border-secondary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .theme-toggle:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: var(--shadow-xs);
  }

  .theme-toggle.expanded {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-bottom-color: var(--color-primary);
    box-shadow: var(--shadow-md);
  }

  .theme-toggle:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .theme-toggle:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .theme-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--font-size-base);
    line-height: 1;
  }

  .theme-label {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
  }

  .expand-indicator {
    font-size: var(--font-size-xs);
    margin-left: var(--space-1);
    opacity: 0.7;
    transition: transform var(--duration-200) var(--ease-out);
  }

  .theme-toggle.expanded .expand-indicator {
    transform: rotate(180deg);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin var(--duration-1000) linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Theme Selector Dropdown */
  .theme-selector {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--color-background);
    border: 1px solid var(--color-primary);
    border-top: none;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    box-shadow: var(--shadow-lg);
    z-index: var(--z-index-dropdown);
    overflow: hidden;
    animation: fadeInDown var(--duration-200) var(--ease-out);
  }

  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .theme-option {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-3);
    background: none;
    border: none;
    color: var(--color-text);
    font-size: var(--font-size-sm);
    font-family: inherit;
    cursor: pointer;
    transition: background-color var(--duration-150) var(--ease-out);
    border-bottom: 1px solid var(--color-border-muted);
  }

  .theme-option:last-child {
    border-bottom: none;
  }

  .theme-option:hover {
    background: var(--color-background-secondary);
  }

  .theme-option:focus {
    background: var(--color-background-secondary);
    outline: 2px solid var(--color-primary);
    outline-offset: -2px;
  }

  .theme-option.active {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: var(--font-weight-medium);
  }

  .option-icon {
    font-size: var(--font-size-base);
    min-width: 20px;
    text-align: center;
  }

  .option-label {
    flex: 1;
    text-align: left;
  }

  .option-check {
    font-size: var(--font-size-sm);
    color: var(--color-primary);
    font-weight: var(--font-weight-bold);
  }

  /* Compact variant for mobile */
  @media (max-width: 640px) {
    .theme-label {
      display: none;
    }

    .theme-toggle {
      padding: var(--space-2);
      min-width: var(--touch-target-min);
    }

    .expand-indicator {
      display: none;
    }

    .theme-selector {
      position: fixed;
      top: auto;
      bottom: 70px; /* Above mobile nav */
      left: var(--space-4);
      right: var(--space-4);
      border-radius: var(--radius-lg);
      border: 1px solid var(--color-border);
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .theme-toggle,
    .theme-option,
    .expand-indicator {
      transition: none;
    }

    .theme-selector {
      animation: none;
    }

    .loading-spinner {
      animation: none;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .theme-toggle {
      border-width: 2px;
    }

    .theme-toggle:focus-visible {
      outline-width: 3px;
    }

    .theme-option:focus {
      outline-width: 3px;
    }
  }
</style>
