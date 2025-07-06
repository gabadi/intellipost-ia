<!--
  Registration page for IntelliPost AI
  
  Mobile-first responsive design with real-time validation
  and password strength indicator
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
  
  let email = '';
  let password = '';
  let firstName = '';
  let lastName = '';
  let showPassword = false;
  let emailError = '';
  let passwordError = '';
  let isSubmitting = false;
  let registrationDisabled = false;

  // Email validation pattern
  const emailPattern = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}';

  $: authState = $authStore;

  // Redirect if already authenticated
  onMount(() => {
    authStore.init();
    if (authState.isAuthenticated) {
      goto('/products');
    }
  });

  // Reactive validation
  $: validateEmail(email);
  $: validatePassword(password);

  function validateEmail(value: string) {
    if (!value) {
      emailError = '';
      return;
    }
    
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(value)) {
      emailError = 'Please enter a valid email address';
    } else {
      emailError = '';
    }
  }

  function validatePassword(value: string) {
    if (!value) {
      passwordError = '';
      return;
    }
    
    const requirements = {
      length: value.length >= 8,
      uppercase: /[A-Z]/.test(value),
      lowercase: /[a-z]/.test(value),
      number: /\d/.test(value),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(value)
    };

    const missingRequirements = [];
    if (!requirements.length) missingRequirements.push('at least 8 characters');
    if (!requirements.uppercase) missingRequirements.push('uppercase letter');
    if (!requirements.lowercase) missingRequirements.push('lowercase letter');
    if (!requirements.number) missingRequirements.push('number');
    if (!requirements.special) missingRequirements.push('special character');

    if (missingRequirements.length > 0) {
      passwordError = `Password must contain ${missingRequirements.join(', ')}`;
    } else {
      passwordError = '';
    }
  }

  function getPasswordStrength(value: string): 'weak' | 'medium' | 'strong' {
    if (!value) return 'weak';
    
    const requirements = {
      length: value.length >= 8,
      uppercase: /[A-Z]/.test(value),
      lowercase: /[a-z]/.test(value),
      number: /\d/.test(value),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(value)
    };

    const score = Object.values(requirements).filter(Boolean).length;
    
    if (score < 3) return 'weak';
    if (score < 5) return 'medium';
    return 'strong';
  }

  async function handleSubmit() {
    if (!email || !password || emailError || passwordError) {
      if (!email) emailError = 'Email is required';
      if (!password) passwordError = 'Password is required';
      return;
    }

    isSubmitting = true;
    authStore.clearError();
    
    try {
      await authStore.register({
        email,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined
      });
    } catch (error) {
      console.error('Registration error:', error);
      // Check if registration is disabled
      if (error && typeof error === 'object' && 'detail' in error) {
        const detail = (error as any).detail;
        if (detail && detail.error_code === 'REGISTRATION_DISABLED') {
          registrationDisabled = true;
        }
      }
    } finally {
      isSubmitting = false;
    }
  }

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }

  $: passwordStrength = getPasswordStrength(password);
</script>

