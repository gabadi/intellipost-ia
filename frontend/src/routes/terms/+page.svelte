<!--
  Terms of Service placeholder page
-->

<script lang="ts">
  // No special logic needed for this placeholder page
</script>

<svelte:head>
  <title>Terms of Service - IntelliPost AI</title>
  <meta
    name="description"
    content="Terms of Service for IntelliPost AI platform"
  />
  <meta name="robots" content="noindex" />
</svelte:head>

<div class="legal-page">
  <div class="legal-container">
    <header class="page-header">
      <a href="/" class="back-link">← Back to Home</a>
      <h1 class="page-title">Terms of Service</h1>
      <p class="page-subtitle">Last updated: {new Date().toLocaleDateString()}</p>
    </header>

    <main class="legal-content">
      <div class="content-section">
        <h2>Overview</h2>
        <p>
          This is a placeholder Terms of Service page for IntelliPost AI. This document would
          typically contain the legal terms and conditions for using the platform.
        </p>
      </div>

      <div class="content-section">
        <h2>Development Notice</h2>
        <p>
          This application is currently in development mode with simplified authentication.
          For production deployment, please ensure proper legal documentation is in place.
        </p>
      </div>

      <div class="content-section">
        <h2>Contact Information</h2>
        <p>
          For questions about these terms, please contact your system administrator.
        </p>
      </div>
    </main>

    <footer class="page-footer">
      <p class="footer-text">
        <a href="/privacy" class="footer-link">Privacy Policy</a>
        •
        <a href="/auth/login" class="footer-link">Login</a>
      </p>
    </footer>
  </div>
</div>

<style>
  .legal-page {
    min-height: 100vh;
    background: var(--color-background);
    padding: var(--spacing-6);
  }

  .legal-container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--color-background);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-8);
    box-shadow: var(--shadow-sm);
  }

  .page-header {
    margin-bottom: var(--spacing-8);
    text-align: center;
  }

  .back-link {
    display: inline-block;
    color: var(--color-primary);
    text-decoration: none;
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-4);
    transition: color 0.2s ease;
  }

  .back-link:hover {
    color: var(--color-primary-hover);
    text-decoration: underline;
  }

  .page-title {
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--color-text);
    margin: 0 0 var(--spacing-2) 0;
    line-height: 1.2;
  }

  .page-subtitle {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .legal-content {
    margin-bottom: var(--spacing-8);
  }

  .content-section {
    margin-bottom: var(--spacing-6);
  }

  .content-section h2 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-text);
    margin: 0 0 var(--spacing-3) 0;
    line-height: 1.3;
  }

  .content-section p {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-3) 0;
    line-height: 1.6;
  }

  .page-footer {
    text-align: center;
    padding-top: var(--spacing-6);
    border-top: 1px solid var(--color-border);
  }

  .footer-text {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .footer-link {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
  }

  .footer-link:hover {
    color: var(--color-primary-hover);
    text-decoration: underline;
  }

  /* Mobile styles */
  @media (max-width: 767px) {
    .legal-page {
      padding: var(--spacing-4);
    }

    .legal-container {
      padding: var(--spacing-6);
    }

    .page-title {
      font-size: var(--font-size-2xl);
    }
  }
</style>
