<!--
Theme Toggle Component
Provides a button to switch between light, dark, and auto themes.
Features:
- Accessible with proper ARIA labels
- Visual feedback for current theme
- Smooth transitions
- Support for reduced motion preferences
-->

<script lang="ts">
  import { theme, resolvedTheme, type Theme } from '$stores/theme.js';
  import { get } from 'svelte/store';

  // Theme options
  const themes: Array<{ value: Theme; label: string; icon: string }> = [
    { value: 'light', label: 'Light theme', icon: '☀️' },
    { value: 'dark', label: 'Dark theme', icon: '🌙' },
    { value: 'auto', label: 'Auto theme (system)', icon: '🔄' },
  ];

  // Current theme values
  let currentTheme: Theme;
  let currentResolvedTheme: 'light' | 'dark';

  // Subscribe to theme changes
  $: currentTheme = $theme;

  // Use get() to avoid $ syntax issues with dependency-cruiser
  $: {
    currentResolvedTheme = get(resolvedTheme);
  }

  // Get next theme in cycle
  function getNextTheme(current: Theme): Theme {
    const currentIndex = themes.findIndex(t => t.value === current);
    const nextIndex = (currentIndex + 1) % themes.length;
    return themes[nextIndex].value;
  }

  // Handle theme toggle
  function handleToggle() {
    const nextTheme = getNextTheme(currentTheme);
    theme.setTheme(nextTheme);
  }

  // Get current theme info for display
  $: currentThemeInfo = themes.find(t => t.value === currentTheme) || themes[0];

  // Generate accessible label
  $: accessibleLabel = `Current theme: ${currentThemeInfo.label}. Click to cycle themes.`;
</script>

<button
  class="theme-toggle"
  on:click={handleToggle}
  aria-label={accessibleLabel}
  title={accessibleLabel}
  type="button"
>
  <span class="theme-icon" aria-hidden="true">
    {currentThemeInfo.icon}
  </span>
  <span class="theme-label">
    {currentThemeInfo.label}
  </span>
  <span class="theme-indicator" data-theme={currentResolvedTheme} aria-hidden="true"></span>
</button>

<style>
  .theme-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: transparent;
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    color: var(--color-gray-700);
    cursor: pointer;
    transition: all var(--duration-200) var(--ease-out);
    min-height: var(--touch-target-min);
    font-size: var(--text-sm);
    font-weight: 500;
    position: relative;
    overflow: hidden;
  }

  .theme-toggle:hover {
    background: var(--color-gray-50);
    border-color: var(--color-gray-400);
    color: var(--color-gray-900);
  }

  .theme-toggle:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
    border-color: var(--color-primary);
  }

  .theme-toggle:active {
    transform: translateY(1px);
    box-shadow: var(--shadow-sm);
  }

  .theme-icon {
    font-size: var(--text-base);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
  }

  .theme-label {
    font-size: var(--text-sm);
    line-height: var(--leading-tight);
    white-space: nowrap;
  }

  .theme-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: background-color var(--duration-200) var(--ease-out);
  }

  .theme-indicator[data-theme='light'] {
    background-color: var(--color-yellow-400);
  }

  .theme-indicator[data-theme='dark'] {
    background-color: var(--color-blue-500);
  }

  /* Mobile-friendly version */
  @media (max-width: 640px) {
    .theme-toggle {
      padding: var(--space-2);
      min-width: var(--touch-target-min);
      justify-content: center;
    }

    .theme-label {
      display: none;
    }

    .theme-icon {
      font-size: var(--text-lg);
    }
  }

  /* Dark theme styles */
  :global(.theme-dark) .theme-toggle {
    border-color: var(--color-gray-600);
    color: var(--color-gray-300);
  }

  :global(.theme-dark) .theme-toggle:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--color-gray-500);
    color: var(--color-gray-100);
  }

  :global(.theme-dark) .theme-toggle:focus {
    border-color: var(--color-primary-light);
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .theme-toggle {
      border-width: 2px;
    }

    .theme-toggle:focus {
      outline-width: 3px;
    }
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .theme-toggle,
    .theme-indicator {
      transition: none;
    }

    .theme-toggle:active {
      transform: none;
    }
  }
</style>
