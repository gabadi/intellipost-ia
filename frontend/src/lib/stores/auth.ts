/**
 * Authentication store for IntelliPost AI frontend.
 *
 * Manages user authentication state, token storage, and automatic
 * token refresh with mobile-optimized behavior.
 */

import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import { AuthAPI, extractAuthError } from '../api/auth';
import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  User,
  UserProfileUpdateRequest,
  ChangePasswordRequest,
} from '../types/auth';

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'intellipost_access_token',
  REFRESH_TOKEN: 'intellipost_refresh_token',
  USER: 'intellipost_user',
};

// Create initial auth state
const createInitialAuthState = (): AuthState => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
});

// Create the auth store
function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(createInitialAuthState());

  /**
   * Save tokens and user data to storage
   */
  const saveToStorage = (accessToken: string, refreshToken: string, user: User) => {
    try {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    } catch (error) {
      // Silently handle localStorage errors in production
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
        console.warn('Failed to save auth data to localStorage:', error);
      }
    }
  };

  /**
   * Load tokens and user data from storage
   */
  const loadFromStorage = (): {
    accessToken: string | null;
    refreshToken: string | null;
    user: User | null;
  } => {
    try {
      const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      const userStr = localStorage.getItem(STORAGE_KEYS.USER);
      const user = userStr ? JSON.parse(userStr) : null;

      return { accessToken, refreshToken, user };
    } catch (error) {
      // Silently handle localStorage errors in production
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
        console.warn('Failed to load auth data from localStorage:', error);
      }
      return { accessToken: null, refreshToken: null, user: null };
    }
  };

  /**
   * Clear storage and reset state
   */
  const clearStorage = () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
    } catch (error) {
      // Silently handle localStorage errors in production
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
        console.warn('Failed to clear auth data from localStorage:', error);
      }
    }
  };

  /**
   * Set authenticated state
   */
  const setAuthenticated = (accessToken: string, refreshToken: string, user: User) => {
    saveToStorage(accessToken, refreshToken, user);
    set({
      user,
      accessToken,
      refreshToken,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
  };

  /**
   * Set error state
   */
  const setError = (error: string) => {
    update(state => ({
      ...state,
      error,
      isLoading: false,
    }));
  };

  /**
   * Set loading state
   */
  const setLoading = (isLoading: boolean) => {
    update(state => ({
      ...state,
      isLoading,
      error: null,
    }));
  };

  return {
    subscribe,

    /**
     * Initialize auth store from localStorage
     */
    init: () => {
      const { accessToken, refreshToken, user } = loadFromStorage();
      if (accessToken && refreshToken && user) {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      }
    },

    /**
     * Register a new user
     */
    register: async (userData: RegisterRequest): Promise<void> => {
      setLoading(true);

      try {
        const response = await AuthAPI.register(userData);

        if (response.success && response.data) {
          const { access_token, refresh_token, user } = response.data;
          setAuthenticated(access_token, refresh_token, user);
          goto('/dashboard');
        } else {
          const authError = extractAuthError(response.error);
          setError(authError.message);
        }
      } catch (error) {
        const authError = extractAuthError(error);
        setError(authError.message);
      }
    },

    /**
     * Login user
     */
    login: async (credentials: LoginRequest): Promise<void> => {
      setLoading(true);

      try {
        const response = await AuthAPI.login(credentials);

        if (response.success && response.data) {
          const { access_token, refresh_token, user } = response.data;
          setAuthenticated(access_token, refresh_token, user);
          goto('/dashboard');
        } else {
          const authError = extractAuthError(response.error);
          setError(authError.message);
        }
      } catch (error) {
        const authError = extractAuthError(error);
        setError(authError.message);
      }
    },

    /**
     * Logout user
     */
    logout: async (): Promise<void> => {
      try {
        // Call logout endpoint for any server-side cleanup
        await AuthAPI.logout();
      } catch (error) {
        // Silently handle logout API failures in production
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.warn('Logout API call failed:', error);
        }
        // Continue with client-side cleanup even if API call fails
      }

      clearStorage();
      set(createInitialAuthState());
      goto('/auth/login');
    },

    /**
     * Refresh access token
     */
    refreshToken: async (): Promise<boolean> => {
      const { refreshToken } = loadFromStorage();

      if (!refreshToken) {
        clearStorage();
        set(createInitialAuthState());
        return false;
      }

      try {
        const response = await AuthAPI.refreshToken({ refresh_token: refreshToken });

        if (response.success && response.data) {
          const { access_token, refresh_token, user } = response.data;
          setAuthenticated(access_token, refresh_token, user);
          return true;
        } else {
          clearStorage();
          set(createInitialAuthState());
          return false;
        }
      } catch {
        // Remove unused 'error' variable
        clearStorage();
        set(createInitialAuthState());
        return false;
      }
    },

    /**
     * Update user profile
     */
    updateProfile: async (profileData: UserProfileUpdateRequest): Promise<boolean> => {
      setLoading(true);

      try {
        const response = await AuthAPI.updateProfile(profileData);

        if (response.success && response.data) {
          update(state => ({
            ...state,
            user: response.data
              ? {
                  id: response.data.id,
                  email: response.data.email,
                  first_name: response.data.first_name,
                  last_name: response.data.last_name,
                  is_active: response.data.is_active,
                  is_email_verified: response.data.is_email_verified,
                  status: response.data.status,
                  created_at: response.data.created_at,
                  last_login_at: response.data.last_login_at,
                }
              : state.user,
            isLoading: false,
            error: null,
          }));

          // Update user in localStorage
          if (response.data) {
            const user = {
              id: response.data.id,
              email: response.data.email,
              first_name: response.data.first_name,
              last_name: response.data.last_name,
              is_active: response.data.is_active,
              is_email_verified: response.data.is_email_verified,
              status: response.data.status,
              created_at: response.data.created_at,
              last_login_at: response.data.last_login_at,
            };
            try {
              localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
            } catch (error) {
              // Silently handle localStorage errors in production
              if (import.meta.env.DEV) {
                // eslint-disable-next-line no-console
                console.warn('Failed to update user in localStorage:', error);
              }
            }
          }

          return true;
        } else {
          const authError = extractAuthError(response.error);
          setError(authError.message);
          return false;
        }
      } catch (error) {
        const authError = extractAuthError(error);
        setError(authError.message);
        return false;
      }
    },

    /**
     * Change user password
     */
    changePassword: async (passwordData: ChangePasswordRequest): Promise<boolean> => {
      setLoading(true);

      try {
        const response = await AuthAPI.changePassword(passwordData);

        if (response.success) {
          update(state => ({
            ...state,
            isLoading: false,
            error: null,
          }));
          return true;
        } else {
          const authError = extractAuthError(response.error);
          setError(authError.message);
          return false;
        }
      } catch (error) {
        const authError = extractAuthError(error);
        setError(authError.message);
        return false;
      }
    },

    /**
     * Set error state
     */
    setError: (error: string) => {
      update(state => ({
        ...state,
        error,
        isLoading: false,
      }));
    },

    /**
     * Clear error state
     */
    clearError: () => {
      update(state => ({
        ...state,
        error: null,
      }));
    },
  };
}

export const authStore = createAuthStore();
