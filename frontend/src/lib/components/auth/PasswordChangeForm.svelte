<!--
  Password change form component for authenticated users.

  Features:
  - Current password verification
  - New password validation with strength requirements
  - Confirmation field
  - Real-time validation
  - Loading states
  - Accessibility support
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { User } from '$types/auth';
  import { validatePassword } from '$utils/auth-validation';
  import { authStore } from '$stores/auth';
  import PasswordInput from './PasswordInput.svelte';

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    success: { message: string };
    error: { error: string };
    cancel: void;
  }>();

  // Form state
  let formData = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  };

  let formErrors: {
    currentPassword?: string;
    newPassword?: string;
    confirmPassword?: string;
  } = {};

  let isSubmitting = false;
  let submitError = '';
  let submitSuccess = '';

  // Reactive validation
  $: passwordValidation = validatePassword(formData.newPassword);
  $: passwordsMatch = formData.newPassword && formData.newPassword === formData.confirmPassword;
  $: canSubmit =
    formData.currentPassword &&
    passwordValidation.isValid &&
    passwordsMatch &&
    !isSubmitting;

  // Handle form submission
  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!canSubmit) return;

    isSubmitting = true;
    submitError = '';
    submitSuccess = '';
    formErrors = {};

    try {
      // Call password change function (to be implemented in auth store)
      const result = await authStore.changePassword({
        currentPassword: formData.currentPassword,
        newPassword: formData.newPassword,
      });

      if (result.success) {
        submitSuccess = 'Password changed successfully!';
        formData = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: '',
        };
        dispatch('success', { message: 'Password changed successfully!' });
      } else {
        submitError = result.error || 'Password change failed';
        dispatch('error', { error: submitError });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password change failed';
      submitError = errorMessage;
      dispatch('error', { error: errorMessage });
    } finally {
      isSubmitting = false;
    }
  }

  // Handle real-time validation
  function validateField(field: keyof typeof formErrors) {
    switch (field) {
      case 'currentPassword':
        if (!formData.currentPassword) {
          formErrors.currentPassword = 'Current password is required';
        } else {
          formErrors.currentPassword = undefined;
        }
        break;
      case 'newPassword':
        if (!passwordValidation.isValid) {
          formErrors.newPassword = 'Password must meet strength requirements';
        } else {
          formErrors.newPassword = undefined;
        }
        break;
      case 'confirmPassword':
        if (!passwordsMatch) {
          formErrors.confirmPassword = 'Passwords do not match';
        } else {
          formErrors.confirmPassword = undefined;
        }
        break;
    }
    // Trigger reactivity
    formErrors = { ...formErrors };
  }

  // Clear errors when user starts typing
  function clearFieldError(field: keyof typeof formErrors) {
    if (formErrors[field]) {
      formErrors = { ...formErrors, [field]: undefined };
    }
    if (submitError) {
      submitError = '';
    }
    if (submitSuccess) {
      submitSuccess = '';
    }
  }

  // Handle cancel
  function handleCancel() {
    dispatch('cancel');
  }
</script>

