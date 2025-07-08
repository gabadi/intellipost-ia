# Story 2.2: Secure Storage of Raw Product Inputs

## Status: Draft

## Story

**As a** user of the IntelliPost AI platform,
**I want** my uploaded images and product data to be securely stored and properly managed,
**so that** I can trust that my product information is safe, accessible, and ready for AI processing.

## Acceptance Criteria

1. **Images stored in secure object storage**
   - All uploaded images must be stored in S3-compatible object storage (MinIO for development)
   - Images must be accessible via secure URLs with appropriate access controls
   - Storage must support efficient retrieval for AI processing workflows

2. **Product metadata persisted in PostgreSQL**
   - Product core data (prompt_text, status, user_id) stored in relational database
   - Proper foreign key relationships maintained between users and products
   - Product status managed through defined state machine (uploading → processing → ready → publishing → published/failed)

3. **Secure URLs generated for image access**
   - Pre-signed URLs generated for temporary image access
   - URLs must expire within reasonable timeframe for security
   - Access URLs must be scoped to authenticated user ownership

4. **Correct relationships between product and images**
   - One product can have multiple images (1:N relationship)
   - Each image must be linked to exactly one product
   - Primary image designation must be tracked
   - Referential integrity maintained through foreign key constraints

5. **Automatic temporary file cleanup**
   - Temporary upload files must be cleaned up after successful storage
   - Failed uploads must have cleanup mechanisms
   - Orphaned files must be identified and removed

6. **Backup strategy defined**
   - Data backup procedures must be documented
   - Recovery procedures must be tested and validated
   - Backup retention policies must be established

## Tasks / Subtasks

- [ ] **Task 1: Implement S3-Compatible Image Storage Service** (AC: 1, 3)
  - [ ] Create S3StorageService implementing object storage operations
  - [ ] Implement secure URL generation with configurable expiration
  - [ ] Add image upload functionality with proper error handling
  - [ ] Configure MinIO for development environment
  - [ ] Add S3 configuration for production environment

- [ ] **Task 2: Create Product and ProductImage Database Models** (AC: 2, 4)
  - [ ] Implement Product SQLAlchemy model with status enum
  - [ ] Implement ProductImage SQLAlchemy model with foreign key relationship
  - [ ] Create database migration for products and product_images tables
  - [ ] Add proper indexes for performance optimization
  - [ ] Implement state machine validation for product status transitions

- [ ] **Task 3: Develop Product Repository Implementation** (AC: 2, 4)
  - [ ] Create ProductRepository implementing ProductRepositoryProtocol
  - [ ] Implement CRUD operations for products and images
  - [ ] Add relationship management between products and images
  - [ ] Implement primary image designation logic
  - [ ] Add proper transaction handling for data consistency

- [ ] **Task 4: Create File Storage Service** (AC: 1, 3, 5)
  - [ ] Implement FileStorageService for file management operations
  - [ ] Add temporary file cleanup mechanisms
  - [ ] Implement orphaned file detection and cleanup
  - [ ] Add file validation and security checks
  - [ ] Create monitoring for storage operations

- [ ] **Task 5: Implement API Endpoints for Product Storage** (AC: 1-6)
  - [ ] Create POST /products endpoint for product creation
  - [ ] Implement image upload handling with validation
  - [ ] Add proper error handling and status codes
  - [ ] Implement authentication and authorization checks
  - [ ] Add comprehensive logging for debugging

- [ ] **Task 6: Create Comprehensive Test Coverage** (AC: All)
  - [ ] Unit tests for all repository operations
  - [ ] Integration tests with test containers (PostgreSQL, MinIO)
  - [ ] API endpoint tests with mock and real storage
  - [ ] Error handling and edge case testing
  - [ ] Performance tests for large file uploads

## Dev Notes

### Previous Story Context
From Epic 2 Story 1, the frontend upload interface is complete and provides:
- Mobile-optimized photo capture and upload functionality
- Form validation for images (JPG/PNG, max 8 images, size limits)
- Product creation API integration with POST /products endpoint
- Auto-save functionality for user data retention
- WebSocket integration for upload progress tracking

**Key Integration Points**: This story must implement the backend storage that the frontend is expecting to interact with via the `/products` API endpoint.

### Data Models and Database Schema

**Products Table** [Source: architecture/database-schema.md#products-table]:
```sql
CREATE TYPE product_status AS ENUM (
    'uploading',     -- Images being uploaded
    'processing',    -- AI content generation in progress
    'ready',         -- Generated content ready for review
    'publishing',    -- Being published to MercadoLibre
    'published',     -- Successfully published
    'failed'         -- Processing or publishing failed
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status product_status NOT NULL DEFAULT 'uploading',
    prompt_text TEXT NOT NULL CHECK (char_length(prompt_text) <= 500),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Product Images Table** [Source: architecture/database-schema.md#product-images-table]:
```sql
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    original_s3_url TEXT NOT NULL,
    processed_s3_url TEXT,
    is_primary BOOLEAN DEFAULT false,
    file_size_bytes INTEGER NOT NULL CHECK (file_size_bytes > 0),
    file_format VARCHAR(10) NOT NULL CHECK (file_format IN ('jpg', 'jpeg', 'png', 'webp')),
    resolution_width INTEGER CHECK (resolution_width > 0),
    resolution_height INTEGER CHECK (resolution_height > 0),
    processing_metadata JSONB DEFAULT '{}',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);
