# IntelliPost AI - Database Schema & Data Architecture

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Phase:** Database Design
- **Database:** PostgreSQL 15+

---

## Entity Relationship Overview

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    Users    │──────▶│     Products     │──────▶│ Generated       │
│             │  1:N  │                  │  1:1  │ Content         │
│ • id        │       │ • id             │       │                 │
│ • email     │       │ • user_id        │       │ • product_id    │
│ • auth      │       │ • status         │       │ • title         │
└─────────────┘       │ • prompt_text    │       │ • description   │
                      │ • created_at     │       │ • category      │
                      └──────────────────┘       │ • confidence    │
                               │                  │ • ml_listing_id │
                               │ 1:N              └─────────────────┘
                               ▼
                      ┌──────────────────┐
                      │ Product Images   │
                      │                  │
                      │ • product_id     │
                      │ • s3_url         │
                      │ • is_primary     │
                      │ • processing_    │
                      │   metadata       │
                      └──────────────────┘

┌─────────────────────┐
│  ML Credentials     │──────▶ Users (1:1)
│                     │
│ • user_id           │
│ • app_id            │
│ • encrypted_tokens  │
│ • expires_at        │
└─────────────────────┘
```

---

## Core Entities

### 1. Users Table
**Purpose:** User authentication and account management

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
```

**Design Decisions:**
- **UUID Primary Keys:** For security and distributed system compatibility
- **Email Validation:** PostgreSQL regex constraint
- **Soft Delete Ready:** `is_active` flag for future user deactivation
- **Timezone Aware:** All timestamps with timezone for global users

### 2. Products Table
**Purpose:** Core product lifecycle management with state machine

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

    -- Processing metadata
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Business constraints
    CONSTRAINT products_prompt_not_empty CHECK (trim(prompt_text) != ''),
    CONSTRAINT products_processing_time CHECK (
        processing_started_at IS NULL OR
        processing_completed_at IS NULL OR
        processing_completed_at >= processing_started_at
    )
);

-- Performance indexes
CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_user_status ON products(user_id, status);

-- Composite index for dashboard queries
CREATE INDEX idx_products_dashboard ON products(user_id, status, created_at DESC);
```

**State Machine Constraints:**
```sql
-- Function to validate state transitions
CREATE OR REPLACE FUNCTION validate_product_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Valid transitions matrix
    IF OLD.status = 'uploading' AND NEW.status NOT IN ('processing', 'failed') THEN
        RAISE EXCEPTION 'Invalid transition from uploading to %', NEW.status;
    ELSIF OLD.status = 'processing' AND NEW.status NOT IN ('ready', 'failed') THEN
        RAISE EXCEPTION 'Invalid transition from processing to %', NEW.status;
    ELSIF OLD.status = 'ready' AND NEW.status NOT IN ('publishing', 'processing', 'failed') THEN
        RAISE EXCEPTION 'Invalid transition from ready to %', NEW.status;
    ELSIF OLD.status = 'publishing' AND NEW.status NOT IN ('published', 'failed') THEN
        RAISE EXCEPTION 'Invalid transition from publishing to %', NEW.status;
    ELSIF OLD.status = 'published' AND NEW.status != 'published' THEN
        RAISE EXCEPTION 'Cannot transition from published state';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_status_transition_trigger
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION validate_product_status_transition();
```

### 3. Product Images Table
**Purpose:** Multiple image management with processing metadata

```sql
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- Image storage
    original_s3_url TEXT NOT NULL,
    processed_s3_url TEXT, -- After background removal/optimization

    -- Image metadata
    is_primary BOOLEAN DEFAULT false,
    file_size_bytes INTEGER NOT NULL CHECK (file_size_bytes > 0),
    file_format VARCHAR(10) NOT NULL CHECK (file_format IN ('jpg', 'jpeg', 'png', 'webp')),
    resolution_width INTEGER CHECK (resolution_width > 0),
    resolution_height INTEGER CHECK (resolution_height > 0),

    -- Processing metadata (JSONB for flexibility)
    processing_metadata JSONB DEFAULT '{}',

    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Business constraints
    CONSTRAINT product_images_one_primary_per_product UNIQUE (product_id, is_primary)
        DEFERRABLE INITIALLY DEFERRED
);

