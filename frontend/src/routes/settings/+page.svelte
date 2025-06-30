<!--
  Settings page with password change functionality
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, currentUser } from '$stores/auth';
  import PasswordChangeForm from '$lib/components/auth/PasswordChangeForm.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let showPasswordChangeModal = false;
  let changePasswordSuccess = false;
  let changePasswordMessage = '';

  // Handle password change success
  function handlePasswordChangeSuccess(event: CustomEvent<{ message: string }>) {
    changePasswordSuccess = true;
    changePasswordMessage = event.detail.message;
    showPasswordChangeModal = false;

    // Auto-hide success message after 5 seconds
    setTimeout(() => {
      changePasswordSuccess = false;
    }, 5000);
  }

  // Handle password change error
  function handlePasswordChangeError(event: CustomEvent<{ error: string }>) {
    // Error is handled within the form component
    // Log error details for debugging in development only
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error('Password change error:', event.detail.error);
    }
  }

  // Handle password change cancel
  function handlePasswordChangeCancel() {
    showPasswordChangeModal = false;
  }

  // Open password change modal
  function openPasswordChange() {
    showPasswordChangeModal = true;
  }

  // Redirect if not authenticated
  onMount(() => {
    if (!$isAuthenticated) {
      goto('/auth/login?redirect=/settings');
    }
  });
</script>

<svelte:head>
  <title>Settings - IntelliPost AI</title>
  <meta name="description" content="Account settings and preferences for IntelliPost AI" />
</svelte:head>

<div class="settings-page">
  <div class="settings-container">
    <header class="page-header">
      <h1 class="page-title">Account Settings</h1>
      <p class="page-subtitle">Manage your account preferences and security</p>
    </header>

    <!-- Success Message -->
    {#if changePasswordSuccess}
      <div class="success-message" role="alert" aria-live="polite">
        <span class="success-icon" aria-hidden="true">✅</span>
        {changePasswordMessage}
      </div>
    {/if}

    <main class="settings-content">
      <!-- Account Information -->
      <section class="settings-section">
        <h2 class="section-title">Account Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Email:</span>
            <span class="info-value">{$currentUser?.email || 'admin@intellipost.ai'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">User ID:</span>
            <span class="info-value">{$currentUser?.id || 'N/A'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Status:</span>
            <span class="info-value status-active">
              {$currentUser?.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Member Since:</span>
            <span class="info-value">
              {$currentUser?.created_at
                ? new Date($currentUser.created_at).toLocaleDateString()
                : 'N/A'}
            </span>
          </div>
        </div>
      </section>

      <!-- Security Settings -->
      <section class="settings-section">
        <h2 class="section-title">Security</h2>
        <div class="security-options">
          <div class="security-item">
            <div class="security-info">
              <h3 class="security-title">Password</h3>
              <p class="security-description">
                Change your account password. Use a strong password with at least 8 characters.
              </p>
            </div>
            <button class="action-button" on:click={openPasswordChange}> Change Password </button>
          </div>
        </div>
      </section>

      <!-- System Information -->
      <section class="settings-section">
        <h2 class="section-title">System Information</h2>
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">Authentication Mode:</span>
            <span class="info-value">Default User System</span>
          </div>
          <div class="info-item">
            <span class="info-label">Registration:</span>
            <span class="info-value">Disabled</span>
          </div>
          <div class="info-item">
            <span class="info-label">Default Email:</span>
            <span class="info-value">admin@intellipost.ai</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</div>

<!-- Password Change Modal -->
<Modal
  bind:open={showPasswordChangeModal}
  title="Change Password"
  onClose={handlePasswordChangeCancel}
>
  <PasswordChangeForm
    on:success={handlePasswordChangeSuccess}
    on:error={handlePasswordChangeError}
    on:cancel={handlePasswordChangeCancel}
  />
</Modal>

<style>
  .settings-page {
    min-height: 100vh;
    background: var(--color-background);
    padding: var(--spacing-6);
  }

  .settings-container {
    max-width: 800px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: var(--spacing-8);
  }

  .page-title {
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--color-text);
    margin: 0 0 var(--spacing-2) 0;
    line-height: 1.2;
  }

  .page-subtitle {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .success-message {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-4);
    background: var(--color-success-background);
    border: 1px solid var(--color-success);
    border-radius: var(--border-radius-md);
    color: var(--color-success);
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-6);
  }

  .success-icon {
    font-size: var(--font-size-lg);
  }

  .settings-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-8);
  }

  .settings-section {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-6);
    box-shadow: var(--shadow-sm);
  }

  .section-title {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--color-text);
    margin: 0 0 var(--spacing-4) 0;
    line-height: 1.3;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-4);
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-3);
    background: var(--color-background-secondary);
    border-radius: var(--border-radius-md);
  }

  .info-label {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .info-value {
    font-size: var(--font-size-sm);
    color: var(--color-text);
    font-weight: 500;
  }

  .status-active {
    color: var(--color-success);
  }

  .security-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-4);
  }

  .security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    background: var(--color-background-secondary);
  }

  .security-info {
    flex: 1;
  }

  .security-title {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--color-text);
    margin: 0 0 var(--spacing-1) 0;
    line-height: 1.3;
  }

  .security-description {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .action-button {
    padding: var(--spacing-2) var(--spacing-4);
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    border: none;
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: 40px;
  }

  .action-button:hover {
    background: var(--color-primary-hover);
    transform: translateY(-1px);
  }

  .action-button:active {
    transform: translateY(0);
  }

  .action-button:focus {
    outline: none;
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }

  .system-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3);
  }

  /* Mobile styles */
  @media (max-width: 767px) {
    .settings-page {
      padding: var(--spacing-4);
    }

    .settings-section {
      padding: var(--spacing-4);
    }

    .info-grid {
      grid-template-columns: 1fr;
    }

    .security-item {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-3);
    }

    .action-button {
      width: 100%;
    }

    .page-title {
      font-size: var(--font-size-2xl);
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .action-button {
      transition: none;
    }
  }
</style>
