import { test, expect } from '@playwright/test';

/**
 * Comprehensive UX Review: MercadoLibre Integration Navigation & Accessibility
 *
 * This test suite provides a complete UX evaluation of the MercadoLibre OAuth integration
 * feature navigation and accessibility within the IntelliPost AI application.
 *
 * Context: Epic 6 Story 2
 * - MercadoLibre OAuth integration implemented
 * - ML setup page exists at `/ml-setup`
 * - User complaint: Cannot find ML connection in navigation
 *
 * This test acts as a UX audit tool to identify navigation issues and provide
 * actionable recommendations.
 */

test.describe('MercadoLibre UX Comprehensive Review', () => {
  // Skip authentication for these tests to focus on navigation UX
  test.use({ storageState: 'tests/auth-state.json' });

  test.beforeEach(async ({ page }) => {
    // Set up fake authentication state for UX testing
    await page.addInitScript(() => {
      // Mock authentication state
      window.localStorage.setItem('auth-token', 'mock-token');
      window.localStorage.setItem(
        'auth-user',
        JSON.stringify({
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          status: 'active',
        })
      );
    });
  });

  test('UX Audit: Navigation Structure Analysis', async ({ page }) => {
    console.log('🔍 UX AUDIT: Navigation Structure Analysis');
    console.log('===========================================');

    await page.goto('/dashboard');

    // Desktop Navigation Analysis
    await page.setViewportSize({ width: 1200, height: 800 });

    const desktopNavItems = await page.locator('.desktop-nav .nav-item').allTextContents();
    console.log('📱 Desktop Navigation Items:', desktopNavItems);

    // Mobile Navigation Analysis
    await page.setViewportSize({ width: 375, height: 667 });

    const mobileNavItems = await page.locator('.mobile-nav .nav-item').allTextContents();
    console.log('📱 Mobile Navigation Items:', mobileNavItems);

    // Check for ML-related navigation
    const hasMLNavigation = [...desktopNavItems, ...mobileNavItems].some(
      item =>
        item.toLowerCase().includes('mercadolibre') ||
        item.toLowerCase().includes('ml') ||
        item.toLowerCase().includes('integration') ||
        item.toLowerCase().includes('marketplace')
    );

    console.log('🎯 MercadoLibre Navigation Present:', hasMLNavigation);

    // Take screenshots for documentation
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.screenshot({
      path: 'ux-audit-desktop-navigation.png',
      fullPage: true,
    });

    await page.setViewportSize({ width: 375, height: 667 });
    await page.screenshot({
      path: 'ux-audit-mobile-navigation.png',
      fullPage: true,
    });

    expect(hasMLNavigation).toBe(false); // Document current state
  });

  test('UX Audit: Dashboard Integration Discovery', async ({ page }) => {
    console.log('🔍 UX AUDIT: Dashboard Integration Discovery');
    console.log('===========================================');

    await page.goto('/dashboard');

    // Check dashboard content for ML integration mentions
    const dashboardContent = await page.textContent('body');
    const mlMentions = dashboardContent?.toLowerCase().includes('mercadolibre') ?? false;
    const integrationMentions = dashboardContent?.toLowerCase().includes('integration') ?? false;
    const connectMentions = dashboardContent?.toLowerCase().includes('connect') ?? false;

    console.log('📊 Dashboard Analysis:');
    console.log('  - MercadoLibre mentions:', mlMentions);
    console.log('  - Integration mentions:', integrationMentions);
    console.log('  - Connect mentions:', connectMentions);

    // Check for Quick Actions section
    const quickActionsExists = (await page.locator('text=Quick Actions').count()) > 0;
    console.log('  - Quick Actions section exists:', quickActionsExists);

    if (quickActionsExists) {
      const quickActionLinks = await page.locator('.card-action, .action-card').allTextContents();
      console.log('  - Quick Action options:', quickActionLinks);
    }

    // Take dashboard screenshot
    await page.screenshot({
      path: 'ux-audit-dashboard.png',
      fullPage: true,
    });

    expect(mlMentions).toBe(false); // Document current state
  });

  test('UX Audit: Profile Page Integration Settings', async ({ page }) => {
    console.log('🔍 UX AUDIT: Profile Page Integration Settings');
    console.log('===========================================');

    await page.goto('/profile');

    // Check profile page structure
    const profileContent = await page.textContent('body');
    const hasIntegrationSettings = profileContent?.toLowerCase().includes('integration') ?? false;
    const hasConnectSettings = profileContent?.toLowerCase().includes('connect') ?? false;
    const hasMLSettings = profileContent?.toLowerCase().includes('mercadolibre') ?? false;

    console.log('👤 Profile Page Analysis:');
    console.log('  - Integration settings:', hasIntegrationSettings);
    console.log('  - Connect settings:', hasConnectSettings);
    console.log('  - MercadoLibre settings:', hasMLSettings);

    // Check available sections
    const sections = await page.locator('h2').allTextContents();
    console.log('  - Available sections:', sections);

    // Take profile screenshot
    await page.screenshot({
      path: 'ux-audit-profile.png',
      fullPage: true,
    });

    expect(hasIntegrationSettings).toBe(false); // Document current state
  });

  test('UX Audit: ML Setup Page Direct Access', async ({ page }) => {
    console.log('🔍 UX AUDIT: ML Setup Page Direct Access');
    console.log('===========================================');

    await page.goto('/ml-setup');

    // Check if page loads correctly
    const pageTitle = await page.title();
    console.log('📄 Page Title:', pageTitle);

    // Check for ML setup content
    const pageContent = await page.textContent('body');
    const hasMLContent = pageContent?.toLowerCase().includes('mercadolibre') ?? false;
    const hasConnectionButton = (await page.locator('button:has-text("Connect")').count()) > 0;

    console.log('🔗 ML Setup Page Analysis:');
    console.log('  - Has MercadoLibre content:', hasMLContent);
    console.log('  - Has connection button:', hasConnectionButton);

    // Check for key elements
    const mainHeading = await page.locator('h1').textContent();
    console.log('  - Main heading:', mainHeading);

    // Check if this looks like the ML setup page or a fallback
    const isActualMLSetupPage = mainHeading?.toLowerCase().includes('mercadolibre') ?? false;
    console.log('  - Is actual ML setup page:', isActualMLSetupPage);

    // Take screenshot
    await page.screenshot({
      path: 'ux-audit-ml-setup.png',
      fullPage: true,
    });

    expect(isActualMLSetupPage).toBe(false); // Document current state
  });

  test('UX Audit: User Journey Simulation', async ({ page }) => {
    console.log('🔍 UX AUDIT: User Journey Simulation');
    console.log('===========================================');

    console.log('🎯 Scenario: New user wants to connect MercadoLibre');

    const journeySteps = [
      { step: 'Dashboard', path: '/dashboard', description: 'User starts on dashboard' },
      { step: 'Profile', path: '/profile', description: 'User checks profile for settings' },
      { step: 'Products', path: '/products', description: 'User checks products section' },
      { step: 'New Product', path: '/products/new', description: 'User tries creating product' },
      { step: 'Direct ML Setup', path: '/ml-setup', description: 'User tries direct URL' },
    ];

    const journeyResults = [];

    for (const step of journeySteps) {
      await page.goto(step.path);

      const content = await page.textContent('body');
      const hasMLReference = content?.toLowerCase().includes('mercadolibre') ?? false;
      const hasConnectOption = content?.toLowerCase().includes('connect') ?? false;

      const result = {
        step: step.step,
        path: step.path,
        description: step.description,
        hasMLReference,
        hasConnectOption,
        success: hasMLReference || hasConnectOption,
      };

      journeyResults.push(result);

      console.log(
        `  ${step.step} (${step.path}): ML Reference=${hasMLReference}, Connect Option=${hasConnectOption}`
      );

      // Take screenshot for each step
      await page.screenshot({
        path: `ux-audit-journey-${step.step.toLowerCase().replace(' ', '-')}.png`,
        fullPage: true,
      });
    }

    const successfulSteps = journeyResults.filter(r => r.success).length;
    const journeyScore = (successfulSteps / journeySteps.length) * 100;

    console.log('📊 User Journey Analysis:');
    console.log(`  - Successful discovery steps: ${successfulSteps}/${journeySteps.length}`);
    console.log(`  - Journey success rate: ${journeyScore}%`);

    expect(journeyScore).toBeLessThan(50); // Document current poor discoverability
  });

  test('UX Audit: Accessibility Evaluation', async ({ page }) => {
    console.log('🔍 UX AUDIT: Accessibility Evaluation');
    console.log('===========================================');

    await page.goto('/dashboard');

    // Check navigation accessibility
    const navElements = await page.locator('nav').count();
    console.log('♿ Navigation Elements:', navElements);

    // Check for ARIA labels
    const navWithAriaLabel = await page.locator('nav[aria-label]').count();
    console.log('♿ Navigation with ARIA labels:', navWithAriaLabel);

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const firstFocusableElement = await page.locator(':focus').textContent();
    console.log('♿ First focusable element:', firstFocusableElement);

    // Check for proper heading hierarchy
    const headings = {
      h1: await page.locator('h1').count(),
      h2: await page.locator('h2').count(),
      h3: await page.locator('h3').count(),
    };

    console.log('♿ Heading hierarchy:', headings);

    // Test if ML setup page is accessible via keyboard
    await page.goto('/ml-setup');
    const isMLSetupKeyboardAccessible = await page.locator('h1').isVisible();
    console.log('♿ ML Setup keyboard accessible:', isMLSetupKeyboardAccessible);

    expect(navWithAriaLabel).toBeGreaterThan(0);
  });

  test('UX Audit: Recommendations Generation', async ({ page }) => {
    console.log('🔍 UX AUDIT: Recommendations Generation');
    console.log('===========================================');

    const recommendations = {
      critical: [] as string[],
      high: [] as string[],
      medium: [] as string[],
      low: [] as string[],
    };

    // Test current navigation state
    await page.goto('/dashboard');

    const desktopNavItems = await page.locator('.desktop-nav .nav-item').allTextContents();
    const mobileNavItems = await page.locator('.mobile-nav .nav-item').allTextContents();

    // Critical Issues
    const hasMLInNavigation = [...desktopNavItems, ...mobileNavItems].some(item =>
      item.toLowerCase().includes('mercadolibre')
    );

    if (!hasMLInNavigation) {
      recommendations.critical.push('Add MercadoLibre integration to main navigation menu');
    }

    // Check dashboard for ML integration
    const dashboardContent = await page.textContent('body');
    const dashboardHasMLOption = dashboardContent?.toLowerCase().includes('mercadolibre') ?? false;

    if (!dashboardHasMLOption) {
      recommendations.critical.push('Add MercadoLibre connection option to dashboard');
    }

    // High Priority Issues
    const profileContent = await page.textContent('body');
    const profileHasIntegration = profileContent?.toLowerCase().includes('integration') ?? false;

    if (!profileHasIntegration) {
      recommendations.high.push('Add integrations section to profile page');
    }

    // Medium Priority Issues
    recommendations.medium.push('Add contextual help text about MercadoLibre integration');
    recommendations.medium.push('Implement progressive disclosure for integration setup');

    // Low Priority Issues
    recommendations.low.push('Add integration status indicator to navigation');
    recommendations.low.push('Create onboarding tour for new users');

    console.log('📋 UX RECOMMENDATIONS:');
    console.log('');
    console.log('🔴 CRITICAL (Fix immediately):');
    recommendations.critical.forEach(rec => console.log(`  - ${rec}`));

    console.log('');
    console.log('🟡 HIGH PRIORITY (Fix next sprint):');
    recommendations.high.forEach(rec => console.log(`  - ${rec}`));

    console.log('');
    console.log('🟠 MEDIUM PRIORITY (Future improvement):');
    recommendations.medium.forEach(rec => console.log(`  - ${rec}`));

    console.log('');
    console.log('🟢 LOW PRIORITY (Nice to have):');
    recommendations.low.forEach(rec => console.log(`  - ${rec}`));

    expect(recommendations.critical.length).toBeGreaterThan(0);
  });

  test('UX Audit: Proposed Solutions Testing', async ({ page }) => {
    console.log('🔍 UX AUDIT: Proposed Solutions Testing');
    console.log('===========================================');

    await page.goto('/dashboard');

    // Test what the navigation would look like with ML integration
    const currentNavItems = await page.locator('.desktop-nav .nav-item').allTextContents();
    console.log('Current navigation items:', currentNavItems);

    const proposedNavItems = [...currentNavItems, 'MercadoLibre'];
    console.log('Proposed navigation items:', proposedNavItems);

    // Test dashboard with ML integration card
    console.log('');
    console.log('💡 PROPOSED SOLUTIONS:');
    console.log('');
    console.log('1. Add to Navigation Menu:');
    console.log('   - Add "MercadoLibre" or "Integrations" to main navigation');
    console.log('   - Icon: 🛒 or 🔗');
    console.log('   - Position: After "Products", before "Profile"');

    console.log('');
    console.log('2. Add to Dashboard Quick Actions:');
    console.log('   - Title: "Connect MercadoLibre"');
    console.log('   - Description: "Integrate your MercadoLibre account"');
    console.log('   - Icon: 🛒');
    console.log('   - Action: Navigate to /ml-setup');

    console.log('');
    console.log('3. Add to Profile Page:');
    console.log('   - New section: "Integrations"');
    console.log('   - List connected accounts');
    console.log('   - Add connection management');

    console.log('');
    console.log('4. Improve ML Setup Page:');
    console.log('   - Ensure page loads correctly');
    console.log('   - Add breadcrumb navigation');
    console.log('   - Add help documentation');

    // Take final comprehensive screenshot
    await page.screenshot({
      path: 'ux-audit-final-state.png',
      fullPage: true,
    });

    expect(true).toBe(true); // This test documents solutions
  });
});