-- Indexes for performance
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_images_primary ON product_images(product_id, is_primary)
    WHERE is_primary = true;
CREATE INDEX idx_product_images_processing ON product_images USING GIN (processing_metadata);
```

**Image Processing Metadata Structure:**
```json
{
    "photoroom": {
        "background_removed": true,
        "processing_time_ms": 350,
        "confidence_score": 0.95,
        "api_version": "2025.1"
    },
    "compression": {
        "original_size": 2048000,
        "compressed_size": 512000,
        "format_converted": "webp",
        "quality_score": 0.9
    }
}
```

### 4. Generated Content Table
**Purpose:** AI-generated listing content with complete MercadoLibre integration

```sql
CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- AI Generated content
    title VARCHAR(60) NOT NULL CHECK (char_length(trim(title)) >= 10),
    description TEXT NOT NULL CHECK (char_length(trim(description)) >= 50),

    -- MercadoLibre specific fields (COMPLETE)
    ml_category_id VARCHAR(50) NOT NULL,
    ml_category_name VARCHAR(200) NOT NULL,
    ml_title VARCHAR(60) NOT NULL, -- May differ from AI title after ML optimization
    ml_price DECIMAL(10,2) NOT NULL CHECK (ml_price > 0),
    ml_currency_id CHAR(3) DEFAULT 'ARS',
    ml_available_quantity INTEGER DEFAULT 1 CHECK (ml_available_quantity > 0),
    ml_buying_mode VARCHAR(20) DEFAULT 'buy_it_now',
    ml_condition VARCHAR(20) DEFAULT 'new',
    ml_listing_type_id VARCHAR(50) DEFAULT 'gold_special',

    -- MercadoLibre flexible attributes and terms
    ml_attributes JSONB DEFAULT '{}', -- Category-specific attributes (brand, model, etc.)
    ml_sale_terms JSONB DEFAULT '{}', -- Payment, shipping terms
    ml_shipping JSONB DEFAULT '{}', -- Shipping configuration

    -- Warranty and service
    ml_warranty VARCHAR(500),
    ml_warranty_type VARCHAR(50) CHECK (ml_warranty_type IN ('manufacturer', 'seller', 'without_warranty')),

    -- AI confidence scoring
    confidence_overall DECIMAL(3,2) NOT NULL CHECK (confidence_overall BETWEEN 0.00 AND 1.00),
    confidence_breakdown JSONB NOT NULL DEFAULT '{}',

    -- AI provider metadata
    ai_provider VARCHAR(50) NOT NULL DEFAULT 'gemini',
    ai_model_version VARCHAR(100) NOT NULL,
    generation_time_ms INTEGER CHECK (generation_time_ms > 0),

    -- Publishing data (after ML publication)
    ml_item_id VARCHAR(50), -- MercadoLibre item ID
    ml_permalink TEXT, -- Public URL to the listing
    ml_status VARCHAR(20), -- active, paused, closed, etc.
    ml_health DECIMAL(3,2) CHECK (ml_health BETWEEN 0.00 AND 1.00), -- Item health score
    ml_sold_quantity INTEGER DEFAULT 0 CHECK (ml_sold_quantity >= 0),

    -- Version control for regeneration
    version INTEGER NOT NULL DEFAULT 1,

    -- Timestamps
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ml_published_at TIMESTAMP WITH TIME ZONE,
    ml_last_updated_at TIMESTAMP WITH TIME ZONE,

    -- Business constraints
    CONSTRAINT ml_title_length_check CHECK (char_length(ml_title) <= 60 AND char_length(trim(ml_title)) >= 10),
    CONSTRAINT ml_currency_supported CHECK (ml_currency_id IN ('ARS', 'USD')),
    CONSTRAINT ml_buying_mode_valid CHECK (ml_buying_mode IN ('buy_it_now', 'auction')),
    CONSTRAINT ml_condition_valid CHECK (ml_condition IN ('new', 'used', 'not_specified')),
    CONSTRAINT ml_listing_type_valid CHECK (ml_listing_type_id IN ('gold_pro', 'gold_premium', 'gold_special', 'silver', 'bronze', 'free')),
    CONSTRAINT ml_status_valid CHECK (ml_status IS NULL OR ml_status IN ('active', 'paused', 'closed', 'under_review', 'inactive'))
);

