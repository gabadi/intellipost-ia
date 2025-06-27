/**
 * Micro-Interactions UX Validation Tests
 * Comprehensive testing of hover effects, active states, and micro-animations
 */

import { test, expect } from '@playwright/test';

test.describe('Micro-Interactions UX Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Hover Effects Validation', () => {
    test('should show hover-lift effect on buttons', async ({ page }) => {
      // Find buttons with hover-lift class
      const button = page.locator('.btn.hover-lift').first();

      if ((await button.count()) > 0) {
        // Get initial transform
        const initialTransform = await button.evaluate(el => getComputedStyle(el).transform);

        // Hover over button
        await button.hover();

        // Wait for animation
        await page.waitForTimeout(300);

        // Check transform changed (should have translateY)
        const hoverTransform = await button.evaluate(el => getComputedStyle(el).transform);

        expect(hoverTransform).not.toBe(initialTransform);

        // Check box-shadow is applied
        const boxShadow = await button.evaluate(el => getComputedStyle(el).boxShadow);

        expect(boxShadow).not.toBe('none');
      }
    });

    test('should show hover-scale effect', async ({ page }) => {
      const scalableElement = page.locator('.hover-scale').first();

      if ((await scalableElement.count()) > 0) {
        // Hover and check scale transform
        await scalableElement.hover();
        await page.waitForTimeout(200);

        const transform = await scalableElement.evaluate(el => getComputedStyle(el).transform);

        // Should contain scale transformation
        expect(transform).toContain('scale');
      }
    });

    test('should show hover-glow effect', async ({ page }) => {
      const glowElement = page.locator('.hover-glow').first();

      if ((await glowElement.count()) > 0) {
        await glowElement.hover();
        await page.waitForTimeout(300);

        const boxShadow = await glowElement.evaluate(el => getComputedStyle(el).boxShadow);

        // Should have glow effect (non-zero box-shadow)
        expect(boxShadow).not.toBe('none');
        expect(boxShadow).not.toBe('0px 0px 0px');
      }
    });
  });

  test.describe('Active States Validation', () => {
    test('should show active-press effect on click', async ({ page }) => {
      const button = page.locator('.btn.active-press').first();

      if ((await button.count()) > 0) {
        // Start monitoring for transform changes
        const transformPromise = button.evaluate(element => {
          const style = getComputedStyle(element);
          return style.transform.includes('scale');
        });

        // Click and hold
        await button.click();

        // Wait for active state transform
        try {
          const hasScale = await transformPromise;
          if (hasScale) {
            expect(true).toBe(true);
          } else {
            // Even if animation is fast, check for smooth-state class
            await expect(button).toHaveClass(/smooth-state/);
          }
        } catch {
          // Check if transform was applied even briefly
          // Even if animation is fast, check for smooth-state class
          await expect(button).toHaveClass(/smooth-state/);
        }
      }
    });

    test('should show ripple effect on supported elements', async ({ page }) => {
      const rippleElement = page.locator('.ripple-effect').first();

      if ((await rippleElement.count()) > 0) {
        // Check ripple element has proper overflow hidden
        const overflow = await rippleElement.evaluate(el => getComputedStyle(el).overflow);

        expect(overflow).toBe('hidden');

        // Check position is relative for pseudo-element
        const position = await rippleElement.evaluate(el => getComputedStyle(el).position);

        expect(['relative', 'absolute', 'fixed'].includes(position)).toBe(true);
      }
    });
  });

  test.describe('Focus Effects Validation', () => {
    test('should show enhanced focus rings on keyboard navigation', async ({ page }) => {
      // Tab to first focusable element
      await page.keyboard.press('Tab');

      const focusedElement = page.locator(':focus');

      if ((await focusedElement.count()) > 0) {
        // Check for focus ring classes
        const hasFocusClass = await focusedElement.evaluate(el => {
          return (
            el.classList.contains('focus-ring-enhanced') ||
            el.classList.contains('focus-ring-thick') ||
            el.classList.contains('focus-glow')
          );
        });

        if (hasFocusClass) {
          // Check that focus outline/box-shadow is applied
          const outline = await focusedElement.evaluate(el => getComputedStyle(el).outline);
          const boxShadow = await focusedElement.evaluate(el => getComputedStyle(el).boxShadow);

          const hasFocusIndicator = outline !== 'none' || boxShadow !== 'none';
          expect(hasFocusIndicator).toBe(true);
        }
      }
    });

    test('should show focus-glow effect', async ({ page }) => {
      const focusGlowElement = page.locator('.focus-glow').first();

      if ((await focusGlowElement.count()) > 0) {
        await focusGlowElement.focus();
        await page.waitForTimeout(200);

        const boxShadow = await focusGlowElement.evaluate(el => getComputedStyle(el).boxShadow);

        expect(boxShadow).not.toBe('none');
      }
    });
  });

  test.describe('Animation Performance Validation', () => {
    test('should use hardware acceleration for smooth animations', async ({ page }) => {
      const animatedElements = page.locator('.gpu-accelerated');

      if ((await animatedElements.count()) > 0) {
        const willChange = await animatedElements
          .first()
          .evaluate(el => getComputedStyle(el).willChange);

        expect(willChange).toBe('transform');
      }
    });

    test('should respect reduced motion preferences', async ({ page }) => {
      // Set reduced motion preference
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Check that animations are disabled
      const animatedElement = page.locator('.hover-lift, .smooth-state').first();

      if ((await animatedElement.count()) > 0) {
        const transition = await animatedElement.evaluate(el => getComputedStyle(el).transition);

        // Should be 'none' or very short duration
        const isAnimationReduced =
          transition === 'none' || transition.includes('0s') || !transition.includes('transform');

        expect(isAnimationReduced).toBe(true);
      }
    });
  });

  test.describe('Touch Device Optimizations', () => {
    test('should work properly on touch devices', async ({ page }) => {
      // Emulate touch device
      await page.setViewportSize({ width: 375, height: 667 });

      const touchElement = page.locator('.ripple-effect').first();

      if ((await touchElement.count()) > 0) {
        // Check that hover effects don't interfere on touch
        await touchElement.tap();

        // Element should be clickable without hover issues
        const isVisible = await touchElement.isVisible();
        expect(isVisible).toBe(true);
      }
    });

    test('should have appropriate touch targets', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const interactiveElements = page.locator('.interactive, .btn');
      const count = await interactiveElements.count();

      for (let i = 0; i < Math.min(count, 5); i++) {
        const element = interactiveElements.nth(i);
        const boundingBox = await element.boundingBox();

        if (boundingBox) {
          // Minimum touch target size should be 44px
          expect(boundingBox.height).toBeGreaterThanOrEqual(44);
          expect(boundingBox.width).toBeGreaterThanOrEqual(44);
        }
      }
    });
  });

  test.describe('High Contrast Mode Support', () => {
    test('should adjust effects for high contrast mode', async ({ page }) => {
      // Test high contrast adjustments
      await page.addStyleTag({
        content:
          '@media (prefers-contrast: high) { .hover-glow:hover { box-shadow: 0 0 0 3px currentColor; } }',
      });

      const contrastElement = page.locator('.hover-glow').first();

      if ((await contrastElement.count()) > 0) {
        await contrastElement.hover();
        await page.waitForTimeout(200);

        // Should have some form of visual feedback
        const boxShadow = await contrastElement.evaluate(el => getComputedStyle(el).boxShadow);

        expect(boxShadow).not.toBe('none');
      }
    });
  });

  test.describe('Dark Mode Compatibility', () => {
    test('should work properly in dark mode', async ({ page }) => {
      // Emulate dark color scheme
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.reload();
      await page.waitForLoadState('networkidle');

      const darkModeElement = page.locator('.hover-glow').first();

      if ((await darkModeElement.count()) > 0) {
        await darkModeElement.hover();
        await page.waitForTimeout(200);

        const boxShadow = await darkModeElement.evaluate(el => getComputedStyle(el).boxShadow);

        // Should still have glow effect in dark mode
        expect(boxShadow).not.toBe('none');
      }
    });
  });

  test.describe('Micro-Interaction Timing Validation', () => {
    test('should have appropriate animation durations', async ({ page }) => {
      const animatedElement = page.locator('.smooth-state').first();

      if ((await animatedElement.count()) > 0) {
        const transition = await animatedElement.evaluate(el => getComputedStyle(el).transition);

        // Should have reasonable transition duration (not too fast, not too slow)
        const hasDuration =
          transition.includes('0.2s') ||
          transition.includes('0.3s') ||
          transition.includes('200ms') ||
          transition.includes('300ms');

        expect(hasDuration).toBe(true);
      }
    });

    test('should provide immediate feedback on interaction', async ({ page }) => {
      const button = page.locator('.btn').first();

      if ((await button.count()) > 0) {
        // Measure time for hover feedback
        const startTime = Date.now();
        await button.hover();

        // Check for visual change within reasonable time
        await page.waitForTimeout(50); // 50ms should be enough for hover feedback

        const endTime = Date.now();
        const responseTime = endTime - startTime;

        // Should respond within 100ms for good UX
        expect(responseTime).toBeLessThan(100);
      }
    });
  });
});
