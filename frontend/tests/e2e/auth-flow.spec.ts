import { test, expect, type Page } from '@playwright/test';

// Test configuration
const TEST_USER_EMAIL = 'test@intellipost.ai';
const TEST_USER_PASSWORD = 'SecurePass123!';
const TEST_USER_FIRST_NAME = 'Test';
const TEST_USER_LAST_NAME = 'User';

// Helper to clear auth state
async function clearAuthState(page: Page) {
  await page.context().clearCookies();
  await page.evaluate(() => {
    localStorage.removeItem('intellipost_access_token');
    localStorage.removeItem('intellipost_refresh_token');
    localStorage.removeItem('intellipost_user');
  });
}

// Helper to check if user is authenticated
async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('intellipost_access_token'));
  return !!token;
}

test.describe('Authentication Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing auth state before each test
    await clearAuthState(page);
  });

  test.describe('Unauthenticated Access Protection', () => {
    test('should redirect to login when accessing protected dashboard', async ({ page }) => {
      // Try to access the dashboard directly
      await page.goto('/dashboard');

      // Should be redirected to login page
      await expect(page).toHaveURL(/\/auth\/login/);
      await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
    });

    test('should redirect to login when accessing protected products', async ({ page }) => {
      // Try to access products page directly
      await page.goto('/products');

      // Should be redirected to login page
      await expect(page).toHaveURL(/\/auth\/login/);
      await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
    });

    test('should redirect to login when accessing protected new product', async ({ page }) => {
      // Try to access new product page directly
      await page.goto('/products/new');

      // Should be redirected to login page
      await expect(page).toHaveURL(/\/auth\/login/);
      await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
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
  });

  test.describe('User Registration Flow', () => {
    test('should display registration form correctly', async ({ page }) => {
      await page.goto('/auth/register');

      // Check that form elements are present
      await expect(page.getByRole('heading', { name: /register|sign up|create account/i })).toBeVisible();
      await expect(page.getByLabel('First Name')).toBeVisible();
      await expect(page.getByLabel('Last Name')).toBeVisible();
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password', { exact: true })).toBeVisible();
      await expect(page.getByLabel(/confirm password/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /create|register|sign up/i })).toBeVisible();
    });

    test('should display form validation requirements', async ({ page }) => {
      await page.goto('/auth/register');

      // Try to submit empty form to check validation
      await page.getByRole('button', { name: /create|register|sign up/i }).click();

      // Form should prevent submission or show validation
      const firstNameField = page.getByLabel('First Name');
      const emailField = page.getByLabel('Email');
      const passwordField = page.getByLabel('Password', { exact: true });

      // Check that required fields are marked as required
      await expect(firstNameField).toHaveAttribute('required', '');
      await expect(emailField).toHaveAttribute('required', '');
      await expect(passwordField).toHaveAttribute('required', '');
    });
  });

  test.describe('User Login Flow', () => {
    test('should display login form correctly', async ({ page }) => {
      await page.goto('/auth/login');

      // Check that form elements are present
      await expect(page.getByRole('heading', { name: /sign in|login/i })).toBeVisible();
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in|login/i })).toBeVisible();

      // Check form validation
      const emailField = page.getByLabel('Email');
      const passwordField = page.getByLabel('Password');

      await expect(emailField).toHaveAttribute('required', '');
      await expect(passwordField).toHaveAttribute('required', '');
    });
  });

  test.describe('Navigation and Links', () => {
    test('should have proper navigation links on auth pages', async ({ page }) => {
      // Check login page links
      await page.goto('/auth/login');
      await expect(page.getByRole('link', { name: /register|sign up|create account/i })).toBeVisible();

      // Check register page links
      await page.goto('/auth/register');
      await expect(page.getByRole('link', { name: /login|sign in/i })).toBeVisible();
    });
  });

  test.describe('Backend Health Check', () => {
    test('should handle backend health check on landing page', async ({ page }) => {
      await page.goto('/');

      // Landing page should load without errors
      await expect(page.getByRole('heading', { name: 'IntelliPost AI' })).toBeVisible();
    });
  });

});
