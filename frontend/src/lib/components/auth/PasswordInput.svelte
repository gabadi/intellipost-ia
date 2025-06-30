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
  import {
    validatePassword,
    getPasswordStrength,
    getPasswordRequirements,
  } from '$utils/auth-validation';
  import type { PasswordRequirements } from '$types/auth';

  // Props
  export let value: string = '';
  export let placeholder: string = 'Password';
  export let required: boolean = true;
  export let showStrength: boolean = false;
  export let showRequirements: boolean = false;
  export let error: string | undefined = undefined;
  export let disabled: boolean = false;
  export let id: string | undefined = undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export let autocomplete: any = undefined;

  // State
  let showPassword = false;
  let isFocused = false;
  let previousRequirements: PasswordRequirements | null = null;

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

  // Track requirement changes for animations
  $: {
    if (previousRequirements && requirements) {
      // Check if any requirement just became met
      const requirementKeys = ['minLength', 'hasUpperCase', 'hasLowerCase', 'hasNumber'] as const;
      const justMet = requirementKeys.filter(key => {
        const prev = previousRequirements?.[key];
        const curr = requirements[key];
        return prev && curr && !prev.met && curr.met;
      });

      if (justMet.length > 0) {
        // Trigger success animations
        justMet.forEach(req => {
          const element = document.querySelector(`[data-requirement="${req}"]`);
          if (element) {
            element.classList.add('just-met');
            setTimeout(() => element.classList.remove('just-met'), 700);
          }
        });
      }
    }
    previousRequirements = requirements ? { ...requirements } : null;
  }

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
      {id}
      type={inputType}
      bind:value
      {placeholder}
      {required}
      {disabled}
      class="password-field"
      {autocomplete}
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
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"
          />
          <path d="m1 1 22 22" />
        </svg>
      {:else}
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
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
          style="width: {passwordStrength === 'weak'
            ? '33%'
            : passwordStrength === 'medium'
              ? '66%'
              : '100%'}"
        ></div>
      </div>
      <span class="strength-text strength-{passwordStrength}">
        {passwordStrength === 'weak' ? 'Weak' : passwordStrength === 'medium' ? 'Medium' : 'Strong'}
        password
      </span>
    </div>
  {/if}

  {#if showRequirements && (isFocused || (hasValue && !passwordValidation.isValid))}
    <div class="requirements">
      <p class="requirements-title">Password must contain:</p>
      <ul class="requirements-list">
        <li
          class="requirement requirement-item"
          class:met={requirements.minLength.met}
          data-requirement="minLength"
        >
          <span
            class="requirement-icon"
            class:success={requirements.minLength.met}
            aria-hidden="true"
          >
            {requirements.minLength.icon}
          </span>
          {requirements.minLength.text}
        </li>
        <li
          class="requirement requirement-item"
          class:met={requirements.hasUpperCase.met}
          data-requirement="hasUpperCase"
        >
          <span
            class="requirement-icon"
            class:success={requirements.hasUpperCase.met}
            aria-hidden="true"
          >
            {requirements.hasUpperCase.icon}
          </span>
          {requirements.hasUpperCase.text}
        </li>
        <li
          class="requirement requirement-item"
          class:met={requirements.hasLowerCase.met}
          data-requirement="hasLowerCase"
        >
          <span
            class="requirement-icon"
            class:success={requirements.hasLowerCase.met}
            aria-hidden="true"
          >
            {requirements.hasLowerCase.icon}
          </span>
          {requirements.hasLowerCase.text}
        </li>
        <li
          class="requirement requirement-item"
          class:met={requirements.hasNumber.met}
          data-requirement="hasNumber"
        >
          <span
            class="requirement-icon"
            class:success={requirements.hasNumber.met}
            aria-hidden="true"
          >
            {requirements.hasNumber.icon}
          </span>
          {requirements.hasNumber.text}
        </li>
      </ul>
      {#if requirements.allMet}
        <div class="password-complete-notice">
          <span class="success-checkmark">✓</span>
          Strong password created!
        </div>
      {/if}
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
    background: var(--color-background-muted);
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
    background: var(--color-background-secondary);
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
    transition:
      width 0.3s ease,
      background-color 0.3s ease;
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
    border: 1px solid var(--color-border-muted);
    animation: slideIn 0.2s ease-out;
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

  .password-complete-notice {
    margin-top: var(--spacing-2);
    padding: var(--spacing-2);
    background: var(--color-success-50);
    border: 1px solid var(--color-success-200);
    border-radius: var(--border-radius-md);
    color: var(--color-success-800);
    font-size: var(--font-size-sm);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    animation: slide-up 0.4s var(--ease-out);
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Mobile-specific styles */
  @media (max-width: 767px) {
    .password-field {
      font-size: 16px; /* Prevents zoom on iOS */
    }
  }

  /* Reduce motion for users who prefer it */
  @media (prefers-reduced-motion: reduce) {
    .requirements {
      animation: none;
    }
    .strength-fill {
      transition: none;
    }
  }
</style>
