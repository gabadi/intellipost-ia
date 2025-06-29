/**
 * Authentication store for managing user authentication state.
 *
 * Provides reactive authentication state, login/logout functionality,
 * and automatic token refresh with localStorage persistence.
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { AuthState, User, LoginFormData, RegisterFormData, PasswordChangeRequest } from '../types/auth';
import { authAPI } from '../api/auth';

// Storage keys
const STORAGE_KEYS = {
  USER: 'intellipost_user',
  ACCESS_TOKEN: 'intellipost_access_token',
  REFRESH_TOKEN: 'intellipost_refresh_token',
} as const;

// Create initial auth state
function createInitialAuthState(): AuthState {
  if (!browser) {
    return {
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    };
  }

  // Try to restore authentication state from localStorage
  try {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    const storedAccessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const storedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);

    if (storedUser && storedAccessToken && storedRefreshToken) {
      const user = JSON.parse(storedUser);
      return {
        user,
        accessToken: storedAccessToken,
        refreshToken: storedRefreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    }
  } catch (error) {
    console.warn('Failed to restore auth state from localStorage:', error);
    // Clear potentially corrupted data
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  return {
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  };
}

// Create the auth store
function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(createInitialAuthState());

  return {
    subscribe,

    /**
     * Set loading state
     */
    setLoading: (loading: boolean) => {
      update(state => ({ ...state, isLoading: loading, error: null }));
    },

    /**
     * Set error state
     */
    setError: (error: string | null) => {
      update(state => ({ ...state, error, isLoading: false }));
    },

    /**
     * Set authentication state after successful login/register
     */
    setAuthenticated: (user: User, accessToken: string, refreshToken: string) => {
      const newState: AuthState = {
        user,
        accessToken,
        refreshToken,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

      set(newState);

      // Persist to localStorage
      if (browser) {
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
      }

      // Set token in API client
      authAPI.setAuthToken(accessToken);
    },

    /**
     * Clear authentication state
     */
    clearAuth: () => {
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });

      // Clear localStorage
      if (browser) {
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      }

      // Clear token in API client
      authAPI.setAuthToken(null);
    },

    /**
     * Update access token (for refresh)
     */
    updateAccessToken: (accessToken: string) => {
      update(state => ({ ...state, accessToken }));

      if (browser) {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
      }

      authAPI.setAuthToken(accessToken);
    },

    /**
     * Register new user
     */
    register: async (data: RegisterFormData) => {
      update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response = await authAPI.register(data);

        const newState: AuthState = {
          user: response.user,
          accessToken: response.tokens.access_token,
          refreshToken: response.tokens.refresh_token,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        };

        set(newState);

        // Persist to localStorage
        if (browser) {
          localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.tokens.access_token);
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.tokens.refresh_token);
        }

        authAPI.setAuthToken(response.tokens.access_token);

        return { success: true, user: response.user };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Registration failed';
        update(state => ({ ...state, isLoading: false, error: errorMessage }));
        return { success: false, error: errorMessage };
      }
    },

    /**
     * Login user
     */
    login: async (data: LoginFormData) => {
      update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response = await authAPI.login(data);

        const newState: AuthState = {
          user: response.user,
          accessToken: response.tokens.access_token,
          refreshToken: response.tokens.refresh_token,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        };

        set(newState);

        // Persist to localStorage
        if (browser) {
          localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user));
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.tokens.access_token);
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.tokens.refresh_token);
        }

        authAPI.setAuthToken(response.tokens.access_token);

        return { success: true, user: response.user };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Login failed';
        update(state => ({ ...state, isLoading: false, error: errorMessage }));
        return { success: false, error: errorMessage };
      }
    },

    /**
     * Logout user
     */
    logout: async () => {
      update(state => ({ ...state, isLoading: true }));

      try {
        // Get current refresh token
        const currentState = get(authStore);
        if (currentState.refreshToken) {
          await authAPI.logout({ refresh_token: currentState.refreshToken });
        }
      } catch (error) {
        console.warn('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      }

      // Clear local state regardless of API call result
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });

      // Clear localStorage
      if (browser) {
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      }

      authAPI.setAuthToken(null);
    },

    /**
     * Refresh access token
     */
    refreshToken: async () => {
      const currentState = get(authStore);

      if (!currentState.refreshToken) {
        throw new Error('No refresh token available');
      }

      try {
        const response = await authAPI.refreshToken({
          refresh_token: currentState.refreshToken,
        });

        update(state => ({ ...state, accessToken: response.access_token }));

        if (browser) {
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token);
        }

        authAPI.setAuthToken(response.access_token);

        return response.access_token;
      } catch (error) {
        // If refresh fails, clear auth state
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: 'Session expired. Please log in again.',
        });

        if (browser) {
          localStorage.removeItem(STORAGE_KEYS.USER);
          localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        }

        authAPI.setAuthToken(null);
        throw error;
      }
    },

    /**
     * Change user password
     */
    changePassword: async (data: PasswordChangeRequest) => {
      update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response = await authAPI.changePassword(data);

        update(state => ({ ...state, isLoading: false }));

        return { success: true, message: response.message };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Password change failed';
        update(state => ({ ...state, isLoading: false, error: errorMessage }));
        return { success: false, error: errorMessage };
      }
    },

    /**
     * Initialize auth state (call on app startup)
     */
    initialize: async () => {
      const currentState = get(authStore);

      if (currentState.accessToken) {
        authAPI.setAuthToken(currentState.accessToken);

        // Optionally verify token is still valid
        try {
          await authAPI.getCurrentUser();
        } catch (error) {
          console.warn('Token validation failed on initialization:', error);
          // Try to refresh token
          if (currentState.refreshToken) {
            try {
              await authStore.refreshToken();
            } catch (refreshError) {
              console.warn('Token refresh failed on initialization:', refreshError);
              // Clear invalid auth state
              set({
                user: null,
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
              });
            }
          }
        }
      }
    },
  };
}

// Helper function to get current state
function get<T>(store: { subscribe: (fn: (value: T) => void) => () => void }): T {
  let value: T;
  const unsubscribe = store.subscribe(v => (value = v));
  unsubscribe();
  return value!;
}

// Create and export the auth store
export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const currentUser = derived(authStore, $auth => $auth.user);
export const authError = derived(authStore, $auth => $auth.error);
export const authLoading = derived(authStore, $auth => $auth.isLoading);