```

### API Specifications

**Product Creation Endpoint** [Source: architecture/api-specification.md#products-api]:
```http
POST /api/products
Content-Type: multipart/form-data
Authorization: Bearer {access_token}

Body:
- prompt_text: string (required, 10-500 characters)
- images[]: File[] (required, 1-8 files, JPG/PNG only)

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploading",
  "prompt_text": "iPhone 13 Pro usado, excelente estado, 128GB",
  "image_count": 3,
  "created_at": "2025-07-07T10:30:00Z",
  "estimated_processing_time_seconds": 15
}
```

### File Storage Configuration

**S3-Compatible Storage** [Source: architecture/tech-stack.md#database-storage]:
```yaml
Object Storage: S3-Compatible (MinIO for development)
  Purpose: Image storage (original and processed)
  Features: CDN integration, signed URLs, lifecycle policies
  Performance: Scalable, cost-effective, mobile-optimized delivery
```

**Development Configuration**: MinIO running in Docker container with credentials configured via environment variables
**Production Configuration**: AWS S3 or compatible cloud storage with proper IAM roles and bucket policies

### Module File Locations

**Product Management Module Structure** [Source: architecture/source-tree.md#product-management]:
```
backend/modules/product_management/
├── domain/
│   ├── entities/product.py            # Product domain entity
│   ├── entities/product_status.py     # Status management
│   └── ports/product_repository_protocol.py
├── infrastructure/
│   ├── models/product_model.py        # SQLAlchemy models
│   ├── repositories/product_repository.py
│   └── services/file_storage_service.py
├── api/
│   ├── routers/product_router.py      # HTTP endpoints
│   └── schemas/product_schemas.py     # Request/Response DTOs
└── tests/                             # Module-specific tests
```

### Architecture Patterns

**Hexagonal Architecture Implementation** [Source: architecture/source-tree.md#hexagonal-architecture]:
- **Domain Layer**: Pure business logic with Protocol interfaces
- **Application Layer**: Use cases orchestrating domain services
- **Infrastructure Layer**: External service implementations (SQLAlchemy, S3)
- **API Layer**: HTTP endpoints and data transformation

**Protocol-Based Communication** [Source: architecture/source-tree.md#protocol-communication]:
- All external dependencies accessed via Protocol interfaces
- Static duck typing validated by Pyright at compile-time
- No cross-module imports - communication via dependency injection
- Zero runtime overhead for protocol compliance

### Security Requirements

**Data Security** [Source: architecture/tech-stack.md#data-security]:
```yaml
Encryption:
  - Database: Connection encryption (TLS)
  - File Storage: Encryption at rest and in transit
  - ML Credentials: AES-256 encryption at rest

API Security:
  - HTTPS only (TLS 1.3)
  - JWT-based authentication with refresh tokens
  - Rate limiting per user/IP
  - Input validation on all endpoints
```

### Testing

**Testing Standards** [Source: architecture/coding-standards.md#testing-requirements]:
- **Unit Tests**: Domain logic isolation using pytest
- **Integration Tests**: External service mocking with httpx-mock + respx
- **Repository Tests**: Test containers for PostgreSQL and MinIO
- **API Tests**: Full request/response testing with test client
- **Coverage Requirement**: Minimum 80% test coverage for all new code

**Test File Locations**: Tests co-located within module at `backend/modules/product_management/tests/`

**Test Database**: Separate test database with fixtures and cleanup between tests

### Error Handling

**Error Handling Strategy** [Source: architecture/coding-standards.md#error-handling]:
- Domain exceptions for business rule violations
- Infrastructure exceptions for external service failures
- Comprehensive logging for debugging and monitoring
- Graceful degradation for non-critical failures
- User-friendly error messages without exposing internal details

### Configuration Management

**Development Environment** [Source: architecture/tech-stack.md#development-environment]:
```yaml
Container Platform: Docker + Docker Compose
Services: PostgreSQL, MinIO, FastAPI, SvelteKit
Environment Variables:
  - DATABASE_URL: PostgreSQL connection string
  - S3_ENDPOINT_URL: MinIO endpoint for development
  - S3_ACCESS_KEY_ID: Storage access credentials
  - S3_SECRET_ACCESS_KEY: Storage secret credentials
  - S3_BUCKET_NAME: Default bucket for image storage
```

## Testing

**Test Coverage Requirements**:
- Minimum 80% coverage for all new modules and services
- Unit tests for domain entities and business logic
- Integration tests with TestContainers for PostgreSQL and MinIO
- API endpoint tests with authentication and authorization scenarios
- Error handling tests for all failure modes

**Test Data Management**:
- Test fixtures for sample product data and images
- Database cleanup between test cases
- Mock external services for unit tests
- Real storage services for integration tests

**Performance Testing**:
- Load testing for multiple concurrent uploads
- Large file upload testing (up to 50MB total)
- Database performance testing with large datasets

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-07-08 | 1.0 | Initial story creation for secure product input storage | Bob (Scrum Master) |

## Dev Agent Record

*This section will be populated by the development agent during implementation*

## QA Results

*This section will be populated by the QA agent during review*
