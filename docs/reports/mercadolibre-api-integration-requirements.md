# MercadoLibre API Integration Requirements - Database Field Specifications

## Document Information
- **Project:** IntelliPost AI MVP
- **Author:** Claude Code Analysis
- **Date:** June 22, 2025
- **Focus:** Argentina Marketplace (MLA)
- **Purpose:** Complete database field requirements for MercadoLibre integration

---

## Executive Summary

This document provides comprehensive database field specifications required for successful MercadoLibre API integration. Based on extensive analysis of MercadoLibre's API documentation, the requirements cover item creation, OAuth authentication, image handling, and Argentina-specific marketplace requirements.

**Key Integration Points:**
- Item creation and management via `/items` API
- OAuth 2.0 authentication with token management
- Image upload and CDN handling
- Category and attribute system compliance
- Argentina (MLA) marketplace regulations

---

## 1. Core Item Creation Fields

### 1.1 Required Fields for POST /items

Based on MercadoLibre API documentation, these fields are **MANDATORY** for item creation:

```sql
-- Add to generated_content table
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS
    -- Core MercadoLibre fields
    ml_title VARCHAR(60) NOT NULL CHECK (char_length(trim(ml_title)) >= 10),
    ml_price DECIMAL(10,2) NOT NULL CHECK (ml_price > 0),
    ml_currency_id CHAR(3) NOT NULL DEFAULT 'ARS',
    ml_available_quantity INTEGER NOT NULL CHECK (ml_available_quantity > 0),
    ml_buying_mode VARCHAR(20) NOT NULL DEFAULT 'buy_it_now',
    ml_condition VARCHAR(20) NOT NULL CHECK (ml_condition IN ('new', 'used', 'not_specified')),
    ml_listing_type_id VARCHAR(50) NOT NULL,
    
    -- Business constraints
    CONSTRAINT ml_title_length_check CHECK (char_length(ml_title) <= 60),
    CONSTRAINT ml_currency_supported CHECK (ml_currency_id IN ('ARS', 'USD')),
    CONSTRAINT ml_buying_mode_valid CHECK (ml_buying_mode IN ('buy_it_now', 'auction')),
    CONSTRAINT ml_listing_type_valid CHECK (ml_listing_type_id IN ('gold_pro', 'gold_premium', 'gold_special', 'silver', 'bronze', 'free'))
);
```

### 1.2 Category and Attributes Storage

MercadoLibre has a complex category/attribute system that requires flexible storage:

```sql
-- Create ML Categories table for caching
CREATE TABLE ml_categories (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'MLA1144'
    name VARCHAR(200) NOT NULL,
    parent_id VARCHAR(50) REFERENCES ml_categories(id),
    site_id CHAR(3) NOT NULL DEFAULT 'MLA',
    listing_allowed BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'enabled',
    max_title_length INTEGER DEFAULT 60,
    immediate_payment BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_categories_status_check CHECK (status IN ('enabled', 'disabled', 'under_review'))
);

-- Create ML Attributes table for category-specific attributes
CREATE TABLE ml_attributes (
    id VARCHAR(100) PRIMARY KEY, -- e.g., 'BRAND'
    category_id VARCHAR(50) NOT NULL REFERENCES ml_categories(id),
    name VARCHAR(200) NOT NULL,
    value_type VARCHAR(50) NOT NULL, -- string, number, boolean, list
    is_required BOOLEAN DEFAULT false,
    is_catalog_required BOOLEAN DEFAULT false,
    is_variation_attribute BOOLEAN DEFAULT false,
    
    -- For list-type attributes
    allowed_values JSONB DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_attributes_value_type_check CHECK (value_type IN ('string', 'number', 'boolean', 'list', 'number_unit'))
);

-- Index for performance
CREATE INDEX idx_ml_attributes_category ON ml_attributes(category_id);
CREATE INDEX idx_ml_attributes_required ON ml_attributes(category_id, is_required) WHERE is_required = true;
```

### 1.3 Enhanced Generated Content Table

Update the existing generated_content table to include all MercadoLibre-specific fields:

```sql
-- Add ML-specific fields to generated_content
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS
    -- MercadoLibre item data
    ml_title VARCHAR(60) NOT NULL DEFAULT '',
    ml_price DECIMAL(10,2),
    ml_currency_id CHAR(3) DEFAULT 'ARS',
    ml_available_quantity INTEGER DEFAULT 1,
    ml_buying_mode VARCHAR(20) DEFAULT 'buy_it_now',
    ml_condition VARCHAR(20) DEFAULT 'new',
    ml_listing_type_id VARCHAR(50) DEFAULT 'gold_special',
    
    -- ML-specific attributes (flexible storage)
    ml_attributes JSONB DEFAULT '{}',
    ml_sale_terms JSONB DEFAULT '{}',
    ml_shipping JSONB DEFAULT '{}',
    
    -- Warranty and service
    ml_warranty VARCHAR(500),
    ml_warranty_type VARCHAR(50),
    
    -- Publishing metadata
    ml_item_id VARCHAR(50), -- MercadoLibre item ID after creation
    ml_permalink TEXT, -- Public URL to the listing
    ml_status VARCHAR(20), -- active, paused, closed, etc.
    ml_health DECIMAL(3,2), -- Item health score (0.00-1.00)
    ml_sold_quantity INTEGER DEFAULT 0,
    
    -- Timestamps
    ml_published_at TIMESTAMP WITH TIME ZONE,
    ml_last_updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT ml_title_required CHECK (ml_title != ''),
    CONSTRAINT ml_price_positive CHECK (ml_price IS NULL OR ml_price > 0),
    CONSTRAINT ml_quantity_positive CHECK (ml_available_quantity > 0),
    CONSTRAINT ml_health_range CHECK (ml_health IS NULL OR ml_health BETWEEN 0.00 AND 1.00)
);

-- Add indexes for ML integration
CREATE INDEX idx_generated_content_ml_item_id ON generated_content(ml_item_id) WHERE ml_item_id IS NOT NULL;
CREATE INDEX idx_generated_content_ml_status ON generated_content(ml_status) WHERE ml_status IS NOT NULL;
CREATE INDEX idx_generated_content_ml_category ON generated_content(ml_category_id);
```

---

## 2. OAuth Authentication and Credentials

### 2.1 Enhanced ML Credentials Table

The existing ml_credentials table needs updates to handle MercadoLibre's OAuth 2.0 flow properly:

```sql
-- Update ml_credentials table with complete OAuth fields
ALTER TABLE ml_credentials ADD COLUMN IF NOT EXISTS
    -- OAuth application data
    ml_app_id VARCHAR(255) NOT NULL DEFAULT '',
    ml_secret_key_encrypted TEXT NOT NULL DEFAULT '',
    
    -- OAuth tokens
    ml_access_token_encrypted TEXT NOT NULL DEFAULT '',
    ml_refresh_token_encrypted TEXT NOT NULL DEFAULT '',
    ml_token_type VARCHAR(20) DEFAULT 'bearer',
    
    -- Token lifecycle
    ml_expires_at TIMESTAMP WITH TIME ZONE,
    ml_refresh_expires_at TIMESTAMP WITH TIME ZONE,
    ml_scopes TEXT DEFAULT 'offline_access read write',
    
    -- User data
    ml_user_id BIGINT, -- MercadoLibre user ID
    ml_nickname VARCHAR(100), -- MercadoLibre nickname
    ml_email VARCHAR(255), -- MercadoLibre email
    
    -- Validation and health
    ml_is_valid BOOLEAN DEFAULT false,
    ml_last_validated_at TIMESTAMP WITH TIME ZONE,
    ml_validation_error TEXT,
    ml_rate_limit_remaining INTEGER,
    ml_rate_limit_reset TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT ml_credentials_app_id_check CHECK (ml_app_id != ''),
    CONSTRAINT ml_credentials_token_type_check CHECK (ml_token_type IN ('bearer')),
    CONSTRAINT ml_credentials_scopes_check CHECK (ml_scopes LIKE '%read%' OR ml_scopes LIKE '%write%')
);

-- Add indexes for OAuth management
CREATE INDEX idx_ml_credentials_ml_user_id ON ml_credentials(ml_user_id) WHERE ml_user_id IS NOT NULL;
CREATE INDEX idx_ml_credentials_expires ON ml_credentials(ml_expires_at) WHERE ml_is_valid = true;
CREATE INDEX idx_ml_credentials_refresh_expires ON ml_credentials(ml_refresh_expires_at) WHERE ml_is_valid = true;
```

