// Base API client for backend communication
import type { APIResponse, HealthCheckResponse } from '$types';
import { config } from '$lib/config';
import { browser } from '$app/environment';

// Generic API client with error handling
class APIClient {
  private baseUrl?: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl;
  }

  private getBaseURL(): string {
    // Use custom base URL if provided, otherwise use config-based URL
    if (this.baseUrl) {
      return this.baseUrl;
    }
    // Use internal URL for server-side rendering, external URL for client-side
    return browser ? config.api.BASE_URL : config.api.INTERNAL_URL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<APIResponse<T>> {
    try {
      const url = `${this.getBaseURL()}${endpoint}`;

      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

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
      const baseURL = this.getBaseURL();
      const response = await fetch(`${baseURL}/health`);
      if (!response.ok) {
        throw new Error(
          `Backend service is unavailable (${response.status}). Please check that the backend server is running on ${baseURL}`
        );
      }
      return response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const baseURL = this.getBaseURL();
        throw new Error(
          `Cannot connect to backend server at ${baseURL}. Please ensure the backend is running and accessible.`
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
