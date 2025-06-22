# IntelliPost AI - API Specification

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Framework:** FastAPI + OpenAPI 3.0
- **Focus:** Mobile-first API design

---

## API Architecture Overview

### Design Principles
```yaml
Mobile-First Design:
  - Minimal payloads for mobile bandwidth
  - Efficient caching strategies
  - Real-time updates via WebSocket
  - Optimistic UI support

RESTful + Real-time Hybrid:
  - REST for CRUD operations
  - WebSocket for status updates
  - Event-driven state management

Performance Targets:
  - API Response: <200ms for standard endpoints
  - Upload Endpoints: <5 seconds for multiple images
  - AI Processing: 10-15 seconds with real-time updates
```

### Base URL Structure
```
Development: http://localhost:8000/api/v1
Production:  https://api.intellipost.ai/v1
```

---

## Core API Endpoints

### 1. Product Management

#### Create Product
```http
POST /products
Content-Type: multipart/form-data

# Request Body
{
  "prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB",
  "images[]": [File, File, File]  # Multiple image upload
}

# Response (201 Created)
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploading",
  "prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB",
  "image_count": 3,
  "created_at": "2025-06-22T10:30:00Z",
  "estimated_processing_time_seconds": 15
}
```

#### Get Product Status
```http
GET /products/{product_id}

# Response (200 OK)
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB",
  "images": [
    {
      "id": "img_1",
      "original_url": "https://s3.../original.jpg",
      "processed_url": "https://s3.../processed.jpg",
      "is_primary": true
    }
  ],
  "generated_content": {
    "title": "iPhone 13 Pro 128GB Usado Excelente Estado",
    "description": "iPhone 13 Pro de 128GB en excelente estado...",
    "ml_category_id": "MLA1055",
    "ml_category_name": "Celulares y Smartphones",
    "ml_price": 850000.00,
    "ml_currency_id": "ARS",
    "confidence_overall": 0.89,
    "confidence_breakdown": {
      "title": 0.92,
      "description": 0.88,
      "category": 0.95,
      "price": 0.75
    }
  },
  "created_at": "2025-06-22T10:30:00Z",
  "updated_at": "2025-06-22T10:30:15Z"
}
```

#### List User Products
```http
GET /products?status=ready&limit=20&offset=0

# Response (200 OK)
{
  "products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "ready",
      "prompt_text": "iPhone 13 Pro usado...",
      "primary_image_url": "https://s3.../processed.jpg",
      "title": "iPhone 13 Pro 128GB Usado",
      "confidence_overall": 0.89,
      "created_at": "2025-06-22T10:30:00Z"
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

#### Trigger AI Processing
```http
POST /products/{product_id}/generate

# Request Body
{
  "regenerate": false,  # true if regenerating existing content
  "category_hint": "MLA1055"  # optional category suggestion
}

# Response (202 Accepted)
{
  "status": "processing",
  "estimated_completion_seconds": 15,
  "websocket_url": "/ws/products/{product_id}/status"
}
```

#### Update Generated Content
```http
PUT /products/{product_id}/content

# Request Body
{
  "title": "iPhone 13 Pro 128GB Usado - Excelente Estado",
  "description": "iPhone 13 Pro de 128GB...",
  "ml_price": 900000.00,
  "ml_attributes": {
    "BRAND": "Apple",
    "MODEL": "iPhone 13 Pro",
    "STORAGE_CAPACITY": "128 GB"
  },
  "regenerate_if_prompt_changed": true
}

# Response (200 OK)
{
  "updated": true,
  "regeneration_triggered": false,
  "content": {
    "title": "iPhone 13 Pro 128GB Usado - Excelente Estado",
    "ml_price": 900000.00,
    "confidence_overall": 0.91
  }
}
```

### 2. Publishing to MercadoLibre

#### Publish Product
```http
POST /products/{product_id}/publish

# Request Body
{
  "ml_listing_type_id": "gold_special",  # optional override
  "ml_available_quantity": 1
}

# Response (202 Accepted)
{
  "status": "publishing",
  "estimated_completion_seconds": 10,
  "websocket_url": "/ws/products/{product_id}/status"
}
```

#### Get Publishing Status
```http
GET /products/{product_id}/publishing-status

# Response (200 OK)
{
  "status": "published",
  "ml_item_id": "MLA123456789",
  "ml_permalink": "https://articulo.mercadolibre.com.ar/MLA-123456789",
  "published_at": "2025-06-22T10:35:00Z",
  "ml_status": "active",
  "ml_health": 0.95
}
```

### 3. MercadoLibre Integration

#### Get/Update ML Credentials
```http
GET /ml-credentials

# Response (200 OK)
{
  "has_credentials": true,
  "ml_nickname": "usuario123",
  "ml_email": "usuario@email.com",
  "is_valid": true,
  "expires_at": "2025-12-22T10:00:00Z",
  "scopes": ["read", "write", "offline_access"]
}

PUT /ml-credentials
# Request Body
{
  "ml_app_id": "1234567890123456",
  "ml_secret_key": "secret123",
  "authorization_code": "TG-abc123..."  # From ML OAuth flow
}

# Response (200 OK)
{
  "updated": true,
  "ml_user_id": 123456789,
  "ml_nickname": "usuario123",
  "expires_at": "2025-12-22T10:00:00Z"
}
```

#### Validate ML Credentials
```http
POST /ml-credentials/validate

