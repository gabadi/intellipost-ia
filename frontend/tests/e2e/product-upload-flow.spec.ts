import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Product Upload Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the product creation page
    await page.goto('/products/new');

    // Wait for the page to load
    await expect(page.getByText('Create New Product')).toBeVisible();
  });

  test('complete mobile product creation workflow', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Verify mobile-optimized layout
    await expect(page.locator('.product-creation-form')).toBeVisible();

    // Check that upload zone is visible
    await expect(page.getByText('Add Product Photos')).toBeVisible();
    await expect(page.getByText('0/8')).toBeVisible();

    // Verify form is initially invalid
    const submitButton = page.getByRole('button', { name: /create product/i });
    await expect(submitButton).toBeDisabled();

    // Test file upload
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /browse files/i }).click();
    const fileChooser = await fileChooserPromise;

    // Upload test images (assuming we have test images in the test fixtures)
    await fileChooser.setFiles([
      path.join(__dirname, '../fixtures/test-image-1.jpg'),
      path.join(__dirname, '../fixtures/test-image-2.jpg'),
    ]);

    // Wait for images to be processed
    await expect(page.getByText('2/8')).toBeVisible();
    await expect(page.getByText('Images ready')).toBeVisible();

    // Add product description
    const textarea = page.getByRole('textbox');
    await textarea.fill(
      'iPhone 13 Pro usado en excelente estado. Batería al 85%, sin rayones, incluye cargador original y funda protectora.'
    );

    // Wait for validation
    await expect(page.getByText('Description ready')).toBeVisible();
    await expect(page.getByText('Ready to create your product!')).toBeVisible();

    // Verify submit button is now enabled
    await expect(submitButton).not.toBeDisabled();

    // Test form submission
    await submitButton.click();

    // Verify loading state
    await expect(page.getByText('Creating...')).toBeVisible();
    await expect(submitButton).toBeDisabled();

    // Wait for completion and redirect
    await page.waitForURL('/products', { timeout: 10000 });
    await expect(page.url()).toContain('/products');
  });

  test('image drag and drop functionality', async ({ page }) => {
    // Create a test file
    const testImagePath = path.join(__dirname, '../fixtures/test-image-1.jpg');

    // Verify upload zone is present
    const uploadZone = page.locator('.upload-zone');
    await expect(uploadZone).toBeVisible();

    // Simulate drag and drop
    await uploadZone.setInputFiles(testImagePath);

    // Verify image was added
    await expect(page.getByText('1/8')).toBeVisible();
    await expect(page.locator('.image-thumbnail')).toBeVisible();
  });

  test('image management features', async ({ page }) => {
    // Upload multiple images first
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /browse files/i }).click();
    const fileChooser = await fileChooserPromise;

    await fileChooser.setFiles([
      path.join(__dirname, '../fixtures/test-image-1.jpg'),
      path.join(__dirname, '../fixtures/test-image-2.jpg'),
      path.join(__dirname, '../fixtures/test-image-3.jpg'),
    ]);

    // Wait for images to be processed
    await expect(page.getByText('3/8')).toBeVisible();

    // Test primary image selection
    const secondImage = page.locator('.image-thumbnail').nth(1);
    await secondImage.hover();
    await secondImage.locator('button[title="Set as primary"]').click();

    // Verify primary badge
    await expect(secondImage.locator('.primary-badge')).toBeVisible();

    // Test image removal
    await secondImage.hover();
    await secondImage.locator('button[title="Remove image"]').click();

    // Confirm removal
    await page.getByRole('button', { name: /remove/i }).click();

    // Verify image count decreased
    await expect(page.getByText('2/8')).toBeVisible();
  });

  test('form validation and error handling', async ({ page }) => {
    const textarea = page.getByRole('textbox');
    const submitButton = page.getByRole('button', { name: /create product/i });

    // Test empty form
    await expect(submitButton).toBeDisabled();
    await expect(page.getByText('Add product photos')).toBeVisible();
    await expect(page.getByText('Add product description')).toBeVisible();

    // Test description too short
    await textarea.fill('short');
    await expect(page.getByText(/minimum 10 characters required/i)).toBeVisible();

    // Test description too long
    const longText = 'x'.repeat(501);
    await textarea.fill(longText);
    await expect(page.getByText(/maximum 500 characters allowed/i)).toBeVisible();

    // Test valid description without images
    await textarea.fill('This is a valid product description with enough characters');
    await expect(page.getByText('Description ready')).toBeVisible();
    await expect(submitButton).toBeDisabled(); // Still disabled due to no images

    // Test character counter
    const currentLength = (await textarea.inputValue()).length;
    await expect(page.getByText(`${currentLength}/500`)).toBeVisible();
  });

  test('auto-save functionality', async ({ page }) => {
    const textarea = page.getByRole('textbox');

    // Add some text
    await textarea.fill('Test auto-save functionality');

    // Wait for auto-save indicator
    await expect(page.getByText(/automatically saved/i)).toBeVisible();

    // Refresh page and verify data is restored
    await page.reload();
    await expect(textarea).toHaveValue('Test auto-save functionality');
  });

  test('camera functionality (mock)', async ({ page }) => {
    // Mock camera permissions
    await page.context().grantPermissions(['camera']);

    // Click camera button
    await page.getByRole('button', { name: /take photos/i }).click();

    // Verify camera modal opens
    await expect(page.locator('.camera-modal')).toBeVisible();
    await expect(page.getByText('Take Photo')).toBeVisible();

    // Close camera modal
    await page.locator('.close-btn').click();
    await expect(page.locator('.camera-modal')).not.toBeVisible();
  });

  test('responsive design across breakpoints', async ({ page }) => {
    // Test mobile (375px)
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.product-creation-form')).toBeVisible();

    // Verify mobile-specific layout
    const formActions = page.locator('.form-actions');
    await expect(formActions).toHaveCSS('flex-direction', 'column');

    // Test tablet (768px)
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('.product-creation-form')).toBeVisible();

    // Test desktop (1200px)
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.locator('.product-creation-form')).toBeVisible();

    // Verify desktop layout
    await expect(formActions).toHaveCSS('flex-direction', 'row');
  });

  test('keyboard navigation and accessibility', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: /take photos/i })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: /browse files/i })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('textbox')).toBeFocused();

    // Test Enter key on buttons
    await page.getByRole('button', { name: /browse files/i }).focus();
    await page.keyboard.press('Enter');
    // Should trigger file dialog (will be blocked in test environment)

    // Verify ARIA labels
    await expect(page.getByRole('textbox')).toHaveAttribute('aria-label', /product description/i);
  });

  test('error recovery and retry functionality', async ({ page }) => {
    // Simulate network error during submission
    await page.route('/api/products', route => {
      route.abort('failed');
    });

    // Fill out form
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: /browse files/i }).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles([path.join(__dirname, '../fixtures/test-image-1.jpg')]);

    const textarea = page.getByRole('textbox');
    await textarea.fill('Test product for error handling');

    // Wait for form to be valid
    await expect(page.getByText('Ready to create your product!')).toBeVisible();

    // Submit and expect error
    await page.getByRole('button', { name: /create product/i }).click();

    // Verify error message appears
    await expect(page.getByText(/failed to create product/i)).toBeVisible();

    // Remove network interception for retry
    await page.unroute('/api/products');

    // Mock successful response
    await page.route('/api/products', route => {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'test-product-1', status: 'created' }),
      });
    });

    // Retry submission
    await page.getByRole('button', { name: /create product/i }).click();

    // Should redirect to products list
    await page.waitForURL('/products');
  });

  test.skip('camera capture workflow', async ({ page }) => {
    // Skip this test in CI as it requires actual camera access
    // This would be run manually or in environments with camera simulation

    await page.context().grantPermissions(['camera']);

    await page.getByRole('button', { name: /take photos/i }).click();
    await expect(page.locator('.camera-modal')).toBeVisible();

    // Wait for camera initialization
    await page.waitForSelector('.video-preview');

    // Capture photo
    await page.locator('.capture-btn').click();

    // Accept photo
    await page.getByRole('button', { name: /use photo/i }).click();

    // Verify image was added
    await expect(page.getByText('1/8')).toBeVisible();
  });
});
