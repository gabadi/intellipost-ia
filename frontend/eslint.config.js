import js from "@eslint/js";
import ts from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import svelte from "eslint-plugin-svelte";
import svelteParser from "svelte-eslint-parser";
// @ts-ignore - eslint-config-prettier doesn't have TypeScript types
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,ts,mjs}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module",
        project: "./tsconfig.json",
        extraFileExtensions: [".svelte"],
      },
    },
    plugins: {
      "@typescript-eslint": ts,
    },
    rules: {
      ...ts.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/explicit-module-boundary-types": "off",
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-var-requires": "off",
    },
  },
  {
    files: ["**/*.svelte"],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        parser: tsParser,
        project: "./tsconfig.json",
        extraFileExtensions: [".svelte"],
      },
    },
    plugins: {
      svelte,
      "@typescript-eslint": ts,
    },
    rules: {
      ...svelte.configs.recommended.rules,
      ...ts.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
    },
  },
  {
    files: ["**/*.{js,ts,svelte}"],
    rules: {
      // General code quality rules
      "no-console": "warn",
      "no-debugger": "error",
      "no-alert": "error",
      "prefer-const": "error",
      "no-var": "error",
      "object-shorthand": "error",
      "prefer-arrow-callback": "error",
      "prefer-template": "error",
      "template-curly-spacing": "error",
      quotes: ["error", "double", { avoidEscape: true }],
      semi: ["error", "always"],
      "comma-dangle": ["error", "never"],
      indent: ["error", 2],
      "max-len": ["warn", { code: 100, ignoreUrls: true }],
    },
  },
  prettier,
  {
    ignores: [
      "build/**",
      ".svelte-kit/**",
      "dist/**",
      "node_modules/**",
      "coverage/**",
      "*.config.js",
      "*.config.ts",
      "vite.config.*",
    ],
  },
];
