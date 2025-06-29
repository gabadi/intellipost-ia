<!--
  Registration form component with progressive disclosure and validation.

  Features:
  - Mobile-first design with 44px touch targets
  - Progressive disclosure for optional fields
  - Real-time validation with password strength
  - Loading states and error handling
  - Accessibility support
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { RegisterFormData } from '$types/auth';
  import { validateRegisterForm } from '$utils/auth-validation';
  import { authStore } from '$stores/auth';
  import PasswordInput from './PasswordInput.svelte';

  // Props
  export let redirectTo: string | undefined = undefined;
  export let disabled: boolean = false;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    success: { user: unknown };
    error: { error: string };
    switchToLogin: void;
  }>();

  // Form state
  const formData: RegisterFormData = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  };

  let formErrors: {
    email?: string;
    password?: string;
    first_name?: string;
    last_name?: string;
  } = {};

  let isSubmitting = false;
  let submitError = '';
  let showOptionalFields = false;

  // Reactive validation
  $: validation = validateRegisterForm(
    formData.email,
    formData.password,
    formData.first_name,
    formData.last_name
  );
  $: canSubmit = validation.isValid && !isSubmitting;

  // Handle form submission
  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!canSubmit) return;

    isSubmitting = true;
    submitError = '';
    formErrors = {};

    try {
      // Clean up optional fields (remove empty strings)
      const cleanData = {
        email: formData.email,
        password: formData.password,
        ...(formData.first_name && { first_name: formData.first_name }),
        ...(formData.last_name && { last_name: formData.last_name }),
      };

      const result = await authStore.register(cleanData);

      if (result.success) {
        dispatch('success', { user: result.user });

        // Redirect if specified
        if (redirectTo && typeof window !== 'undefined') {
          window.location.href = redirectTo;
        }
      } else {
        submitError = result.error || 'Registration failed';
        dispatch('error', { error: submitError });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      submitError = errorMessage;
      dispatch('error', { error: errorMessage });
    } finally {
      isSubmitting = false;
    }
  }

  // Handle real-time validation
  function validateField(field: keyof typeof formErrors) {
    const currentValidation = validateRegisterForm(
      formData.email,
      formData.password,
      formData.first_name,
      formData.last_name
    );
    // Map field names correctly
    const errorField =
      field === 'first_name' ? 'firstName' : field === 'last_name' ? 'lastName' : field;
    formErrors = {
      ...formErrors,
      [field]: currentValidation.errors[errorField as keyof typeof currentValidation.errors],
    };
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

  // Toggle optional fields
  function toggleOptionalFields() {
    showOptionalFields = !showOptionalFields;
  }
</script>

<form class="register-form" on:submit={handleSubmit} novalidate>
  <div class="form-header">
    <h2 class="form-title">Create account</h2>
    <p class="form-subtitle">Sign up to start using IntelliPost AI</p>
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
        placeholder="Create a strong password"
        error={formErrors.password}
        disabled={disabled || isSubmitting}
        showStrength={true}
        showRequirements={true}
        on:input={() => clearFieldError('password')}
        on:blur={() => validateField('password')}
      />
    </div>

    <!-- Optional Fields Toggle -->
    <div class="optional-fields-toggle">
      <button
        type="button"
        class="toggle-button"
        on:click={toggleOptionalFields}
        disabled={disabled || isSubmitting}
        aria-expanded={showOptionalFields}
        aria-controls="optional-fields"
      >
        {showOptionalFields ? 'Hide' : 'Add'} name (optional)
        <span class="toggle-icon" aria-hidden="true">
          {showOptionalFields ? '−' : '+'}
        </span>
      </button>
    </div>

    <!-- Optional Fields -->
    {#if showOptionalFields}
      <div class="optional-fields" id="optional-fields">
        <div class="field-row">
          <div class="field">
            <label for="first_name" class="field-label">First name</label>
            <input
              id="first_name"
              type="text"
              bind:value={formData.first_name}
              class="field-input"
              class:error={formErrors.first_name}
              placeholder="First name"
              disabled={disabled || isSubmitting}
              autocomplete="given-name"
              aria-invalid={formErrors.first_name ? 'true' : 'false'}
              aria-describedby={formErrors.first_name ? 'first-name-error' : undefined}
              on:input={() => clearFieldError('first_name')}
              on:blur={() => validateField('first_name')}
            />
            {#if formErrors.first_name}
              <div class="field-error" id="first-name-error" role="alert">
                {formErrors.first_name}
              </div>
            {/if}
          </div>

          <div class="field">
            <label for="last_name" class="field-label">Last name</label>
            <input
              id="last_name"
              type="text"
              bind:value={formData.last_name}
              class="field-input"
              class:error={formErrors.last_name}
              placeholder="Last name"
              disabled={disabled || isSubmitting}
              autocomplete="family-name"
              aria-invalid={formErrors.last_name ? 'true' : 'false'}
              aria-describedby={formErrors.last_name ? 'last-name-error' : undefined}
              on:input={() => clearFieldError('last_name')}
              on:blur={() => validateField('last_name')}
            />
            {#if formErrors.last_name}
              <div class="field-error" id="last-name-error" role="alert">
                {formErrors.last_name}
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
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
        <span id="loading-text">Creating account...</span>
      {:else}
        Create account
      {/if}
    </button>

    <div class="form-footer">
      <p class="switch-form">
        Already have an account?
        <button
          type="button"
          class="link-button"
          on:click={() => dispatch('switchToLogin')}
          disabled={disabled || isSubmitting}
        >
          Sign in
        </button>
      </p>
    </div>
  </div>
</form>

<style>
  .register-form {
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

  .field-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-3);
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

  .optional-fields-toggle {
    display: flex;
    justify-content: center;
  }

  .toggle-button {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-2) var(--spacing-3);
    background: none;
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .toggle-button:hover:not(:disabled) {
    background: var(--color-background-hover);
    border-color: var(--color-border-hover);
    color: var(--color-text);
  }

  .toggle-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
  }

  .toggle-button:disabled {
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  .toggle-icon {
    font-size: var(--font-size-lg);
    font-weight: bold;
    line-height: 1;
  }

  .optional-fields {
    animation: slideDown 0.3s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
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

    .register-form {
      gap: var(--spacing-5);
    }

    .form-fields {
      gap: var(--spacing-3);
    }

    .field-row {
      grid-template-columns: 1fr;
      gap: var(--spacing-3);
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .submit-button,
    .field-input,
    .link-button,
    .toggle-button {
      transition: none;
    }

    .loading-spinner {
      animation: none;
    }

    .optional-fields {
      animation: none;
    }
  }
</style>
