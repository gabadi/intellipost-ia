import { test, expect } from '@playwright/test';

/**
 * UX Validation: MercadoLibre Navigation and Accessibility
 *
 * This test suite evaluates the user experience and accessibility of the
 * MercadoLibre OAuth integration feature navigation within the IntelliPost AI application.
 *
 * Epic 6 Story 2 Context:
 * - MercadoLibre OAuth integration with PKCE was implemented
 * - ML connection modal with pre-auth education
 * - ML setup page at `/ml-setup`
 * - OAuth callback handling at `/ml-setup/callback`
 *
 * User Issue:
 * - Users cannot find the MercadoLibre connection option in the navigation
 * - Expected to see it in navbar/menu but it's not visible
 */

test.describe('MercadoLibre Navigation & Accessibility UX Review', () => {
  test.beforeEach(async ({ page }) => {
    // Start fresh for each test
    await page.goto('/');
  });

  test('should evaluate current navigation structure on desktop', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });

    // Navigate to dashboard (assuming user is authenticated)
    await page.goto('/dashboard');

    // Check for desktop navigation
    const desktopNav = page.locator('.desktop-nav');
    await expect(desktopNav).toBeVisible();

    // Extract all navigation items
    const navItems = await page.locator('.desktop-nav .nav-item').all();
    const navLabels = await Promise.all(
      navItems.map(item => item.locator('.nav-label').textContent())
    );

    console.log('Desktop Navigation Items:', navLabels);

    // Check if MercadoLibre is mentioned in navigation
    const hasMLNavigation = navLabels.some(
      label => label && label.toLowerCase().includes('mercadolibre')
    );

    console.log('Has MercadoLibre in navigation:', hasMLNavigation);

    // Take screenshot for UX review
    await page.screenshot({
      path: 'ux-review-desktop-navigation.png',
      fullPage: true,
    });
  });

  test('should evaluate current navigation structure on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Navigate to dashboard
    await page.goto('/dashboard');

    // Check for mobile navigation
    const mobileNav = page.locator('.mobile-nav');
    await expect(mobileNav).toBeVisible();

    // Extract all navigation items
    const navItems = await page.locator('.mobile-nav .nav-item').all();
    const navLabels = await Promise.all(navItems.map(item => item.locator('.label').textContent()));

    console.log('Mobile Navigation Items:', navLabels);

    // Check if MercadoLibre is mentioned in navigation
    const hasMLNavigation = navLabels.some(
      label => label && label.toLowerCase().includes('mercadolibre')
    );

    console.log('Has MercadoLibre in mobile navigation:', hasMLNavigation);

    // Take screenshot for UX review
    await page.screenshot({
      path: 'ux-review-mobile-navigation.png',
      fullPage: true,
    });
  });

  test('should check dashboard for MercadoLibre connection options', async ({ page }) => {
    await page.goto('/dashboard');

    // Look for any MercadoLibre-related content on dashboard
    const dashboardContent = await page.textContent('body');
    const hasMLMention = dashboardContent?.toLowerCase().includes('mercadolibre') ?? false;

    console.log('Dashboard mentions MercadoLibre:', hasMLMention);

    // Check for connection buttons or links
    const connectionButtons = await page.locator('button, a').all();
    const connectionTexts = await Promise.all(
      connectionButtons.map(async button => {
        try {
          const text = await button.textContent();
          return text || '';
        } catch {
          return '';
        }
      })
    );

    const hasConnectButton = connectionTexts.some(
      text => text.toLowerCase().includes('connect') || text.toLowerCase().includes('mercadolibre')
    );

    console.log('Has connection-related buttons:', hasConnectButton);

    // Take screenshot of dashboard
    await page.screenshot({
      path: 'ux-review-dashboard.png',
      fullPage: true,
    });
  });

  test('should check profile page for integration settings', async ({ page }) => {
    await page.goto('/profile');

    // Look for integration settings
    const profileContent = await page.textContent('body');
    const hasIntegrationSettings = profileContent?.toLowerCase().includes('integration') ?? false;

    console.log('Profile has integration settings:', hasIntegrationSettings);

    // Check for MercadoLibre mentions
    const hasMLMention = profileContent?.toLowerCase().includes('mercadolibre') ?? false;
    console.log('Profile mentions MercadoLibre:', hasMLMention);

    // Take screenshot of profile page
    await page.screenshot({
      path: 'ux-review-profile.png',
      fullPage: true,
    });
  });

  test('should test direct access to ML setup page', async ({ page }) => {
    // Test direct URL access
    await page.goto('/ml-setup');

    // Check if page exists and loads properly
    const pageTitle = await page.title();
    console.log('ML Setup Page Title:', pageTitle);

    // Check for key elements
    const hasConnectionButton = (await page.locator('button:has-text("Connect")').count()) > 0;
    const hasMLContent = (await page.locator('text=MercadoLibre').count()) > 0;

    console.log('ML Setup page has connection button:', hasConnectionButton);
    console.log('ML Setup page has MercadoLibre content:', hasMLContent);

    // Check accessibility
    const mlSetupHeading = page.locator('h1');
    const headingText = await mlSetupHeading.textContent();
    console.log('Main heading:', headingText);

    // Take screenshot of ML setup page
    await page.screenshot({
      path: 'ux-review-ml-setup.png',
      fullPage: true,
    });
  });

  test('should evaluate navigation accessibility', async ({ page }) => {
    await page.goto('/dashboard');

    // Check navigation accessibility
    const navElement = page.locator('nav[aria-label="Main navigation"]');
    await expect(navElement).toBeVisible();

    // Check for proper ARIA labels
    const navItems = await page.locator('.nav-item').all();

    for (const item of navItems) {
      const hasAriaLabel = await item.getAttribute('aria-label');
      const hasAriaCurrentPage = await item.getAttribute('aria-current');

      console.log('Navigation item accessibility:', {
        hasAriaLabel: !!hasAriaLabel,
        hasAriaCurrentPage: !!hasAriaCurrentPage,
      });
    }

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Check focus states
    const focusedElement = await page.locator(':focus').textContent();
    console.log('Focused element after tabbing:', focusedElement);
  });

  test('should evaluate discoverability of ML integration', async ({ page }) => {
    await page.goto('/dashboard');

    // Simulate user looking for MercadoLibre integration
    const searchScenarios = ['mercadolibre', 'connect', 'integration', 'marketplace', 'setup'];

    const discoverabilityResults: Record<string, boolean> = {};

    for (const searchTerm of searchScenarios) {
      const bodyContent = await page.textContent('body');
      const found = bodyContent?.toLowerCase().includes(searchTerm) ?? false;
      discoverabilityResults[searchTerm] = found;

      console.log(`Search term "${searchTerm}" found on dashboard:`, found);
    }

    // Count total discoverable terms
    const foundTerms = Object.values(discoverabilityResults).filter(Boolean).length;
    const discoverabilityScore = (foundTerms / searchScenarios.length) * 100;

    console.log('Overall discoverability score:', `${discoverabilityScore}%`);

    // Test if user can find ML setup through any logical path
    const logicalPaths = [
      { path: '/profile', description: 'Profile page' },
      { path: '/products', description: 'Products page' },
      { path: '/products/new', description: 'New product page' },
    ];

    for (const logicalPath of logicalPaths) {
      await page.goto(logicalPath.path);
      const pageContent = await page.textContent('body');
      const hasMLReference = pageContent?.toLowerCase().includes('mercadolibre') ?? false;

      console.log(`${logicalPath.description} has ML reference:`, hasMLReference);
    }
  });

  test('should test user journey to discover ML integration', async ({ page }) => {
    // Simulate a new user trying to find MercadoLibre integration
    await page.goto('/dashboard');

    // User starts on dashboard - what do they see?
    await page.screenshot({
      path: 'user-journey-01-dashboard.png',
      fullPage: true,
    });

    // User checks profile for settings
    await page.goto('/profile');
    await page.screenshot({
      path: 'user-journey-02-profile.png',
      fullPage: true,
    });

    // User checks products section
    await page.goto('/products');
    await page.screenshot({
      path: 'user-journey-03-products.png',
      fullPage: true,
    });

    // User tries to create new product to see if ML integration is there
    await page.goto('/products/new');
    await page.screenshot({
      path: 'user-journey-04-new-product.png',
      fullPage: true,
    });

    // Finally, user tries direct URL (if they somehow know about it)
    await page.goto('/ml-setup');
    await page.screenshot({
      path: 'user-journey-05-ml-setup-direct.png',
      fullPage: true,
    });

    // Test ML setup page functionality
    const connectButton = page.locator('button:has-text("Connect")').first();
    if (await connectButton.isVisible()) {
      await connectButton.click();

      // Check if modal appears
      const modal = page.locator('.modal, [role="dialog"]');
      if (await modal.isVisible()) {
        await page.screenshot({
          path: 'user-journey-06-ml-modal.png',
          fullPage: true,
        });
      }
    }
  });

  test('should provide comprehensive UX recommendations', async ({ page }) => {
    // This test documents findings and provides recommendations
    await page.goto('/dashboard');

    const findings = {
      navigationStructure: {
        desktop: [] as string[],
        mobile: [] as string[],
      },
      mlIntegrationVisibility: {
        dashboard: false,
        profile: false,
        products: false,
        navigation: false,
      },
      accessibilityIssues: [] as string[],
      userJourneyBlocks: [] as string[],
      recommendations: [] as string[],
    };

    // Collect navigation structure
    const desktopNavItems = await page
      .locator('.desktop-nav .nav-item .nav-label')
      .allTextContents();
    const mobileNavItems = await page.locator('.mobile-nav .nav-item .label').allTextContents();

    findings.navigationStructure.desktop = desktopNavItems;
    findings.navigationStructure.mobile = mobileNavItems;

    // Test ML integration visibility
    const dashboardContent = await page.textContent('body');
    findings.mlIntegrationVisibility.dashboard =
      dashboardContent?.toLowerCase().includes('mercadolibre') ?? false;

    // Generate recommendations based on findings
    if (!findings.mlIntegrationVisibility.dashboard) {
      findings.recommendations.push('Add MercadoLibre connection option to dashboard');
    }

    if (!findings.mlIntegrationVisibility.navigation) {
      findings.recommendations.push('Add MercadoLibre integration to main navigation');
    }

    console.log('UX Analysis Findings:', JSON.stringify(findings, null, 2));

    // Create final comprehensive screenshot
    await page.screenshot({
      path: 'ux-review-comprehensive-findings.png',
      fullPage: true,
    });
  });
});
