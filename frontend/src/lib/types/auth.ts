/**
 * Authentication types for the frontend application.
 *
 * This module defines TypeScript interfaces for authentication-related data structures.
 */

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthError {
  message: string;
  code?: string;
  details?: unknown;
}

// API response types
export interface ApiError {
  detail: string;
  code?: string;
}

export interface AuthResponse {
  success: boolean;
  data?: TokenResponse;
  error?: ApiError;
}

// Token storage keys
export const TOKEN_STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  USER_DATA: 'auth_user_data',
} as const;

// Authentication event types
export type AuthEvent =
  | 'login_success'
  | 'login_error'
  | 'logout'
  | 'token_refresh'
  | 'token_expired'
  | 'session_expired';
