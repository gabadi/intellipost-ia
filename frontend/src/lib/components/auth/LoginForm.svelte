<!--
  Login form component with email/password authentication.

  Features:
  - Mobile-first design with 44px touch targets
  - Real-time validation
  - Loading states
  - Accessibility support
  - Progressive enhancement
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { LoginFormData, User } from '$types/auth';
  import { validateLoginForm } from '$utils/auth-validation';
  import { authStore } from '$stores/auth';
  import PasswordInput from './PasswordInput.svelte';

  // Props
  export let redirectTo: string | undefined = undefined;
  export let disabled: boolean = false;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    success: { user: User };
    error: { error: string };
    switchToRegister: void;
  }>();

  // Form state
  const formData: LoginFormData = {
    email: '',
    password: '',
  };

  let formErrors: { email?: string; password?: string } = {};
  let isSubmitting = false;
  let submitError = '';

  // Reactive validation
  $: validation = validateLoginForm(formData.email, formData.password);
  $: canSubmit = validation.isValid && !isSubmitting;

  // Handle form submission
  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!canSubmit) return;

    isSubmitting = true;
    submitError = '';
    formErrors = {};

    try {
      const result = await authStore.login(formData);

      if (result.success && result.user) {
        dispatch('success', { user: result.user });

        // Redirect if specified
        if (redirectTo && typeof window !== 'undefined') {
          window.location.href = redirectTo;
        }
      } else {
        submitError = result.error || 'Login failed';
        dispatch('error', { error: submitError });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      submitError = errorMessage;
      dispatch('error', { error: errorMessage });
    } finally {
      isSubmitting = false;
    }
  }

  // Handle real-time validation
  function validateField(field: keyof typeof formErrors) {
    const currentValidation = validateLoginForm(formData.email, formData.password);
    formErrors = { ...formErrors, [field]: currentValidation.errors[field] };
  }

  // Clear errors when user starts typing
  function clearFieldError(field: keyof typeof formErrors) {
    if (formErrors[field]) {
      formErrors = { ...formErrors, [field]: undefined };
    }
    if (submitError) {
      submitError = '';
    }
  }
</script>

<form class="login-form" on:submit={handleSubmit} novalidate>
  <div class="form-header">
    <h2 class="form-title">Welcome back</h2>
    <p class="form-subtitle">Sign in to your account to continue</p>
  </div>

  <div class="form-fields">
    <!-- Email Field -->
    <div class="field">
      <label for="email" class="field-label">
        Email address
        <span class="required" aria-label="required">*</span>
      </label>
      <input
        id="email"
        type="email"
        bind:value={formData.email}
        class="field-input"
        class:error={formErrors.email}
        placeholder="Enter your email"
        required
        disabled={disabled || isSubmitting}
        autocomplete="email"
        aria-invalid={formErrors.email ? 'true' : 'false'}
        aria-describedby={formErrors.email ? 'email-error' : undefined}
        on:input={() => clearFieldError('email')}
        on:blur={() => validateField('email')}
      />
      {#if formErrors.email}
        <div class="field-error" id="email-error" role="alert">
          {formErrors.email}
        </div>
      {/if}
    </div>

    <!-- Password Field -->
    <div class="field">
      <label for="password" class="field-label">
        Password
        <span class="required" aria-label="required">*</span>
      </label>
      <PasswordInput
        bind:value={formData.password}
        placeholder="Enter your password"
        error={formErrors.password}
        disabled={disabled || isSubmitting}
        on:input={() => clearFieldError('password')}
        on:blur={() => validateField('password')}
      />
    </div>
  </div>

  <!-- Submit Error -->
  {#if submitError}
    <div class="submit-error" role="alert" aria-live="polite">
      {submitError}
    </div>
  {/if}

  <!-- Form Actions -->
  <div class="form-actions">
    <button
      type="submit"
      class="submit-button"
      class:loading={isSubmitting}
      disabled={!canSubmit || disabled}
      aria-describedby={isSubmitting ? 'loading-text' : undefined}
    >
      {#if isSubmitting}
        <span class="loading-spinner" aria-hidden="true"></span>
        <span id="loading-text">Signing in...</span>
      {:else}
        Sign in
      {/if}
    </button>

    <div class="form-footer">
      <p class="switch-form">
        Don't have an account?
        <button
          type="button"
          class="link-button"
          on:click={() => dispatch('switchToRegister')}
          disabled={disabled || isSubmitting}
        >
          Create account
        </button>
      </p>
    </div>
  </div>
</form>

<style>
  .login-form {
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

  .field-input {
    width: 100%;
    height: 44px; /* Mobile-optimized touch target */
    padding: var(--spacing-3);
    border: 2px solid var(--color-border);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-family: var(--font-family-base);
    background: var(--color-background);
    color: var(--color-text);
    transition: all 0.2s ease;
  }

  .field-input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }

  .field-input:disabled {
    background: var(--color-background-disabled);
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  .field-input.error {
    border-color: var(--color-error);
  }

  .field-input.error:focus {
    border-color: var(--color-error);
    box-shadow: 0 0 0 3px var(--color-error-alpha);
  }

  .field-error {
    color: var(--color-error);
    font-size: var(--font-size-sm);
    line-height: 1.4;
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

  .form-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-4);
  }

  .submit-button {
    width: 100%;
    height: 44px; /* Mobile-optimized touch target */
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

  .form-footer {
    text-align: center;
  }

  .switch-form {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .link-button {
    background: none;
    border: none;
    color: var(--color-primary);
    font-size: inherit;
    font-weight: 500;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 2px;
    transition: color 0.2s ease;
  }

  .link-button:hover:not(:disabled) {
    color: var(--color-primary-hover);
  }

  .link-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
    border-radius: var(--border-radius-sm);
  }

  .link-button:disabled {
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .field-input {
      font-size: 16px; /* Prevents zoom on iOS */
    }

    .form-title {
      font-size: var(--font-size-xl);
    }

    .login-form {
      gap: var(--spacing-5);
    }

    .form-fields {
      gap: var(--spacing-3);
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .submit-button,
    .field-input,
    .link-button {
      transition: none;
    }

    .loading-spinner {
      animation: none;
    }
  }
</style>
