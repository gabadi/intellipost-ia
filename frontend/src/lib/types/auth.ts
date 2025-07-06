/**
 * Authentication type definitions for IntelliPost AI frontend.
 * 
 * Defines TypeScript interfaces for authentication state, user data,
 * and API request/response structures.
 */

export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  is_email_verified: boolean;
  status: string;
  created_at: string;
  last_login_at: string | null;
}

export interface UserDetail extends User {
  ml_user_id: string | null;
  is_ml_connected: boolean;
  default_ml_site: string;
  auto_publish: boolean;
  ai_confidence_threshold: string;
  updated_at: string;
  email_verified_at: string | null;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
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

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface AuthError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface UserProfileUpdateRequest {
  first_name?: string;
  last_name?: string;
  auto_publish?: boolean;
  ai_confidence_threshold?: string;
  default_ml_site?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}