# Response (200 OK)
{
  "is_valid": true,
  "ml_user_id": 123456789,
  "available_sites": ["MLA"],
  "permissions": ["read", "write"]
}
```

#### Get ML Categories
```http
GET /ml-categories?parent_id=MLA1144&search=celular

# Response (200 OK)
{
  "categories": [
    {
      "id": "MLA1055",
      "name": "Celulares y Smartphones",
      "parent_id": "MLA1144",
      "listing_allowed": true,
      "max_title_length": 60
    }
  ],
  "total": 1
}
```

#### Get Category Attributes
```http
GET /ml-categories/{category_id}/attributes

# Response (200 OK)
{
  "attributes": [
    {
      "id": "BRAND",
      "name": "Marca",
      "value_type": "list",
      "is_required": true,
      "allowed_values": [
        {"id": "7815", "name": "Apple"},
        {"id": "2230284", "name": "Samsung"}
      ]
    }
  ]
}
```

---

## Real-time WebSocket API

### Product Status Updates
```javascript
// WebSocket Connection
const ws = new WebSocket('/ws/products/{product_id}/status');

// Message Types Received
{
  "type": "status_change",
  "data": {
    "product_id": "550e8400-...",
    "status": "processing",
    "progress": 45,
    "message": "Analyzing images..."
  }
}

{
  "type": "processing_complete",
  "data": {
    "product_id": "550e8400-...",
    "status": "ready",
    "generated_content": {
      "title": "iPhone 13 Pro 128GB",
      "confidence_overall": 0.89
    }
  }
}

{
  "type": "publishing_complete",
  "data": {
    "product_id": "550e8400-...",
    "status": "published",
    "ml_item_id": "MLA123456789",
    "ml_permalink": "https://..."
  }
}

{
  "type": "error",
  "data": {
    "product_id": "550e8400-...",
    "error_type": "ai_processing_failed",
    "error_message": "AI service temporarily unavailable",
    "retry_available": true
  }
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "INVALID_PROMPT",
    "message": "Prompt text is required and must be at least 10 characters",
    "details": {
      "field": "prompt_text",
      "min_length": 10,
      "received_length": 5
    },
    "request_id": "req_123456789"
  }
}
```

### Error Codes
```yaml
Client Errors (4xx):
  INVALID_PROMPT: Prompt validation failed
  INVALID_IMAGE: Image format/size validation failed
  PRODUCT_NOT_FOUND: Product ID not found
  INSUFFICIENT_CONFIDENCE: AI confidence too low for auto-publish
  ML_CREDENTIALS_INVALID: MercadoLibre credentials expired/invalid
  
Server Errors (5xx):
  AI_SERVICE_UNAVAILABLE: AI provider temporarily down
  ML_API_ERROR: MercadoLibre API error
  PROCESSING_TIMEOUT: AI processing exceeded time limit
  STORAGE_ERROR: Image upload/processing failed
```

---

## Mobile Optimization Features

### Compression and Bandwidth
```yaml
Image Upload Optimization:
  - Client-side compression before upload
  - Progressive upload with resume capability
  - WebP format for mobile delivery
  - Thumbnail generation for lists

Response Optimization:
  - Minimal JSON payloads
  - Conditional requests (ETags)
  - Gzip compression
  - CDN integration for images
```

### Caching Strategy
```yaml
API Response Caching:
  - Product lists: 30 seconds
  - ML categories: 24 hours
  - User credentials status: 5 minutes
  
Mobile Client Caching:
  - Aggressive image caching
  - Offline-first for generated content
  - Service Worker for API responses
```

### Offline Support
```yaml
Offline Capabilities:
  - Cache generated content locally
  - Queue publish actions when offline
  - Sync when connection restored
  - Progressive enhancement approach
```

---

## API Authentication

### JWT Token Authentication
```yaml
Authentication Flow:
  1. ML OAuth → Get ML credentials
  2. JWT issued for app authentication
  3. Bearer token in Authorization header
  
Token Structure:
  - Access Token: 6 hours validity
  - Refresh Token: 30 days validity
  - Automatic refresh before expiration
```

### Request Headers
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
X-Request-ID: req_123456789  # For tracing
X-Client-Version: mobile-1.0.0  # For compatibility
```

---

## Rate Limiting (Simple)

### MVP Rate Limiting Strategy
```yaml
Approach: Simple and Pragmatic
  - No complex rate limiting tracking
  - Let MercadoLibre API handle its own limits
  - Exponential backoff on 429 responses
  - Circuit breaker for AI services

Implementation:
  - Retry logic in service layer
  - User feedback on temporary failures
  - No rate limit storage in database
```

---

## API Versioning

### Versioning Strategy
```yaml
URL Versioning: /api/v1/
  - Semantic versioning
  - Backward compatibility within major version
  - Deprecation notices for breaking changes

Mobile Client Support:
  - Version detection via headers
  - Graceful degradation for older clients
  - Feature flags for gradual rollouts
```

---

## Performance Monitoring

### API Metrics
```yaml
Key Metrics to Track:
  - Response time per endpoint
  - Error rate by error type
  - AI processing success rate
  - ML publishing success rate
  - Image upload performance

Monitoring Tools:
  - FastAPI built-in metrics
  - Custom middleware for timing
  - Error tracking and alerting
  - Performance dashboard
```

---

**Esta especificación API cubre el flujo completo mobile-first MVP. ¿Continuamos con Frontend Architecture o quieres revisar algún endpoint específico?**