### 2.2 OAuth Token Management

Key considerations for token management:

**Token Lifecycles:**
- Access Token: 6 hours validity
- Refresh Token: 6 months validity, one-time use
- Automatic refresh required before expiration

**Required Scopes:**
- `offline_access`: For refresh token functionality
- `read`: Read user data and listings
- `write`: Create and modify listings

**Database Fields for Token Storage:**
```json
{
  "ml_app_id": "123456789",
  "ml_secret_key_encrypted": "AES256_encrypted_secret",
  "ml_access_token_encrypted": "AES256_encrypted_token",
  "ml_refresh_token_encrypted": "AES256_encrypted_refresh",
  "ml_token_type": "bearer",
  "ml_expires_at": "2025-06-22T20:00:00Z",
  "ml_refresh_expires_at": "2025-12-22T14:00:00Z",
  "ml_scopes": "offline_access read write",
  "ml_user_id": 123456789,
  "ml_nickname": "TESTUSER123",
  "ml_email": "user@example.com"
}
```

---

## 3. Image Upload and Management

### 3.1 Enhanced Product Images Table

Update the existing product_images table to handle MercadoLibre's image requirements:

```sql
-- Add ML-specific image fields
ALTER TABLE product_images ADD COLUMN IF NOT EXISTS
    -- MercadoLibre image data
    ml_picture_id VARCHAR(100), -- ML's internal picture ID
    ml_picture_url TEXT, -- ML's CDN URL
    ml_max_size VARCHAR(20), -- e.g., "1920x1920"
    ml_variations JSONB DEFAULT '{}', -- Different size variations
    
    -- Image validation
    ml_upload_status VARCHAR(20) DEFAULT 'pending',
    ml_upload_error TEXT,
    ml_dominant_color VARCHAR(7), -- Hex color code
    
    -- Crop and positioning data
    ml_crop_data JSONB DEFAULT '{}',
    
    -- Timestamps
    ml_uploaded_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT ml_upload_status_check CHECK (ml_upload_status IN ('pending', 'uploading', 'success', 'failed')),
    CONSTRAINT ml_dominant_color_format CHECK (ml_dominant_color IS NULL OR ml_dominant_color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Add indexes for ML image management
CREATE INDEX idx_product_images_ml_picture_id ON product_images(ml_picture_id) WHERE ml_picture_id IS NOT NULL;
CREATE INDEX idx_product_images_ml_status ON product_images(ml_upload_status);
```

### 3.2 Image Upload Specifications

**Technical Requirements:**
```yaml
Image Upload API:
  endpoint: "https://api.mercadolibre.com/pictures/items/upload"
  method: "POST"
  auth: "Bearer token required"
  content_type: "multipart/form-data"

Image Specifications:
  formats: ["JPG", "JPEG", "PNG"]
  max_size: "10 MB"
  recommended_resolution: "1200x1200 px"
  min_resolution: "500x500 px"
  max_resolution: "1920x1920 px"
  aspect_ratio: "Square (1:1) preferred"
  quality: "Product should occupy 95% of space"

Quantity Limits:
  standard_items: 6
  variation_items: 10
  minimum_required: 1
```

**Database Storage Structure:**
```json
{
  "ml_picture_id": "959699-MLA43299127002_092020",
  "ml_picture_url": "https://http2.mlstatic.com/D_959699-MLA43299127002_092020-O.jpg",
  "ml_max_size": "1920x1920",
  "ml_variations": {
    "S": "https://http2.mlstatic.com/D_959699-MLA43299127002_092020-S.jpg",
    "M": "https://http2.mlstatic.com/D_959699-MLA43299127002_092020-M.jpg",
    "F": "https://http2.mlstatic.com/D_959699-MLA43299127002_092020-F.jpg"
  },
  "ml_upload_status": "success",
  "ml_dominant_color": "#FFFFFF",
  "ml_crop_data": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1920
  }
}
```

---

## 4. Argentina (MLA) Marketplace Specific Requirements

### 4.1 Currency and Pricing

