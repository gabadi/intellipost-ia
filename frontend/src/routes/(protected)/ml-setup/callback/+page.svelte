<script lang="ts">
  /**
   * MercadoLibre OAuth Callback Page
   *
   * Handles the OAuth callback from MercadoLibre after user authorization.
   * Implements error states and manager account validation feedback.
   */

  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { mlConnectionStore } from '$lib/stores/ml-connection';
  import { MLManagerAccountError, MLRateLimitError, mlOAuthApi } from '$lib/api/ml-oauth';
  import type { MLOAuthCallbackResponse } from '$lib/types/ml-connection';

  // Component state
  let callbackState: 'processing' | 'success' | 'error' = 'processing';
  let result: MLOAuthCallbackResponse | null = null;
  let error: string | null = null;
  let isManagerAccountError = false;
  let isRateLimitError = false;
  let retryAfter = 0;
  let countdown = 0;
  let countdownTimer: ReturnType<typeof setInterval> | null = null;

  // Handle OAuth callback
  onMount(async () => {
    try {
      // Get parameters from URL
      const urlParams = $page.url.searchParams;
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const errorParam = urlParams.get('error');
      const errorDescription = urlParams.get('error_description');

      // Handle OAuth errors
      if (errorParam) {
        throw new Error(errorDescription || `OAuth error: ${errorParam}`);
      }

      // Validate required parameters
      if (!code || !state) {
        throw new Error('Missing authorization code or state parameter');
      }

      // Process the callback
      result = await mlConnectionStore.handleCallback(code, state);

      if (result.success) {
        callbackState = 'success';
        // Redirect to dashboard after successful connection
        setTimeout(() => {
          goto('/dashboard');
        }, 3000);
      } else {
        throw new Error(result.message || 'OAuth callback failed');
      }
    } catch (err) {
      callbackState = 'error';

      if (err instanceof MLManagerAccountError) {
        isManagerAccountError = true;
        error = `Manager Account Required: ${err.message}\n\n${err.guidance}`;
      } else if (err instanceof MLRateLimitError) {
        isRateLimitError = true;
        retryAfter = err.retryAfter;
        error = err.message;
        startCountdown(retryAfter);
      } else {
        error = mlOAuthApi.formatError(err);
      }
    }
  });

  /**
   * Start countdown timer for rate limit
   */
  function startCountdown(seconds: number) {
    countdown = seconds;
    countdownTimer = setInterval(() => {
      countdown--;
      if (countdown <= 0) {
        clearInterval(countdownTimer!);
        countdownTimer = null;
      }
    }, 1000);
  }

  /**
   * Go back to dashboard
   */
  function goToDashboard() {
    goto('/dashboard');
  }

  /**
   * Try connecting again
   */
  function tryAgain() {
    goto('/dashboard'); // User can try again from dashboard
  }

  /**
   * Copy error details for support
   */
  function copyErrorDetails() {
    const errorDetails = `
MercadoLibre OAuth Error:
${error}

URL: ${$page.url.href}
Timestamp: ${new Date().toISOString()}
		`.trim();

    navigator.clipboard.writeText(errorDetails).then(() => {
      // Error details copied to clipboard (replace with toast notification)
    });
  }
</script>

<svelte:head>
  <title>MercadoLibre Connection - IntelliPost AI</title>
</svelte:head>

