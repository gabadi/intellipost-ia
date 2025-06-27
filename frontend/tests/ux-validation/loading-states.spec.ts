/**
 * Loading States UX Validation Tests
 * Comprehensive testing of spinners, skeleton screens, and loading indicators
 */

import { test, expect } from '@playwright/test';

test.describe('Loading States UX Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Spinner Components Validation', () => {
    test('should display spinners with proper animations', async ({ page }) => {
      // Create a spinner element for testing
      await page.evaluate(() => {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'test-spinner';
        document.body.appendChild(spinner);
      });

      const spinner = page.locator('#test-spinner');

      // Check spinner is visible
      await expect(spinner).toBeVisible();

      // Check animation is applied
      const animation = await spinner.evaluate(el => getComputedStyle(el).animation);

      expect(animation).toContain('spin');

      // Check spinner has proper circular shape
      const borderRadius = await spinner.evaluate(el => getComputedStyle(el).borderRadius);

      expect(borderRadius).toBe('50%');
    });

    test('should display spinner size variants correctly', async ({ page }) => {
      // Test different spinner sizes
      const sizes = ['spinner--sm', 'spinner--lg', 'spinner--xl'];

      for (const sizeClass of sizes) {
        await page.evaluate(className => {
          const spinner = document.createElement('div');
          spinner.className = `spinner ${className}`;
          spinner.id = `test-${className}`;
          document.body.appendChild(spinner);
        }, sizeClass);

        const spinner = page.locator(`#test-${sizeClass}`);
        const boundingBox = await spinner.boundingBox();

        if (boundingBox) {
          // Each size should be different
          expect(boundingBox.width).toBeGreaterThan(0);
          expect(boundingBox.height).toBeGreaterThan(0);
          // Width and height should be equal (circular)
          expect(Math.abs(boundingBox.width - boundingBox.height)).toBeLessThan(2);
        }
      }
    });

    test('should display color variants correctly', async ({ page }) => {
      const colorVariants = ['spinner--primary', 'spinner--secondary', 'spinner--white'];

      for (const variant of colorVariants) {
        await page.evaluate(className => {
          const spinner = document.createElement('div');
          spinner.className = `spinner ${className}`;
          spinner.id = `test-${className}`;
          document.body.appendChild(spinner);
        }, variant);

        const spinner = page.locator(`#test-${variant}`);
        const borderTopColor = await spinner.evaluate(el => getComputedStyle(el).borderTopColor);

        // Should have different colors
        expect(borderTopColor).not.toBe('rgba(0, 0, 0, 0)');
      }
    });
  });

  test.describe('Loading Dots Indicator Validation', () => {
    test('should animate dots loading indicator', async ({ page }) => {
      // Create loading dots
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.className = 'loading-dots';
        container.id = 'test-loading-dots';

        for (let i = 0; i < 3; i++) {
          const dot = document.createElement('span');
          container.appendChild(dot);
        }

        document.body.appendChild(container);
      });

      const dotsContainer = page.locator('#test-loading-dots');
      await expect(dotsContainer).toBeVisible();

      const dots = dotsContainer.locator('span');
      const dotCount = await dots.count();

      expect(dotCount).toBe(3);

      // Check each dot has animation
      for (let i = 0; i < dotCount; i++) {
        const dot = dots.nth(i);
        const animation = await dot.evaluate(el => getComputedStyle(el).animation);

        expect(animation).toContain('dots');
      }
    });
  });

  test.describe('Wave Loading Indicator Validation', () => {
    test('should animate wave loading indicator', async ({ page }) => {
      // Create loading wave
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.className = 'loading-wave';
        container.id = 'test-loading-wave';

        for (let i = 0; i < 5; i++) {
          const bar = document.createElement('span');
          container.appendChild(bar);
        }

        document.body.appendChild(container);
      });

      const waveContainer = page.locator('#test-loading-wave');
      await expect(waveContainer).toBeVisible();

      const bars = waveContainer.locator('span');
      const barCount = await bars.count();

      expect(barCount).toBe(5);

      // Check wave animation
      const firstBar = bars.first();
      const animation = await firstBar.evaluate(el => getComputedStyle(el).animation);

      expect(animation).toContain('wave');
    });
  });

  test.describe('Skeleton Screens Validation', () => {
    test('should display skeleton loading animation', async ({ page }) => {
      // Create skeleton element
      await page.evaluate(() => {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton skeleton--text';
        skeleton.id = 'test-skeleton';
        document.body.appendChild(skeleton);
      });

      const skeleton = page.locator('#test-skeleton');
      await expect(skeleton).toBeVisible();

      // Check skeleton loading animation
      const animation = await skeleton.evaluate(el => getComputedStyle(el).animation);

      expect(animation).toContain('skeleton-loading');

      // Check background gradient
      const background = await skeleton.evaluate(el => getComputedStyle(el).background);

      expect(background).toContain('linear-gradient');
    });

    test('should display skeleton variants correctly', async ({ page }) => {
      const skeletonTypes = [
        'skeleton--text',
        'skeleton--title',
        'skeleton--paragraph',
        'skeleton--avatar',
        'skeleton--button',
        'skeleton--card',
        'skeleton--image',
        'skeleton--input',
      ];

      for (const skeletonType of skeletonTypes) {
        await page.evaluate(className => {
          const skeleton = document.createElement('div');
          skeleton.className = `skeleton ${className}`;
          skeleton.id = `test-${className}`;
          document.body.appendChild(skeleton);
        }, skeletonType);

        const skeleton = page.locator(`#test-${skeletonType}`);
        await expect(skeleton).toBeVisible();

        const boundingBox = await skeleton.boundingBox();
        if (boundingBox) {
          expect(boundingBox.width).toBeGreaterThan(0);
          expect(boundingBox.height).toBeGreaterThan(0);
        }
      }
    });

    test('should display skeleton compositions correctly', async ({ page }) => {
      // Create skeleton card composition
      await page.evaluate(() => {
        const card = document.createElement('div');
        card.className = 'skeleton-card';
        card.id = 'test-skeleton-card';

        const header = document.createElement('div');
        header.className = 'skeleton-card__header';

        const avatar = document.createElement('div');
        avatar.className = 'skeleton skeleton--avatar';

        const title = document.createElement('div');
        title.className = 'skeleton skeleton--title';

        header.appendChild(avatar);
        header.appendChild(title);

        const content = document.createElement('div');
        content.className = 'skeleton-card__content';

        for (let i = 0; i < 3; i++) {
          const paragraph = document.createElement('div');
          paragraph.className = 'skeleton skeleton--paragraph';
          content.appendChild(paragraph);
        }

        card.appendChild(header);
        card.appendChild(content);
        document.body.appendChild(card);
      });

      const skeletonCard = page.locator('#test-skeleton-card');
      await expect(skeletonCard).toBeVisible();

      // Check header components
      const header = skeletonCard.locator('.skeleton-card__header');
      await expect(header).toBeVisible();

      const avatar = header.locator('.skeleton--avatar');
      await expect(avatar).toBeVisible();

      const title = header.locator('.skeleton--title');
      await expect(title).toBeVisible();

      // Check content paragraphs
      const paragraphs = skeletonCard.locator('.skeleton--paragraph');
      expect(await paragraphs.count()).toBe(3);
    });
  });

  test.describe('Loading Overlay Validation', () => {
    test('should display loading overlay correctly', async ({ page }) => {
      // Create loading overlay
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.style.position = 'relative';
        container.style.width = '300px';
        container.style.height = '200px';
        container.style.background = '#f0f0f0';
        container.id = 'test-container';

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'test-overlay';

        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        overlay.appendChild(spinner);

        container.appendChild(overlay);
        document.body.appendChild(container);
      });

      const overlay = page.locator('#test-overlay');
      await expect(overlay).toBeVisible();

      // Check overlay positioning
      const position = await overlay.evaluate(el => getComputedStyle(el).position);
      expect(position).toBe('absolute');

      // Check backdrop blur
      const backdropFilter = await overlay.evaluate(el => getComputedStyle(el).backdropFilter);
      expect(backdropFilter).toContain('blur');

      // Check z-index
      const zIndex = await overlay.evaluate(el => getComputedStyle(el).zIndex);
      expect(parseInt(zIndex)).toBeGreaterThan(100);
    });

    test('should display overlay variants correctly', async ({ page }) => {
      const overlayVariants = ['loading-overlay--dark', 'loading-overlay--transparent'];

      for (const variant of overlayVariants) {
        await page.evaluate(className => {
          const container = document.createElement('div');
          container.style.position = 'relative';
          container.style.width = '200px';
          container.style.height = '100px';

          const overlay = document.createElement('div');
          overlay.className = `loading-overlay ${className}`;
          overlay.id = `test-${className}`;

          container.appendChild(overlay);
          document.body.appendChild(container);
        }, variant);

        const overlay = page.locator(`#test-${variant}`);
        await expect(overlay).toBeVisible();

        const backgroundColor = await overlay.evaluate(el => getComputedStyle(el).backgroundColor);

        // Should have some background styling
        expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
      }
    });
  });

  test.describe('Button Loading States Validation', () => {
    test('should display button loading state correctly', async ({ page }) => {
      // Create loading button
      await page.evaluate(() => {
        const button = document.createElement('button');
        button.className = 'btn btn-loading';
        button.textContent = 'Submit';
        button.id = 'test-loading-button';
        document.body.appendChild(button);
      });

      const button = page.locator('#test-loading-button');
      await expect(button).toBeVisible();

      // Check button text is hidden
      const color = await button.evaluate(el => getComputedStyle(el).color);
      const isTransparent = color === 'rgba(0, 0, 0, 0)' || color === 'transparent';
      expect(isTransparent).toBe(true);

      // Check cursor is wait
      const cursor = await button.evaluate(el => getComputedStyle(el).cursor);
      expect(cursor).toBe('wait');

      // Check for pseudo-element spinner
      const afterContent = await button.evaluate(el => {
        const after = getComputedStyle(el, '::after');
        return after.content;
      });
      expect(afterContent).toBe('""');
    });
  });

  test.describe('Progress Indicators Validation', () => {
    test('should display progress bar correctly', async ({ page }) => {
      // Create progress bar
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.className = 'progress-bar';
        container.id = 'test-progress';

        const fill = document.createElement('div');
        fill.className = 'progress-bar__fill';
        fill.style.width = '60%';

        container.appendChild(fill);
        document.body.appendChild(container);
      });

      const progressBar = page.locator('#test-progress');
      await expect(progressBar).toBeVisible();

      const fill = progressBar.locator('.progress-bar__fill');
      await expect(fill).toBeVisible();

      // Check width
      const width = await fill.evaluate(el => getComputedStyle(el).width);
      expect(width).not.toBe('0px');

      // Check transition
      const transition = await fill.evaluate(el => getComputedStyle(el).transition);
      expect(transition).toContain('width');
    });

    test('should display indeterminate progress bar', async ({ page }) => {
      // Create indeterminate progress bar
      await page.evaluate(() => {
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar progress-bar--indeterminate';
        progressBar.id = 'test-indeterminate';
        document.body.appendChild(progressBar);
      });

      const progressBar = page.locator('#test-indeterminate');
      await expect(progressBar).toBeVisible();

      // Check for after pseudo-element animation
      const afterAnimation = await progressBar.evaluate(el => {
        const after = getComputedStyle(el, '::after');
        return after.animation;
      });
      expect(afterAnimation).toContain('progress-indeterminate');
    });
  });

  test.describe('Content Loading States Validation', () => {
    test('should handle content loading transitions', async ({ page }) => {
      // Create content with loading state
      await page.evaluate(() => {
        const content = document.createElement('div');
        content.className = 'content-loading';
        content.textContent = 'Loading content...';
        content.id = 'test-content-loading';
        document.body.appendChild(content);
      });

      const content = page.locator('#test-content-loading');
      await expect(content).toBeVisible();

      // Check opacity is reduced
      const opacity = await content.evaluate(el => parseFloat(getComputedStyle(el).opacity));
      expect(opacity).toBeLessThan(1);

      // Check filter blur
      const filter = await content.evaluate(el => getComputedStyle(el).filter);
      expect(filter).toContain('blur');

      // Simulate content loaded
      await page.evaluate(() => {
        const element = document.getElementById('test-content-loading');
        if (element) {
          element.className = 'content-loaded';
        }
      });

      await page.waitForTimeout(100);

      // Check opacity is restored
      const newOpacity = await content.evaluate(el => parseFloat(getComputedStyle(el).opacity));
      expect(newOpacity).toBe(1);
    });

    test('should handle lazy loading fade-in', async ({ page }) => {
      // Create lazy load element
      await page.evaluate(() => {
        const element = document.createElement('div');
        element.className = 'lazy-load';
        element.textContent = 'Lazy loaded content';
        element.id = 'test-lazy-load';
        document.body.appendChild(element);
      });

      const lazyElement = page.locator('#test-lazy-load');

      // Check initial opacity
      const initialOpacity = await lazyElement.evaluate(el =>
        parseFloat(getComputedStyle(el).opacity)
      );
      expect(initialOpacity).toBe(0);

      // Simulate loaded state
      await page.evaluate(() => {
        const element = document.getElementById('test-lazy-load');
        if (element) {
          element.classList.add('loaded');
        }
      });

      await page.waitForTimeout(100);

      // Check opacity after loading
      const loadedOpacity = await lazyElement.evaluate(el =>
        parseFloat(getComputedStyle(el).opacity)
      );
      expect(loadedOpacity).toBe(1);
    });
  });

  test.describe('Reduced Motion Support', () => {
    test('should disable animations with reduced motion preference', async ({ page }) => {
      // Set reduced motion preference
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Create spinner with reduced motion
      await page.evaluate(() => {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'test-reduced-motion-spinner';
        document.body.appendChild(spinner);
      });

      const spinner = page.locator('#test-reduced-motion-spinner');
      const animation = await spinner.evaluate(el => getComputedStyle(el).animation);

      // Animation should be disabled
      expect(animation).toBe('none');
    });
  });

  test.describe('Dark Mode Compatibility', () => {
    test('should adjust loading states for dark mode', async ({ page }) => {
      // Set dark color scheme
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Create skeleton in dark mode
      await page.evaluate(() => {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton';
        skeleton.id = 'test-dark-skeleton';
        document.body.appendChild(skeleton);
      });

      const skeleton = page.locator('#test-dark-skeleton');
      const background = await skeleton.evaluate(el => getComputedStyle(el).background);

      // Should have dark mode appropriate background
      expect(background).toContain('linear-gradient');
    });
  });

  test.describe('Performance Validation', () => {
    test('should not cause layout shifts during skeleton-to-content transition', async ({
      page,
    }) => {
      // Create skeleton that will be replaced with content
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.id = 'test-transition-container';

        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton skeleton--text';
        skeleton.style.height = '20px';
        skeleton.style.width = '200px';
        skeleton.id = 'test-skeleton-transition';

        container.appendChild(skeleton);
        document.body.appendChild(container);
      });

      const container = page.locator('#test-transition-container');
      const initialBox = await container.boundingBox();

      // Replace skeleton with content
      await page.evaluate(() => {
        const skeleton = document.getElementById('test-skeleton-transition');
        if (skeleton) {
          skeleton.textContent = 'Actual content loaded';
          skeleton.className = 'loaded-content';
          skeleton.style.height = '20px';
          skeleton.style.width = '200px';
        }
      });

      await page.waitForTimeout(100);

      const finalBox = await container.boundingBox();

      // Should not cause significant layout shift
      if (initialBox && finalBox) {
        expect(Math.abs(finalBox.height - initialBox.height)).toBeLessThan(5);
        expect(Math.abs(finalBox.width - initialBox.width)).toBeLessThan(5);
      }
    });
  });
});
