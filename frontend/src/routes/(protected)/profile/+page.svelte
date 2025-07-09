<!--
  User Profile page for IntelliPost AI

  Mobile-first responsive design with password change functionality
-->

<script lang="ts">
  // onMount import removed as it's not being used
  import { authStore } from '$lib/stores/auth';
  import { AuthAPI } from '$lib/api/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
  import { mlConnectionStore, isMLConnected, mlConnectionHealth } from '$lib/stores/ml-connection';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';

  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  let currentPasswordError = '';
  let newPasswordError = '';
  let confirmPasswordError = '';
  let isSubmitting = false;
  let showCurrentPassword = false;
  let showNewPassword = false;
  let showConfirmPassword = false;
  let successMessage = '';

  $: authState = $authStore;
  let connectedToML = false;
  let mlHealth: any;

  // Use get() to avoid $ syntax issues with dependency-cruiser
  $: {
    connectedToML = get(isMLConnected);
    mlHealth = get(mlConnectionHealth);
  }

  // Initialize ML connection store on mount
  onMount(() => {
    mlConnectionStore.init();
  });

  // Reactive validation
  $: validateNewPassword(newPassword);
  $: validateConfirmPassword(confirmPassword);

  function validateNewPassword(value: string) {
    if (!value) {
      newPasswordError = '';
      return;
    }

    const requirements = {
      length: value.length >= 8,
      uppercase: /[A-Z]/.test(value),
      lowercase: /[a-z]/.test(value),
      number: /\d/.test(value),
      special: /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(value),
    };

    const missingRequirements = [];
    if (!requirements.length) missingRequirements.push('at least 8 characters');
    if (!requirements.uppercase) missingRequirements.push('uppercase letter');
    if (!requirements.lowercase) missingRequirements.push('lowercase letter');
    if (!requirements.number) missingRequirements.push('number');
    if (!requirements.special) missingRequirements.push('special character');

    if (missingRequirements.length > 0) {
      newPasswordError = `Password must contain ${missingRequirements.join(', ')}`;
    } else {
      newPasswordError = '';
    }
  }

  function validateConfirmPassword(value: string) {
    if (!value) {
      confirmPasswordError = '';
      return;
    }

    if (value !== newPassword) {
      confirmPasswordError = 'Passwords do not match';
    } else {
      confirmPasswordError = '';
    }
  }

  async function handlePasswordChange() {
    // Clear previous messages
    successMessage = '';
    authStore.clearError();

    if (!currentPassword || !newPassword || !confirmPassword) {
      if (!currentPassword) currentPasswordError = 'Current password is required';
      if (!newPassword) newPasswordError = 'New password is required';
      if (!confirmPassword) confirmPasswordError = 'Password confirmation is required';
      return;
    }

    if (newPasswordError || confirmPasswordError) {
      return;
    }

    isSubmitting = true;

    try {
      const response = await AuthAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      if (response.success) {
        successMessage = 'Password changed successfully!';
        // Clear form
        currentPassword = '';
        newPassword = '';
        confirmPassword = '';
        currentPasswordError = '';
      }
    } catch (error) {
      // Handle password change errors properly
      if (import.meta.env.DEV) {
        // Password change error
      }
      if (error && typeof error === 'object' && 'detail' in error) {
        const detail = (error as Record<string, unknown>).detail;
        if (
          detail &&
          typeof detail === 'object' &&
          'error_code' in detail &&
          detail.error_code === 'INVALID_CURRENT_PASSWORD'
        ) {
          currentPasswordError = 'Current password is incorrect';
        } else {
          const message =
            detail && typeof detail === 'object' && 'message' in detail
              ? String(detail.message)
              : 'Failed to change password';
          authStore.setError(message);
        }
      } else {
        authStore.setError('Failed to change password');
      }
    } finally {
      isSubmitting = false;
    }
  }

  function togglePasswordVisibility(field: 'current' | 'new' | 'confirm') {
    switch (field) {
      case 'current':
        showCurrentPassword = !showCurrentPassword;
        break;
      case 'new':
        showNewPassword = !showNewPassword;
        break;
      case 'confirm':
        showConfirmPassword = !showConfirmPassword;
        break;
    }
  }

  /**
   * Get ML connection status for display
   */
  function getMLConnectionStatus(): { label: string; class: string; icon: string } {
    if (!connectedToML) {
      return { label: 'Not Connected', class: 'disconnected', icon: '⚫' };
    }
    if (mlHealth === 'healthy') {
      return { label: 'Connected', class: 'connected', icon: '✅' };
    }
    if (mlHealth === 'expired') {
      return { label: 'Expired', class: 'warning', icon: '⏰' };
    }
    if (mlHealth === 'invalid') {
      return { label: 'Invalid', class: 'error', icon: '❌' };
    }
    return { label: 'Checking...', class: 'checking', icon: '🔄' };
  }

  /**
   * Handle ML connection management
   */
  function handleMLConnection() {
    window.location.href = '/ml-setup';
  }

  /**
   * Handle ML disconnection
   */
  async function handleMLDisconnect() {
    // Note: In production, replace with a proper modal confirmation
    // eslint-disable-next-line no-alert
    if (window.confirm('Are you sure you want to disconnect your MercadoLibre account?')) {
      try {
        await mlConnectionStore.disconnect();
      } catch {
        // Failed to disconnect ML account
      }
    }
  }
