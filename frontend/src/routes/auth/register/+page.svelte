<script lang="ts">
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
  import SkipLink from '$lib/components/ui/SkipLink.svelte';
  import { auth } from '$lib/stores/auth';
  import type { RegisterRequest } from '$lib/types/auth';
  import { ErrorHandler, type AuthError } from '$lib/utils/error-handler';
  import { onMount } from 'svelte';

  // Form state
  const formData: RegisterRequest = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  };

  let errors: { [key: string]: string } = {};
  let isSubmitting = false;
  let showPassword = false;
  let acceptTerms = false;
  let errorSuggestions: string[] = [];
  let isRetryable = false;

  // Real-time validation
  $: emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email);
  $: passwordValid = formData.password.length >= 8;
  // Password strength is handled by getPasswordStrength function
  // $: passwordStrong = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/.test(
  //   formData.password
  // );
  $: nameValid = (formData.first_name?.trim().length ?? 0) >= 1;
  $: formValid = emailValid && passwordValid && nameValid && acceptTerms && !isSubmitting;

  // Password strength indicator
  function getPasswordStrength(password: string): { level: number; text: string; color: string } {
    if (password.length === 0) return { level: 0, text: '', color: '' };
    if (password.length < 8) return { level: 1, text: 'Too short', color: 'var(--error-500)' };

    let score = 0;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[@$!%*?&]/.test(password)) score++;

    if (score === 1) return { level: 2, text: 'Weak', color: 'var(--warning-500)' };
    if (score === 2) return { level: 3, text: 'Fair', color: 'var(--warning-400)' };
    if (score === 3) return { level: 4, text: 'Good', color: 'var(--success-400)' };
    if (score === 4) return { level: 5, text: 'Strong', color: 'var(--success-500)' };

    return { level: 2, text: 'Weak', color: 'var(--warning-500)' };
  }

  $: passwordStrength = getPasswordStrength(formData.password);

  // Handle form submission
  async function handleSubmit() {
    if (!formValid) return;

    isSubmitting = true;
    errors = {};

    try {
      await auth.register(formData);
      // Redirect to products page on successful registration
      goto('/products');
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Registration failed:', error);

      if (error && typeof error === 'object' && 'details' in error) {
        const authError = error as AuthError;
        // Check if it's a specific field error
        if (authError.details.code === 'AUTH_EMAIL_EXISTS') {
          errors.email = authError.details.userMessage;
        } else if (authError.details.code === 'AUTH_WEAK_PASSWORD') {
          errors.password = authError.details.userMessage;
        } else {
          errors.submit = authError.details.userMessage;
        }
        errorSuggestions = authError.details.suggestions || [];
        isRetryable = ErrorHandler.isRetryable(authError);
      } else {
        // Fallback for non-AuthError errors
        const authError = ErrorHandler.processError(error);
        errors.submit = authError.details.userMessage;
        errorSuggestions = authError.details.suggestions || [];
        isRetryable = ErrorHandler.isRetryable(authError);
      }
    } finally {
      isSubmitting = false;
    }
  }

  // Handle input changes and clear related errors
  function handleEmailChange(event: Event) {
    const target = event.target as HTMLInputElement;
    formData.email = target.value;
    if (errors.email) delete errors.email;
    if (errors.submit) {
      delete errors.submit;
      errorSuggestions = [];
      isRetryable = false;
    }
  }

  function handlePasswordChange(event: Event) {
    const target = event.target as HTMLInputElement;
    formData.password = target.value;
    if (errors.password) delete errors.password;
    if (errors.submit) {
      delete errors.submit;
      errorSuggestions = [];
      isRetryable = false;
    }
  }

  function handleFirstNameChange(event: Event) {
    const target = event.target as HTMLInputElement;
    formData.first_name = target.value;
    if (errors.first_name) delete errors.first_name;
    if (errors.submit) {
      delete errors.submit;
      errorSuggestions = [];
      isRetryable = false;
    }
  }

  function handleLastNameChange(event: Event) {
    const target = event.target as HTMLInputElement;
    formData.last_name = target.value;
    if (errors.last_name) delete errors.last_name;
    if (errors.submit) {
      delete errors.submit;
      errorSuggestions = [];
      isRetryable = false;
    }
  }

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }

  // Clear form errors when component mounts
  onMount(() => {
    auth.clearError();
  });
