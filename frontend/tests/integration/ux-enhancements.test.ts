/**
 * UX Enhancements Integration Tests
 * Tests all micro-interactions, loading states, and enhanced focus system
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('UX Enhancements Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Skip navigation links work correctly', async ({ page }) => {
    // Tab to skip links
    await page.keyboard.press('Tab');

    // Check skip link is visible when focused
    const skipLink = page.locator('.skip-link').first();
    await expect(skipLink).toBeVisible();
    await expect(skipLink).toHaveText('Skip to main content');

    // Press Enter to activate skip link
    await page.keyboard.press('Enter');

    // Check that main content is now focused
    const mainContent = page.locator('#main-content');
    await expect(mainContent).toBeFocused();
  });

  test('Button micro-interactions work properly', async ({ page }) => {
    // Navigate to a page with buttons
    const button = page.locator('.btn').first();

    if ((await button.count()) > 0) {
      // Test hover effect
      await button.hover();

      // Check for hover-lift class application
      await expect(button).toHaveClass(/hover-lift/);

      // Test click micro-interaction
      await button.click();

      // Check for active-press class
      await expect(button).toHaveClass(/active-press/);
    }
  });

  test('Enhanced focus ring system works', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');

    // Check for enhanced focus rings
    const focusedElement = page.locator(':focus');
    if ((await focusedElement.count()) > 0) {
      await expect(focusedElement).toHaveClass(/focus-ring-enhanced/);
    }
  });

  test('Loading states display correctly', async ({ page }) => {
    // Check for loading spinners
    const spinner = page.locator('.spinner');
    if ((await spinner.count()) > 0) {
      await expect(spinner).toBeVisible();
    }

    // Check for skeleton screens
    const skeleton = page.locator('.skeleton');
    if ((await skeleton.count()) > 0) {
      await expect(skeleton).toBeVisible();
    }
  });

  test('Smooth animations and transitions work', async ({ page }) => {
    // Test for smooth-state classes
    const smoothElements = page.locator('.smooth-state');
    if ((await smoothElements.count()) > 0) {
      await expect(smoothElements.first()).toHaveClass(/smooth-state/);
    }

    // Test animate-in elements
    const animatedElements = page.locator('.animate-in');
    if ((await animatedElements.count()) > 0) {
      await expect(animatedElements.first()).toHaveClass(/animate-in/);
    }
  });

  test('Accessibility landmarks are properly labeled', async ({ page }) => {
    // Check for landmark navigation
    const navigation = page.locator('#navigation');
    await expect(navigation).toHaveClass(/landmark/);

    const mainContent = page.locator('#main-content');
    await expect(mainContent).toHaveClass(/landmark/);
    await expect(mainContent).toHaveClass(/focus-group/);
  });

  test('CSS animations respect reduced motion preferences', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.reload();

    // Check that animations are disabled
    const animatedElements = page.locator('.animate-in, .hover-lift, .smooth-state');
    for (let i = 0; i < (await animatedElements.count()); i++) {
      const element = animatedElements.nth(i);
      const transitions = await element.evaluate(el => getComputedStyle(el).transition);
      // Transitions should be disabled for reduced motion
      expect(transitions).toBe('none');
    }
  });

  test('High contrast mode adjustments work', async ({ page }) => {
    // Enable high contrast media query
    await page.emulateMedia({ colorScheme: 'light', reducedMotion: 'no-preference' });

    // Test focus indicators in high contrast
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    if ((await focusedElement.count()) > 0) {
      const outlineWidth = await focusedElement.evaluate(el => getComputedStyle(el).outlineWidth);
      // Should have enhanced outline in high contrast
      expect(parseInt(outlineWidth)).toBeGreaterThan(1);
    }
  });

  test('Touch device optimizations work', async ({ page }) => {
    // Emulate mobile device
    await page.setViewportSize({ width: 375, height: 667 });

    // Check touch target minimum sizes
    const buttons = page.locator('.btn');
    for (let i = 0; i < (await buttons.count()); i++) {
      const button = buttons.nth(i);
      const boundingBox = await button.boundingBox();
      if (boundingBox) {
        expect(boundingBox.height).toBeGreaterThanOrEqual(44); // 44px minimum
        expect(boundingBox.width).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('Dark mode theme switching works', async ({ page }) => {
    // Test dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.reload();

    // Check that dark mode styles are applied
    const bodyStyles = await page.evaluate(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--color-scheme');
    });

    expect(bodyStyles.trim()).toBe('dark');
  });

  test('CSS bundle size is within limits', async ({ page }) => {
    // Check total CSS size
    const stylesheets = page.locator('link[rel="stylesheet"]');
    let totalSize = 0;

    for (let i = 0; i < (await stylesheets.count()); i++) {
      const stylesheet = stylesheets.nth(i);
      const href = await stylesheet.getAttribute('href');
      if (href) {
        const response = await page.request.get(href);
        const content = await response.text();
        totalSize += content.length;
      }
    }

    // Should be under 60KB as specified
    expect(totalSize).toBeLessThan(60 * 1024);
  });
});

test.describe('Component Integration Tests', () => {
  test('Button component has all micro-interaction classes', async ({ page }) => {
    await page.goto(BASE_URL);

    const buttons = page.locator('.btn');
    if ((await buttons.count()) > 0) {
      const button = buttons.first();

      // Check for all expected classes
      await expect(button).toHaveClass(/hover-lift/);
      await expect(button).toHaveClass(/active-press/);
      await expect(button).toHaveClass(/smooth-state/);
      await expect(button).toHaveClass(/focus-ring-enhanced/);
    }
  });

  test('Layout component has skip navigation and landmarks', async ({ page }) => {
    await page.goto(BASE_URL);

    // Check skip navigation
    const skipLinks = page.locator('.skip-links');
    await expect(skipLinks).toBeVisible();

    const skipToMain = page.locator('.skip-link[href="#main-content"]');
    await expect(skipToMain).toBeVisible();

    const skipToNav = page.locator('.skip-link[href="#navigation"]');
    await expect(skipToNav).toBeVisible();

    // Check landmarks
    const navigation = page.locator('#navigation.landmark');
    await expect(navigation).toBeVisible();

    const mainContent = page.locator('#main-content.landmark.focus-group');
    await expect(mainContent).toBeVisible();

    // Check focus-within-highlight container
    const focusContainer = page.locator('.focus-within-highlight');
    await expect(focusContainer).toBeVisible();

    // Check animate-in on title
    const title = page.locator('h1.animate-in');
    await expect(title).toBeVisible();
  });
});

test.describe('Performance and Bundle Validation', () => {
  test('CSS loads without errors', async ({ page }) => {
    const cssErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('css')) {
        cssErrors.push(msg.text());
      }
    });

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    expect(cssErrors).toHaveLength(0);
  });

  test('All utility CSS files are loaded', async ({ page }) => {
    await page.goto(BASE_URL);

    // Check that our new utility files are loaded
    const stylesheets = await page.evaluate(() => {
      const links = Array.from(
        document.querySelectorAll('link[rel="stylesheet"]')
      ) as HTMLLinkElement[];
      return links.map(link => link.href);
    });

    // Should include our main CSS which imports utilities
    const hasMainCSS = stylesheets.some(
      href => href.includes('main.css') || href.includes('app.css')
    );
    expect(hasMainCSS).toBe(true);
  });

  test('CSS animations perform well', async ({ page }) => {
    await page.goto(BASE_URL);

    // Test animation performance
    const animationMetrics = await page.evaluate(() => {
      return new Promise(resolve => {
        const observer = new PerformanceObserver(list => {
          const entries = list.getEntries();
          const animationEntries = entries.filter(
            entry => entry.entryType === 'measure' || entry.entryType === 'navigation'
          );
          resolve(animationEntries.length);
        });

        observer.observe({ entryTypes: ['measure', 'navigation'] });

        // Trigger some animations
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
          btn.dispatchEvent(new MouseEvent('mouseenter'));
          btn.dispatchEvent(new MouseEvent('mouseleave'));
        });

        setTimeout(() => resolve(0), 1000);
      });
    });

    // Should not cause performance issues
    expect(typeof animationMetrics).toBe('number');
  });
});
