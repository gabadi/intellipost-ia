/**
 * Authentication API client for frontend application.
 *
 * This module provides functions for making authenticated API requests
 * with automatic token refresh and enhanced error handling.
 */

import type { LoginRequest, RegisterRequest, TokenResponse, User } from '$lib/types/auth';
// ErrorHandler is imported but not used in this file

// API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * API client class for authentication endpoints.
 */
export class AuthApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Login user with credentials.
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'Login failed',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }

    return response.json();
  }

  /**
   * Register new user account.
   */
  async register(userData: RegisterRequest): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'Registration failed',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }

    return response.json();
  }

  /**
   * Refresh access token.
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'Token refresh failed',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }

    return response.json();
  }

  /**
   * Logout user (invalidate tokens).
   */
  async logout(accessToken: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/auth/logout`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'Logout failed',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }
  }

  /**
   * Get current user profile.
   */
  async getCurrentUser(accessToken: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'Failed to get user profile',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }

    return response.json();
  }

  /**
   * Make authenticated API request with automatic token refresh.
   */
  async authenticatedRequest<T>(
    url: string,
    options: RequestInit,
    accessToken: string,
    refreshToken?: string
  ): Promise<T> {
    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
      },
    };

    let response = await fetch(`${this.baseUrl}${url}`, requestOptions);

    // If unauthorized and we have a refresh token, try to refresh
    if (response.status === 401 && refreshToken) {
      try {
        const tokenResponse = await this.refreshToken(refreshToken);

        // Retry the original request with new token
        requestOptions.headers = {
          ...requestOptions.headers,
          Authorization: `Bearer ${tokenResponse.access_token}`,
        };

        response = await fetch(`${this.baseUrl}${url}`, requestOptions);
      } catch {
        // Refresh failed, throw original 401 error
        const errorObj = {
          message: 'Authentication failed',
          status: 401,
          detail: 'Token refresh failed',
        };
        throw errorObj;
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorObj = {
        message: error.detail || 'API request failed',
        status: response.status,
        detail: error.detail,
      };
      throw errorObj;
    }

    return response.json();
  }
}

// Default auth API client instance
export const authApi = new AuthApiClient();

// Utility functions for common auth operations
export const authOperations = {
  /**
   * Login user and return token response.
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    return authApi.login({ email, password });
  },

  /**
   * Register user and return token response.
   */
  async register(
    email: string,
    password: string,
    firstName?: string,
    lastName?: string
  ): Promise<TokenResponse> {
    return authApi.register({
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
  },

  /**
   * Refresh access token.
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    return authApi.refreshToken(refreshToken);
  },

  /**
   * Logout user.
   */
  async logout(accessToken: string): Promise<void> {
    return authApi.logout(accessToken);
  },
};
