<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { authStore, authError, isLoading } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';

  // Event dispatcher for component communication
  const dispatch = createEventDispatcher<{
    success: void;
    switchToRegister: void;
  }>();

  // Form state
  let email = '';
  let password = '';
  let emailError = '';
  let passwordError = '';
  let isSubmitting = false;

  // Validation functions
  function validateEmail(value: string): string {
    if (!value.trim()) {
      return 'Email is required';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Please enter a valid email address';
    }

    return '';
  }

  function validatePassword(value: string): string {
    if (!value) {
      return 'Password is required';
    }

    if (value.length < 8) {
      return 'Password must be at least 8 characters long';
    }

    return '';
  }

  // Real-time validation
  $: emailError = email ? validateEmail(email) : '';
  $: passwordError = password ? validatePassword(password) : '';
  $: isFormValid = email && password && !emailError && !passwordError;

  // Handle form submission
  async function handleSubmit() {
    // Clear previous errors
    authStore.clearError();

    // Validate all fields
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    if (emailValidation || passwordValidation) {
      emailError = emailValidation;
      passwordError = passwordValidation;
      return;
    }

    isSubmitting = true;

    try {
      const success = await authStore.login(email, password);

      if (success) {
        dispatch('success');
        // Form will be automatically reset by parent component
      }
      // Errors are handled by the auth store
    } finally {
      isSubmitting = false;
    }
  }

  // Handle input changes (clear errors when user starts typing)
  function handleEmailInput() {
    if (emailError) emailError = '';
    authStore.clearError();
  }

  function handlePasswordInput() {
    if (passwordError) passwordError = '';
    authStore.clearError();
  }

  // Handle Enter key
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && isFormValid && !isSubmitting) {
      handleSubmit();
    }
  }
</script>

<div class="auth-form">
  <div class="auth-form__header">
    <h2 class="auth-form__title">Welcome back</h2>
    <p class="auth-form__subtitle">Sign in to your account to continue</p>
  </div>

  <form on:submit|preventDefault={handleSubmit} class="auth-form__form">
    <!-- Email Input -->
    <div class="auth-form__field">
      <Input
        id="login-email"
        type="email"
        label="Email address"
        bind:value={email}
        error={emailError}
        placeholder="Enter your email"
        required
        autocomplete="email"
        disabled={isSubmitting || $isLoading}
        on:input={handleEmailInput}
        on:keydown={handleKeydown}
      />
    </div>

    <!-- Password Input -->
    <div class="auth-form__field">
      <Input
        id="login-password"
        type="password"
        label="Password"
        bind:value={password}
        error={passwordError}
        placeholder="Enter your password"
        required
        autocomplete="current-password"
        disabled={isSubmitting || $isLoading}
        on:input={handlePasswordInput}
        on:keydown={handleKeydown}
      />
    </div>

    <!-- Global Error Message -->
    {#if $authError}
      <div class="auth-form__error" role="alert" aria-live="polite">
        <span class="auth-form__error-icon" aria-hidden="true">⚠</span>
        <span class="auth-form__error-text">{$authError}</span>
      </div>
    {/if}

    <!-- Submit Button -->
    <Button
      type="submit"
      variant="primary"
      size="large"
      disabled={!isFormValid || isSubmitting || $isLoading}
      loading={isSubmitting || $isLoading}
      class="auth-form__submit"
    >
      {isSubmitting || $isLoading ? 'Signing in...' : 'Sign in'}
    </Button>

    <!-- Switch to Register -->
    <div class="auth-form__switch">
      <span class="auth-form__switch-text">Don't have an account?</span>
      <button
        type="button"
        class="auth-form__switch-link"
        disabled={isSubmitting || $isLoading}
        on:click={() => dispatch('switchToRegister')}
      >
        Create account
      </button>
    </div>
  </form>
</div>

<style>
  .auth-form {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }

  .auth-form__header {
    text-align: center;
    margin-bottom: var(--spacing-6);
  }

  .auth-form__title {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-2) 0;
    line-height: var(--line-height-tight);
  }

  .auth-form__subtitle {
    font-size: var(--font-size-base);
    color: var(--color-text-secondary);
    margin: 0;
    line-height: var(--line-height-relaxed);
  }

  .auth-form__form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-4);
  }

  .auth-form__field {
    display: flex;
    flex-direction: column;
  }

  .auth-form__error {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-3);
    background-color: var(--color-error-50);
    border: 1px solid var(--color-error-200);
    border-radius: var(--border-radius-md);
    color: var(--color-error-800);
    font-size: var(--font-size-sm);
    line-height: var(--line-height-relaxed);
  }

  .auth-form__error-icon {
    font-size: var(--font-size-base);
    flex-shrink: 0;
  }

  .auth-form__error-text {
    flex: 1;
  }

  .auth-form__submit {
    margin-top: var(--spacing-2);
  }

  .auth-form__switch {
    text-align: center;
    margin-top: var(--spacing-4);
  }

  .auth-form__switch-text {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    margin-right: var(--spacing-1);
  }

  .auth-form__switch-link {
    background: none;
    border: none;
    color: var(--color-primary-600);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    text-decoration: underline;
    padding: var(--spacing-1);
    border-radius: var(--border-radius-sm);
    transition: color var(--transition-fast);
  }

  .auth-form__switch-link:hover:not(:disabled) {
    color: var(--color-primary-700);
  }

  .auth-form__switch-link:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }

  .auth-form__switch-link:disabled {
    color: var(--color-text-disabled);
    cursor: not-allowed;
    text-decoration: none;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .auth-form {
      max-width: 100%;
      padding: 0 var(--spacing-4);
    }

    .auth-form__title {
      font-size: var(--font-size-xl);
    }

    .auth-form__subtitle {
      font-size: var(--font-size-sm);
    }
  }

  /* Focus enhancement for accessibility */
  .auth-form__form:focus-within .auth-form__submit {
    box-shadow: 0 0 0 2px var(--color-primary-100);
  }

  /* Loading state */
  .auth-form:has(:disabled) {
    pointer-events: none;
  }

  .auth-form:has(:disabled) .auth-form__switch-link {
    opacity: 0.5;
  }
</style>
