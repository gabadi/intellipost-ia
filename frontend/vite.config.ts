/// <reference types="vitest" />
import { sveltekit } from "@sveltejs/kit/vite";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit(), svelteTesting()],
  // @ts-expect-error - vitest config in vite config
  test: {
    include: ["src/**/*.{test,spec}.{js,ts}"],
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
    coverage: {
      reporter: ["text", "json", "json-summary", "html"],
      include: ["src/**/*"],
      exclude: ["src/**/*.{test,spec}.{js,ts}", "src/test-setup.ts"]
    }
  }
});