**Argentina-Specific Fields:**
```sql
-- Add to generated_content table
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS
    -- Argentina-specific pricing
    ml_original_price DECIMAL(10,2), -- For discount display
    ml_price_currency_local CHAR(3) DEFAULT 'ARS',
    ml_price_usd DECIMAL(10,2), -- USD price for Global Selling
    ml_installments JSONB DEFAULT '{}', -- Installment options
    
    -- Argentina tax and regulation
    ml_tax_mode VARCHAR(20) DEFAULT 'not_specified',
    ml_tax_percentage DECIMAL(5,2),
    ml_accepts_mercadopago BOOLEAN DEFAULT true,
    ml_immediate_payment BOOLEAN DEFAULT false,
    
    -- Shipping (Argentina specific)
    ml_free_shipping BOOLEAN DEFAULT false,
    ml_local_pick_up BOOLEAN DEFAULT false,
    ml_shipping_mode VARCHAR(20) DEFAULT 'me2',
    
    -- Constraints
    CONSTRAINT ml_price_currency_check CHECK (ml_price_currency_local IN ('ARS', 'USD')),
    CONSTRAINT ml_tax_mode_check CHECK (ml_tax_mode IN ('not_specified', 'tax_included', 'tax_not_included')),
    CONSTRAINT ml_shipping_mode_check CHECK (ml_shipping_mode IN ('me2', 'me1', 'custom', 'not_specified'))
);
```

### 4.2 Installment and Payment Options

```json
{
  "ml_installments": {
    "quantity": 12,
    "amount": 833.33,
    "rate": 0,
    "currency_id": "ARS"
  },
  "ml_accepts_mercadopago": true,
  "ml_immediate_payment": false
}
```

### 4.3 Argentina Regulatory Compliance

```sql
-- Create table for Argentina-specific compliance
CREATE TABLE ml_argentina_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- AFIP/CUIT information
    cuit_number VARCHAR(15),
    tax_condition VARCHAR(50), -- monotributo, responsable_inscripto, etc.
    
    -- Business information
    business_name VARCHAR(200),
    business_address TEXT,
    business_phone VARCHAR(20),
    
    -- Compliance status
    is_verified BOOLEAN DEFAULT false,
    verification_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_argentina_compliance_one_per_user UNIQUE (user_id)
);
```

---

## 5. Item Status and Lifecycle Management

### 5.1 Item Status Tracking

```sql
-- Add item lifecycle tracking
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS
    -- MercadoLibre item status
    ml_status VARCHAR(20) DEFAULT 'draft',
    ml_health DECIMAL(3,2),
    ml_catalog_listing BOOLEAN DEFAULT false,
    ml_catalog_product_id VARCHAR(100),
    
    -- Performance metrics
    ml_views INTEGER DEFAULT 0,
    ml_sold_quantity INTEGER DEFAULT 0,
    ml_available_quantity_current INTEGER,
    
    -- Modification tracking
    ml_last_updated_at TIMESTAMP WITH TIME ZONE,
    ml_status_history JSONB DEFAULT '[]',
    
    -- Constraints
    CONSTRAINT ml_status_valid CHECK (ml_status IN ('draft', 'active', 'paused', 'closed', 'under_review', 'inactive')),
    CONSTRAINT ml_health_range CHECK (ml_health IS NULL OR ml_health BETWEEN 0.00 AND 1.00)
);
```

### 5.2 Status Transition Rules

```json
{
  "ml_status_history": [
    {
      "status": "draft",
      "timestamp": "2025-06-22T10:00:00Z",
      "reason": "initial_creation"
    },
    {
      "status": "active",
      "timestamp": "2025-06-22T10:30:00Z",
      "reason": "published_successfully"
    },
    {
      "status": "paused",
      "timestamp": "2025-06-22T15:00:00Z",
      "reason": "user_paused"
    }
  ]
}
```

---

## 6. Error Handling and Logging

### 6.1 API Error Tracking