</script>

<svelte:head>
  <title>Sign Up - IntelliPost AI</title>
  <meta name="description" content="Create your IntelliPost AI account" />
</svelte:head>

<SkipLink href="#main-content" text="Skip to registration form" />

<div class="register-container">
  <div class="register-card">
    <!-- Header -->
    <div class="register-header">
      <h1 class="register-title">Create Account</h1>
      <p class="register-subtitle">Start generating amazing content with AI</p>
    </div>

    <!-- Registration Form -->
    <form
      id="main-content"
      class="register-form"
      on:submit|preventDefault={handleSubmit}
      aria-label="User registration form"
      novalidate
    >
      <!-- Name Fields -->
      <div class="name-row">
        <div class="form-group">
          <label for="first_name" class="form-label">First Name</label>
          <Input
            id="first_name"
            type="text"
            placeholder="Enter your first name"
            value={formData.first_name}
            on:input={handleFirstNameChange}
            required
            autocomplete="given-name"
            class="form-input"
            disabled={isSubmitting}
          />
          {#if errors.first_name}
            <span class="error-message">{errors.first_name}</span>
          {/if}
        </div>

        <div class="form-group">
          <label for="last_name" class="form-label">Last Name</label>
          <Input
            id="last_name"
            type="text"
            placeholder="Enter your last name"
            value={formData.last_name}
            on:input={handleLastNameChange}
            autocomplete="family-name"
            class="form-input"
            disabled={isSubmitting}
          />
          {#if errors.last_name}
            <span class="error-message">{errors.last_name}</span>
          {/if}
        </div>
      </div>

      <!-- Email Field -->
      <div class="form-group">
        <label for="email" class="form-label">Email Address</label>
        <Input
          id="email"
          type="email"
          placeholder="Enter your email"
          value={formData.email}
          on:input={handleEmailChange}
          required
          autocomplete="email"
          class="form-input"
          disabled={isSubmitting}
        />
        {#if errors.email}
          <span id="email-error" class="error-message" role="alert" aria-live="polite">
            {errors.email}
          </span>
        {:else if formData.email && !emailValid}
          <span id="email-error" class="error-message" role="alert" aria-live="polite">
            Please enter a valid email address
          </span>
        {/if}
      </div>

      <!-- Password Field -->
      <div class="form-group">
        <label for="password" class="form-label">Password</label>
        <div class="password-input-container">
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Create a strong password"
            value={formData.password}
            on:input={handlePasswordChange}
            required
            autocomplete="new-password"
            class="form-input password-input"
            disabled={isSubmitting}
          />
          <button
            type="button"
            class="password-toggle"
            on:click={togglePasswordVisibility}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {#if showPassword}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            {:else}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            {/if}
          </button>
        </div>

        <!-- Password Strength Indicator -->
        {#if formData.password}
          <div class="password-strength">
            <div class="strength-bar">
              <div
                class="strength-fill"
                style="width: {(passwordStrength.level / 5) *
                  100}%; background-color: {passwordStrength.color}"
              ></div>
            </div>
            <span class="strength-text" style="color: {passwordStrength.color}">
              {passwordStrength.text}
            </span>
          </div>
        {/if}

        <!-- Password Requirements -->
        <div class="password-requirements" aria-labelledby="password-requirements-title">
          <p id="password-requirements-title" class="requirements-title">Password must contain:</p>
          <ul class="requirements-list" role="list">
            <li
              class:valid={formData.password.length >= 8}
              role="listitem"
              aria-label="At least 8 characters: {formData.password.length >= 8
                ? 'met'
                : 'not met'}"
            >
              At least 8 characters
            </li>
            <li
              class:valid={/[a-z]/.test(formData.password)}
              role="listitem"
              aria-label="One lowercase letter: {/[a-z]/.test(formData.password)
                ? 'met'
                : 'not met'}"
            >
              One lowercase letter
            </li>
            <li
              class:valid={/[A-Z]/.test(formData.password)}
              role="listitem"
              aria-label="One uppercase letter: {/[A-Z]/.test(formData.password)
                ? 'met'
                : 'not met'}"
            >
              One uppercase letter
            </li>
            <li
              class:valid={/\d/.test(formData.password)}
              role="listitem"
              aria-label="One number: {/\d/.test(formData.password) ? 'met' : 'not met'}"
            >
              One number
            </li>
            <li
              class:valid={/[@$!%*?&]/.test(formData.password)}
              role="listitem"
              aria-label="One special character: {/[@$!%*?&]/.test(formData.password)
                ? 'met'
                : 'not met'}"
            >
              One special character
            </li>
          </ul>
        </div>

        {#if errors.password}
          <span id="password-error" class="error-message" role="alert" aria-live="polite">
            {errors.password}
          </span>
        {/if}
      </div>

      <!-- Terms and Conditions -->
      <div class="form-group">
        <label class="checkbox-label">
          <input
            type="checkbox"
            bind:checked={acceptTerms}
            class="checkbox-input"
            disabled={isSubmitting}
            required
          />
          <span class="checkbox-text">
            I agree to the <a href="/terms" class="terms-link">Terms of Service</a>
            and <a href="/privacy" class="terms-link">Privacy Policy</a>
          </span>
        </label>
      </div>

      <!-- Submit Button -->
      <div class="form-group">
        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={!formValid}
          class="submit-button"
        >
          {#if isSubmitting}
            <LoadingSpinner size="sm" />
            <span>Creating Account...</span>
          {:else}
            Create Account
          {/if}
        </Button>
      </div>

      <!-- Form Errors -->
      {#if errors.submit}
        <div class="error-banner" role="alert" aria-live="assertive">
          <div class="error-header">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
            <span>{errors.submit}</span>
          </div>

          {#if errorSuggestions.length > 0}
            <div class="error-suggestions">
              <p class="suggestions-title">What you can try:</p>
              <ul class="suggestions-list">
                {#each errorSuggestions as suggestion}
                  <li>{suggestion}</li>
                {/each}
              </ul>
            </div>
          {/if}

          {#if isRetryable}
            <div class="retry-section">
              <button
                type="button"
                class="retry-button"
                on:click={handleSubmit}
                disabled={isSubmitting}
              >
                Try Again
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </form>

    <!-- Footer -->
    <div class="register-footer">
      <p class="footer-text">
        Already have an account?
        <a href="/auth/login" class="footer-link">Sign in</a>
      </p>
    </div>
  </div>
</div>

<style>
  .register-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  }

  .register-card {
    width: 100%;
    max-width: 480px;
    background: var(--surface-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: 2rem;
    border: 1px solid var(--border-subtle);
  }

  .register-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .register-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
  }

  .register-subtitle {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  .register-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .name-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-label {
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-primary);
  }

  :global(.form-input) {
    min-height: 44px; /* Mobile touch target requirement */
  }

  .password-input-container {
    position: relative;
  }

  :global(.password-input) {
    padding-right: 3rem;
  }

  .password-toggle {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: var(--radius-sm);
    transition: color var(--transition-base);
    min-height: 44px; /* Mobile touch target */
    width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .password-toggle:hover {
    color: var(--text-primary);
  }

  .password-toggle:focus {
    outline: 2px solid var(--primary-500);
    outline-offset: 2px;
  }

  .password-strength {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.25rem;
  }

  .strength-bar {
    flex: 1;
    height: 4px;
    background: var(--border-subtle);
    border-radius: var(--radius-full);
    overflow: hidden;
  }

  .strength-fill {
    height: 100%;
    transition:
      width var(--transition-base),
      background-color var(--transition-base);
    border-radius: var(--radius-full);
  }

  .strength-text {
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    min-width: 60px;
  }

  .password-requirements {
    background: var(--surface-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.75rem;
    margin-top: 0.5rem;
  }

  .requirements-title {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    margin: 0 0 0.5rem 0;
    font-weight: var(--font-medium);
  }

  .requirements-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .requirements-list li {
    font-size: var(--text-xs);
    color: var(--text-tertiary);
    position: relative;
    padding-left: 1.25rem;
    transition: color var(--transition-base);
  }

  .requirements-list li::before {
    content: '✗';
    position: absolute;
    left: 0;
    color: var(--error-400);
    font-weight: var(--font-bold);
  }

  .requirements-list li.valid {
    color: var(--success-600);
  }

  .requirements-list li.valid::before {
    content: '✓';
    color: var(--success-500);
  }

  .checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    cursor: pointer;
    font-size: var(--text-sm);
    color: var(--text-primary);
    line-height: 1.5;
  }

  .checkbox-input {
    width: 18px;
    height: 18px;
    border: 2px solid var(--border-default);
    border-radius: var(--radius-sm);
    cursor: pointer;
    margin-top: 0.125rem;
    flex-shrink: 0;
  }

  .checkbox-input:checked {
    background-color: var(--primary-500);
    border-color: var(--primary-500);
  }

  .checkbox-text {
    user-select: none;
  }

  .terms-link {
    color: var(--primary-500);
    text-decoration: none;
    font-weight: var(--font-medium);
    transition: color var(--transition-base);
  }

  .terms-link:hover {
    color: var(--primary-600);
    text-decoration: underline;
  }

  :global(.submit-button) {
    min-height: 44px; /* Mobile touch target requirement */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .error-message {
    font-size: var(--text-xs);
    color: var(--error-500);
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .error-banner {
    background: var(--error-50);
    border: 1px solid var(--error-200);
    border-radius: var(--radius-md);
    padding: 0.75rem;
    font-size: var(--text-sm);
    color: var(--error-700);
  }

  .error-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .error-suggestions {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--error-200);
  }

  .suggestions-title {
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    margin: 0 0 0.5rem 0;
    color: var(--error-600);
  }

  .suggestions-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .suggestions-list li {
    font-size: var(--text-xs);
    color: var(--error-600);
    position: relative;
    padding-left: 1rem;
    line-height: 1.4;
  }

  .suggestions-list li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: var(--error-500);
    font-weight: var(--font-bold);
  }

  .retry-section {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--error-200);
  }

  .retry-button {
    background: var(--error-100);
    border: 1px solid var(--error-300);
    color: var(--error-700);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-base);
    min-height: 36px;
  }

  .retry-button:hover:not(:disabled) {
    background: var(--error-200);
    border-color: var(--error-400);
  }

  .retry-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .register-footer {
    margin-top: 2rem;
    text-align: center;
  }

  .footer-text {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  .footer-link {
    color: var(--primary-500);
    text-decoration: none;
    font-weight: var(--font-medium);
    transition: color var(--transition-base);
  }

  .footer-link:hover {
    color: var(--primary-600);
    text-decoration: underline;
  }

  .footer-link:focus {
    outline: 2px solid var(--primary-500);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
  }

  /* Mobile optimizations */
  @media (max-width: 600px) {
    .name-row {
      grid-template-columns: 1fr;
    }

    .register-container {
      padding: 0.5rem;
    }

    .register-card {
      padding: 1.5rem;
    }

    .register-title {
      font-size: var(--text-lg);
    }
  }

  @media (max-width: 480px) {
    .password-requirements {
      padding: 0.5rem;
    }

    .requirements-list {
      font-size: var(--text-xs);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .register-container {
      background: linear-gradient(
        135deg,
        var(--surface-secondary) 0%,
        var(--surface-tertiary) 100%
      );
    }
  }
</style>
