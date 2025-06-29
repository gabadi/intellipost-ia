import { PurgeCSS } from 'purgecss';
import type { Plugin } from 'vite';

/**
 * Vite plugin to purge unused CSS for maximum bundle size reduction
 */
export function purgeCssPlugin(): Plugin {
  return {
    name: 'purge-css',
    generateBundle: {
      order: 'post',
      async handler(options: any, bundle: any): Promise<void> {
        // Only apply in production builds
        if (process.env.NODE_ENV !== 'production') {
          return;
        }

        try {
          // Find CSS assets in the bundle
          const cssAssets = Object.keys(bundle).filter(
            fileName => fileName.endsWith('.css') && bundle[fileName].type === 'asset'
          );

          for (const cssFileName of cssAssets) {
            const cssAsset = bundle[cssFileName];
            const originalCss = cssAsset.source;

            // Get all HTML and JS files for content analysis
            const htmlFiles = Object.keys(bundle).filter(
              fileName => fileName.endsWith('.html') && bundle[fileName].type === 'asset'
            );

            const jsFiles = Object.keys(bundle).filter(
              fileName => fileName.endsWith('.js') && bundle[fileName].type === 'chunk'
            );

            // Collect content for PurgeCSS analysis
            const content: Array<{ raw: string; extension: string }> = [];

            // Add HTML content
            htmlFiles.forEach(fileName => {
              content.push({
                raw: bundle[fileName].source,
                extension: 'html',
              });
            });

            // Add JS content
            jsFiles.forEach(fileName => {
              content.push({
                raw: bundle[fileName].code || '',
                extension: 'js',
              });
            });

            // Configure PurgeCSS
            const purgeCSS = new PurgeCSS();
            const result = await purgeCSS.purge({
              content,
              css: [{ raw: originalCss }],
              safelist: [
                // Theme-related classes
                'dark',
                /^theme-/,
                /^data-theme/,
                // Status-based classes
                /^status-/,
                /^color-status-/,
                // Button variants
                /^btn-/,
                // Interactive states
                'loading',
                'active',
                'focus',
                'hover',
                'disabled',
                // Utility classes that might be used dynamically
                /^text-/,
                /^bg-/,
                /^border-/,
                /^p-/,
                /^m-/,
                /^flex-/,
                /^grid-/,
                // Animation classes
                /^animate-/,
                /^transition-/,
                // Focus ring classes
                /^focus:/,
                // Error and validation states
                /^error/,
                /^valid/,
                /^invalid/,
                // Form states
                /^form-/,
                // Layout classes
                /^container/,
                /^layout-/,
                // CSS Variables (design tokens)
                /^:root/,
                /^--/,
                // Media queries and pseudo-classes
                /:hover/,
                /:focus/,
                /:active/,
                /:disabled/,
                // Dark mode selectors
                /\[data-theme=['"]dark['"]\]/,
                /@media \(prefers-color-scheme: dark\)/,
              ],
              keyframes: true,
              fontFace: true,
              variables: true,
            });

            if (result.length > 0) {
              const purgedCss = result[0].css;
              const originalSize = Buffer.byteLength(originalCss, 'utf8');
              const purgedSize = Buffer.byteLength(purgedCss, 'utf8');
              const reduction = (((originalSize - purgedSize) / originalSize) * 100).toFixed(1);

              console.log(
                `PurgeCSS: ${cssFileName} reduced from ${(originalSize / 1024).toFixed(1)}KB to ${(purgedSize / 1024).toFixed(1)}KB (${reduction}% reduction)`
              );

              // Update the CSS asset with purged content
              cssAsset.source = purgedCss;
            }
          }
        } catch (error) {
          console.warn('PurgeCSS processing failed:', (error as Error).message);
        }
      },
    },
  };
}