```sql
-- Create ML API error log table
CREATE TABLE ml_api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    
    -- API call details
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_body JSONB,
    response_body JSONB,
    
    -- Response details
    status_code INTEGER NOT NULL,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Rate limiting
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_time_ms INTEGER,
    
    -- Constraints
    CONSTRAINT ml_api_logs_method_check CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    CONSTRAINT ml_api_logs_status_check CHECK (status_code BETWEEN 100 AND 599)
);

-- Indexes for error analysis
CREATE INDEX idx_ml_api_logs_user_id ON ml_api_logs(user_id);
CREATE INDEX idx_ml_api_logs_status_code ON ml_api_logs(status_code);
CREATE INDEX idx_ml_api_logs_created_at ON ml_api_logs(created_at DESC);
CREATE INDEX idx_ml_api_logs_errors ON ml_api_logs(success, error_code) WHERE success = false;
```

---

## 7. Database Migration Script

### 7.1 Complete Migration SQL

```sql
-- Migration: Add MercadoLibre integration fields
-- Date: 2025-06-22
-- Description: Complete database schema for MercadoLibre API integration

BEGIN;

-- 1. Update ml_credentials table
ALTER TABLE ml_credentials ADD COLUMN IF NOT EXISTS
    ml_app_id VARCHAR(255) NOT NULL DEFAULT '',
    ml_secret_key_encrypted TEXT NOT NULL DEFAULT '',
    ml_access_token_encrypted TEXT NOT NULL DEFAULT '',
    ml_refresh_token_encrypted TEXT NOT NULL DEFAULT '',
    ml_token_type VARCHAR(20) DEFAULT 'bearer',
    ml_expires_at TIMESTAMP WITH TIME ZONE,
    ml_refresh_expires_at TIMESTAMP WITH TIME ZONE,
    ml_scopes TEXT DEFAULT 'offline_access read write',
    ml_user_id BIGINT,
    ml_nickname VARCHAR(100),
    ml_email VARCHAR(255),
    ml_is_valid BOOLEAN DEFAULT false,
    ml_last_validated_at TIMESTAMP WITH TIME ZONE,
    ml_validation_error TEXT,
    ml_rate_limit_remaining INTEGER,
    ml_rate_limit_reset TIMESTAMP WITH TIME ZONE;

-- 2. Update generated_content table
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS
    -- Core ML fields
    ml_title VARCHAR(60) NOT NULL DEFAULT '',
    ml_price DECIMAL(10,2),
    ml_currency_id CHAR(3) DEFAULT 'ARS',
    ml_available_quantity INTEGER DEFAULT 1,
    ml_buying_mode VARCHAR(20) DEFAULT 'buy_it_now',
    ml_condition VARCHAR(20) DEFAULT 'new',
    ml_listing_type_id VARCHAR(50) DEFAULT 'gold_special',
    
    -- ML attributes and metadata
    ml_attributes JSONB DEFAULT '{}',
    ml_sale_terms JSONB DEFAULT '{}',
    ml_shipping JSONB DEFAULT '{}',
    ml_warranty VARCHAR(500),
    ml_warranty_type VARCHAR(50),
    
    -- Publishing data
    ml_item_id VARCHAR(50),
    ml_permalink TEXT,
    ml_status VARCHAR(20) DEFAULT 'draft',
    ml_health DECIMAL(3,2),
    ml_sold_quantity INTEGER DEFAULT 0,
    ml_published_at TIMESTAMP WITH TIME ZONE,
    ml_last_updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Argentina-specific
    ml_original_price DECIMAL(10,2),
    ml_price_currency_local CHAR(3) DEFAULT 'ARS',
    ml_price_usd DECIMAL(10,2),
    ml_installments JSONB DEFAULT '{}',
    ml_tax_mode VARCHAR(20) DEFAULT 'not_specified',
    ml_tax_percentage DECIMAL(5,2),
    ml_accepts_mercadopago BOOLEAN DEFAULT true,
    ml_immediate_payment BOOLEAN DEFAULT false,
    ml_free_shipping BOOLEAN DEFAULT false,
    ml_local_pick_up BOOLEAN DEFAULT false,
    ml_shipping_mode VARCHAR(20) DEFAULT 'me2',
    
    -- Lifecycle tracking
    ml_catalog_listing BOOLEAN DEFAULT false,
    ml_catalog_product_id VARCHAR(100),
    ml_views INTEGER DEFAULT 0,
    ml_available_quantity_current INTEGER,
    ml_status_history JSONB DEFAULT '[]';

-- 3. Update product_images table
ALTER TABLE product_images ADD COLUMN IF NOT EXISTS
    ml_picture_id VARCHAR(100),
    ml_picture_url TEXT,
    ml_max_size VARCHAR(20),
    ml_variations JSONB DEFAULT '{}',
    ml_upload_status VARCHAR(20) DEFAULT 'pending',
    ml_upload_error TEXT,
    ml_dominant_color VARCHAR(7),
    ml_crop_data JSONB DEFAULT '{}',
    ml_uploaded_at TIMESTAMP WITH TIME ZONE;

-- 4. Create ML Categories table
CREATE TABLE IF NOT EXISTS ml_categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    parent_id VARCHAR(50) REFERENCES ml_categories(id),
    site_id CHAR(3) NOT NULL DEFAULT 'MLA',
    listing_allowed BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'enabled',
    max_title_length INTEGER DEFAULT 60,
    immediate_payment BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create ML Attributes table
CREATE TABLE IF NOT EXISTS ml_attributes (
    id VARCHAR(100) PRIMARY KEY,
    category_id VARCHAR(50) NOT NULL REFERENCES ml_categories(id),
    name VARCHAR(200) NOT NULL,
    value_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT false,
    is_catalog_required BOOLEAN DEFAULT false,
    is_variation_attribute BOOLEAN DEFAULT false,
    allowed_values JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create ML API Logs table
CREATE TABLE IF NOT EXISTS ml_api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_body JSONB,
    response_body JSONB,
    status_code INTEGER NOT NULL,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    error_code VARCHAR(50),
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_time_ms INTEGER
);

-- 7. Create ML Argentina Compliance table
CREATE TABLE IF NOT EXISTS ml_argentina_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cuit_number VARCHAR(15),
    tax_condition VARCHAR(50),
    business_name VARCHAR(200),
    business_address TEXT,
    business_phone VARCHAR(20),
    is_verified BOOLEAN DEFAULT false,
    verification_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT ml_argentina_compliance_one_per_user UNIQUE (user_id)
);

-- 8. Add all indexes
CREATE INDEX IF NOT EXISTS idx_ml_credentials_ml_user_id ON ml_credentials(ml_user_id) WHERE ml_user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ml_credentials_expires ON ml_credentials(ml_expires_at) WHERE ml_is_valid = true;
CREATE INDEX IF NOT EXISTS idx_generated_content_ml_item_id ON generated_content(ml_item_id) WHERE ml_item_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_generated_content_ml_status ON generated_content(ml_status) WHERE ml_status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_product_images_ml_picture_id ON product_images(ml_picture_id) WHERE ml_picture_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ml_categories_parent ON ml_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_ml_attributes_category ON ml_attributes(category_id);
CREATE INDEX IF NOT EXISTS idx_ml_api_logs_user_id ON ml_api_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_api_logs_errors ON ml_api_logs(success, error_code) WHERE success = false;

COMMIT;
```

