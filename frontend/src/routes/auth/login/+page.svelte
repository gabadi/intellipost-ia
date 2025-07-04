<script lang="ts">
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
  import SkipLink from '$lib/components/ui/SkipLink.svelte';
  import { auth } from '$lib/stores/auth';
  import type { LoginRequest } from '$lib/types/auth';
  import { ErrorHandler, type AuthError } from '$lib/utils/error-handler';
  import { onMount } from 'svelte';

  // Form state
  const formData: LoginRequest = {
    email: '',
    password: '',
  };

  let errors: { [key: string]: string } = {};
  let isSubmitting = false;
  let showPassword = false;
  let rememberMe = true; // Default to true as per story requirements
  let errorSuggestions: string[] = [];
  let isRetryable = false;

  // Reactive validation
  $: emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email);
  $: passwordValid = formData.password.length >= 1;
  $: formValid = emailValid && passwordValid && !isSubmitting;

  // Handle form submission
  async function handleSubmit() {
    if (!formValid) return;

    isSubmitting = true;
    errors = {};

    try {
      await auth.login(formData);
      // Redirect to products page on successful login
      goto('/products');
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Login failed:', error);

      if (error && typeof error === 'object' && 'details' in error) {
        const authError = error as AuthError;
        errors.submit = authError.details.userMessage;
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

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }

  // Clear form errors when component mounts
  onMount(() => {
    auth.clearError();
  });
</script>

<svelte:head>
  <title>Login - IntelliPost AI</title>
  <meta name="description" content="Sign in to your IntelliPost AI account" />
</svelte:head>

<SkipLink href="#main-content" text="Skip to login form" />

<div class="login-container">
  <div class="login-card">
    <!-- Header -->
    <div class="login-header">
      <h1 class="login-title">Welcome Back</h1>
      <p class="login-subtitle">Sign in to your IntelliPost AI account</p>
    </div>

    <!-- Login Form -->
    <form
      id="main-content"
      class="login-form"
      on:submit|preventDefault={handleSubmit}
      aria-label="User login form"
      novalidate
    >
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
          ariaDescribedby={errors.email ? 'email-error' : undefined}
          ariaInvalid={!!errors.email}
        />
        {#if errors.email}
          <span id="email-error" class="error-message" role="alert" aria-live="polite">
            {errors.email}
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
            placeholder="Enter your password"
            value={formData.password}
            on:input={handlePasswordChange}
            required
            autocomplete="current-password"
            class="form-input password-input"
            disabled={isSubmitting}
            ariaDescribedby={errors.password ? 'password-error' : 'password-toggle-help'}
            ariaInvalid={!!errors.password}
          />
          <button
            type="button"
            class="password-toggle"
            on:click={togglePasswordVisibility}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            aria-pressed={showPassword}
            tabindex="0"
          >
            {#if showPassword}
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            {:else}
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            {/if}
          </button>
        </div>
        <div id="password-toggle-help" class="sr-only">Click to toggle password visibility</div>
        {#if errors.password}
          <span id="password-error" class="error-message" role="alert" aria-live="polite">
            {errors.password}
          </span>
        {/if}
      </div>

      <!-- Remember Me Checkbox -->
      <div class="form-group">
        <label class="checkbox-label">
          <input
            type="checkbox"
            bind:checked={rememberMe}
            class="checkbox-input"
            disabled={isSubmitting}
          />
          <span class="checkbox-text">Remember me</span>
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
            <span>Signing In...</span>
          {:else}
            Sign In
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
    <div class="login-footer">
      <p class="footer-text">
        Don't have an account?
        <a href="/auth/register" class="footer-link">Sign up</a>
      </p>
    </div>
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  }

  .login-card {
    width: 100%;
    max-width: 400px;
    background: var(--surface-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: 2rem;
    border: 1px solid var(--border-subtle);
  }

  .login-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .login-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
  }

  .login-subtitle {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
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

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: var(--text-sm);
    color: var(--text-primary);
    min-height: 44px; /* Mobile touch target */
  }

  .checkbox-input {
    width: 18px;
    height: 18px;
    border: 2px solid var(--border-default);
    border-radius: var(--radius-sm);
    cursor: pointer;
  }

  .checkbox-input:checked {
    background-color: var(--primary-500);
    border-color: var(--primary-500);
  }

  .checkbox-text {
    user-select: none;
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

  .login-footer {
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

  /* Screen reader only utility class */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  /* Mobile optimizations */
  @media (max-width: 480px) {
    .login-container {
      padding: 0.5rem;
    }

    .login-card {
      padding: 1.5rem;
    }

    .login-title {
      font-size: var(--text-lg);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .login-container {
      background: linear-gradient(
        135deg,
        var(--surface-secondary) 0%,
        var(--surface-tertiary) 100%
      );
    }
  }
</style>
