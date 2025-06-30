// Authentication API client
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  SessionResponse,
  APIResponse
} from '$types';
import { apiClient } from './client';

class AuthAPI {
  /**
   * Register a new user account
   */
  async register(email: string, password: string): Promise<APIResponse<AuthResponse>> {
    const request: RegisterRequest = { email, password };
    return apiClient.post<AuthResponse>('/api/auth/register', request);
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<APIResponse<AuthResponse>> {
    const request: LoginRequest = { email, password };
    return apiClient.post<AuthResponse>('/api/auth/login', request);
  }

  /**
   * Logout current user
   */
  async logout(accessToken: string): Promise<APIResponse<void>> {
    return apiClient.post<void>('/api/auth/logout', undefined, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
  }

  /**
   * Refresh authentication tokens
   */
  async refreshToken(refreshToken: string): Promise<APIResponse<TokenResponse>> {
    return apiClient.post<TokenResponse>('/api/auth/refresh', {
      refresh_token: refreshToken
    });
  }

  /**
   * Get current session information
   */
  async getSession(accessToken: string): Promise<APIResponse<SessionResponse>> {
    return apiClient.get<SessionResponse>('/api/auth/session', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
  }

  /**
   * Change user password
   */
  async changePassword(
    accessToken: string,
    currentPassword: string,
    newPassword: string
  ): Promise<APIResponse<void>> {
    return apiClient.post<void>('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    }, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
  }
}

// Singleton instance
export const authAPI = new AuthAPI();
