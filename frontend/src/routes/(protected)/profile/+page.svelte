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
        console.error('Password change error:', error);
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
  }
</style>
