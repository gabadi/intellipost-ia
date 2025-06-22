# MercadoLibre Support Tables - Database Schema

## Document Information
- **Project:** IntelliPost AI MVP
- **Purpose:** Support tables for MercadoLibre category/attribute system
- **Database:** PostgreSQL 15+

---

## 1. MercadoLibre Categories Table
**Purpose:** Cache ML categories for offline validation and performance

```sql
CREATE TABLE ml_categories (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'MLA1144'
    name VARCHAR(200) NOT NULL,
    parent_id VARCHAR(50) REFERENCES ml_categories(id),
    site_id CHAR(3) NOT NULL DEFAULT 'MLA',
    
    -- Category properties
    listing_allowed BOOLEAN DEFAULT true,
    catalog_listing BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'enabled',
    
    -- Listing constraints
    max_title_length INTEGER DEFAULT 60,
    max_description_length INTEGER DEFAULT 50000,
    immediate_payment BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_categories_status_check CHECK (status IN ('enabled', 'disabled', 'under_review')),
    CONSTRAINT ml_categories_site_check CHECK (site_id = 'MLA') -- Argentina only for MVP
);

-- Indexes for category navigation
CREATE INDEX idx_ml_categories_parent ON ml_categories(parent_id);
CREATE INDEX idx_ml_categories_site ON ml_categories(site_id);
CREATE INDEX idx_ml_categories_listing_allowed ON ml_categories(listing_allowed) WHERE listing_allowed = true;
CREATE INDEX idx_ml_categories_name ON ml_categories(name);

-- Full-text search on category names
CREATE INDEX idx_ml_categories_name_fts ON ml_categories USING gin(to_tsvector('spanish', name));
```

---

## 2. MercadoLibre Attributes Table
**Purpose:** Store category-specific attributes for validation

```sql
CREATE TABLE ml_attributes (
    id VARCHAR(100) PRIMARY KEY, -- e.g., 'BRAND'
    category_id VARCHAR(50) NOT NULL REFERENCES ml_categories(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    
    -- Attribute type and validation
    value_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT false,
    is_catalog_required BOOLEAN DEFAULT false,
    is_variation_attribute BOOLEAN DEFAULT false,
    is_searchable BOOLEAN DEFAULT false,
    
    -- For list-type attributes
    allowed_values JSONB DEFAULT '[]',
    default_value TEXT,
    
    -- Constraints
    min_value DECIMAL(15,4),
    max_value DECIMAL(15,4),
    max_values_allowed INTEGER DEFAULT 1,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_attributes_value_type_check CHECK (
        value_type IN ('string', 'number', 'boolean', 'list', 'number_unit', 'date')
    ),
    CONSTRAINT ml_attributes_values_count_check CHECK (max_values_allowed > 0)
);

-- Indexes for attribute lookup
CREATE INDEX idx_ml_attributes_category ON ml_attributes(category_id);
CREATE INDEX idx_ml_attributes_required ON ml_attributes(category_id, is_required) WHERE is_required = true;
CREATE INDEX idx_ml_attributes_searchable ON ml_attributes(is_searchable) WHERE is_searchable = true;
CREATE INDEX idx_ml_attributes_name ON ml_attributes(name);
CREATE INDEX idx_ml_attributes_allowed_values ON ml_attributes USING GIN (allowed_values);
```

**Allowed Values JSON Structure:**
```json
[
    {"id": "2230284", "name": "Samsung"},
    {"id": "7815", "name": "Apple"},
    {"id": "59387", "name": "Motorola"}
]
```

---

## 3. Product Images Enhanced Table
**Purpose:** Add MercadoLibre-specific image metadata

```sql
-- Add ML-specific fields to existing product_images table
ALTER TABLE product_images ADD COLUMN IF NOT EXISTS
    -- MercadoLibre image data
    ml_image_id VARCHAR(100), -- ML returns image ID after upload
    ml_secure_url TEXT, -- HTTPS URL provided by ML
    ml_size VARCHAR(20), -- O, B, S, M, L, X (Original, Big, Small, Medium, Large, Extra)
    ml_quality VARCHAR(20), -- "good", "excellent" based on ML analysis
    
    -- ML processing metadata
    ml_uploaded_at TIMESTAMP WITH TIME ZONE,
    ml_upload_error TEXT,
    ml_upload_retry_count INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT ml_size_valid CHECK (ml_size IS NULL OR ml_size IN ('O', 'B', 'S', 'M', 'L', 'X')),
    CONSTRAINT ml_quality_valid CHECK (ml_quality IS NULL OR ml_quality IN ('good', 'excellent')),
    CONSTRAINT ml_retry_count_valid CHECK (ml_upload_retry_count >= 0 AND ml_upload_retry_count <= 3)
);

-- Indexes for ML image management
CREATE INDEX idx_product_images_ml_image_id ON product_images(ml_image_id) WHERE ml_image_id IS NOT NULL;
CREATE INDEX idx_product_images_ml_upload_status ON product_images(product_id, ml_uploaded_at);
```

---

## 4. API Logs Table
**Purpose:** Track MercadoLibre API calls for debugging and rate limiting

