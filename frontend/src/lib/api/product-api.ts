import type { ProductImageData } from '../types/product';

interface CreateProductResponse {
  id: string;
  user_id: string;
  status: string;
  prompt_text: string;
  images_uploaded: number;
  created_at: string;
  message: string;
}

interface ProductListResponse {
  products: Array<{
    id: string;
    user_id: string;
    status: string;
    confidence?: string;
    title?: string;
    description?: string;
    price?: number;
    category_id?: string;
    ai_title?: string;
    ai_description?: string;
    ai_tags?: string[];
    ml_listing_id?: string;
    ml_category_id?: string;
    created_at: string;
    updated_at: string;
    published_at?: string;
    images: Array<{
      id: string;
      product_id: string;
      original_filename: string;
      s3_url: string;
      file_size_bytes: number;
      file_format: string;
      resolution_width: number;
      resolution_height: number;
      is_primary: boolean;
      processing_metadata?: Record<string, unknown>;
      created_at: string;
      updated_at: string;
    }>;
  }>;
  total: number;
  page: number;
  page_size: number;
}

interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}

// Get API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  // In a real app, you'd get this from your auth state management
  // For now, we'll look for it in localStorage
  return localStorage.getItem('access_token');
}

/**
 * Create authenticated fetch headers
 */
function createAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Handle API response errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiError;

    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error_code: 'NETWORK_ERROR',
        message: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    throw new Error(errorData.message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

/**
 * Create a new product with images
 */
export async function createProduct(
  promptText: string,
  images: ProductImageData[]
): Promise<CreateProductResponse> {
  if (!promptText.trim()) {
    throw new Error('Product description cannot be empty');
  }

  if (images.length === 0) {
    throw new Error('At least one image is required');
  }

  if (images.length > 8) {
    throw new Error('Maximum 8 images allowed');
  }

  // Create FormData for multipart upload
  const formData = new FormData();
  formData.append('prompt_text', promptText.trim());

  // Add image files
  images.forEach(imageData => {
    if (imageData.file) {
      formData.append('images', imageData.file);
    }
  });

  const response = await fetch(`${API_BASE_URL}/products/`, {
    method: 'POST',
    headers: createAuthHeaders(),
    body: formData,
  });

  return handleResponse<CreateProductResponse>(response);
}

/**
 * Get all products for the current user
 */
export async function getProducts(): Promise<ProductListResponse> {
  const response = await fetch(`${API_BASE_URL}/products/`, {
    method: 'GET',
    headers: {
      ...createAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  return handleResponse<ProductListResponse>(response);
}

/**
 * Get a specific product by ID
 */
export async function getProduct(productId: string): Promise<ProductListResponse['products'][0]> {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
    method: 'GET',
    headers: {
      ...createAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  return handleResponse<ProductListResponse['products'][0]>(response);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

/**
 * Simulate upload progress for UI feedback
 * In a real implementation, you might use XMLHttpRequest or a library that supports progress events
 */
export function simulateUploadProgress(
  onProgress: (progress: number) => void,
  duration: number = 2000
): Promise<void> {
  return new Promise(resolve => {
    let progress = 0;
    const increment = 100 / (duration / 50); // Update every 50ms

    const interval = setInterval(() => {
      progress += increment;

      if (progress >= 100) {
        progress = 100;
        onProgress(progress);
        clearInterval(interval);
        resolve();
      } else {
        onProgress(progress);
      }
    }, 50);
  });
}
