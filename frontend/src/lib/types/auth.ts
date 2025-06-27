/**
 * Authentication types for the IntelliPost AI frontend.
 *
 * These types match the backend API schemas for authentication operations.
 */

export interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  status: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  email_verified_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number; // seconds
}

export interface AuthenticationResponse {
  user: User;
  tokens: TokenResponse;
  message: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
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

export interface TokenRefreshRequest {
  refresh_token: string;
}

export interface LogoutRequest {
  refresh_token: string;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}

export interface AuthFormProps {
  onSuccess?: (user: User) => void;
  onError?: (error: string) => void;
  redirectTo?: string;
}

export interface PasswordValidation {
  minLength: boolean;
  hasUpperCase: boolean;
  hasLowerCase: boolean;
  hasNumber: boolean;
  isValid: boolean;
}

export type AuthMode = 'login' | 'register';

export interface AuthenticatedUser {
  user_id: string;
  email: string;
  is_active: boolean;
  exp: number;
}
