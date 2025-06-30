import { readFileSync } from 'fs';
import { resolve } from 'path';
import type { Plugin } from 'vite';

/**
 * Vite plugin to inline critical CSS for improved First Contentful Paint
 */
export function criticalCssPlugin(): Plugin {
  return {
    name: 'critical-css',
    transformIndexHtml: {
      order: 'post',
      handler(html: string, context: any): string {
        // Only apply in production builds - check multiple environment indicators
        const isProduction =
          process.env.NODE_ENV === 'production' ||
          context?.bundle ||
          process.env.VITE_ENVIRONMENT === 'production';

        if (!isProduction) {
          return html;
        }

        try {
          // Read the critical CSS file
          const criticalCssPath = resolve(process.cwd(), 'src/styles/critical.css');
          const criticalCss = readFileSync(criticalCssPath, 'utf8');

          // Minify the critical CSS (basic minification)
          const minifiedCss = criticalCss
            .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
            .replace(/\s+/g, ' ') // Collapse whitespace
            .replace(/;\s*}/g, '}') // Remove semicolon before closing brace
            .replace(/\s*{\s*/g, '{') // Remove spaces around opening brace
            .replace(/\s*}\s*/g, '}') // Remove spaces around closing brace
            .replace(/\s*,\s*/g, ',') // Remove spaces around commas
            .replace(/\s*:\s*/g, ':') // Remove spaces around colons
            .replace(/\s*;\s*/g, ';') // Remove spaces around semicolons
            .trim();

          // Replace the placeholder comment with actual critical CSS
          return html.replace(
            '/* Critical CSS will be inlined here during build */\n      /* This is handled by the build process to reduce First Contentful Paint */',
            minifiedCss
          );
        } catch (error) {
          console.warn(
            'Critical CSS file not found or could not be read:',
            (error as Error).message
          );
          return html;
        }
      },
    },
  };
}
