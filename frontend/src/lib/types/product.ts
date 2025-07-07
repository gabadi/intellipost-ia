export interface ProductImageData {
  id: string;
  file: File;
  original_s3_url?: string;
  file_size_bytes: number;
  file_format: 'jpg' | 'jpeg' | 'png' | 'webp';
  resolution_width: number;
  resolution_height: number;
  is_primary: boolean;
  processing_metadata?: ImageProcessingMetadata;
}

export interface ImageProcessingMetadata {
  compressed_size_bytes?: number;
  original_orientation?: number;
  corrected_orientation?: number;
  processing_time_ms?: number;
}

export interface ProductInputs {
  id: string;
  prompt_text: string;
  images: ProductImageData[];
  created_at: string;
  status: 'uploading' | 'processing' | 'ready' | 'publishing' | 'published' | 'failed';
}

export interface ImageValidationRules {
  maxImages: number;
  maxFileSize: number; // 10MB
  maxTotalSize: number; // 50MB
  minResolution: { width: number; height: number };
  allowedFormats: string[];
}

export interface ProductCreationState {
  prompt_text: string;
  images: ProductImageData[];
  isUploading: boolean;
  uploadProgress: Record<string, number>;
  validation: {
    prompt: ValidationState;
    images: ValidationState;
    form: ValidationState;
  };
  errors: string[];
  autoSaved: boolean;
}

export interface ValidationState {
  isValid: boolean;
  message?: string;
  type: 'success' | 'warning' | 'error';
}

export interface UploadProgressEvent {
  type: 'upload_progress';
  data: {
    product_id: string;
    uploaded_images: number;
    total_images: number;
    current_file: string;
    progress_percent: number;
  };
}

export interface CameraCapture {
  stream: MediaStream | null;
  isActive: boolean;
  permissionStatus: 'granted' | 'denied' | 'prompt' | 'unknown';
  error: string | null;
}

export interface ImageCompression {
  quality: number;
  maxWidth: number;
  maxHeight: number;
  outputFormat: 'jpeg' | 'png' | 'webp';
}

export const DEFAULT_IMAGE_VALIDATION_RULES: ImageValidationRules = {
  maxImages: 8,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxTotalSize: 50 * 1024 * 1024, // 50MB
  minResolution: { width: 800, height: 600 },
  allowedFormats: ['jpg', 'jpeg', 'png'],
};

export const DEFAULT_IMAGE_COMPRESSION: ImageCompression = {
  quality: 0.8,
  maxWidth: 1920,
  maxHeight: 1080,
  outputFormat: 'jpeg',
};
