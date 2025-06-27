/** @type {import('postcss-load-config').Config} */
export default {
  plugins: {
    'postcss-nesting': {},
    autoprefixer: {
      // Support last 2 versions of major browsers
      overrideBrowserslist: ['last 2 versions', '> 1%', 'not dead', 'not ie 11'],
    },
    // Only apply optimizations in production
    ...(process.env.NODE_ENV === 'production' && {
      cssnano: {
        preset: [
          'default',
          {
            // Preserve important CSS custom properties for theme switching
            customProperties: false,
            // Don't remove unused CSS (handled by Vite's built-in purging)
            discardUnused: false,
            // Preserve calc() functions for dynamic spacing
            calc: false,
            // Minimize file size while preserving functionality
            normalizeWhitespace: true,
            discardComments: {
              removeAll: true,
            },
            minifySelectors: true,
            minifyParams: true,
            mergeRules: true,
            // Optimize color values
            colormin: true,
            // Convert length values
            convertValues: true,
            // Merge media queries
            mergeMediaQueries: true,
          },
        ],
      },
    }),
  },
};
