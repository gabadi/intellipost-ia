<!--
  Password input component with visibility toggle and strength indication.

  Features:
  - Toggle password visibility
  - Real-time strength indication
  - Mobile-optimized touch targets (44px)
  - Accessibility support
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { PasswordValidation } from '$types/auth';
  import { validatePassword, getPasswordStrength, getPasswordRequirements } from '$utils/auth-validation';

  // Props
  export let value: string = '';
  export let placeholder: string = 'Password';
  export let required: boolean = true;
  export let showStrength: boolean = false;
  export let showRequirements: boolean = false;
  export let error: string | undefined = undefined;
  export let disabled: boolean = false;

  // State
  let showPassword = false;
  let isFocused = false;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    input: string;
    focus: void;
    blur: void;
  }>();

  // Reactive values
  $: passwordValidation = validatePassword(value);
  $: passwordStrength = getPasswordStrength(value);
  $: requirements = getPasswordRequirements(value);
  $: hasValue = value.length > 0;

  // Event handlers
  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    value = target.value;
    dispatch('input', value);
  }

  function handleFocus() {
    isFocused = true;
    dispatch('focus');
  }

  function handleBlur() {
    isFocused = false;
    dispatch('blur');
  }

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }

  // Accessibility
  $: inputType = showPassword ? 'text' : 'password';
  $: toggleButtonLabel = showPassword ? 'Hide password' : 'Show password';
</script>

<div class="password-input" class:error class:focused={isFocused} class:disabled>
  <div class="input-wrapper">
    <input
      type={inputType}
      bind:value
      {placeholder}
      {required}
      {disabled}
      class="password-field"
      autocomplete="current-password"
      on:input={handleInput}
      on:focus={handleFocus}
      on:blur={handleBlur}
      aria-invalid={error ? 'true' : 'false'}
      aria-describedby={error ? 'password-error' : undefined}
    />

    <button
      type="button"
      class="toggle-button"
      on:click={togglePasswordVisibility}
      {disabled}
      aria-label={toggleButtonLabel}
      tabindex="0"
    >
      {#if showPassword}
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
          <path d="m1 1 22 22"/>
        </svg>
      {:else}
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      {/if}
    </button>
  </div>

  {#if error}
    <div class="error-message" id="password-error" role="alert">
      {error}
    </div>
  {/if}

  {#if showStrength && hasValue}
    <div class="strength-indicator">
      <div class="strength-bar">
        <div
          class="strength-fill strength-{passwordStrength}"
          style="width: {passwordStrength === 'weak' ? '33%' : passwordStrength === 'medium' ? '66%' : '100%'}"
        ></div>
      </div>
      <span class="strength-text strength-{passwordStrength}">
        {passwordStrength === 'weak' ? 'Weak' : passwordStrength === 'medium' ? 'Medium' : 'Strong'} password
      </span>
    </div>
  {/if}

  {#if showRequirements && hasValue && !passwordValidation.isValid}
    <div class="requirements">
      <p class="requirements-title">Password must contain:</p>
      <ul class="requirements-list">
        <li class="requirement" class:met={requirements.minLength.met}>
          <span class="requirement-icon" aria-hidden="true">
            {requirements.minLength.met ? '✓' : '○'}
          </span>
          {requirements.minLength.text}
        </li>
        <li class="requirement" class:met={requirements.hasUpperCase.met}>
          <span class="requirement-icon" aria-hidden="true">
            {requirements.hasUpperCase.met ? '✓' : '○'}
          </span>
          {requirements.hasUpperCase.text}
        </li>
        <li class="requirement" class:met={requirements.hasLowerCase.met}>
          <span class="requirement-icon" aria-hidden="true">
            {requirements.hasLowerCase.met ? '✓' : '○'}
          </span>
          {requirements.hasLowerCase.text}
        </li>
        <li class="requirement" class:met={requirements.hasNumber.met}>
          <span class="requirement-icon" aria-hidden="true">
            {requirements.hasNumber.met ? '✓' : '○'}
          </span>
          {requirements.hasNumber.text}
        </li>
      </ul>
    </div>
  {/if}
</div>

<style>
  .password-input {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
    width: 100%;
  }

  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .password-field {
    width: 100%;
    height: 44px; /* Mobile-optimized touch target */
    padding: var(--spacing-3) var(--spacing-12) var(--spacing-3) var(--spacing-3);
    border: 2px solid var(--color-border);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-family: var(--font-family-base);
    background: var(--color-background);
    color: var(--color-text);
    transition: all 0.2s ease;
  }

  .password-field:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-alpha);
  }

  .password-field:disabled {
    background: var(--color-background-disabled);
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  .toggle-button {
    position: absolute;
    right: var(--spacing-3);
    top: 50%;
    transform: translateY(-50%);
    width: 44px; /* Mobile-optimized touch target */
    height: 44px;
    border: none;
    background: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    border-radius: var(--border-radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .toggle-button:hover:not(:disabled) {
    color: var(--color-text);
    background: var(--color-background-hover);
  }

  .toggle-button:focus {
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-alpha);
  }

  .toggle-button:disabled {
    color: var(--color-text-disabled);
    cursor: not-allowed;
  }

  .error-message {
    color: var(--color-error);
    font-size: var(--font-size-sm);
    line-height: 1.4;
  }

  .strength-indicator {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-1);
  }

  .strength-bar {
    height: 4px;
    background: var(--color-background-secondary);
    border-radius: 2px;
    overflow: hidden;
  }

  .strength-fill {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
    border-radius: 2px;
  }

  .strength-fill.strength-weak {
    background: var(--color-error);
  }

  .strength-fill.strength-medium {
    background: var(--color-warning);
  }

  .strength-fill.strength-strong {
    background: var(--color-success);
  }

  .strength-text {
    font-size: var(--font-size-xs);
    font-weight: 500;
  }

  .strength-text.strength-weak {
    color: var(--color-error);
  }

  .strength-text.strength-medium {
    color: var(--color-warning);
  }

  .strength-text.strength-strong {
    color: var(--color-success);
  }

  .requirements {
    padding: var(--spacing-3);
    background: var(--color-background-secondary);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--color-border-light);
  }

  .requirements-title {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-2) 0;
  }

  .requirements-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-1);
  }

  .requirement {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    transition: color 0.2s ease;
  }

  .requirement.met {
    color: var(--color-success);
  }

  .requirement-icon {
    font-size: var(--font-size-xs);
    font-weight: bold;
    min-width: 12px;
  }

  .password-input.error .password-field {
    border-color: var(--color-error);
  }

  .password-input.error .password-field:focus {
    border-color: var(--color-error);
    box-shadow: 0 0 0 3px var(--color-error-alpha);
  }

  .password-input.disabled {
    opacity: 0.6;
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .password-field {
      font-size: 16px; /* Prevents zoom on iOS */
    }
  }
</style>
