<script lang="ts">
  export let type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'file' =
    'text';
  export let value: string = '';
  export let placeholder: string = '';
  export let label: string = '';
  export let error: string = '';
  export let success: string = '';
  export let help: string = '';
  export let disabled: boolean = false;
  export let readonly: boolean = false;
  export let required: boolean = false;
  export let id: string = '';
  export let name: string = '';
  export let maxlength: number | undefined = undefined;
  export let minlength: number | undefined = undefined;
  export let pattern: string = '';
  export let autocomplete: string | undefined = undefined;
  export let size: 'sm' | 'md' | 'lg' = 'md';

  // ARIA attributes for accessibility
  export let ariaDescribedby: string | undefined = undefined;
  export let ariaInvalid: boolean | undefined = undefined;

  // Additional classes
  let className: string = '';
  export { className as class };

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
  $: hasSuccess = success && !displayError;

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
      clearTimeout(validationTimer);
    }

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
      clearTimeout(validationTimer);
    }
  }
</script>

<div class="input-group">
  {#if label}
    <label for={inputId} class="input-label" class:input-label--required={required}>
      {label}
    </label>
  {/if}

  <div
    class="input-wrapper"
    class:input-wrapper--valid={hasSuccess}
    class:input-wrapper--error={displayError}
    class:input-wrapper--with-end-icon={hasSuccess || displayError}
  >
    <input
      {type}
      {placeholder}
      {disabled}
      {required}
      {readonly}
      {maxlength}
      {minlength}
      {pattern}
      {autocomplete}
      id={inputId}
      name={name || inputId}
      class="input input--{size} {className}"
      class:input--valid={hasSuccess}
      class:input--error={displayError}
      class:input--search={type === 'search'}
      class:input--file={type === 'file'}
      {value}
      on:input={handleInput}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:change
      on:keydown
      on:keyup
      aria-invalid={ariaInvalid !== undefined ? ariaInvalid : !!displayError}
      aria-describedby={ariaDescribedby ||
        (displayError
          ? `${inputId}-error`
          : hasSuccess
            ? `${inputId}-success`
            : help
              ? `${inputId}-help`
              : undefined)}
    />

    {#if hasSuccess}
      <div class="validation-icon validation-icon--valid" aria-hidden="true">✓</div>
    {:else if displayError}
      <div class="validation-icon validation-icon--error" aria-hidden="true">⚠</div>
    {/if}
  </div>

  {#if help && !displayError && !hasSuccess}
    <div class="input-help" id="{inputId}-help">
      {help}
    </div>
  {/if}

  {#if hasSuccess}
    <div class="input-success" id="{inputId}-success">
      {success}
    </div>
  {/if}

  {#if displayError}
    <div class="input-error" role="alert" id="{inputId}-error">
      {displayError}
    </div>
  {/if}
</div>

<!-- No component-specific styles needed - handled by semantic CSS classes -->