<form class="password-change-form" on:submit={handleSubmit} novalidate>
  <div class="form-header">
    <h2 class="form-title">Change Password</h2>
    <p class="form-subtitle">Update your account password</p>
  </div>

  <div class="form-fields">
    <!-- Current Password Field -->
    <div class="field">
      <label for="current-password" class="field-label">
        Current Password
        <span class="required" aria-label="required">*</span>
      </label>
      <PasswordInput
        id="current-password"
        bind:value={formData.currentPassword}
        placeholder="Enter your current password"
        error={formErrors.currentPassword}
        disabled={isSubmitting}
        autocomplete="current-password"
        on:input={() => clearFieldError('currentPassword')}
        on:blur={() => validateField('currentPassword')}
      />
    </div>

    <!-- New Password Field -->
    <div class="field">
      <label for="new-password" class="field-label">
        New Password
        <span class="required" aria-label="required">*</span>
      </label>
      <PasswordInput
        id="new-password"
        bind:value={formData.newPassword}
        placeholder="Enter your new password"
        error={formErrors.newPassword}
        disabled={isSubmitting}
        showStrength={true}
        showRequirements={true}
        autocomplete="new-password"
        on:input={() => clearFieldError('newPassword')}
        on:blur={() => validateField('newPassword')}
      />
    </div>

    <!-- Confirm Password Field -->
    <div class="field">
      <label for="confirm-password" class="field-label">
        Confirm New Password
        <span class="required" aria-label="required">*</span>
      </label>
      <PasswordInput
        id="confirm-password"
        bind:value={formData.confirmPassword}
        placeholder="Confirm your new password"
        error={formErrors.confirmPassword}
        disabled={isSubmitting}
        autocomplete="new-password"
        on:input={() => clearFieldError('confirmPassword')}
        on:blur={() => validateField('confirmPassword')}
      />
    </div>
  </div>

  <!-- Submit Error -->
  {#if submitError}
    <div class="submit-error" role="alert" aria-live="polite">
      {submitError}
    </div>
  {/if}

  <!-- Submit Success -->
  {#if submitSuccess}
    <div class="submit-success" role="alert" aria-live="polite">
      {submitSuccess}
    </div>
  {/if}

  <!-- Form Actions -->
  <div class="form-actions">
    <button
      type="submit"
      class="submit-button"
      class:loading={isSubmitting}
      disabled={!canSubmit}
      aria-describedby={isSubmitting ? 'loading-text' : undefined}
    >
      {#if isSubmitting}
        <span class="loading-spinner" aria-hidden="true"></span>
        <span id="loading-text">Changing password...</span>
      {:else}
        Change Password
      {/if}
    </button>

    <button
      type="button"
      class="cancel-button"
      on:click={handleCancel}
      disabled={isSubmitting}
    >
      Cancel
    </button>
  </div>
</form>

<style>
  .password-change-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-6);
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }

  .form-header {
    text-align: center;
    margin-bottom: var(--spacing-2);
  }

  .form-title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--color-text);
    margin: 0 0 var(--spacing-2) 0;
    line-height: 1.2;
  }

  .form-subtitle {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .form-fields {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-4);
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
  }

  .field-label {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--color-text);
    line-height: 1.4;
  }

  .required {
    color: var(--color-error);
  }

  .submit-error {
    padding: var(--spacing-3);
    background: var(--color-error-background);
    border: 1px solid var(--color-error);
    border-radius: var(--border-radius-md);
    color: var(--color-error);
    font-size: var(--font-size-sm);
    line-height: 1.4;
    text-align: center;
  }

  .submit-success {
    padding: var(--spacing-3);
    background: var(--color-success-background);
    border: 1px solid var(--color-success);
    border-radius: var(--border-radius-md);
    color: var(--color-success);
    font-size: var(--font-size-sm);
    line-height: 1.4;
    text-align: center;
  }

  .form-actions {
    display: flex;
    gap: var(--spacing-3);
  }

  .submit-button {
    flex: 1;
    height: 44px;
    padding: var(--spacing-3) var(--spacing-4);
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    border: none;
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-2);
  }

  .submit-button:hover:not(:disabled) {
    background: var(--color-primary-hover);
    transform: translateY(-1px);
  }

  .submit-button:active:not(:disabled) {
    transform: translateY(0);
  }

  .submit-button:focus {
    outline: none;
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }

  .submit-button:disabled {
    background: var(--color-background-disabled);
    color: var(--color-text-disabled);
    cursor: not-allowed;
    transform: none;
  }

  .submit-button.loading {
    background: var(--color-primary-hover);
    cursor: wait;
  }

  .cancel-button {
    flex: 1;
    height: 44px;
    padding: var(--spacing-3) var(--spacing-4);
    background: transparent;
    color: var(--color-text-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .cancel-button:hover:not(:disabled) {
    background: var(--color-background-secondary);
    border-color: var(--color-border-secondary);
    color: var(--color-text);
  }

  .cancel-button:focus {
    outline: none;
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }

  .cancel-button:disabled {
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .form-title {
      font-size: var(--font-size-xl);
    }

    .password-change-form {
      gap: var(--spacing-5);
    }

    .form-fields {
      gap: var(--spacing-3);
    }

    .form-actions {
      flex-direction: column;
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .submit-button,
    .cancel-button {
      transition: none;
    }

    .loading-spinner {
      animation: none;
    }
  }
</style>
