import { test, expect } from '@playwright/test';

test.describe('Basic Security Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing auth state before each test
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.removeItem('intellipost_access_token');
      localStorage.removeItem('intellipost_refresh_token');
      localStorage.removeItem('intellipost_user');
    });
  });

  test('should show public landing page for unauthenticated users', async ({ page }) => {
    await page.goto('/');

    // Should stay on landing page
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: 'IntelliPost AI' })).toBeVisible();
    await expect(page.getByText('Intelligent Social Media Posting Platform')).toBeVisible();

    // Should show auth buttons
    await expect(page.getByRole('link', { name: 'Get Started' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Create Account' })).toBeVisible();
  });

  test('should redirect to login when accessing protected dashboard', async ({ page }) => {
    // Try to access the dashboard directly
    await page.goto('/dashboard');

    // Should be redirected to login page
    await expect(page).toHaveURL(/\/auth\/login/);
    await expect(page.getByRole('heading')).toBeVisible();
  });

  test('should redirect to login when accessing protected products', async ({ page }) => {
    // Try to access products page directly
    await page.goto('/products');

    // Should be redirected to login page
    await expect(page).toHaveURL(/\/auth\/login/);
    await expect(page.getByRole('heading')).toBeVisible();
  });

  test('should redirect to login when accessing protected new product', async ({ page }) => {
    // Try to access new product page directly
    await page.goto('/products/new');

    // Should be redirected to login page
    await expect(page).toHaveURL(/\/auth\/login/);
    await expect(page.getByRole('heading')).toBeVisible();
  });

  test('should display login form correctly', async ({ page }) => {
    await page.goto('/auth/login');

    // Check that form elements are present
    await expect(page.getByRole('heading')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in|login/i })).toBeVisible();
  });

  test('should display registration form correctly', async ({ page }) => {
    await page.goto('/auth/register');

    // Check that form elements are present
    await expect(page.getByRole('heading')).toBeVisible();
    await expect(page.getByLabel('First Name')).toBeVisible();
    await expect(page.getByLabel('Last Name')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password', { exact: true })).toBeVisible();
    await expect(page.getByRole('button')).toBeVisible();
  });
});
