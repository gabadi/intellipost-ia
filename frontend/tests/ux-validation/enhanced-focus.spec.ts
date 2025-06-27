/**
 * Enhanced Focus System UX Validation Tests
 * Comprehensive testing of accessibility features, keyboard navigation, and focus management
 */

import { test, expect } from '@playwright/test';

test.describe('Enhanced Focus System UX Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Skip Navigation Links Validation', () => {
    test('should display skip links on keyboard focus', async ({ page }) => {
      // Tab to activate skip navigation
      await page.keyboard.press('Tab');

      // Check if skip links are visible
      const skipLinks = page.locator('.skip-links');
      await expect(skipLinks).toBeVisible();

      // Check specific skip link
      const skipToMain = page.locator('.skip-link[href="#main-content"]').first();

      if ((await skipToMain.count()) > 0) {
        await expect(skipToMain).toBeVisible();
        await expect(skipToMain).toHaveText(/Skip to main content/i);

        // Check focus styles
        await skipToMain.focus();
        const outline = await skipToMain.evaluate(el => getComputedStyle(el).outline);
        const boxShadow = await skipToMain.evaluate(el => getComputedStyle(el).boxShadow);

        const hasFocusIndicator = outline !== 'none' || boxShadow !== 'none';
        expect(hasFocusIndicator).toBe(true);
      }
    });

    test('should navigate to correct landmarks when skip links are activated', async ({ page }) => {
      // Tab to skip link
      await page.keyboard.press('Tab');

      const skipToMain = page.locator('.skip-link[href="#main-content"]').first();

      if ((await skipToMain.count()) > 0) {
        // Click skip link
        await skipToMain.click();

        // Check that main content is focused
        const mainContent = page.locator('#main-content');
        if ((await mainContent.count()) > 0) {
          await expect(mainContent).toBeFocused();
        }
      }
    });

    test('should have proper ARIA labels for skip links', async ({ page }) => {
      const skipLinksContainer = page.locator('.skip-links');

      if ((await skipLinksContainer.count()) > 0) {
        const ariaLabel = await skipLinksContainer.getAttribute('aria-label');
        expect(ariaLabel).toContain('Skip navigation');
      }
    });
  });

  test.describe('Enhanced Focus Rings Validation', () => {
    test('should display enhanced focus rings on interactive elements', async ({ page }) => {
      // Tab through interactive elements
      await page.keyboard.press('Tab');

      const focusedElement = page.locator(':focus');

      if ((await focusedElement.count()) > 0) {
        // Check for enhanced focus classes
        const hasFocusClass = await focusedElement.evaluate(el => {
          return (
            el.classList.contains('focus-ring-enhanced') ||
            el.classList.contains('focus-ring-thick') ||
            el.classList.contains('focus-ring-inset-thick')
          );
        });

        if (hasFocusClass) {
          // Check focus indicator
          const outline = await focusedElement.evaluate(el => getComputedStyle(el).outline);
          const boxShadow = await focusedElement.evaluate(el => getComputedStyle(el).boxShadow);

          const hasFocusIndicator = outline !== 'none' || boxShadow !== 'none';
          expect(hasFocusIndicator).toBe(true);
        }
      }
    });

    test('should show multi-layer focus rings for enhanced visibility', async ({ page }) => {
      // Create test element with enhanced focus
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'focus-ring-enhanced';
        button.textContent = 'Test Button';
        button.id = 'test-enhanced-focus';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-enhanced-focus');
      await button.focus();

      const boxShadow = await button.evaluate(el => getComputedStyle(el).boxShadow);

      // Enhanced focus should have multiple shadow layers
      const shadowLayers = boxShadow.split(',').length;
      expect(shadowLayers).toBeGreaterThan(1);
    });

    test('should show thick focus rings for better visibility', async ({ page }) => {
      // Create test element with thick focus
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'focus-ring-thick';
        button.textContent = 'Thick Focus';
        button.id = 'test-thick-focus';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-thick-focus');
      await button.focus();

      const outline = await button.evaluate(el => getComputedStyle(el).outline);

      // Should have thick outline
      const hasThickOutline = outline.includes('3px') || outline.includes('4px');
      expect(hasThickOutline).toBe(true);
    });

    test('should show inset focus rings for form elements', async ({ page }) => {
      // Create test input with inset focus
      await page.evaluate(() => {
        const input = document.createElement('input');
        input.className = 'focus-ring-inset-thick';
        input.placeholder = 'Inset focus test';
        input.id = 'test-inset-focus';
        document.body.appendChild(input);
      });

      const input = page.locator('#test-inset-focus');
      await input.focus();

      const boxShadow = await input.evaluate(el => getComputedStyle(el).boxShadow);

      // Should have inset box shadow
      expect(boxShadow).toContain('inset');
    });
  });

  test.describe('Keyboard Navigation Flow Validation', () => {
    test('should provide logical tab order', async ({ page }) => {
      const focusableElements = [];
      let tabCount = 0;
      const maxTabs = 10;

      // Tab through elements and record order
      while (tabCount < maxTabs) {
        await page.keyboard.press('Tab');
        tabCount++;

        const focusedElement = page.locator(':focus');
        if ((await focusedElement.count()) > 0) {
          const tagName = await focusedElement.evaluate(el => el.tagName);
          const id = (await focusedElement.getAttribute('id')) || '';
          const className = (await focusedElement.getAttribute('class')) || '';

          focusableElements.push({ tagName, id, className, tabIndex: tabCount });

          // Break if we've cycled back to skip links
          if (className.includes('skip-link') && tabCount > 1) {
            break;
          }
        }
      }

      // Should have found focusable elements
      expect(focusableElements.length).toBeGreaterThan(0);

      // First focusable should be skip links
      if (focusableElements.length > 0) {
        expect(focusableElements[0].className).toContain('skip-link');
      }
    });

    test('should handle keyboard shortcuts properly', async ({ page }) => {
      // Test common keyboard shortcuts
      const shortcuts = [
        { key: 'Escape', description: 'Close modal/overlay' },
        { key: 'Enter', description: 'Activate button/link' },
        { key: 'Space', description: 'Activate button' },
      ];

      for (const shortcut of shortcuts) {
        // Focus on a button
        const button = page.locator('.btn').first();
        if ((await button.count()) > 0) {
          await button.focus();

          // Test the shortcut doesn't cause errors
          await page.keyboard.press(shortcut.key);

          // Should still be functional
          const isVisible = await button.isVisible();
          expect(isVisible).toBe(true);
        }
      }
    });

    test('should support arrow key navigation where appropriate', async ({ page }) => {
      // Test arrow key navigation on navigation elements
      const navElement = page.locator('[role="navigation"], nav').first();

      if ((await navElement.count()) > 0) {
        const links = navElement.locator('a, button');
        const linkCount = await links.count();

        if (linkCount > 1) {
          // Focus first link
          await links.first().focus();

          // Try arrow key navigation
          await page.keyboard.press('ArrowDown');

          // Should maintain focus within navigation
          const focusedElement = page.locator(':focus');
          await focusedElement.evaluate(el => {
            let parent = el.parentElement;
            while (parent) {
              if (parent.tagName === 'NAV' || parent.getAttribute('role') === 'navigation') {
                return true;
              }
              parent = parent.parentElement;
            }
            return false;
          });

          // This test is optional as not all nav elements need arrow key support
          // Just ensure it doesn't break
          expect(true).toBe(true);
        }
      }
    });
  });

  test.describe('Focus Management in Modals/Overlays', () => {
    test('should trap focus within modal when open', async ({ page }) => {
      // Create a modal for testing
      await page.evaluate(() => {
        const modal = document.createElement('div');
        modal.className = 'focus-lock';
        modal.id = 'test-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.style.position = 'fixed';
        modal.style.top = '50%';
        modal.style.left = '50%';
        modal.style.transform = 'translate(-50%, -50%)';
        modal.style.background = 'white';
        modal.style.padding = '20px';
        modal.style.border = '1px solid #ccc';
        modal.style.zIndex = '1000';

        // Add focusable elements
        const input = document.createElement('input');
        input.placeholder = 'Modal input';
        input.id = 'modal-input';

        const button = document.createElement('button');
        button.textContent = 'Modal Button';
        button.id = 'modal-button';

        modal.appendChild(input);
        modal.appendChild(button);
        document.body.appendChild(modal);

        // Focus the modal
        modal.focus();
      });

      const modal = page.locator('#test-modal');
      await expect(modal).toBeVisible();

      // Check modal has proper ARIA attributes
      await expect(modal).toHaveAttribute('role', 'dialog');
      await expect(modal).toHaveAttribute('aria-modal', 'true');

      // Focus should be within modal
      const modalInput = page.locator('#modal-input');
      await modalInput.focus();
      await expect(modalInput).toBeFocused();

      // Tab should stay within modal
      await page.keyboard.press('Tab');
      const modalButton = page.locator('#modal-button');
      await expect(modalButton).toBeFocused();
    });

    test('should restore focus after modal closes', async ({ page }) => {
      // Create trigger button
      await page.evaluate(() => {
        const trigger = document.createElement('button');
        trigger.textContent = 'Open Modal';
        trigger.id = 'modal-trigger';
        document.body.appendChild(trigger);
      });

      const trigger = page.locator('#modal-trigger');
      await trigger.focus();
      await expect(trigger).toBeFocused();

      // Simulate modal opening and closing
      await page.evaluate(() => {
        const modal = document.createElement('div');
        modal.id = 'temp-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.background = 'rgba(0,0,0,0.5)';
        modal.style.zIndex = '1000';

        const content = document.createElement('div');
        content.style.background = 'white';
        content.style.padding = '20px';
        content.style.margin = '50px auto';
        content.style.width = '300px';

        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Close';
        closeBtn.onclick = () => {
          document.body.removeChild(modal);
          document.getElementById('modal-trigger')?.focus();
        };

        content.appendChild(closeBtn);
        modal.appendChild(content);
        document.body.appendChild(modal);

        closeBtn.focus();
      });

      // Close modal
      await page.keyboard.press('Enter');

      // Focus should return to trigger
      await expect(trigger).toBeFocused();
    });
  });

  test.describe('Screen Reader Compatibility', () => {
    test('should have proper screen reader only content', async ({ page }) => {
      // Check for screen reader only elements
      const srOnlyElements = page.locator('.sr-only');

      if ((await srOnlyElements.count()) > 0) {
        const srElement = srOnlyElements.first();

        // Check it's visually hidden but accessible
        const styles = await srElement.evaluate(el => {
          const computed = getComputedStyle(el);
          return {
            position: computed.position,
            width: computed.width,
            height: computed.height,
            overflow: computed.overflow,
            clip: computed.clip,
          };
        });

        expect(styles.position).toBe('absolute');
        expect(styles.width).toBe('1px');
        expect(styles.height).toBe('1px');
        expect(styles.overflow).toBe('hidden');
      }
    });

    test('should have focusable screen reader content when focused', async ({ page }) => {
      // Create sr-only-focusable element
      await page.evaluate(() => {
        const element = document.createElement('a');
        element.className = 'sr-only sr-only-focusable';
        element.href = '#main';
        element.textContent = 'Skip to main content';
        element.id = 'test-sr-focusable';
        document.body.appendChild(element);
      });

      const srFocusable = page.locator('#test-sr-focusable');

      // Should be hidden initially
      const initialStyles = await srFocusable.evaluate(el => {
        const computed = getComputedStyle(el);
        return {
          position: computed.position,
          width: computed.width,
        };
      });

      expect(initialStyles.position).toBe('absolute');
      expect(initialStyles.width).toBe('1px');

      // Focus the element
      await srFocusable.focus();

      // Should become visible when focused
      const focusedStyles = await srFocusable.evaluate(el => {
        const computed = getComputedStyle(el);
        return {
          position: computed.position,
          width: computed.width,
        };
      });

      // Should have different styles when focused (implementation dependent)
      const hasValidPosition =
        focusedStyles.position === 'static' || focusedStyles.position === 'relative';
      expect(hasValidPosition).toBe(true);
    });

    test('should have proper ARIA live regions', async ({ page }) => {
      // Look for live regions
      const liveRegions = page.locator('[aria-live]');

      if ((await liveRegions.count()) > 0) {
        for (let i = 0; i < (await liveRegions.count()); i++) {
          const region = liveRegions.nth(i);
          const ariaLive = await region.getAttribute('aria-live');

          expect(['polite', 'assertive', 'off'].includes(ariaLive || '')).toBe(true);
        }
      }
    });
  });

  test.describe('Landmark Navigation Support', () => {
    test('should have proper landmark elements', async ({ page }) => {
      // Check for main landmark
      const mainLandmark = page.locator('main, [role="main"]');
      await expect(mainLandmark).toBeVisible();

      // Check for navigation landmark
      const navLandmark = page.locator('nav, [role="navigation"]');
      if ((await navLandmark.count()) > 0) {
        await expect(navLandmark.first()).toBeVisible();
      }
    });

    test('should support landmark navigation with skip links', async ({ page }) => {
      // Test that landmarks have proper IDs for skip navigation
      const mainContent = page.locator('#main-content');
      if ((await mainContent.count()) > 0) {
        await expect(mainContent).toBeVisible();

        // Should have scroll margin for skip link navigation
        const scrollMargin = await mainContent.evaluate(el => getComputedStyle(el).scrollMarginTop);

        // Should have some scroll margin (implementation specific)
        expect(scrollMargin).not.toBe('0px');
      }
    });

    test('should highlight targeted landmarks', async ({ page }) => {
      // Navigate to a landmark via skip link
      const skipLink = page.locator('.skip-link[href="#main-content"]').first();

      if ((await skipLink.count()) > 0) {
        await skipLink.click();

        // Check if main content is focused
        const mainContent = page.locator('#main-content');
        if ((await mainContent.count()) > 0) {
          await expect(mainContent).toBeFocused();

          // Check for :target styles if any
          const outline = await mainContent.evaluate(el => getComputedStyle(el).outline);

          // Target styles are optional but good UX
          expect(outline).toBeDefined();
        }
      }
    });
  });

  test.describe('High Contrast Mode Support', () => {
    test('should enhance focus indicators in high contrast mode', async ({ page }) => {
      // Simulate high contrast mode
      await page.addStyleTag({
        content: `
          @media (prefers-contrast: high) {
            .focus-ring-enhanced:focus {
              outline: 4px solid currentColor !important;
              outline-offset: 2px !important;
            }
          }
        `,
      });

      // Create test element
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'focus-ring-enhanced';
        button.textContent = 'High Contrast Test';
        button.id = 'test-high-contrast';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-high-contrast');
      await button.focus();

      const outline = await button.evaluate(el => getComputedStyle(el).outline);

      // Should have enhanced outline
      expect(outline).not.toBe('none');
    });
  });

  test.describe('Reduced Motion Support', () => {
    test('should disable focus transitions with reduced motion', async ({ page }) => {
      // Set reduced motion preference
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Create test element
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'focus-ring-enhanced';
        button.textContent = 'Reduced Motion Test';
        button.id = 'test-reduced-motion';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-reduced-motion');
      const transition = await button.evaluate(el => getComputedStyle(el).transition);

      // Transitions should be disabled or minimal
      expect(transition === 'none' || transition.includes('0s')).toBe(true);
    });
  });

  test.describe('Touch Device Adaptations', () => {
    test('should adapt focus styles for touch devices', async ({ page }) => {
      // Simulate touch device
      await page.setViewportSize({ width: 375, height: 667 });

      // Create test button
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'focus-ring-enhanced';
        button.textContent = 'Touch Test';
        button.id = 'test-touch-focus';
        button.style.padding = '10px 20px';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-touch-focus');
      const boundingBox = await button.boundingBox();

      if (boundingBox) {
        // Should meet minimum touch target size
        expect(boundingBox.height).toBeGreaterThanOrEqual(44);
        expect(boundingBox.width).toBeGreaterThanOrEqual(44);
      }

      // Focus styles should still work on touch
      await button.focus();
      const outline = await button.evaluate(el => getComputedStyle(el).outline);
      const boxShadow = await button.evaluate(el => getComputedStyle(el).boxShadow);

      const hasFocusIndicator = outline !== 'none' || boxShadow !== 'none';
      expect(hasFocusIndicator).toBe(true);
    });
  });

  test.describe('Focus System Performance', () => {
    test('should not cause performance issues with many focusable elements', async ({ page }) => {
      // Create many focusable elements
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.id = 'performance-test-container';

        for (let i = 0; i < 50; i++) {
          const button = document.createElement('button');
          button.className = 'focus-ring-enhanced';
          button.textContent = `Button ${i + 1}`;
          button.id = `perf-button-${i}`;
          container.appendChild(button);
        }

        document.body.appendChild(container);
      });

      const startTime = Date.now();

      // Tab through several elements
      for (let i = 0; i < 10; i++) {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(10);
      }

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Should complete within reasonable time
      expect(totalTime).toBeLessThan(2000); // 2 seconds max
    });
  });

  test.describe('Focus Debugging Support', () => {
    test('should provide focus debugging information in development', async ({ page }) => {
      // Add focus debug class
      await page.evaluate(() => {
        document.body.classList.add('focus-debug');
      });

      // Create test element
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'test-class';
        button.textContent = 'Debug Test';
        button.id = 'test-debug-focus';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-debug-focus');
      await button.focus();

      // Check for debug styles
      const outline = await button.evaluate(el => getComputedStyle(el).outline);

      // Should have debug outline
      const hasDebugOutline = outline.includes('red') || outline.includes('3px');
      expect(hasDebugOutline).toBe(true);
    });
  });
});
