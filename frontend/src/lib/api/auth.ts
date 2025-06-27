/**
 * Authentication API client for the IntelliPost AI frontend.
 *
 * Provides functions to interact with the authentication endpoints.
 */

import type {
  AuthenticationResponse,
  LoginRequest,
  RegisterRequest,
  TokenRefreshRequest,
  LogoutRequest,
  AccessTokenResponse,
  MessageResponse,
  User,
} from '../types/auth';

const API_BASE_URL = 'http://localhost:8080'; // Updated to match backend port

class AuthAPI {
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Set the authentication token for subsequent requests
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  /**
   * Make HTTP request with proper error handling
   */
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        let errorMessage = `Request failed (${response.status})`;

        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Use default error message if JSON parsing fails
        }

        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(
          `Cannot connect to authentication service at ${this.baseURL}. Please ensure the backend is running.`
        );
      }
      throw error;
    }
  }

  /**
   * Register a new user account
   */
  async register(data: RegisterRequest): Promise<AuthenticationResponse> {
    return this.request<AuthenticationResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<AuthenticationResponse> {
    return this.request<AuthenticationResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(data: TokenRefreshRequest): Promise<AccessTokenResponse> {
    return this.request<AccessTokenResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Logout user by validating refresh token
   */
  async logout(data: LogoutRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>('/auth/logout', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'GET',
    });
  }
}

// Create and export auth API instance
const authAPI = new AuthAPI();
export { authAPI };
