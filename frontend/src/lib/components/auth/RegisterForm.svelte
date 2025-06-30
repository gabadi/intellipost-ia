<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { authStore, authError, isLoading } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';

  // Event dispatcher for component communication
  const dispatch = createEventDispatcher<{
    success: void;
    switchToLogin: void;
  }>();

  // Form state
  let email = '';
  let password = '';
  let confirmPassword = '';
  let emailError = '';
  let passwordError = '';
  let confirmPasswordError = '';
  let isSubmitting = false;

  // Password strength indicators
  let passwordStrength = {
    score: 0,
    feedback: [] as string[],
    isValid: false
  };

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

  function validatePassword(value: string): { isValid: boolean; error: string; strength: typeof passwordStrength } {
    const feedback: string[] = [];
    let score = 0;

    if (!value) {
      return {
        isValid: false,
        error: 'Password is required',
        strength: { score: 0, feedback: [], isValid: false }
      };
    }

    // Length check
    if (value.length < 8) {
      feedback.push('At least 8 characters');
    } else {
      score += 1;
    }

    // Uppercase check
    if (!/[A-Z]/.test(value)) {
      feedback.push('One uppercase letter');
    } else {
      score += 1;
    }

    // Lowercase check
    if (!/[a-z]/.test(value)) {
      feedback.push('One lowercase letter');
    } else {
      score += 1;
    }

    // Number check
    if (!/\d/.test(value)) {
      feedback.push('One number');
    } else {
      score += 1;
    }

    // Special character check
    if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(value)) {
      feedback.push('One special character');
    } else {
      score += 1;
    }

    const isValid = score >= 4; // Require at least 4 out of 5 criteria
    const error = isValid ? '' : 'Password must meet security requirements';

    return {
      isValid,
      error,
      strength: {
        score,
        feedback,
        isValid
      }
    };
  }

  function validateConfirmPassword(password: string, confirmPassword: string): string {
    if (!confirmPassword) {
      return 'Please confirm your password';
    }

    if (password !== confirmPassword) {
      return 'Passwords do not match';
    }

    return '';
  }

  // Real-time validation
  $: emailError = email ? validateEmail(email) : '';
  $: {
    const passwordValidation = validatePassword(password);
    passwordError = password ? passwordValidation.error : '';
    passwordStrength = passwordValidation.strength;
  }
  $: confirmPasswordError = confirmPassword ? validateConfirmPassword(password, confirmPassword) : '';
  $: isFormValid = email && password && confirmPassword &&
                   !emailError && !passwordError && !confirmPasswordError;

  // Handle form submission
  async function handleSubmit() {
    // Clear previous errors
    authStore.clearError();

    // Validate all fields
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);
    const confirmPasswordValidation = validateConfirmPassword(password, confirmPassword);

    if (emailValidation || passwordValidation.error || confirmPasswordValidation) {
      emailError = emailValidation;
      passwordError = passwordValidation.error;
      confirmPasswordError = confirmPasswordValidation;
      return;
    }

    isSubmitting = true;

    try {
      const success = await authStore.register(email, password);

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

  function handleConfirmPasswordInput() {
    if (confirmPasswordError) confirmPasswordError = '';
    authStore.clearError();
  }

  // Handle Enter key
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && isFormValid && !isSubmitting) {
      handleSubmit();
    }
  }

  // Password strength indicator color
  function getStrengthColor(score: number): string {
    if (score < 2) return 'var(--color-error-500)';
    if (score < 4) return 'var(--color-warning-500)';
    return 'var(--color-success-500)';
  }

  function getStrengthText(score: number): string {
    if (score < 2) return 'Weak';
    if (score < 4) return 'Fair';
    return 'Strong';
  }
</script>

<div class="auth-form">
  <div class="auth-form__header">
    <h2 class="auth-form__title">Create your account</h2>
    <p class="auth-form__subtitle">Join IntelliPost AI to start creating amazing content</p>
  </div>

  <form on:submit|preventDefault={handleSubmit} class="auth-form__form">
    <!-- Email Input -->
    <div class="auth-form__field">
      <Input
        id="register-email"
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
        id="register-password"
        type="password"
        label="Password"
        bind:value={password}
        error={passwordError}
        placeholder="Create a strong password"
        required
        autocomplete="new-password"
        disabled={isSubmitting || $isLoading}
        on:input={handlePasswordInput}
        on:keydown={handleKeydown}
      />

      <!-- Password Strength Indicator -->
      {#if password}
        <div class="password-strength">
          <div class="password-strength__bar">
            <div
              class="password-strength__progress"
              style="width: {(passwordStrength.score / 5) * 100}%; background-color: {getStrengthColor(passwordStrength.score)}"
            ></div>
          </div>
          <div class="password-strength__info">
            <span
              class="password-strength__label"
              style="color: {getStrengthColor(passwordStrength.score)}"
            >
              {getStrengthText(passwordStrength.score)}
            </span>
            {#if passwordStrength.feedback.length > 0}
              <span class="password-strength__requirements">
                Needs: {passwordStrength.feedback.join(', ')}
              </span>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <!-- Confirm Password Input -->
    <div class="auth-form__field">
      <Input
        id="register-confirm-password"
        type="password"
        label="Confirm password"
        bind:value={confirmPassword}
        error={confirmPasswordError}
        placeholder="Confirm your password"
        required
        autocomplete="new-password"
        disabled={isSubmitting || $isLoading}
        on:input={handleConfirmPasswordInput}
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
      {isSubmitting || $isLoading ? 'Creating account...' : 'Create account'}
    </Button>

    <!-- Switch to Login -->
    <div class="auth-form__switch">
      <span class="auth-form__switch-text">Already have an account?</span>
      <button
        type="button"
        class="auth-form__switch-link"
        disabled={isSubmitting || $isLoading}
        on:click={() => dispatch('switchToLogin')}
      >
        Sign in
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

  .password-strength {
    margin-top: var(--spacing-2);
  }

  .password-strength__bar {
    width: 100%;
    height: 4px;
    background-color: var(--color-gray-200);
    border-radius: var(--border-radius-full);
    overflow: hidden;
    margin-bottom: var(--spacing-2);
  }

  .password-strength__progress {
    height: 100%;
    transition: width var(--transition-normal), background-color var(--transition-normal);
    border-radius: var(--border-radius-full);
  }

  .password-strength__info {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--spacing-2);
    font-size: var(--font-size-xs);
    line-height: var(--line-height-tight);
  }

  .password-strength__label {
    font-weight: var(--font-weight-medium);
    flex-shrink: 0;
  }

  .password-strength__requirements {
    color: var(--color-text-secondary);
    text-align: right;
    flex: 1;
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

    .password-strength__info {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-1);
    }

    .password-strength__requirements {
      text-align: left;
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