<div class="callback-container">
  {#if callbackState === 'processing'}
    <!-- Processing state -->
    <div class="callback-card processing">
      <div class="loading-spinner"></div>
      <h1>Processing Connection...</h1>
      <p>We're completing your MercadoLibre connection. Please wait a moment.</p>
    </div>
  {:else if callbackState === 'success' && result}
    <!-- Success state -->
    <div class="callback-card success">
      <div class="success-icon">✅</div>
      <h1>Connection Successful!</h1>
      <p>Your MercadoLibre account has been connected successfully.</p>

      <div class="connection-details">
        {#if result.ml_nickname}
          <div class="detail-item">
            <span class="detail-label">Account:</span>
            <span class="detail-value">{result.ml_nickname}</span>
          </div>
        {/if}

        {#if result.ml_email}
          <div class="detail-item">
            <span class="detail-label">Email:</span>
            <span class="detail-value">{result.ml_email}</span>
          </div>
        {/if}

        <div class="detail-item">
          <span class="detail-label">Marketplace:</span>
          <span class="detail-value">{result.ml_site_id}</span>
        </div>

        <div class="detail-item">
          <span class="detail-label">Status:</span>
          <span class="detail-value status-{result.connection_health}">
            {result.connection_health}
          </span>
        </div>
      </div>

      <div class="success-actions">
        <p class="redirect-message">You'll be redirected to your dashboard in a few seconds...</p>
        <button class="action-button primary" on:click={goToDashboard}>
          Go to Dashboard Now
        </button>
      </div>
    </div>
  {:else if callbackState === 'error'}
    <!-- Error state -->
    <div class="callback-card error">
      <div class="error-icon">❌</div>
      <h1>Connection Failed</h1>

      {#if isManagerAccountError}
        <!-- Manager account specific error -->
        <div class="manager-account-error">
          <h2>Manager Account Required</h2>
          <div class="error-content">
            <div class="error-explanation">
              <p>
                <strong>Only MercadoLibre manager accounts can connect to IntelliPost AI.</strong>
                Collaborator accounts cannot authorize applications.
              </p>
              <p>
                If you're using a collaborator account, please contact your account manager to
                complete this connection with a manager account.
              </p>
            </div>

            <div class="resolution-steps">
              <h3>To resolve this:</h3>
              <ol>
                <li>Log out of your current MercadoLibre account</li>
                <li>Log in with a manager account</li>
                <li>Try the connection process again</li>
              </ol>
            </div>
          </div>
        </div>
      {:else if isRateLimitError}
        <!-- Rate limit specific error -->
        <div class="rate-limit-error">
          <h2>Too Many Requests</h2>
          <p>You've made too many connection attempts. Please wait before trying again.</p>
          {#if countdown > 0}
            <div class="countdown">
              <p>You can try again in <strong>{countdown}</strong> seconds.</p>
            </div>
          {:else}
            <p class="can-retry">You can now try connecting again.</p>
          {/if}
        </div>
      {:else}
        <!-- General error -->
        <div class="general-error">
          <p class="error-message">{error}</p>
        </div>
      {/if}

      <!-- Error actions -->
      <div class="error-actions">
        {#if isRateLimitError}
          <button class="action-button primary" on:click={tryAgain} disabled={countdown > 0}>
            {countdown > 0 ? `Wait ${countdown}s` : 'Try Again'}
          </button>
        {:else}
          <button class="action-button primary" on:click={tryAgain}> Try Again </button>
        {/if}

        <button class="action-button secondary" on:click={goToDashboard}>
          Back to Dashboard
        </button>

        <button class="action-button tertiary" on:click={copyErrorDetails}>
          Copy Error Details
        </button>
      </div>

      <!-- Support information -->
      <div class="support-info">
        <p>
          If you continue to experience issues, please contact support with the error details above.
        </p>
      </div>
    </div>
  {/if}
</div>

<style>
  .callback-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .callback-card {
    background: white;
    border-radius: 16px;
    padding: 40px;
    max-width: 600px;
    width: 100%;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    text-align: center;
    animation: slideUp 0.5s ease-out;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .callback-card h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 20px 0 16px 0;
    color: #111827;
  }

  .callback-card h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 16px 0 12px 0;
    color: #111827;
  }

  .callback-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 16px 0 8px 0;
    color: #111827;
  }

  .callback-card p {
    color: #6b7280;
    margin-bottom: 16px;
    line-height: 1.6;
  }

  /* Processing state */
  .callback-card.processing {
    border-top: 4px solid #3b82f6;
  }

  .loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid #e5e7eb;
    border-left: 4px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px auto;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Success state */
  .callback-card.success {
    border-top: 4px solid #10b981;
  }

  .success-icon {
    font-size: 4rem;
    margin-bottom: 20px;
  }

  .connection-details {
    background-color: #f9fafb;
    border-radius: 8px;
    padding: 20px;
    margin: 24px 0;
    text-align: left;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .detail-item:last-child {
    border-bottom: none;
  }

  .detail-label {
    font-weight: 500;
    color: #374151;
  }

  .detail-value {
    font-weight: 600;
    color: #111827;
  }

  .detail-value.status-healthy {
    color: #10b981;
  }

  .detail-value.status-warning {
    color: #f59e0b;
  }

  .success-actions {
    margin-top: 32px;
  }

  .redirect-message {
    font-style: italic;
    margin-bottom: 16px;
  }

  /* Error state */
  .callback-card.error {
    border-top: 4px solid #ef4444;
  }

  .error-icon {
    font-size: 4rem;
    margin-bottom: 20px;
  }

  .manager-account-error {
    text-align: left;
    margin: 24px 0;
  }

  .error-content {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 20px;
    margin: 16px 0;
  }

  .error-explanation {
    margin-bottom: 20px;
  }

  .error-explanation p {
    margin-bottom: 12px;
    color: #991b1b;
  }

  .resolution-steps h3 {
    color: #991b1b;
    margin-bottom: 12px;
  }

  .resolution-steps ol {
    color: #991b1b;
    margin-left: 20px;
  }

  .resolution-steps li {
    margin-bottom: 8px;
  }

  .rate-limit-error {
    text-align: center;
    margin: 24px 0;
  }

  .countdown {
    background-color: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
  }

  .countdown p {
    margin: 0;
    color: #92400e;
    font-weight: 600;
  }

  .can-retry {
    color: #059669;
    font-weight: 600;
  }

  .general-error {
    margin: 24px 0;
  }

  .error-message {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 16px;
    color: #991b1b;
    white-space: pre-line;
    text-align: left;
  }

  /* Action buttons */
  .success-actions,
  .error-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 32px;
  }

  .action-button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
  }

  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-button.primary {
    background-color: #3b82f6;
    color: white;
  }

  .action-button.primary:hover:not(:disabled) {
    background-color: #2563eb;
  }

  .action-button.secondary {
    background-color: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
  }

  .action-button.secondary:hover:not(:disabled) {
    background-color: #e5e7eb;
  }

  .action-button.tertiary {
    background-color: transparent;
    color: #6b7280;
    border: 1px solid #d1d5db;
  }

  .action-button.tertiary:hover:not(:disabled) {
    background-color: #f3f4f6;
    color: #374151;
  }

  /* Support info */
  .support-info {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
  }

  .support-info p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .callback-container {
      padding: 10px;
    }

    .callback-card {
      padding: 24px;
    }

    .callback-card h1 {
      font-size: 1.5rem;
    }

    .success-actions,
    .error-actions {
      gap: 8px;
    }

    .action-button {
      width: 100%;
    }

    .detail-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }
  }
</style>
