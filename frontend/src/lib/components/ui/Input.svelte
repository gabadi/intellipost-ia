<script lang="ts">
  export let type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' = 'text';
  export let value: string = '';
  export let placeholder: string = '';
  export let label: string = '';
  export let error: string = '';
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let id: string = '';
  export let name: string = '';
  // Removed autocomplete for TypeScript strict compatibility
  export let maxlength: number | undefined = undefined;
  export let minlength: number | undefined = undefined;
  export let pattern: string = '';
  export let readonly: boolean = false;

  // Real-time validation props
  export let validateOnInput: boolean = true;
  export let validateOnBlur: boolean = true;
  export let customValidator: ((value: string) => string | null) | undefined = undefined;

  // Generate ID if not provided
  $: inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  // Internal validation state
  let internalError: string = '';
  let touched: boolean = false;
  let validationTimer: number | undefined;

  // Combined error (external or internal)
  $: displayError = error || (touched ? internalError : '');
  $: isValid = !displayError;

  // Real-time validation function
  function validateInput(inputValue: string): string {
    // Required field validation
    if (required && !inputValue) {
      return 'This field is required';
    }

    // Type-specific validation
    if (inputValue) {
      switch (type) {
        case 'email': {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(inputValue)) {
            return 'Please enter a valid email address';
          }
          break;
        }
        case 'url':
          try {
            new URL(inputValue);
          } catch {
            return 'Please enter a valid URL';
          }
          break;
        case 'tel': {
          const phoneRegex = /^[+]?[1-9][\d]{0,15}$/;
          if (!phoneRegex.test(inputValue.replace(/[\s\-()]/g, ''))) {
            return 'Please enter a valid phone number';
          }
          break;
        }
      }

      // Length validation
      if (minlength && inputValue.length < minlength) {
        return `Must be at least ${minlength} characters long`;
      }
      if (maxlength && inputValue.length > maxlength) {
        return `Must be no more than ${maxlength} characters long`;
      }

      // Pattern validation
      if (pattern && !new RegExp(pattern).test(inputValue)) {
        return 'Please match the required format';
      }
    }

    // Custom validation
    if (customValidator) {
      const customError = customValidator(inputValue);
      if (customError) {
        return customError;
      }
    }

    return '';
  }

  // Debounced validation for input events
  function performValidation(inputValue: string) {
    if (validationTimer) {
      // eslint-disable-next-line no-undef
      clearTimeout(validationTimer);
    }

    // eslint-disable-next-line no-undef
    validationTimer = window.setTimeout(() => {
      internalError = validateInput(inputValue);
    }, 300); // 300ms debounce
  }

  // Input event handlers
  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    value = target.value;

    if (validateOnInput && touched) {
      performValidation(value);
    }
  }

  function handleBlur(_event: FocusEvent) {
    touched = true;

    if (validateOnBlur) {
      internalError = validateInput(value);
    }
  }

  function handleFocus(_event: FocusEvent) {
    // Clear timer on focus to prevent validation during typing
    if (validationTimer) {
      // eslint-disable-next-line no-undef
      clearTimeout(validationTimer);
    }
  }
</script>

<div class="input-group">
  {#if label}
    <label for={inputId} class="input-label">
      {label}
      {#if required}
        <span class="required-asterisk">*</span>
      {/if}
    </label>
  {/if}

  <div class="input-wrapper">
    <input
      {type}
      {placeholder}
      {disabled}
      {required}
      {readonly}
      {maxlength}
      {minlength}
      {pattern}
      id={inputId}
      name={name || inputId}
      class="input"
      class:error={displayError}
      class:valid={isValid && touched && value}
      class:disabled
      {value}
      on:input={handleInput}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:change
      on:keydown
      on:keyup
      aria-invalid={!!displayError}
      aria-describedby={displayError ? `${inputId}-error` : undefined}
    />

    {#if isValid && touched && value}
      <div class="validation-icon valid-icon" aria-hidden="true">✓</div>
    {:else if displayError}
      <div class="validation-icon error-icon" aria-hidden="true">⚠</div>
    {/if}
  </div>

  {#if displayError}
    <div class="error-message" role="alert" id="{inputId}-error">
      {displayError}
    </div>
  {/if}
</div>

<style>
  .input-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .input-label {
    font-weight: 500;
    color: var(--color-gray-700);
    font-size: var(--text-sm);
    line-height: var(--leading-tight);
  }

  .required-asterisk {
    color: var(--color-error);
    margin-left: var(--space-1);
  }

  .input-wrapper {
    position: relative;
  }

  .validation-icon {
    position: absolute;
    right: var(--space-3);
    top: 50%;
    transform: translateY(-50%);
    font-size: var(--text-base);
    font-weight: 600;
    pointer-events: none;
  }

  .valid-icon {
    color: var(--color-success);
  }

  .error-icon {
    color: var(--color-error);
  }

  .input {
    width: 100%;
    padding: var(--space-3);
    padding-right: calc(var(--space-3) + 24px); /* Space for validation icon */
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    background-color: white;
    transition: all 0.2s ease;
    min-height: var(--touch-target-min);
    box-sizing: border-box;
  }

  .input.valid {
    border-color: var(--color-success);
    background-color: #f0fdf4; /* Very light green */
  }

  .input.valid:focus {
    border-color: var(--color-success);
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
  }

  .input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
  }

  .input:hover:not(:disabled):not(.error) {
    border-color: var(--color-gray-400);
  }

  .input.error {
    border-color: var(--color-error);
  }

  .input.error:focus {
    border-color: var(--color-error);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .input:disabled,
  .input.disabled {
    background-color: var(--color-gray-100);
    color: var(--color-gray-500);
    cursor: not-allowed;
  }

  .input:read-only {
    background-color: var(--color-gray-50);
    cursor: default;
  }

  .input::placeholder {
    color: var(--color-gray-400);
  }

  .error-message {
    color: var(--color-error);
    font-size: var(--text-sm);
    line-height: var(--leading-tight);
  }

  /* Auto-fill styling */
  .input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 30px white inset;
    -webkit-text-fill-color: var(--color-gray-900);
  }

  .input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 30px white inset;
    -webkit-text-fill-color: var(--color-gray-900);
  }
</style>
