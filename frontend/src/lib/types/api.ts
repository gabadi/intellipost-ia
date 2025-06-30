// API response interfaces for backend communication
export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
}

export interface APIResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

export interface Product {
  id: string;
  user_id: string;
  status: ProductStatus;
  confidence?: number;
  created_at: string;
  updated_at: string;
}

export type ProductStatus =
  | 'uploading'
  | 'processing'
  | 'ready'
  | 'publishing'
  | 'published'
  | 'failed';

// Authentication interfaces
export interface User {
  user_id: string;
  email: string;
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SessionResponse {
  user_id: string;
  email: string;
  created_at: string;
}

export interface ErrorResponse {
  detail: string;
}