---

## 8. Implementation Checklist

### 8.1 Database Schema Updates
- [ ] Run migration script to add all ML-specific fields
- [ ] Verify all indexes are created properly
- [ ] Test constraints and validation rules
- [ ] Create sample data for development/testing

### 8.2 API Integration Points
- [ ] Implement OAuth 2.0 authentication flow
- [ ] Create category and attribute caching mechanism
- [ ] Build item creation and update endpoints
- [ ] Implement image upload workflow
- [ ] Add error handling and logging

### 8.3 Argentina-Specific Features
- [ ] Handle ARS currency and pricing
- [ ] Implement installment options
- [ ] Add tax calculation logic
- [ ] Configure shipping options
- [ ] Implement compliance tracking

### 8.4 Security and Compliance
- [ ] Encrypt all sensitive credentials
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Create backup procedures
- [ ] Test GDPR compliance (future)

---

## 9. Summary

This comprehensive database schema provides all necessary fields for complete MercadoLibre integration. The design ensures:

**Scalability:** Flexible JSONB fields for varying category attributes
**Security:** Encrypted credential storage with proper access controls
**Compliance:** Argentina-specific tax and regulatory requirements
**Performance:** Optimized indexes for common query patterns
**Maintainability:** Clear field naming and comprehensive documentation

The schema supports the full MercadoLibre API workflow from OAuth authentication through item creation, image upload, and ongoing lifecycle management, specifically optimized for the Argentina marketplace (MLA).