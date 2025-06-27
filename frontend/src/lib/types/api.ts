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
