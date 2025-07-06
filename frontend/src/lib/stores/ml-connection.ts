/**
 * MercadoLibre Connection Store
 *
 * Manages state for MercadoLibre OAuth integration and connection status.
 * Implements the story requirements for ML connection management.
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type {
  MLConnectionState,
  MLOAuthInitiateResponse,
  MLOAuthCallbackResponse,
} from '$lib/types/ml-connection';
import { mlOAuthApi } from '$lib/api/ml-oauth';

// Initial state
const initialState: MLConnectionState = {
  isConnected: false,
  connectionHealth: 'disconnected',
  mlNickname: null,
  mlEmail: null,
  mlSiteId: null,
  expiresAt: null,
  lastValidatedAt: null,
  isLoading: false,
  error: null,
  shouldRefresh: false,
  timeUntilRefresh: null,
};

// Create writable store
const { subscribe, set, update } = writable<MLConnectionState>(initialState);

// Derived stores for specific aspects
export const isMLConnected = derived({ subscribe }, $mlConnection => $mlConnection.isConnected);

export const mlConnectionHealth = derived(
  { subscribe },
  $mlConnection => $mlConnection.connectionHealth
);

export const mlUserInfo = derived({ subscribe }, $mlConnection => ({
  nickname: $mlConnection.mlNickname,
  email: $mlConnection.mlEmail,
  siteId: $mlConnection.mlSiteId,
}));

// Action creators
export const mlConnectionStore = {
  subscribe,

  /**
   * Initialize the store and check connection status
   */
  async init(): Promise<void> {
    if (!browser) return;

    await this.checkStatus();
  },

  /**
   * Initiate ML OAuth connection flow
   */
  async initiateConnection(
    redirectUri: string,
    siteId: string = 'MLA'
  ): Promise<MLOAuthInitiateResponse> {
    update(state => ({ ...state, isLoading: true, error: null }));

    try {
      const response = await mlOAuthApi.initiateOAuth(redirectUri, siteId);

      // Store PKCE parameters in sessionStorage for callback
      if (browser) {
        sessionStorage.setItem('ml_oauth_state', response.state);
        sessionStorage.setItem('ml_oauth_code_verifier', response.code_verifier);
      }

      update(state => ({ ...state, isLoading: false }));
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initiate connection';
      update(state => ({
        ...state,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  },

  /**
   * Handle OAuth callback after user authorization
   */
  async handleCallback(code: string, state: string): Promise<MLOAuthCallbackResponse> {
    update(state => ({ ...state, isLoading: true, error: null }));

    try {
      // Get stored PKCE parameters
      const storedState = browser ? sessionStorage.getItem('ml_oauth_state') : null;
      const codeVerifier = browser ? sessionStorage.getItem('ml_oauth_code_verifier') : null;

      if (!storedState || !codeVerifier) {
        throw new Error('OAuth session not found. Please try connecting again.');
      }

      if (storedState !== state) {
        throw new Error('Invalid OAuth state. Possible CSRF attack.');
      }

      const response = await mlOAuthApi.handleCallback(code, state, codeVerifier);

      if (response.success) {
        // Update connection state
        update(currentState => ({
          ...currentState,
          isConnected: true,
          connectionHealth: response.connection_health as
            | 'healthy'
            | 'expired'
            | 'invalid'
            | 'disconnected',
          mlNickname: response.ml_nickname || null,
          mlEmail: response.ml_email || null,
          mlSiteId: response.ml_site_id,
          isLoading: false,
          error: null,
        }));

        // Clean up session storage
        if (browser) {
          sessionStorage.removeItem('ml_oauth_state');
          sessionStorage.removeItem('ml_oauth_code_verifier');
        }

        // Refresh status to get complete info
        await this.checkStatus();
      }

      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to complete connection';
      update(state => ({
        ...state,
        isLoading: false,
        error: errorMessage,
        isConnected: false,
        connectionHealth: 'disconnected',
      }));

      // Clean up session storage on error
      if (browser) {
        sessionStorage.removeItem('ml_oauth_state');
        sessionStorage.removeItem('ml_oauth_code_verifier');
      }

      throw error;
    }
  },

  /**
   * Disconnect ML account
   */
  async disconnect(): Promise<void> {
    update(state => ({ ...state, isLoading: true, error: null }));

    try {
      await mlOAuthApi.disconnect();

      // Reset to disconnected state
      set({
        ...initialState,
        isLoading: false,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to disconnect';
      update(state => ({ ...state, isLoading: false, error: errorMessage }));
      throw error;
    }
  },

  /**
   * Check current connection status
   */
  async checkStatus(): Promise<void> {
    update(state => ({ ...state, isLoading: true, error: null }));

    try {
      const status = await mlOAuthApi.getConnectionStatus();

      update(state => ({
        ...state,
        isConnected: status.is_connected,
        connectionHealth: status.connection_health,
        mlNickname: status.ml_nickname || null,
        mlEmail: status.ml_email || null,
        mlSiteId: status.ml_site_id || null,
        expiresAt: status.expires_at ? new Date(status.expires_at) : null,
        lastValidatedAt: status.last_validated_at ? new Date(status.last_validated_at) : null,
        shouldRefresh: status.should_refresh || false,
        timeUntilRefresh: status.time_until_refresh || null,
        error: status.error_message || null,
        isLoading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to check status';
      update(state => ({
        ...state,
        isLoading: false,
        error: errorMessage,
        isConnected: false,
        connectionHealth: 'disconnected',
      }));
    }
  },

  /**
   * Manually refresh tokens
   */
  async refreshTokens(): Promise<void> {
    update(state => ({ ...state, isLoading: true, error: null }));

    try {
      await mlOAuthApi.refreshTokens();
      // Check status to get updated info
      await this.checkStatus();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to refresh tokens';
      update(state => ({ ...state, isLoading: false, error: errorMessage }));
      throw error;
    }
  },

  /**
   * Clear error state
   */
  clearError(): void {
    update(state => ({ ...state, error: null }));
  },

  /**
   * Reset store to initial state
   */
  reset(): void {
    set(initialState);

    // Clean up session storage
    if (browser) {
      sessionStorage.removeItem('ml_oauth_state');
      sessionStorage.removeItem('ml_oauth_code_verifier');
    }
  },

  /**
   * Check if connection needs attention (expired or invalid)
   */
  needsAttention: derived({ subscribe }, $mlConnection => {
    if (!$mlConnection.isConnected) return false;
    return ['expired', 'invalid'].includes($mlConnection.connectionHealth);
  }),

  /**
   * Get formatted connection status for display
   */
  statusMessage: derived({ subscribe }, $mlConnection => {
    if ($mlConnection.isLoading) return 'Checking connection...';
    if ($mlConnection.error) return $mlConnection.error;

    switch ($mlConnection.connectionHealth) {
      case 'healthy':
        return 'Connected and active';
      case 'expired':
        return 'Connection expired - please reconnect';
      case 'invalid':
        return 'Connection invalid - please reconnect';
      case 'disconnected':
        return 'Not connected to MercadoLibre';
      default:
        return 'Unknown connection status';
    }
  }),
};

// Auto-initialize when in browser
if (browser) {
  mlConnectionStore.init();
}