-- Performance indexes
CREATE INDEX idx_generated_content_product_id ON generated_content(product_id);
CREATE INDEX idx_generated_content_confidence ON generated_content(confidence_overall DESC);
CREATE INDEX idx_generated_content_ml_item_id ON generated_content(ml_item_id) WHERE ml_item_id IS NOT NULL;
CREATE INDEX idx_generated_content_ml_status ON generated_content(ml_status) WHERE ml_status IS NOT NULL;
CREATE INDEX idx_generated_content_ml_category ON generated_content(ml_category_id);
CREATE INDEX idx_generated_content_attributes ON generated_content USING GIN (ml_attributes);
CREATE INDEX idx_generated_content_sale_terms ON generated_content USING GIN (ml_sale_terms);
CREATE INDEX idx_generated_content_confidence_breakdown ON generated_content USING GIN (confidence_breakdown);

-- Unique constraint: one content per product version
CREATE UNIQUE INDEX idx_generated_content_product_version ON generated_content(product_id, version);
```

**Confidence Breakdown Structure:**
```json
{
    "title": 0.92,
    "description": 0.88,
    "category": 0.95,
    "price": 0.75,
    "attributes": 0.90,
    "image_analysis": 0.93
}
```

### 5. ML Credentials Table
**Purpose:** Complete MercadoLibre OAuth 2.0 credential management

```sql
CREATE TABLE ml_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- OAuth application data
    ml_app_id VARCHAR(255) NOT NULL,
    ml_secret_key_encrypted TEXT NOT NULL, -- AES-256 encrypted

    -- OAuth tokens (6-hour access, 6-month refresh)
    ml_access_token_encrypted TEXT NOT NULL, -- AES-256 encrypted
    ml_refresh_token_encrypted TEXT NOT NULL, -- AES-256 encrypted
    ml_token_type VARCHAR(20) DEFAULT 'bearer',

    -- Token lifecycle
    ml_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ml_refresh_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ml_scopes TEXT DEFAULT 'offline_access read write',

    -- MercadoLibre user data
    ml_user_id BIGINT NOT NULL, -- MercadoLibre user ID
    ml_nickname VARCHAR(100), -- MercadoLibre nickname
    ml_email VARCHAR(255), -- MercadoLibre email
    ml_site_id CHAR(3) DEFAULT 'MLA', -- Argentina marketplace

    -- Validation and health
    ml_is_valid BOOLEAN DEFAULT false,
    ml_last_validated_at TIMESTAMP WITH TIME ZONE,
    ml_validation_error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Business constraints
    CONSTRAINT ml_credentials_app_id_check CHECK (ml_app_id != ''),
    CONSTRAINT ml_credentials_token_type_check CHECK (ml_token_type = 'bearer'),
    CONSTRAINT ml_credentials_expires_future CHECK (ml_expires_at > NOW()),
    CONSTRAINT ml_credentials_refresh_future CHECK (ml_refresh_expires_at > ml_expires_at),
    CONSTRAINT ml_credentials_scopes_check CHECK (ml_scopes LIKE '%read%' AND ml_scopes LIKE '%write%')
);

-- Indexes for OAuth management
CREATE INDEX idx_ml_credentials_ml_user_id ON ml_credentials(ml_user_id);
CREATE INDEX idx_ml_credentials_expires ON ml_credentials(ml_expires_at) WHERE ml_is_valid = true;
CREATE INDEX idx_ml_credentials_refresh_expires ON ml_credentials(ml_refresh_expires_at) WHERE ml_is_valid = true;
CREATE INDEX idx_ml_credentials_site_id ON ml_credentials(ml_site_id);
```

---

## Data Access Patterns & Queries

### Mobile Dashboard Query (Primary Use Case)
```sql
-- Get user's recent products with images for mobile dashboard
SELECT
    p.id,
    p.status,
    p.prompt_text,
    p.created_at,
    gc.title,
    gc.confidence_overall,
    pi.processed_s3_url as primary_image_url