<svelte:head>
  <title>Sign Up - IntelliPost AI</title>
  <meta name="description" content="Create your IntelliPost AI account to start generating professional MercadoLibre listings with AI-powered content." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div class="register-container">
  <div class="register-card">
    <!-- Header -->
    <div class="register-header">
      <h1>Create your account</h1>
      <p>Join IntelliPost AI and revolutionize your MercadoLibre listings</p>
    </div>

    {#if registrationDisabled}
      <!-- Registration Disabled Message -->
      <div class="disabled-message">
        <div class="disabled-icon">🔒</div>
        <h2>Registration Currently Disabled</h2>
        <p>New user registration is temporarily disabled. Please contact your administrator for access.</p>
        <p>If you already have an account, you can <a href="/auth/login">sign in here</a>.</p>
      </div>
    {:else}
      <!-- Registration Form -->
      <form on:submit|preventDefault={handleSubmit} class="register-form">
      <!-- Name Fields -->
      <div class="name-fields">
        <div class="form-field">
          <Input
            bind:value={firstName}
            type="text"
            placeholder="First name"
            label="First Name (Optional)"
            disabled={isSubmitting}
            autocomplete="given-name"
          />
        </div>
        <div class="form-field">
          <Input
            bind:value={lastName}
            type="text"
            placeholder="Last name"
            label="Last Name (Optional)"
            disabled={isSubmitting}
            autocomplete="family-name"
          />
        </div>
      </div>

      <!-- Email Field -->
      <div class="form-field">
        <Input
          bind:value={email}
          type="email"
          placeholder="Enter your email"
          label="Email"
          error={emailError}
          disabled={isSubmitting}
          autocomplete="email"
          pattern={emailPattern}
          required
        />
      </div>

      <!-- Password Field -->
      <div class="form-field">
        <div class="password-input-container">
          <Input
            bind:value={password}
            type={showPassword ? 'text' : 'password'}
            placeholder="Create a strong password"
            label="Password"
            error={passwordError}
            disabled={isSubmitting}
            autocomplete="new-password"
            required
          />
          <button
            type="button"
            class="password-toggle"
            on:click={togglePasswordVisibility}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>
        
        <!-- Password Strength Indicator -->
        {#if password}
          <div class="password-strength">
            <div class="strength-bar">
              <div class="strength-fill strength-{passwordStrength}"></div>
            </div>
            <span class="strength-text strength-{passwordStrength}">
              {passwordStrength === 'weak' ? 'Weak' : passwordStrength === 'medium' ? 'Medium' : 'Strong'} password
            </span>
          </div>
        {/if}
      </div>

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
        disabled={isSubmitting || !!emailError || !!passwordError || !email || !password}
        class="register-button"
      >
        {#if isSubmitting}
          <LoadingSpinner size="sm" />
          Creating account...
        {:else}
          Create Account
        {/if}
      </Button>

      <!-- Terms -->
      <div class="terms">
        <p>By creating an account, you agree to our Terms of Service and Privacy Policy</p>
      </div>
    </form>

    <!-- Footer -->
    <div class="register-footer">
      <p>Already have an account? <a href="/auth/login">Sign in</a></p>
    </div>
    {/if}
  </div>
</div>

<style>
  .register-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .register-card {
    width: 100%;
    max-width: 480px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    padding: 2rem;
  }

  .register-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .register-header h1 {
    font-size: 1.875rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .register-header p {
    color: #6b7280;
    margin: 0;
    font-size: 0.875rem;
  }

  .register-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .name-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
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
    background-color: #f3f4f6;
  }

  .password-toggle:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .password-strength {
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .strength-bar {
    flex: 1;
    height: 4px;
    background-color: #e5e7eb;
    border-radius: 2px;
    overflow: hidden;
  }

  .strength-fill {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
  }

  .strength-fill.strength-weak {
    width: 33%;
    background-color: #ef4444;
  }

  .strength-fill.strength-medium {
    width: 66%;
    background-color: #f59e0b;
  }

  .strength-fill.strength-strong {
    width: 100%;
    background-color: #10b981;
  }

  .strength-text {
    font-size: 0.75rem;
    font-weight: 500;
    min-width: fit-content;
  }

  .strength-text.strength-weak {
    color: #ef4444;
  }

  .strength-text.strength-medium {
    color: #f59e0b;
  }

  .strength-text.strength-strong {
    color: #10b981;
  }

  .error-message {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #dc2626;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.875rem;
    text-align: center;
  }

  :global(.register-button) {
    width: 100%;
    min-height: 44px;
  }

  .terms {
    text-align: center;
  }

  .terms p {
    margin: 0;
    color: #6b7280;
    font-size: 0.75rem;
    line-height: 1.4;
  }

  .register-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
  }

  .register-footer p {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
  }

  .register-footer a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }

  .register-footer a:hover {
    text-decoration: underline;
  }

  .disabled-message {
    text-align: center;
    padding: 2rem;
    background-color: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    margin-bottom: 2rem;
  }

  .disabled-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .disabled-message h2 {
    color: #374151;
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
  }

  .disabled-message p {
    color: #6b7280;
    margin: 0.5rem 0;
    line-height: 1.5;
  }

  .disabled-message a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }

  .disabled-message a:hover {
    text-decoration: underline;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .register-container {
      padding: 0.5rem;
    }

    .register-card {
      padding: 1.5rem;
    }

    .register-header h1 {
      font-size: 1.5rem;
    }

    .name-fields {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }
  }
</style>