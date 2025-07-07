/// <reference types="vitest" />
import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit(), svelteTesting()],
  server: {
    port: 3000,
    host: true,
  },
  build: {
    target: 'es2022',
    cssMinify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte', '@sveltejs/kit'],
        },
        // Optimize CSS asset organization
        assetFileNames: assetInfo => {
          const info = assetInfo.name?.split('.') ?? [];
          const extType = info[info.length - 1];
          if (/css/i.test(extType)) {
            return 'assets/css/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
    cssCodeSplit: true,
  },
  css: {
    postcss: './postcss.config.js',
    devSourcemap: true,
  },
  // @ts-expect-error - vitest config in vite config
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'json-summary', 'html'],
      include: ['src/**/*'],
      exclude: ['src/**/*.{test,spec}.{js,ts}', 'src/test-setup.ts'],
    },
    // Fix CSS preprocessing issues in test environment
    css: true,
    transformMode: {
      web: [/\.[jt]sx?$/, /\.svelte$/],
    },
    server: {
      deps: {
        inline: ['@testing-library/svelte'],
      },
    },
  },
});
