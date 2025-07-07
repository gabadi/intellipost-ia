<script lang="ts">
  import type { ValidationState } from '../../types/product';
  import { debounceStringFunction } from '../../utils/validation';

  export let value: string = '';
  export let onChange: (value: string) => void;
  export let onValidationChange: (validation: ValidationState) => void;
  export let maxLength = 500;
  export let minLength = 10;
  export let placeholder =
    'Describe your product (e.g., iPhone 13 Pro usado, excelente estado, 128GB)';
  export let disabled = false;

  let validationState: ValidationState = { isValid: false, type: 'error' };
  let characterCount = 0;

  // Debounced validation to avoid excessive calls
  const debouncedValidation = debounceStringFunction(validatePrompt, 300);

  // Keep a local copy of the current input value for immediate character counting
  let currentInputValue = value;

  // Reactive character count based on the current input value
  $: characterCount = currentInputValue.length;

  // Update local value when prop changes (e.g., from store)
  $: currentInputValue = value;

  function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    const newValue = target.value;

    // Update local value immediately for real-time character counting
    currentInputValue = newValue;

    // Call onChange to update the store
    onChange(newValue);
    debouncedValidation(newValue);
  }

  function validatePrompt(text: string) {
    const trimmedText = text.trim();

    if (trimmedText.length === 0) {
      validationState = {
        isValid: false,
        message: 'Product description is required',
        type: 'error',
      };
    } else if (trimmedText.length < minLength) {
      validationState = {
        isValid: false,
        message: `Minimum ${minLength} characters required`,
        type: 'error',
      };
    } else if (trimmedText.length > maxLength) {
      validationState = {
        isValid: false,
        message: `Maximum ${maxLength} characters allowed`,
        type: 'error',
      };
    } else if (trimmedText.length > maxLength * 0.8) {
      validationState = {
        isValid: true,
        message: `${maxLength - trimmedText.length} characters remaining`,
        type: 'warning',
      };
    } else {
      validationState = {
        isValid: true,
        message: 'Valid description',
        type: 'success',
      };
    }

    onValidationChange(validationState);
  }

  function getCharacterCountClass(): string {
    if (characterCount > maxLength * 0.9) return 'character-count--danger';
    if (characterCount > maxLength * 0.8) return 'character-count--warning';
    return '';
  }

  function getTextareaClass(): string {
    if (!value || value.trim().length === 0) return '';
    return validationState.isValid ? 'prompt-textarea--valid' : 'prompt-textarea--invalid';
  }
</script>

<div class="prompt-input-container">
  <label for="prompt" class="prompt-label"> Product Description * </label>

  <textarea
    id="prompt"
    bind:value={currentInputValue}
    on:input={handleInput}
    {placeholder}
    maxlength={maxLength}
    rows="4"
    class="prompt-textarea {getTextareaClass()}"
    {disabled}
  ></textarea>

  <div class="prompt-footer">
    <span class="character-count {getCharacterCountClass()}">
      {characterCount}/{maxLength}
    </span>

    {#if validationState.message && value.trim().length > 0}
      <span class="validation-message validation-message--{validationState.type}">
        {#if validationState.type === 'success'}✓{/if}
        {#if validationState.type === 'warning'}⚠{/if}
        {#if validationState.type === 'error'}✕{/if}
        {validationState.message}
      </span>
    {/if}
  </div>
</div>

<style>
  .prompt-input-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    width: 100%;
  }

  .prompt-label {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--space-1);
  }

  .prompt-textarea {
    width: 100%;
    min-height: 100px;
    padding: var(--space-4);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);
    font-size: 16px; /* Prevent zoom on iOS */
    font-family: inherit;
    resize: vertical;
    transition: all 0.2s ease;
    background-color: var(--color-background);
    color: var(--color-text-primary);
  }

  .prompt-textarea:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-light);
  }

  .prompt-textarea:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .prompt-textarea--invalid {
    border-color: var(--color-error);
  }

  .prompt-textarea--invalid:focus {
    border-color: var(--color-error);
    box-shadow: 0 0 0 3px var(--color-error-light);
  }

  .prompt-textarea--valid {
    border-color: var(--color-success);
  }

  .prompt-textarea--valid:focus {
    border-color: var(--color-success);
    box-shadow: 0 0 0 3px var(--color-success-light);
  }

  .prompt-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-2);
    flex-wrap: wrap;
  }

  .character-count {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    font-weight: 500;
    transition: color 0.2s ease;
  }

  .character-count--warning {
    color: var(--color-warning);
    font-weight: 600;
  }

  .character-count--danger {
    color: var(--color-error);
    font-weight: 600;
  }

  .validation-message {
    font-size: var(--text-xs);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .validation-message--success {
    color: var(--color-success);
  }

  .validation-message--warning {
    color: var(--color-warning);
  }

  .validation-message--error {
    color: var(--color-error);
  }

  /* Mobile optimizations */
  @media (max-width: 768px) {
    .prompt-textarea {
      font-size: 16px; /* Prevent zoom on iOS */
      padding: var(--space-3);
      min-height: 80px;
    }

    .prompt-footer {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-1);
    }

    .character-count {
      align-self: flex-end;
    }
  }
</style>
