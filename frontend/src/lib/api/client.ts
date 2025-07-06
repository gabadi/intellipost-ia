// Base API client for backend communication with JWT authentication
import type { APIResponse, HealthCheckResponse } from '$types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Storage keys for tokens
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'intellipost_access_token',
  REFRESH_TOKEN: 'intellipost_refresh_token'
};

// Generic API client with error handling and JWT authentication
class APIClient {
  private baseURL: string;
  private isRefreshing = false;
  private refreshPromise: Promise<boolean> | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getAccessToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    } catch {
      return null;
    }
  }

  private getRefreshToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch {
      return null;
    }
  }

  private async refreshAccessToken(): Promise<boolean> {
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performTokenRefresh();

    try {
      const result = await this.refreshPromise;
      return result;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();

      // Store new tokens
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);

      return true;
    } catch {
      return false;
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<APIResponse<T>> {
    const attemptRequest = async (includeAuth = true): Promise<Response> => {
      const url = `${this.baseURL}${endpoint}`;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      };

      // Add Authorization header if token exists and not auth endpoints
      if (includeAuth && !endpoint.startsWith('/auth/')) {
        const accessToken = this.getAccessToken();
        if (accessToken) {
          headers.Authorization = `Bearer ${accessToken}`;
        }
      }

      return fetch(url, {
        ...options,
        headers,
      });
    };

    try {
      let response = await attemptRequest();

      // If unauthorized and not on auth endpoints, try to refresh token
      if (response.status === 401 && !endpoint.startsWith('/auth/')) {
        const refreshSuccessful = await this.refreshAccessToken();
        if (refreshSuccessful) {
          // Retry request with new token
          response = await attemptRequest();
        }
      }

      if (!response.ok) {
        // Create actionable error messages based on status codes
        const errorMessage = `Request failed (${response.status})`;
        let actionableMessage = '';

        switch (response.status) {
          case 400:
            actionableMessage = 'Please check your input and try again';
            break;
          case 401:
            actionableMessage = 'Please log in to continue';
            break;
          case 403:
            actionableMessage = "You don't have permission to perform this action";
            break;
          case 404:
            actionableMessage = 'The requested resource was not found';
            break;
          case 409:
            actionableMessage =
              'This action conflicts with current data. Please refresh and try again';
            break;
          case 422:
            actionableMessage = 'Please check your input format and try again';
            break;
          case 429:
            actionableMessage = 'Too many requests. Please wait a moment and try again';
            break;
          case 500:
            actionableMessage = 'Server error. Please try again later or contact support';
            break;
          case 502:
          case 503:
          case 504:
            actionableMessage =
              'Service temporarily unavailable. Please try again in a few minutes';
            break;
          default:
            actionableMessage = 'Please try again or contact support if the problem persists';
        }

        throw new Error(`${errorMessage}: ${actionableMessage}`);
      }

      const data = await response.json();

      return {
        data,
        success: true,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';

      return {
        data: null as unknown as T,
        error: errorMessage,
        success: false,
      };
    }
  }

  // Health check endpoint
  async checkHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      if (!response.ok) {
        throw new Error(
          `Backend service is unavailable (${response.status}). Please check that the backend server is running on ${this.baseURL}`
        );
      }
      return response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(
          `Cannot connect to backend server at ${this.baseURL}. Please ensure the backend is running and accessible.`
        );
      }
      throw error;
    }
  }

  // GET request
  async get<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data?: unknown): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: unknown): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Singleton instance
export const apiClient = new APIClient();

// Named exports for convenience
export const checkBackendHealth = () => apiClient.checkHealth();

// Export the class for custom instances if needed
export { APIClient };
