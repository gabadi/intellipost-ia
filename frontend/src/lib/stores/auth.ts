/**
 * Authentication store for managing user authentication state.
 *
 * This module provides a Svelte store for authentication state management
 * with automatic token persistence and refresh functionality.
 */

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import type {
  AuthState,
  User,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  AuthEvent,
} from '$lib/types/auth';
import { TOKEN_STORAGE_KEYS } from '$lib/types/auth';
import { authApi } from '$lib/api/auth';
import { ErrorHandler, type AuthError } from '$lib/utils/error-handler';

// Initial authentication state
const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Create the main auth store
export const authStore = writable<AuthState>(initialState);

// Derived stores for common use cases
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const isLoading = derived(authStore, $auth => $auth.isLoading);
export const authError = derived(authStore, $auth => $auth.error);

/**
 * Authentication store manager with methods for login, logout, and token management.
 */
class AuthManager {
  private store = authStore;
  private tokenRefreshTimer: ReturnType<typeof setTimeout> | null = null;

  /**
   * Initialize authentication state from stored tokens.
   * Should be called on app startup.
   */
  async initialize(): Promise<void> {
    if (!browser) return;

    try {
      const accessToken = localStorage.getItem(TOKEN_STORAGE_KEYS.ACCESS_TOKEN);
      const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEYS.REFRESH_TOKEN);
      const userData = localStorage.getItem(TOKEN_STORAGE_KEYS.USER_DATA);

      if (accessToken && refreshToken && userData) {
        const user: User = JSON.parse(userData);

        this.store.update(state => ({
          ...state,
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        }));

        // Set up automatic token refresh
        this.scheduleTokenRefresh();
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to initialize auth state:', error);
      this.clearTokens();
    }
  }

  /**
   * Login user with email and password.
   */
  async login(credentials: LoginRequest): Promise<void> {
    this.store.update(state => ({ ...state, isLoading: true, error: null }));

    try {
      const tokenResponse = await authApi.login(credentials);
      this.setTokens(tokenResponse);
      this.emitAuthEvent('login_success');
    } catch (error) {
      const authError = ErrorHandler.processError(error);
      ErrorHandler.logError(authError, 'login');

      this.store.update(state => ({
        ...state,
        isLoading: false,
        error: authError.details.userMessage,
      }));
      this.emitAuthEvent('login_error');
      throw authError;
    }
  }

  /**
   * Register new user account.
   */
  async register(userData: RegisterRequest): Promise<void> {
    this.store.update(state => ({ ...state, isLoading: true, error: null }));

    try {
      const tokenResponse = await authApi.register(userData);
      this.setTokens(tokenResponse);
    } catch (error) {
      const authError = ErrorHandler.processError(error);
      ErrorHandler.logError(authError, 'register');

      this.store.update(state => ({
        ...state,
        isLoading: false,
        error: authError.details.userMessage,
      }));
      throw authError;
    }
  }

  /**
   * Logout user and clear authentication state.
   */
  async logout(): Promise<void> {
    const currentState = get(this.store);

    // Call logout endpoint if authenticated
    if (currentState.isAuthenticated && currentState.accessToken) {
      try {
        await authApi.logout(currentState.accessToken);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Logout API call failed:', error);
      }
    }

    this.clearTokens();
    this.emitAuthEvent('logout');
  }

  /**
   * Refresh access token using refresh token.
   */
  async refreshToken(): Promise<boolean> {
    const currentState = get(this.store);

    if (!currentState.refreshToken) {
      this.logout();
      return false;
    }

    try {
      const tokenResponse = await authApi.refreshToken(currentState.refreshToken);
      this.setTokens(tokenResponse);
      this.emitAuthEvent('token_refresh');
      return true;
    } catch (error) {
      const authError = ErrorHandler.processError(error);
      ErrorHandler.logError(authError, 'token_refresh');
      this.logout();
      return false;
    }
  }

  /**
   * Clear authentication error.
   */
  clearError(): void {
    this.store.update(state => ({ ...state, error: null }));
  }

  /**
   * Handle authentication errors with retry logic.
   */
  async handleAuthError(
    error: AuthError,
    operation: string,
    retryFn?: () => Promise<void>
  ): Promise<void> {
    if (ErrorHandler.isRetryable(error) && retryFn) {
      const delay = ErrorHandler.getRetryDelay(error);
      if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
        try {
          await retryFn();
        } catch (retryError) {
          const retryAuthError = ErrorHandler.processError(retryError);
          ErrorHandler.logError(retryAuthError, `${operation}_retry`);
          throw retryAuthError;
        }
      }
    }
    throw error;
  }

  /**
   * Set authentication tokens and user data.
   */
  private setTokens(tokenResponse: TokenResponse): void {
    if (browser) {
      localStorage.setItem(TOKEN_STORAGE_KEYS.ACCESS_TOKEN, tokenResponse.access_token);
      localStorage.setItem(TOKEN_STORAGE_KEYS.REFRESH_TOKEN, tokenResponse.refresh_token);
      localStorage.setItem(TOKEN_STORAGE_KEYS.USER_DATA, JSON.stringify(tokenResponse.user));
    }

    this.store.update(state => ({
      ...state,
      user: tokenResponse.user,
      accessToken: tokenResponse.access_token,
      refreshToken: tokenResponse.refresh_token,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    }));

    this.scheduleTokenRefresh();
  }

  /**
   * Clear all authentication tokens and state.
   */
  private clearTokens(): void {
    if (browser) {
      localStorage.removeItem(TOKEN_STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(TOKEN_STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(TOKEN_STORAGE_KEYS.USER_DATA);
    }

    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = null;
    }

    this.store.set(initialState);
  }

  /**
   * Schedule automatic token refresh before expiration.
   */
  private scheduleTokenRefresh(): void {
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
    }

    // Refresh token 2 minutes before expiration (13 minutes for 15 minute tokens)
    const refreshInterval = (15 - 2) * 60 * 1000; // 13 minutes in milliseconds

    this.tokenRefreshTimer = setTimeout(async () => {
      await this.refreshToken();
    }, refreshInterval);
  }

  /**
   * Emit authentication events for external listeners.
   */
  private emitAuthEvent(event: AuthEvent): void {
    if (browser) {
      window.dispatchEvent(new CustomEvent(`auth:${event}`));
    }
  }
}

// Create and export the auth manager instance
export const auth = new AuthManager();

// Initialize auth state when the module loads (client-side only)
if (browser) {
  auth.initialize();
}
