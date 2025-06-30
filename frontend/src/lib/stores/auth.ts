// Authentication store for managing user state
import { writable, derived, get } from 'svelte/store';
import type { User, AuthResponse, APIResponse } from '$types';
import { authAPI } from '$lib/api/auth';
import { browser } from '$app/environment';

// Authentication state interface
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}

// Initial state
const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: false,
  error: null,
};

// Create the main auth store
function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(initialState);

  // Token storage keys
  const ACCESS_TOKEN_KEY = 'intellipost_access_token';
  const REFRESH_TOKEN_KEY = 'intellipost_refresh_token';
  const USER_KEY = 'intellipost_user';

  // Helper functions for secure storage
  const storage = {
    get: (key: string): string | null => {
      if (!browser) return null;
      try {
        return localStorage.getItem(key);
      } catch {
        return null;
      }
    },
    set: (key: string, value: string): void => {
      if (!browser) return;
      try {
        localStorage.setItem(key, value);
      } catch {
        // Silently fail if storage is not available
      }
    },
    remove: (key: string): void => {
      if (!browser) return;
      try {
        localStorage.removeItem(key);
      } catch {
        // Silently fail if storage is not available
      }
    },
    clear: (): void => {
      if (!browser) return;
      try {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      } catch {
        // Silently fail if storage is not available
      }
    }
  };

  return {
    subscribe,

    // Initialize auth state from storage
    init: (): void => {
      const accessToken = storage.get(ACCESS_TOKEN_KEY);
      const refreshToken = storage.get(REFRESH_TOKEN_KEY);
      const userData = storage.get(USER_KEY);

      if (accessToken && refreshToken && userData) {
        try {
          const user: User = JSON.parse(userData);
          update(state => ({
            ...state,
            user,
            accessToken,
            refreshToken,
            error: null
          }));

          // Validate token by checking session
          authStore.validateSession();
        } catch {
          // Clear invalid stored data
          storage.clear();
        }
      }
    },

    // Register new user
    register: async (email: string, password: string): Promise<boolean> => {
      update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response: APIResponse<AuthResponse> = await authAPI.register(email, password);

        if (response.success && response.data) {
          const { user_id, email: userEmail, access_token, refresh_token } = response.data;
          const user: User = { user_id, email: userEmail };

          // Store tokens and user data
          storage.set(ACCESS_TOKEN_KEY, access_token);
          storage.set(REFRESH_TOKEN_KEY, refresh_token);
          storage.set(USER_KEY, JSON.stringify(user));

          update(state => ({
            ...state,
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isLoading: false,
            error: null
          }));

          return true;
        } else {
          update(state => ({
            ...state,
            isLoading: false,
            error: response.error || 'Registration failed'
          }));
          return false;
        }
      } catch (error) {
        update(state => ({
          ...state,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Registration failed'
        }));
        return false;
      }
    },

    // Login user
    login: async (email: string, password: string): Promise<boolean> => {
      update(state => ({ ...state, isLoading: true, error: null }));

      try {
        const response: APIResponse<AuthResponse> = await authAPI.login(email, password);

        if (response.success && response.data) {
          const { user_id, email: userEmail, access_token, refresh_token } = response.data;
          const user: User = { user_id, email: userEmail };

          // Store tokens and user data
          storage.set(ACCESS_TOKEN_KEY, access_token);
          storage.set(REFRESH_TOKEN_KEY, refresh_token);
          storage.set(USER_KEY, JSON.stringify(user));

          update(state => ({
            ...state,
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isLoading: false,
            error: null
          }));

          return true;
        } else {
          update(state => ({
            ...state,
            isLoading: false,
            error: response.error || 'Login failed'
          }));
          return false;
        }
      } catch (error) {
        update(state => ({
          ...state,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Login failed'
        }));
        return false;
      }
    },

    // Logout user
    logout: async (): Promise<void> => {
      const currentState = get({ subscribe });

      // Call logout API if we have a token
      if (currentState.accessToken) {
        try {
          await authAPI.logout(currentState.accessToken);
        } catch {
          // Continue with logout even if API call fails
        }
      }

      // Clear storage and state
      storage.clear();
      set(initialState);
    },

    // Refresh authentication tokens
    refreshTokens: async (): Promise<boolean> => {
      const currentState = get({ subscribe });

      if (!currentState.refreshToken) {
        return false;
      }

      try {
        const response = await authAPI.refreshToken(currentState.refreshToken);

        if (response.success && response.data) {
          const { access_token, refresh_token } = response.data;

          // Update stored tokens
          storage.set(ACCESS_TOKEN_KEY, access_token);
          storage.set(REFRESH_TOKEN_KEY, refresh_token);

          update(state => ({
            ...state,
            accessToken: access_token,
            refreshToken: refresh_token,
            error: null
          }));

          return true;
        } else {
          // Refresh failed, logout user
          authStore.logout();
          return false;
        }
      } catch {
        // Refresh failed, logout user
        authStore.logout();
        return false;
      }
    },

    // Validate current session
    validateSession: async (): Promise<boolean> => {
      const currentState = get({ subscribe });

      if (!currentState.accessToken) {
        return false;
      }

      try {
        const response = await authAPI.getSession(currentState.accessToken);

        if (response.success && response.data) {
          // Session is valid, update user data if needed
          const { user_id, email } = response.data;
          const user: User = { user_id, email };

          update(state => ({
            ...state,
            user,
            error: null
          }));

          storage.set(USER_KEY, JSON.stringify(user));
          return true;
        } else {
          // Session invalid, try to refresh
          return await authStore.refreshTokens();
        }
      } catch {
        // Session validation failed, try to refresh
        return await authStore.refreshTokens();
      }
    },

    // Clear error
    clearError: (): void => {
      update(state => ({ ...state, error: null }));
    },
  };
}

// Create and export the auth store
export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(
  authStore,
  ($auth) => $auth.user !== null && $auth.accessToken !== null
);

export const currentUser = derived(
  authStore,
  ($auth) => $auth.user
);

export const isLoading = derived(
  authStore,
  ($auth) => $auth.isLoading
);

export const authError = derived(
  authStore,
  ($auth) => $auth.error
);

// Auto-initialize auth store when module loads
if (browser) {
  authStore.init();
}