</script>

<svelte:head>
  <title>Profile - IntelliPost AI</title>
  <meta name="description" content="Manage your IntelliPost AI profile and account settings." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div class="profile-container">
  <div class="profile-header">
    <h1>Profile Settings</h1>
    <p>Manage your account information and security settings</p>
  </div>

  <div class="profile-content">
    <!-- User Information -->
    <div class="section">
      <h2>Account Information</h2>
      <div class="user-info">
        <div class="info-item">
          <div class="info-label">Email</div>
          <div class="info-value">{authState.user?.email || 'Not available'}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Name</div>
          <div class="info-value">
            {authState.user?.first_name || ''}
            {authState.user?.last_name || ''}
          </div>
        </div>
        <div class="info-item">
          <div class="info-label">Account Status</div>
          <div class="info-value status {authState.user?.status || 'unknown'}">
            {authState.user?.status || 'Unknown'}
          </div>
        </div>
      </div>
    </div>

    <!-- Connected Accounts -->
    <div class="section">
      <h2>Connected Accounts</h2>
      <p class="section-description">
        Manage your third-party integrations and connected marketplace accounts.
      </p>

      <div class="connected-accounts">
        <!-- MercadoLibre Account -->
        <div class="account-card">
          <div class="account-header">
            <div class="account-info">
              <div class="account-icon">🛒</div>
              <div class="account-details">
                <h3>MercadoLibre</h3>
                <p>E-commerce marketplace integration</p>
              </div>
            </div>
            <div class="account-status">
              {#if getMLConnectionStatus()}
                <span class="status-indicator {getMLConnectionStatus().class}">
                  <span class="status-icon">{getMLConnectionStatus().icon}</span>
                  <span class="status-text">{getMLConnectionStatus().label}</span>
                </span>
              {/if}
            </div>
          </div>

          <div class="account-content">
            {#if connectedToML}
              <div class="account-features">
                <p class="feature-text">
                  Your MercadoLibre account is connected and ready for automated publishing.
                </p>
                <ul class="feature-list">
                  <li>✅ Automated product publishing</li>
                  <li>✅ Real-time inventory sync</li>
                  <li>✅ AI-optimized listings</li>
                </ul>
              </div>
            {:else}
              <div class="account-features">
                <p class="feature-text">
                  Connect your MercadoLibre account to enable automated publishing and inventory
                  management.
                </p>
                <ul class="feature-list">
                  <li>🚀 Automated product publishing</li>
                  <li>⚡ Real-time inventory sync</li>
                  <li>🎯 AI-optimized listings</li>
                </ul>
              </div>
            {/if}
          </div>

          <div class="account-actions">
            {#if connectedToML}
              <Button variant="secondary" size="sm" on:click={handleMLConnection}>
                Manage Integration
              </Button>
              <Button variant="danger" size="sm" on:click={handleMLDisconnect}>Disconnect</Button>
            {:else}
              <Button variant="primary" size="sm" on:click={handleMLConnection}>
                Connect Account
              </Button>
            {/if}
          </div>
        </div>

        <!-- Future Integrations Placeholder -->
        <div class="account-card coming-soon">
          <div class="account-header">
            <div class="account-info">
              <div class="account-icon">🔮</div>
              <div class="account-details">
                <h3>More Integrations</h3>
                <p>Additional marketplaces coming soon</p>
              </div>
            </div>
            <div class="account-status">
              <span class="status-indicator coming-soon">
                <span class="status-icon">⭐</span>
                <span class="status-text">Coming Soon</span>
              </span>
            </div>
          </div>

          <div class="account-content">
            <div class="account-features">
              <p class="feature-text">
                We're working on integrations with more marketplaces and services.
              </p>
              <ul class="feature-list">
                <li>🛍️ Amazon Marketplace</li>
                <li>📱 Social Media Platforms</li>
                <li>📧 Email Marketing Tools</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change -->
    <div class="section">
      <h2>Change Password</h2>
      <form on:submit|preventDefault={handlePasswordChange} class="password-form">
        <!-- Current Password -->
        <div class="form-field">
          <div class="password-input-container">
            <Input
              bind:value={currentPassword}
              type={showCurrentPassword ? 'text' : 'password'}
              placeholder="Enter current password"
              label="Current Password"
              error={currentPasswordError}
              disabled={isSubmitting}
              autocomplete="current-password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              on:click={() => togglePasswordVisibility('current')}
              aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
            >
              {showCurrentPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        </div>

        <!-- New Password -->
        <div class="form-field">
          <div class="password-input-container">
            <Input
              bind:value={newPassword}
              type={showNewPassword ? 'text' : 'password'}
              placeholder="Enter new password"
              label="New Password"
              error={newPasswordError}
              disabled={isSubmitting}
              autocomplete="new-password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              on:click={() => togglePasswordVisibility('new')}
              aria-label={showNewPassword ? 'Hide password' : 'Show password'}
            >
              {showNewPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        </div>

        <!-- Confirm Password -->
        <div class="form-field">
          <div class="password-input-container">
            <Input
              bind:value={confirmPassword}
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm new password"
              label="Confirm New Password"
              error={confirmPasswordError}
              disabled={isSubmitting}
              autocomplete="new-password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              on:click={() => togglePasswordVisibility('confirm')}
              aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
            >
              {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        </div>

        <!-- Success Message -->
        {#if successMessage}
          <div class="success-message" role="alert">
            {successMessage}
          </div>
        {/if}

        <!-- Error Message -->
        {#if authState.error}
          <div class="error-message" role="alert">
            {authState.error}
          </div>
        {/if}

        <!-- Submit Button -->
        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={isSubmitting ||
            !!newPasswordError ||
            !!confirmPasswordError ||
            !currentPassword ||
            !newPassword ||
            !confirmPassword}
          class="change-password-button"
        >
          {#if isSubmitting}
            <LoadingSpinner size="sm" />
            Changing Password...
          {:else}
            Change Password
          {/if}
        </Button>
      </form>
    </div>
  </div>
</div>

<style>
  .profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-6);
  }

  .profile-header {
    margin-bottom: var(--space-8);
    text-align: center;
  }

  .profile-header h1 {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 var(--space-2) 0;
  }

  .profile-header p {
    color: var(--color-text-secondary);
    margin: 0;
    font-size: var(--text-base);
  }

  .profile-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
  }

  .section {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
  }

  .section h2 {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 var(--space-4) 0;
  }

  .user-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .info-label {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .info-value {
    font-size: var(--text-base);
    color: var(--color-text-primary);
    padding: var(--space-2) 0;
  }

  .info-value.status {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    text-transform: capitalize;
  }

  .info-value.status.active {
    background: #dcfce7;
    color: #16a34a;
  }

  .info-value.status.inactive {
    background: #fee2e2;
    color: #dc2626;
  }

  /* Connected Accounts Section */
  .section-description {
    color: var(--color-text-secondary);
    margin: 0 0 var(--space-6) 0;
    font-size: var(--text-sm);
    line-height: 1.6;
  }

  .connected-accounts {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .account-card {
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border-muted);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    transition: all 0.2s ease;
  }

  .account-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .account-card.coming-soon {
    opacity: 0.8;
  }

  .account-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-4);
  }

  .account-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .account-icon {
    font-size: 2rem;
    flex-shrink: 0;
  }

  .account-details h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 var(--space-1) 0;
  }

  .account-details p {
    color: var(--color-text-secondary);
    margin: 0;
    font-size: var(--text-sm);
  }

  .account-status {
    flex-shrink: 0;
  }

  .status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .status-indicator.connected {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  .status-indicator.disconnected {
    background: var(--color-background-tertiary);
    color: var(--color-text-muted);
  }

  .status-indicator.warning {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  .status-indicator.error {
    background: var(--color-error-light);
    color: var(--color-error-dark);
  }

  .status-indicator.checking {
    background: var(--color-primary-light);
    color: var(--color-primary-dark);
  }

  .status-indicator.coming-soon {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  .status-icon {
    font-size: 0.875rem;
  }

  .account-content {
    margin-bottom: var(--space-4);
  }

  .account-features {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .feature-text {
    color: var(--color-text-secondary);
    margin: 0;
    font-size: var(--text-sm);
    line-height: 1.6;
  }

  .feature-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .feature-list li {
    display: flex;
    align-items: center;
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: 1.4;
  }

  .account-actions {
    display: flex;
    gap: var(--space-3);
    flex-wrap: wrap;
  }

  .password-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .form-field {
    position: relative;
  }

  .password-input-container {
    position: relative;
  }

  .password-toggle {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
  }

  .password-toggle:hover {
    background-color: var(--color-background-secondary);
  }

  .password-toggle:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .success-message {
    background-color: #dcfce7;
    border: 1px solid #bbf7d0;
    color: #16a34a;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    text-align: center;
  }

  .error-message {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #dc2626;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    text-align: center;
  }

  :global(.change-password-button) {
    width: 100%;
    min-height: 44px;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .profile-container {
      padding: var(--space-4);
    }

    .profile-header h1 {
      font-size: var(--text-2xl);
    }

    .section {
      padding: var(--space-4);
    }

    .user-info {
      gap: var(--space-3);
    }

    .account-header {
      flex-direction: column;
      gap: var(--space-3);
      align-items: flex-start;
    }

    .account-info {
      width: 100%;
    }

    .account-actions {
      flex-direction: column;
    }

    .account-actions :global(button) {
      width: 100%;
    }
  }
</style>
