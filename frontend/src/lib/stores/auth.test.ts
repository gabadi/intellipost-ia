/**
 * Unit tests for auth store
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { authStore } from './auth';

// Mock the API
vi.mock('../api/auth', () => ({
  AuthAPI: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
  },
  extractAuthError: vi.fn(),
}));

// Mock SvelteKit navigation
vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('Auth Store', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store to initial state
    authStore.logout();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const state = get(authStore);

      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('Initialization', () => {
    it('should initialize from localStorage when tokens exist', () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        is_active: true,
        is_email_verified: true,
        status: 'active',
        created_at: '2023-01-01T00:00:00Z',
        last_login_at: null,
      };

      localStorageMock.getItem.mockImplementation((key: string) => {
        switch (key) {
          case 'intellipost_access_token':
            return 'mock_access_token';
          case 'intellipost_refresh_token':
            return 'mock_refresh_token';
          case 'intellipost_user':
            return JSON.stringify(mockUser);
          default:
            return null;
        }
      });

      authStore.init();

      const state = get(authStore);
      expect(state.user).toEqual(mockUser);
      expect(state.accessToken).toBe('mock_access_token');
      expect(state.refreshToken).toBe('mock_refresh_token');
      expect(state.isAuthenticated).toBe(true);
    });

    it('should handle localStorage errors gracefully', () => {
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });

      // Should not throw
      expect(() => authStore.init()).not.toThrow();

      const state = get(authStore);
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('Login', () => {
    it('should handle successful login', async () => {
      const { AuthAPI } = await import('../api/auth');
      const { goto } = await import('$app/navigation');

      const mockResponse = {
        success: true,
        data: {
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
          token_type: 'Bearer',
          expires_in: 3600,
          user: {
            id: '123',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User',
            is_active: true,
            is_email_verified: true,
            status: 'active',
            created_at: '2023-01-01T00:00:00Z',
            last_login_at: null,
          },
        },
      };

      vi.mocked(AuthAPI.login).mockResolvedValue(mockResponse);

      await authStore.login({
        email: 'test@example.com',
        password: 'password123',
      });

      const state = get(authStore);
      expect(state.isAuthenticated).toBe(true);
      expect(state.user).toEqual(mockResponse.data.user);
      expect(state.accessToken).toBe('new_access_token');
      expect(state.refreshToken).toBe('new_refresh_token');
      expect(state.error).toBeNull();
      expect(state.isLoading).toBe(false);

      // Should save to localStorage
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'intellipost_access_token',
        'new_access_token'
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'intellipost_refresh_token',
        'new_refresh_token'
      );

      // Should redirect to dashboard
      expect(goto).toHaveBeenCalledWith('/dashboard');
    });

    it('should handle login failure', async () => {
      const { AuthAPI, extractAuthError } = await import('../api/auth');

      const mockError = {
        error_code: 'INVALID_CREDENTIALS',
        message: 'Invalid email or password',
      };

      vi.mocked(AuthAPI.login).mockResolvedValue({
        success: false,
        error: 'Login failed',
        data: null as never,
      });

      vi.mocked(extractAuthError).mockReturnValue(mockError);

      await authStore.login({
        email: 'test@example.com',
        password: 'wrong_password',
      });

      const state = get(authStore);
      expect(state.isAuthenticated).toBe(false);
      expect(state.error).toBe(mockError.message);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('Registration', () => {
    it('should handle successful registration', async () => {
      const { AuthAPI } = await import('../api/auth');
      const { goto } = await import('$app/navigation');

      const mockResponse = {
        success: true,
        data: {
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
          token_type: 'Bearer',
          expires_in: 3600,
          user: {
            id: '123',
            email: 'new@example.com',
            first_name: 'New',
            last_name: 'User',
            is_active: true,
            is_email_verified: false,
            status: 'pending_verification',
            created_at: '2023-01-01T00:00:00Z',
            last_login_at: null,
          },
        },
      };

      vi.mocked(AuthAPI.register).mockResolvedValue(mockResponse);

      await authStore.register({
        email: 'new@example.com',
        password: 'password123',
        first_name: 'New',
        last_name: 'User',
      });

      const state = get(authStore);
      expect(state.isAuthenticated).toBe(true);
      expect(state.user).toEqual(mockResponse.data.user);
      expect(goto).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('Logout', () => {
    it('should clear state and storage on logout', async () => {
      const { goto } = await import('$app/navigation');

      // Set authenticated state first
      authStore.init();
      localStorageMock.getItem.mockReturnValue('some_token');

      await authStore.logout();

      const state = get(authStore);
      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);

      // Should clear localStorage
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('intellipost_access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('intellipost_refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('intellipost_user');

      // Should redirect to login
      expect(goto).toHaveBeenCalledWith('/auth/login');
    });
  });

  describe('Token Refresh', () => {
    it('should refresh tokens successfully', async () => {
      const { AuthAPI } = await import('../api/auth');

      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'intellipost_refresh_token') {
          return 'valid_refresh_token';
        }
        return null;
      });

      const mockResponse = {
        success: true,
        data: {
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
          token_type: 'Bearer',
          expires_in: 3600,
          user: {
            id: '123',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User',
            is_active: true,
            is_email_verified: true,
            status: 'active',
            created_at: '2023-01-01T00:00:00Z',
            last_login_at: null,
          },
        },
      };

      vi.mocked(AuthAPI.refreshToken).mockResolvedValue(mockResponse);

      const result = await authStore.refreshToken();

      expect(result).toBe(true);
      const state = get(authStore);
      expect(state.isAuthenticated).toBe(true);
      expect(state.accessToken).toBe('new_access_token');
    });

    it('should handle refresh failure', async () => {
      const { AuthAPI } = await import('../api/auth');

      localStorageMock.getItem.mockReturnValue('invalid_refresh_token');

      vi.mocked(AuthAPI.refreshToken).mockResolvedValue({
        success: false,
        error: 'Invalid refresh token',
        data: null as never,
      });

      const result = await authStore.refreshToken();

      expect(result).toBe(false);
      const state = get(authStore);
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('should clear errors', () => {
      // Set an error first
      authStore.login({ email: 'test', password: 'test' });

      authStore.clearError();

      const state = get(authStore);
      expect(state.error).toBeNull();
    });
  });
});