FROM products p
LEFT JOIN generated_content gc ON p.id = gc.product_id
LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true
WHERE p.user_id = $1
ORDER BY p.created_at DESC
LIMIT 20;
```

### Real-time Status Updates Query
```sql
-- Get product status for WebSocket updates
SELECT
    id,
    status,
    processing_started_at,
    processing_completed_at,
    processing_error
FROM products
WHERE id = $1;
```

### Confidence-based Routing Query
```sql
-- Determine user flow based on AI confidence
SELECT
    p.id,
    p.status,
    gc.confidence_overall,
    CASE
        WHEN gc.confidence_overall > 0.85 THEN 'quick_approval'
        WHEN gc.confidence_overall > 0.70 THEN 'balanced_review'
        ELSE 'manual_edit'
    END as recommended_flow
FROM products p
JOIN generated_content gc ON p.id = gc.product_id
WHERE p.id = $1;
```

---

## Performance Optimizations

### Connection Pooling Configuration
```python
# FastAPI database configuration
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
    "pool_recycle": 3600,  # 1 hour
    "echo": False  # Set to True for SQL debugging
}
```

### Caching Strategy
```yaml
Application Level Caching:
  - User sessions: Redis (future)
  - Generated content: In-memory for active products

Database Level:
  - Query plan caching: PostgreSQL default
  - Connection pooling: SQLAlchemy

CDN Level:
  - Image delivery: CloudFront/similar
  - Static assets: Service Worker (PWA)
```

### Monitoring Queries
```sql
-- Slow query monitoring
SELECT
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Index usage monitoring
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0; -- Unused indexes
```

---

## Data Migration Strategy

### Migration Framework
```python
# Alembic configuration for schema versioning
# migrations/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# Import your models
from src.models import Base

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Initial Data Seeding
```sql
-- Create default ML categories for development
INSERT INTO ml_categories (id, name, parent_id) VALUES
('MLA1144', 'Electrónicos, Audio y Video', NULL),
('MLA1000', 'Celulares y Teléfonos', 'MLA1144'),
('MLA1055', 'Accesorios para Celulares', 'MLA1000');

-- Create test users for development
INSERT INTO users (email, password_hash, first_name, last_name) VALUES
('test@intellipost.ai', '$2b$12$...', 'Test', 'User')
ON CONFLICT (email) DO NOTHING;
```

---

## Backup & Recovery Strategy

### Automated Backup Configuration
```yaml
Backup Schedule:
  - Full backup: Daily at 2 AM UTC
  - Incremental: Every 6 hours
  - Point-in-time recovery: 7 days retention

Backup Storage:
  - Primary: S3/MinIO encrypted
  - Geographic redundancy: Different region

Recovery Testing:
  - Monthly recovery test
  - RTO: 30 minutes
  - RPO: 1 hour maximum
```

### Docker Compose Backup Integration
```yaml
# docker-compose.yml backup service
services:
  db-backup:
    image: postgres:15
    command: |
      sh -c "
        while true; do
          pg_dump -h db -U postgres intellipost > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql
          find /backups -name '*.sql' -mtime +7 -delete
          sleep 86400
        done
      "
    volumes:
      - ./backups:/backups
    depends_on:
      - db
```

---

## Security Considerations

### Encryption at Rest
```sql
-- Enable row-level security for sensitive tables
ALTER TABLE ml_credentials ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own credentials
CREATE POLICY ml_credentials_user_policy ON ml_credentials
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());
```

### Data Anonymization (Future GDPR)
```sql
-- Function for user data anonymization
CREATE OR REPLACE FUNCTION anonymize_user_data(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Anonymize user data
    UPDATE users SET
        email = 'deleted_' || gen_random_uuid() || '@deleted.com',
        first_name = 'Deleted',
        last_name = 'User',
        is_active = false
    WHERE id = user_uuid;

    -- Keep products but remove sensitive prompt data
    UPDATE products SET
        prompt_text = '[User content deleted]'
    WHERE user_id = user_uuid;

    -- Delete ML credentials completely
    DELETE FROM ml_credentials WHERE user_id = user_uuid;
END;
$$ LANGUAGE plpgsql;
```

---

**¿Apruebas esta estructura de base de datos o necesitas ajustes antes de continuar con API Design?**
