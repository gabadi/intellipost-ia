/**
 * Authentication API client for IntelliPost AI frontend.
 *
 * Provides functions for making authentication-related API calls
 * with automatic token refresh and error handling.
 */

import { apiClient } from './client';
import type { APIResponse } from '../types/api';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  RefreshTokenRequest,
  UserDetail,
  UserProfileUpdateRequest,
  ChangePasswordRequest,
  AuthError,
} from '../types/auth';

export class AuthAPI {
  /**
   * Register a new user account
   */
  static async register(request: RegisterRequest): Promise<APIResponse<TokenResponse>> {
    return apiClient.post<TokenResponse>('/auth/register', request);
  }

  /**
   * Login with email and password
   */
  static async login(request: LoginRequest): Promise<APIResponse<TokenResponse>> {
    return apiClient.post<TokenResponse>('/auth/login', request);
  }

  /**
   * Refresh access token using refresh token
   */
  static async refreshToken(request: RefreshTokenRequest): Promise<APIResponse<TokenResponse>> {
    return apiClient.post<TokenResponse>('/auth/refresh', request);
  }

  /**
   * Logout user (client-side token cleanup)
   */
  static async logout(): Promise<APIResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>('/auth/logout', {});
  }

  /**
   * Get current user profile
   */
  static async getCurrentUser(): Promise<APIResponse<UserDetail>> {
    return apiClient.get<UserDetail>('/users/me');
  }

  /**
   * Update current user profile
   */
  static async updateProfile(request: UserProfileUpdateRequest): Promise<APIResponse<UserDetail>> {
    return apiClient.put<UserDetail>('/users/me', request);
  }

  /**
   * Change current user password
   */
  static async changePassword(
    request: ChangePasswordRequest
  ): Promise<APIResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>('/users/me/change-password', request);
  }

  /**
   * Get feature flags and configuration
   */
  static async getFeatureFlags(): Promise<APIResponse<{ registration_enabled: boolean }>> {
    return apiClient.get<{ registration_enabled: boolean }>('/config/features');
  }
}

/**
 * Helper function to extract error details from auth error responses
 */
export function extractAuthError(error: unknown): AuthError {
  if (typeof error === 'object' && error !== null && 'detail' in error) {
    const detail = (error as any).detail;
    if (typeof detail === 'object' && detail !== null) {
      return {
        error_code: detail.error_code || 'UNKNOWN_ERROR',
        message: detail.message || 'An unknown error occurred',
        details: detail.details,
      };
    }
  }

  return {
    error_code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred',
  };
}
