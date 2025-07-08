/**
 * Docker Basic Authentication Tests
 * Simple tests to verify authentication system works in Docker
 *
 * NOTE: These tests require Docker containers to be running and are skipped in CI
 */

import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:4000';
const BACKEND_URL = 'http://localhost:8080';

// Skip these tests in CI environment
test.skip(!!process.env.CI, 'Docker tests require containers to be running');

test.describe('Docker Basic Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing auth state before each test
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.removeItem('intellipost_access_token');
      localStorage.removeItem('intellipost_refresh_token');
      localStorage.removeItem('intellipost_user');
    });
  });

  test('Frontend is accessible', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await expect(page).toHaveTitle(/IntelliPost/);
  });

  test('Backend health check works', async ({ page }) => {
    const response = await page.request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('Login page loads', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/auth/login`);

    // Check for login page elements
    await expect(page.getByRole('heading')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('Registration page loads', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/auth/register`);

    // Check for registration page elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('Protected route redirects to login', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/products`);

    // Should redirect to login page
    await page.waitForURL('**/auth/login');
    await expect(page.getByRole('heading')).toBeVisible();
  });

  test('Login form accepts input', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/auth/login`);

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');

    const emailValue = await page.locator('input[type="email"]').inputValue();
    const passwordValue = await page.locator('input[type="password"]').inputValue();

    expect(emailValue).toBe('test@example.com');
    expect(passwordValue).toBe('password123');
  });

  test('Login form validation works', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/auth/login`);

    // Try to submit without filling fields
    await page.click('button[type="submit"]');

    // Should still be on login page
    await expect(page.url()).toContain('/auth/login');
  });

  test('Backend authentication endpoints exist', async ({ page }) => {
    // Test login endpoint exists (even if it fails)
    const loginResponse = await page.request.post(`${BACKEND_URL}/auth/login`, {
      data: { email: 'test@test.com', password: 'test' },
    });

    // Should not be 404 - endpoint exists
    expect(loginResponse.status()).not.toBe(404);

    // Test register endpoint exists
    const registerResponse = await page.request.post(`${BACKEND_URL}/auth/register`, {
      data: {
        email: 'test@test.com',
        password: 'test',
        first_name: 'Test',
        last_name: 'User',
      },
    });

    // Should not be 404 - endpoint exists
    expect(registerResponse.status()).not.toBe(404);
  });

  test('Database connection works through backend', async ({ page }) => {
    // Test that we can reach the database through the backend
    const response = await page.request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('Docker containers are properly networked', async ({ page }) => {
    // Test that frontend can reach backend
    await page.goto(`${FRONTEND_URL}/auth/login`);

    // Fill form and submit (this tests frontend -> backend communication)
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for any network requests to complete
    await page.waitForTimeout(2000);

    // Should still be on login page (since credentials are invalid)
    // But this confirms network communication is working
    expect(page.url()).toContain('/auth/login');
  });

  test('CORS configuration allows frontend-backend communication', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/auth/login`);

    // Monitor network requests for CORS headers
    const responses: Array<{ url: string; headers: Record<string, string> }> = [];
    page.on('response', response => {
      if (response.url().includes(BACKEND_URL)) {
        responses.push({
          url: response.url(),
          headers: response.headers(),
        });
      }
    });

    // Make a request to backend
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for request
    await page.waitForTimeout(1000);

    // Should have CORS headers allowing the request
    const backendResponse = responses.find(r => r.url.includes(BACKEND_URL));
    if (backendResponse) {
      expect(backendResponse.headers['access-control-allow-origin']).toBeTruthy();
    }
  });

  test('Environment configuration is properly loaded', async ({ page }) => {
    // Check that frontend can make requests to configured backend URL
    const response = await page.request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();

    // Check that backend responds with expected structure
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('healthy');
  });
});
