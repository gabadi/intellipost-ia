<!--
  Login page for IntelliPost AI
  
  Mobile-first responsive design with 44px touch targets
  and real-time validation feedback
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { AuthAPI } from '$lib/api/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
  
  let email = '';
  let password = '';
  let showPassword = false;
  let emailError = '';
  let passwordError = '';
  let isSubmitting = false;
  let registrationEnabled = true; // Default to true until we know otherwise

  // Email validation pattern
  const emailPattern = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}';

  $: authState = $authStore;

  // Redirect if already authenticated
  onMount(async () => {
    authStore.init();
    if (authState.isAuthenticated) {
      goto('/products');
    }

    // Check if registration is enabled
    try {
      const response = await AuthAPI.getFeatureFlags();
      if (response.success && response.data) {
        registrationEnabled = response.data.registration_enabled;
      }
    } catch (error) {
      console.error('Failed to fetch feature flags:', error);
      // Keep default value of true on error
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
    // For login, we don't validate password format - only check if it's provided
    if (!value) {
      passwordError = '';
      return;
    }
    
    // No format validation for login - let the backend handle authentication
    passwordError = '';
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
      await authStore.login({ email, password });
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      isSubmitting = false;
    }
  }

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }
</script>

<svelte:head>
  <title>Login - IntelliPost AI</title>
  <meta name="description" content="Login to your IntelliPost AI account to manage your MercadoLibre listings with AI-powered content generation." />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div class="login-container">
  <div class="login-card">
    <!-- Header -->
    <div class="login-header">
      <h1>Welcome back</h1>
      <p>Sign in to your IntelliPost AI account</p>
    </div>

    <!-- Login Form -->
    <form on:submit|preventDefault={handleSubmit} class="login-form">
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
            placeholder="Enter your password"
            label="Password"
            error={passwordError}
            disabled={isSubmitting}
            autocomplete="current-password"
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
        class="login-button"
      >
        {#if isSubmitting}
          <LoadingSpinner size="sm" />
          Signing in...
        {:else}
          Sign In
        {/if}
      </Button>

      <!-- Remember Me -->
      <div class="form-options">
        <label class="remember-me">
          <input type="checkbox" checked disabled={isSubmitting} />
          <span>Remember me</span>
        </label>
      </div>
    </form>

    <!-- Footer -->
    {#if registrationEnabled}
      <div class="login-footer">
        <p>Don't have an account? <a href="/auth/register">Sign up</a></p>
      </div>
    {/if}
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .login-card {
    width: 100%;
    max-width: 400px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    padding: 2rem;
  }

  .login-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .login-header h1 {
    font-size: 1.875rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 0.5rem 0;
  }

  .login-header p {
    color: #6b7280;
    margin: 0;
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
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

  .error-message {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #dc2626;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.875rem;
    text-align: center;
  }

  :global(.login-button) {
    width: 100%;
    min-height: 44px;
  }

  .form-options {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remember-me {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
    cursor: pointer;
  }

  .remember-me input[type="checkbox"] {
    min-width: 16px;
    min-height: 16px;
  }

  .login-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
  }

  .login-footer p {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
  }

  .login-footer a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }

  .login-footer a:hover {
    text-decoration: underline;
  }

  /* Mobile optimizations */
  @media (max-width: 640px) {
    .login-container {
      padding: 0.5rem;
    }

    .login-card {
      padding: 1.5rem;
    }

    .login-header h1 {
      font-size: 1.5rem;
    }
  }
</style>