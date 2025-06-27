/**
 * End-to-end tests for authentication flow
 */

import { test, expect, type Page } from '@playwright/test';

test.describe('Authentication Flow E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Start each test with a clean slate
    await page.goto('/');
  });

  test('User registration flow - complete journey', async ({ page }) => {
    // Navigate to registration page
    await page.click('[data-testid="register-link"]');
    await expect(page).toHaveURL('/auth/register');
    
    // Fill registration form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="first-name-input"]', 'Test');
    await page.fill('[data-testid="last-name-input"]', 'User');
    
    // Submit registration
    await page.click('[data-testid="register-submit"]');
    
    // Should redirect to dashboard or home after successful registration
    await expect(page).toHaveURL('/');
    
    // Should show success message or user indicator
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
  });

  test('User login flow - complete journey', async ({ page }) => {
    // First register a user (assuming registration works)
    await page.goto('/auth/register');
    await page.fill('[data-testid="email-input"]', 'login-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="first-name-input"]', 'Login');
    await page.fill('[data-testid="last-name-input"]', 'Test');
    await page.click('[data-testid="register-submit"]');
    
    // Logout first
    await page.click('[data-testid="logout-button"]');
    
    // Now test login flow
    await page.click('[data-testid="login-link"]');
    await expect(page).toHaveURL('/auth/login');
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', 'login-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    
    // Submit login
    await page.click('[data-testid="login-submit"]');
    
    // Should redirect after successful login
    await expect(page).toHaveURL('/');
    
    // Should show user indicator
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
  });

  test('Authentication state persistence across page refresh', async ({ page }) => {
    // Register and login user
    await page.goto('/auth/register');
    await page.fill('[data-testid="email-input"]', 'persist-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="first-name-input"]', 'Persist');
    await page.fill('[data-testid="last-name-input"]', 'Test');
    await page.click('[data-testid="register-submit"]');
    
    // Verify logged in state
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
    
    // Refresh page
    await page.reload();
    
    // Should maintain logged in state
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
    await expect(page).toHaveURL('/');
  });

  test('Logout functionality', async ({ page }) => {
    // Register and login user
    await page.goto('/auth/register');
    await page.fill('[data-testid="email-input"]', 'logout-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="first-name-input"]', 'Logout');
    await page.fill('[data-testid="last-name-input"]', 'Test');
    await page.click('[data-testid="register-submit"]');
    
    // Verify logged in state
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
    
    // Logout
    await page.click('[data-testid="logout-button"]');
    
    // Should redirect to login or home page
    await expect(page.locator('[data-testid="user-profile"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="login-link"]')).toBeVisible();
  });

  test('Protected route access control', async ({ page }) => {
    // Try to access protected route without authentication
    await page.goto('/products/new');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login');
    
    // Login first
    await page.fill('[data-testid="email-input"]', 'protected-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-submit"]');
    
    // Now try accessing protected route
    await page.goto('/products/new');
    
    // Should be able to access the protected route
    await expect(page).toHaveURL('/products/new');
  });

  test('Form validation - registration', async ({ page }) => {
    await page.goto('/auth/register');
    
    // Test invalid email
    await page.fill('[data-testid="email-input"]', 'invalid-email');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="register-submit"]');
    
    // Should show email validation error
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    
    // Test weak password
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'weak');
    await page.click('[data-testid="register-submit"]');
    
    // Should show password validation error
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('Form validation - login', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Test with empty fields
    await page.click('[data-testid="login-submit"]');
    
    // Should show validation errors
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    
    // Test with invalid credentials
    await page.fill('[data-testid="email-input"]', 'nonexistent@example.com');
    await page.fill('[data-testid="password-input"]', 'WrongPassword123!');
    await page.click('[data-testid="login-submit"]');
    
    // Should show authentication error
    await expect(page.locator('[data-testid="auth-error"]')).toBeVisible();
  });

  test('Mobile responsive authentication forms', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/auth/register');
    
    // Test that form elements are properly sized for mobile
    const emailInput = page.locator('[data-testid="email-input"]');
    const passwordInput = page.locator('[data-testid="password-input"]');
    const submitButton = page.locator('[data-testid="register-submit"]');
    
    // Touch targets should be at least 44px
    const emailBox = await emailInput.boundingBox();
    const passwordBox = await passwordInput.boundingBox();
    const buttonBox = await submitButton.boundingBox();
    
    expect(emailBox?.height).toBeGreaterThanOrEqual(44);
    expect(passwordBox?.height).toBeGreaterThanOrEqual(44);
    expect(buttonBox?.height).toBeGreaterThanOrEqual(44);
    
    // Form should be usable on mobile
    await emailInput.fill('mobile-test@example.com');
    await passwordInput.fill('MobileTest123!');
    await page.fill('[data-testid="first-name-input"]', 'Mobile');
    await page.fill('[data-testid="last-name-input"]', 'Test');
    
    await submitButton.click();
    
    // Should successfully register on mobile
    await expect(page).toHaveURL('/');
  });

  test('Password visibility toggle functionality', async ({ page }) => {
    await page.goto('/auth/login');
    
    const passwordInput = page.locator('[data-testid="password-input"]');
    const toggleButton = page.locator('[data-testid="password-toggle"]');
    
    // Initially password should be hidden (type="password")
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Fill password
    await passwordInput.fill('TestPassword123!');
    
    // Click toggle to show password
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle to hide password again
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('Authentication error handling and recovery', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Test network error scenario (simulate by using invalid credentials)
    await page.fill('[data-testid="email-input"]', 'error-test@example.com');
    await page.fill('[data-testid="password-input"]', 'WrongPassword');
    await page.click('[data-testid="login-submit"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="auth-error"]')).toBeVisible();
    
    // Error should be dismissible
    await page.click('[data-testid="error-dismiss"]');
    await expect(page.locator('[data-testid="auth-error"]')).not.toBeVisible();
    
    // Form should be ready for retry
    await expect(page.locator('[data-testid="login-submit"]')).toBeEnabled();
  });

  test('Loading states during authentication', async ({ page }) => {
    await page.goto('/auth/register');
    
    // Fill form
    await page.fill('[data-testid="email-input"]', 'loading-test@example.com');
    await page.fill('[data-testid="password-input"]', 'LoadingTest123!');
    await page.fill('[data-testid="first-name-input"]', 'Loading');
    await page.fill('[data-testid="last-name-input"]', 'Test');
    
    // Submit and check loading state
    await page.click('[data-testid="register-submit"]');
    
    // Should show loading spinner
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    // Submit button should be disabled during loading
    await expect(page.locator('[data-testid="register-submit"]')).toBeDisabled();
    
    // Wait for completion
    await expect(page).toHaveURL('/', { timeout: 5000 });
  });

});