import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts', // Only run .spec.ts files for E2E tests
  /* Global test timeout - 30 seconds per test */
  timeout: 30 * 1000,
  /* Test action timeout - 10 seconds per action */
  expect: {
    timeout: 10 * 1000,
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Optimize workers for performance */
  workers: process.env.CI ? 1 : 2,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI ? 'github' : 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.CI ? 'http://localhost:4173' : 'http://localhost:4000',

    /* Navigation timeout optimization */
    navigationTimeout: 10 * 1000,

    /* Action timeout optimization */
    actionTimeout: 8 * 1000,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Capture screenshot on failure */
    screenshot: 'only-on-failure',

    /* Capture video on failure - only in CI for faster local runs */
    video: process.env.CI ? 'retain-on-failure' : 'off',
  },

  /* Configure projects for essential browsers - optimized for speed */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Only run Firefox in CI or when explicitly requested
    ...(process.env.CI || process.env.PLAYWRIGHT_FIREFOX
      ? [
          {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
          },
        ]
      : []),

    // Only run mobile tests when explicitly requested
    ...(process.env.PLAYWRIGHT_MOBILE
      ? [
          {
            name: 'Mobile Chrome',
            use: { ...devices['Pixel 5'] },
          },
        ]
      : []),
  ],

  /* Run your local dev server before starting the tests */
  webServer: process.env.CI
    ? {
        // In CI, use preview server (faster startup)
        command: 'npm run preview',
        url: 'http://localhost:4173',
        timeout: 60 * 1000,
        stdout: 'ignore',
        stderr: 'pipe',
      }
    : {
        // Local development, use dev server
        command: 'npm run dev',
        url: 'http://localhost:4000',
        reuseExistingServer: true, // Allow reusing existing server for faster runs
        timeout: 180 * 1000, // More generous timeout for local dev
        stdout: 'ignore',
        stderr: 'pipe',
        env: {
          PORT: '4000',
        },
      },
});
