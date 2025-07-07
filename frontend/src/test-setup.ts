import '@testing-library/jest-dom/vitest';

// Mock CSS imports for test environment
// This resolves "Cannot create proxy with a non-object as target or handler" errors
import { vi } from 'vitest';

// Mock CSS modules to prevent preprocessing issues
vi.mock('*.css', () => ({}));
vi.mock('*.scss', () => ({}));
vi.mock('*.sass', () => ({}));

// Set up CSS custom properties for testing
document.documentElement.style.setProperty('--color-primary', '#3b82f6');
document.documentElement.style.setProperty('--color-text-primary', '#111827');
document.documentElement.style.setProperty('--color-background', '#ffffff');
document.documentElement.style.setProperty('--color-border', '#d1d5db');
document.documentElement.style.setProperty('--color-error', '#ef4444');
document.documentElement.style.setProperty('--color-success', '#10b981');
document.documentElement.style.setProperty('--space-1', '0.25rem');
document.documentElement.style.setProperty('--space-4', '1rem');
document.documentElement.style.setProperty('--radius-lg', '0.5rem');
document.documentElement.style.setProperty('--text-sm', '0.875rem');