```sql
CREATE TABLE ml_api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Request data
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_id VARCHAR(100), -- ML request ID for tracing
    
    -- Response data
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    
    -- Error tracking
    error_type VARCHAR(100),
    error_message TEXT,
    error_details JSONB,
    
    -- Context
    product_id UUID REFERENCES products(id),
    operation VARCHAR(50), -- 'create_item', 'upload_image', 'get_categories', etc.
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ml_api_logs_method_check CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE')),
    CONSTRAINT ml_api_logs_status_check CHECK (status_code >= 100 AND status_code < 600),
    CONSTRAINT ml_api_logs_response_time_check CHECK (response_time_ms IS NULL OR response_time_ms >= 0)
);

-- Indexes for API monitoring
CREATE INDEX idx_ml_api_logs_created_at ON ml_api_logs(created_at DESC);
CREATE INDEX idx_ml_api_logs_endpoint ON ml_api_logs(endpoint);
CREATE INDEX idx_ml_api_logs_status_code ON ml_api_logs(status_code);
CREATE INDEX idx_ml_api_logs_error_type ON ml_api_logs(error_type) WHERE error_type IS NOT NULL;
CREATE INDEX idx_ml_api_logs_product_id ON ml_api_logs(product_id) WHERE product_id IS NOT NULL;
CREATE INDEX idx_ml_api_logs_operation ON ml_api_logs(operation);
```

---

## 5. Data Synchronization Functions

### Category Sync Function
```sql
-- Function to sync categories from MercadoLibre API
CREATE OR REPLACE FUNCTION sync_ml_categories()
RETURNS INTEGER AS $$
DECLARE
    synced_count INTEGER := 0;
BEGIN
    -- Mark all categories as potentially stale
    UPDATE ml_categories SET last_synced_at = NOW() - INTERVAL '1 day';
    
    -- This would be called by Python code that fetches from ML API
    -- and inserts/updates categories
    
    -- Return count of synced categories
    SELECT COUNT(*) INTO synced_count 
    FROM ml_categories 
    WHERE last_synced_at > NOW() - INTERVAL '1 hour';
    
    RETURN synced_count;
END;
$$ LANGUAGE plpgsql;
```

### Attribute Validation Function
```sql
-- Function to validate product attributes against ML requirements
CREATE OR REPLACE FUNCTION validate_ml_attributes(
    p_category_id VARCHAR(50),
    p_attributes JSONB
) RETURNS TABLE(
    attribute_id VARCHAR(100),
    is_valid BOOLEAN,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ma.id,
        CASE 
            WHEN ma.is_required AND NOT (p_attributes ? ma.id) THEN false
            WHEN ma.value_type = 'list' AND (p_attributes ->> ma.id) IS NOT NULL 
                 AND NOT (ma.allowed_values @> jsonb_build_array(p_attributes ->> ma.id)) THEN false
            ELSE true
        END as is_valid,
        CASE 
            WHEN ma.is_required AND NOT (p_attributes ? ma.id) THEN 
                'Required attribute ' || ma.name || ' is missing'
            WHEN ma.value_type = 'list' AND (p_attributes ->> ma.id) IS NOT NULL 
                 AND NOT (ma.allowed_values @> jsonb_build_array(p_attributes ->> ma.id)) THEN 
                'Invalid value for ' || ma.name || '. Allowed values: ' || ma.allowed_values::text
            ELSE NULL
        END as error_message
    FROM ml_attributes ma
    WHERE ma.category_id = p_category_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. Initial Data Population

### Seed Categories (Top-level Argentina)
```sql
-- Insert main Argentina categories for development
INSERT INTO ml_categories (id, name, parent_id, site_id, listing_allowed) VALUES
('MLA5725', 'Accesorios para Vehículos', NULL, 'MLA', true),
('MLA1071', 'Animales y Mascotas', NULL, 'MLA', true),
('MLA1367', 'Antigüedades y Colecciones', NULL, 'MLA', true),
('MLA1368', 'Arte, Librería y Mercería', NULL, 'MLA', true),
('MLA1384', 'Bebés', NULL, 'MLA', true),
('MLA1403', 'Cámaras y Accesorios', NULL, 'MLA', true),
('MLA1071', 'Celulares y Teléfonos', NULL, 'MLA', true),
('MLA1144', 'Electrónicos, Audio y Video', NULL, 'MLA', true),
('MLA1276', 'Deportes y Fitness', NULL, 'MLA', true),
('MLA1430', 'Ropa y Accesorios', NULL, 'MLA', true)
ON CONFLICT (id) DO NOTHING;

-- Insert common attributes for electronics
INSERT INTO ml_attributes (id, category_id, name, value_type, is_required, allowed_values) VALUES
('BRAND', 'MLA1144', 'Marca', 'list', true, '[{"id":"2230284","name":"Samsung"},{"id":"7815","name":"Apple"},{"id":"59387","name":"Motorola"}]'),
('MODEL', 'MLA1144', 'Modelo', 'string', false, '[]'),
('COLOR', 'MLA1144', 'Color', 'list', false, '[{"id":"52049","name":"Negro"},{"id":"52050","name":"Blanco"},{"id":"52051","name":"Azul"}]')
ON CONFLICT (id) DO NOTHING;
```

---

**Este esquema completa la integración con MercadoLibre. ¿Continuamos con API Design o quieres revisar algún aspecto específico?**