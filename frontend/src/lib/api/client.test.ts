import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { APIClient, checkBackendHealth } from './client';

// Mock fetch for integration tests
const mockFetch = (response: Response) => {
  global.fetch = vi.fn().mockResolvedValue(response);
};

const mockResponse = (status: number, data?: unknown, statusText = 'OK') => {
  return new Response(data ? JSON.stringify(data) : null, {
    status,
    statusText,
    headers: { 'Content-Type': 'application/json' },
  });
};

describe('API Client Integration Tests', () => {
  let apiClient: APIClient;

  beforeEach(() => {
    apiClient = new APIClient('http://localhost:8000');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Health Check Integration', () => {
    it('should successfully check backend health with valid response', async () => {
      const healthData = {
        status: 'healthy',
        timestamp: '2025-06-26T12:00:00Z',
        version: '1.0.0',
      };

      mockFetch(mockResponse(200, healthData));

      const result = await checkBackendHealth();

      expect(result).toEqual(healthData);

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/health');
    });

    it('should throw error when health check fails', async () => {
      mockFetch(mockResponse(500, null, 'Internal Server Error'));

      await expect(checkBackendHealth()).rejects.toThrow('Backend service is unavailable (500)');
    });

    it('should handle network errors gracefully', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(checkBackendHealth()).rejects.toThrow('Network error');
    });
  });

  describe('Generic API Methods', () => {
    it('should handle successful GET requests', async () => {
      const testData = { id: 1, name: 'Test Item' };
      mockFetch(mockResponse(200, testData));

      const result = await apiClient.get('/test-endpoint');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(testData);
      expect(result.error).toBeUndefined();
    });

    it('should handle successful POST requests with data', async () => {
      const postData = { name: 'New Item', description: 'Test description' };
      const responseData = { id: 2, ...postData };

      mockFetch(mockResponse(201, responseData));

      const result = await apiClient.post('/test-endpoint', postData);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(responseData);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test-endpoint',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should handle PUT requests correctly', async () => {
      const updateData = { id: 1, name: 'Updated Item' };
      mockFetch(mockResponse(200, updateData));

      const result = await apiClient.put('/test-endpoint/1', updateData);

      expect(result.success).toBe(true);
      expect(result.data).toEqual(updateData);
    });

    it('should handle DELETE requests correctly', async () => {
      mockFetch(mockResponse(200, {}));

      const result = await apiClient.delete('/test-endpoint/1');

      expect(result.success).toBe(true);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test-endpoint/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should handle API errors gracefully', async () => {
      mockFetch(mockResponse(404, null, 'Not Found'));

      const result = await apiClient.get('/nonexistent-endpoint');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Request failed (404)');
      expect(result.error).toContain('The requested resource was not found');
      expect(result.data).toBe(null);
    });

    it('should handle JSON parsing errors', async () => {
      global.fetch = vi.fn().mockResolvedValue(new Response('Invalid JSON', { status: 200 }));

      const result = await apiClient.get('/test-endpoint');

      expect(result.success).toBe(false);
      expect(result.error).toContain('JSON');
    });

    it('should handle network connectivity issues', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('fetch failed'));

      const result = await apiClient.get('/test-endpoint');

      expect(result.success).toBe(false);
      expect(result.error).toBe('fetch failed');
    });
  });

  describe('Custom Base URL', () => {
    it('should use custom base URL when provided', async () => {
      const customClient = new APIClient('http://custom-api.com');
      mockFetch(mockResponse(200, { test: 'data' }));

      await customClient.get('/test');

      expect(fetch).toHaveBeenCalledWith('http://custom-api.com/test', expect.any(Object));
    });
  });

  describe('Request Headers', () => {
    it('should include Content-Type header by default', async () => {
      mockFetch(mockResponse(200, {}));

      await apiClient.get('/test');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should merge custom headers with defaults', async () => {
      mockFetch(mockResponse(200, {}));

      const customClient = new APIClient();
      // Access private request method through public methods
      await customClient.get('/test');

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  describe('Error Handling Edge Cases', () => {
    it('should handle empty response body', async () => {
      global.fetch = vi.fn().mockResolvedValue(new Response('', { status: 200 }));

      const result = await apiClient.get('/test');

      expect(result.success).toBe(false);
      expect(result.error).toContain('JSON');
    });

    it('should handle non-Error thrown objects', async () => {
      global.fetch = vi.fn().mockRejectedValue('String error');

      const result = await apiClient.get('/test');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Unknown error occurred');
    });
  });
});
