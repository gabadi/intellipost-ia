/**
 * Theme Store - Manages light/dark theme state with persistence
 *
 * Features:
 * - Automatic theme detection from system preferences
 * - Persistent theme storage using localStorage
 * - Reactive theme switching
 * - CSS class application for theme switching
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark' | 'auto';

// Theme preference with persistence
function createThemeStore() {
  // Initial theme preference from localStorage or 'auto'
  const getInitialTheme = (): Theme => {
    if (!browser) return 'auto';

    try {
      const stored = localStorage.getItem('theme-preference');
      if (stored && ['light', 'dark', 'auto'].includes(stored)) {
        return stored as Theme;
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Failed to read theme preference from localStorage:', error);
    }

    return 'auto';
  };

  // Resolve actual theme (convert 'auto' to 'light'/'dark')
  const resolveTheme = (preference: Theme): 'light' | 'dark' => {
    if (preference === 'auto') {
      if (!browser) return 'light';
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return preference;
  };

  const { subscribe, set, update } = writable<Theme>(getInitialTheme());

  // Apply theme to document
  const applyTheme = (theme: Theme) => {
    if (!browser) return;

    const resolved = resolveTheme(theme);
    const html = document.documentElement;

    // Remove existing theme classes and data attributes
    html.classList.remove('theme-light', 'theme-dark');
    html.removeAttribute('data-theme');

    // Add theme using class approach
    html.classList.add(`theme-${resolved}`);

    // Update meta theme-color for mobile browsers
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.setAttribute('name', 'theme-color');
      document.head.appendChild(metaThemeColor);
    }

    // Set theme colors
    const themeColors = {
      light: '#1e40af', // Primary blue
      dark: '#1f2937', // Dark gray
    };

    metaThemeColor.setAttribute('content', themeColors[resolved]);
  };

  // Persist theme preference
  const persistTheme = (theme: Theme) => {
    if (!browser) return;

    try {
      localStorage.setItem('theme-preference', theme);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Failed to save theme preference to localStorage:', error);
    }
  };

  // Listen for system theme changes when preference is 'auto'
  const setupSystemThemeListener = () => {
    if (!browser) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      update(currentTheme => {
        if (currentTheme === 'auto') {
          applyTheme('auto');
        }
        return currentTheme;
      });
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);

    // Return cleanup function
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  };

  // Initialize theme application and system listener
  let cleanup: (() => void) | undefined;

  if (browser) {
    // Apply initial theme
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);

    // Setup system theme listener
    cleanup = setupSystemThemeListener();
  }

  return {
    subscribe,

    // Set theme preference
    setTheme: (theme: Theme) => {
      set(theme);
      applyTheme(theme);
      persistTheme(theme);
    },

    // Toggle between light and dark (ignores auto)
    toggle: () => {
      update(currentTheme => {
        const resolved = resolveTheme(currentTheme);
        const newTheme: Theme = resolved === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
        persistTheme(newTheme);
        return newTheme;
      });
    },

    // Get the resolved theme (never returns 'auto')
    getResolvedTheme: (preference: Theme): 'light' | 'dark' => resolveTheme(preference),

    // Cleanup function for component destruction
    destroy: () => {
      if (cleanup) cleanup();
    },
  };
}

export const theme = createThemeStore();

// Derived store for resolved theme
export const resolvedTheme = {
  subscribe: (callback: (value: 'light' | 'dark') => void) => {
    return theme.subscribe(preference => {
      callback(theme.getResolvedTheme(preference));
    });
  },
};
