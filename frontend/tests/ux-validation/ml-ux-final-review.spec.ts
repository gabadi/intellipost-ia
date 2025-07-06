import { test, expect } from '@playwright/test';

/**
 * Final UX Review: MercadoLibre Integration Navigation & Accessibility
 *
 * This test provides a comprehensive UX evaluation of the MercadoLibre integration
 * feature navigation and accessibility issues.
 */

test.describe('MercadoLibre Final UX Review', () => {
  test('Complete UX Navigation Analysis', async ({ page }) => {
    console.log('🔍 COMPREHENSIVE UX ANALYSIS: MercadoLibre Integration');
    console.log('=====================================================');

    // Mock authentication to bypass login
    await page.addInitScript(() => {
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

    await page.goto('/dashboard');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    console.log('');
    console.log('📱 NAVIGATION STRUCTURE ANALYSIS');
    console.log('================================');

    // Desktop Navigation Analysis
    await page.setViewportSize({ width: 1200, height: 800 });

    const desktopNavVisible = await page.locator('.desktop-nav').isVisible();
    console.log('Desktop Navigation Visible:', desktopNavVisible);

    if (desktopNavVisible) {
      const desktopNavItems = await page
        .locator('.desktop-nav .nav-item .nav-label')
        .allTextContents();
      console.log('Desktop Navigation Items:', desktopNavItems);

      const hasMLInDesktopNav = desktopNavItems.some(
        item =>
          item.toLowerCase().includes('mercadolibre') || item.toLowerCase().includes('integration')
      );
      console.log('MercadoLibre in Desktop Navigation:', hasMLInDesktopNav);
    }

    // Mobile Navigation Analysis
    await page.setViewportSize({ width: 375, height: 667 });

    const mobileNavVisible = await page.locator('.mobile-nav').isVisible();
    console.log('Mobile Navigation Visible:', mobileNavVisible);

    if (mobileNavVisible) {
      const mobileNavItems = await page.locator('.mobile-nav .nav-item .label').allTextContents();
      console.log('Mobile Navigation Items:', mobileNavItems);

      const hasMLInMobileNav = mobileNavItems.some(
        item =>
          item.toLowerCase().includes('mercadolibre') || item.toLowerCase().includes('integration')
      );
      console.log('MercadoLibre in Mobile Navigation:', hasMLInMobileNav);
    }

    console.log('');
    console.log('🏠 DASHBOARD CONTENT ANALYSIS');
    console.log('============================');

    // Reset to desktop view for dashboard analysis
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto('/dashboard');

    const dashboardContent = await page.textContent('body');
    const dashboardAnalysis = {
      hasMercadoLibre: dashboardContent?.toLowerCase().includes('mercadolibre') ?? false,
      hasIntegration: dashboardContent?.toLowerCase().includes('integration') ?? false,
      hasConnect: dashboardContent?.toLowerCase().includes('connect') ?? false,
      hasMarketplace: dashboardContent?.toLowerCase().includes('marketplace') ?? false,
      hasSetup: dashboardContent?.toLowerCase().includes('setup') ?? false,
    };

    console.log('Dashboard Content Analysis:', dashboardAnalysis);

    // Check for Quick Actions
    const quickActionsVisible = await page.locator('text=Quick Actions').isVisible();
    console.log('Quick Actions Section Visible:', quickActionsVisible);

    if (quickActionsVisible) {
      const quickActions = await page.locator('.card-action, .action-card').allTextContents();
      console.log('Quick Actions Available:', quickActions);
    }

    console.log('');
    console.log('👤 PROFILE PAGE ANALYSIS');
    console.log('========================');

    await page.goto('/profile');

    const profileContent = await page.textContent('body');
    const profileAnalysis = {
      hasIntegrationSection: profileContent?.toLowerCase().includes('integration') ?? false,
      hasConnectedAccounts: profileContent?.toLowerCase().includes('connected') ?? false,
      hasMercadoLibre: profileContent?.toLowerCase().includes('mercadolibre') ?? false,
      hasAccountSettings: profileContent?.toLowerCase().includes('account') ?? false,
    };

    console.log('Profile Content Analysis:', profileAnalysis);

    const profileSections = await page.locator('h2').allTextContents();
    console.log('Profile Sections Available:', profileSections);

    console.log('');
    console.log('🛒 ML SETUP PAGE ANALYSIS');
    console.log('=========================');

    await page.goto('/ml-setup');

    const mlSetupPageTitle = await page.title();
    console.log('ML Setup Page Title:', mlSetupPageTitle);

    const mlSetupContent = await page.textContent('body');
    const mlSetupAnalysis = {
      hasMercadoLibre: mlSetupContent?.toLowerCase().includes('mercadolibre') ?? false,
      hasConnectionButton: mlSetupContent?.toLowerCase().includes('connect') ?? false,
      hasIntegrationContent: mlSetupContent?.toLowerCase().includes('integration') ?? false,
      hasOAuthMention: mlSetupContent?.toLowerCase().includes('oauth') ?? false,
    };

    console.log('ML Setup Content Analysis:', mlSetupAnalysis);

    // Check if this is actually the ML setup page
    const mainHeading = await page.locator('h1').first().textContent();
    console.log('Main Heading:', mainHeading);

    const isActualMLSetupPage = mainHeading?.toLowerCase().includes('mercadolibre') ?? false;
    console.log('Is Actual ML Setup Page:', isActualMLSetupPage);

    console.log('');
    console.log('🎯 USER JOURNEY ANALYSIS');
    console.log('========================');

    const userJourneySteps = [
      { name: 'Dashboard', path: '/dashboard', expectation: 'Find ML integration option' },
      { name: 'Profile', path: '/profile', expectation: 'Find integration settings' },
      { name: 'Products', path: '/products', expectation: 'Find ML publishing options' },
      {
        name: 'New Product',
        path: '/products/new',
        expectation: 'Find ML connection during creation',
      },
    ];

    const journeyResults = [];

    for (const step of userJourneySteps) {
      await page.goto(step.path);
      const content = await page.textContent('body');

      const foundML = content?.toLowerCase().includes('mercadolibre') ?? false;
      const foundIntegration = content?.toLowerCase().includes('integration') ?? false;
      const foundConnect = content?.toLowerCase().includes('connect') ?? false;

      const success = foundML || foundIntegration || foundConnect;

      journeyResults.push({
        step: step.name,
        success,
        foundML,
        foundIntegration,
        foundConnect,
      });

      console.log(
        `${step.name}: Success=${success}, ML=${foundML}, Integration=${foundIntegration}, Connect=${foundConnect}`
      );
    }

    const successfulSteps = journeyResults.filter(r => r.success).length;
    const journeySuccessRate = (successfulSteps / userJourneySteps.length) * 100;

    console.log('User Journey Success Rate:', `${journeySuccessRate}%`);

    console.log('');
    console.log('♿ ACCESSIBILITY ANALYSIS');
    console.log('========================');

    await page.goto('/dashboard');

    const accessibilityResults = {
      navigationAriaLabels: await page.locator('nav[aria-label]').count(),
      headingHierarchy: {
        h1: await page.locator('h1').count(),
        h2: await page.locator('h2').count(),
        h3: await page.locator('h3').count(),
      },
      focusableElements: await page.locator('button, a, input, [tabindex]').count(),
    };

    console.log('Accessibility Analysis:', accessibilityResults);

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const firstFocusable = await page.locator(':focus').textContent();
    console.log('First Focusable Element:', firstFocusable);

    console.log('');
    console.log('📊 SUMMARY & RECOMMENDATIONS');
    console.log('============================');

    const issues = {
      critical: [] as string[],
      high: [] as string[],
      medium: [] as string[],
      low: [] as string[],
    };

    // Critical issues
    if (!dashboardAnalysis.hasMercadoLibre) {
      issues.critical.push('Dashboard has no MercadoLibre integration option');
    }

    if (!desktopNavVisible || !mobileNavVisible) {
      issues.critical.push('Navigation not properly visible on all devices');
    }

    if (!isActualMLSetupPage) {
      issues.critical.push('ML Setup page not loading correctly');
    }

    // High priority issues
    if (!profileAnalysis.hasIntegrationSection) {
      issues.high.push('Profile page lacks integration settings section');
    }

    if (journeySuccessRate < 25) {
      issues.high.push('User journey success rate too low (<25%)');
    }

    // Medium priority issues
    if (!quickActionsVisible) {
      issues.medium.push('Dashboard lacks quick actions for easy access');
    }

    // Low priority issues
    if (accessibilityResults.navigationAriaLabels < 2) {
      issues.low.push('Navigation could have better ARIA labels');
    }

    console.log('');
    console.log('🔴 CRITICAL ISSUES (Fix immediately):');
    issues.critical.forEach(issue => console.log(`  - ${issue}`));

    console.log('');
    console.log('🟡 HIGH PRIORITY ISSUES (Fix next sprint):');
    issues.high.forEach(issue => console.log(`  - ${issue}`));

    console.log('');
    console.log('🟠 MEDIUM PRIORITY ISSUES (Future improvement):');
    issues.medium.forEach(issue => console.log(`  - ${issue}`));

    console.log('');
    console.log('🟢 LOW PRIORITY ISSUES (Nice to have):');
    issues.low.forEach(issue => console.log(`  - ${issue}`));

    console.log('');
    console.log('💡 SPECIFIC RECOMMENDATIONS:');
    console.log('1. Add "MercadoLibre" or "Integrations" to main navigation');
    console.log('2. Add ML connection card to dashboard Quick Actions');
    console.log('3. Add Integrations section to Profile page');
    console.log('4. Fix ML Setup page routing/loading issues');
    console.log('5. Add contextual help and discovery hints');
    console.log('6. Implement progressive disclosure for integration setup');
    console.log('7. Add integration status indicators');
    console.log('8. Create onboarding flow for new users');

    // Take comprehensive screenshots
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto('/dashboard');
    await page.screenshot({ path: 'ux-final-desktop-dashboard.png', fullPage: true });

    await page.setViewportSize({ width: 375, height: 667 });
    await page.screenshot({ path: 'ux-final-mobile-dashboard.png', fullPage: true });

    await page.goto('/profile');
    await page.screenshot({ path: 'ux-final-profile.png', fullPage: true });

    await page.goto('/ml-setup');
    await page.screenshot({ path: 'ux-final-ml-setup.png', fullPage: true });

    // Document the findings
    expect(issues.critical.length).toBeGreaterThan(0);
    expect(journeySuccessRate).toBeLessThan(50);
    expect(isActualMLSetupPage).toBe(false);
  });
});
