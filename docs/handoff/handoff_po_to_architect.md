# IntelliPost AI - Product Owner to Architect Handoff

## 📋 **Handoff Summary**

**From:** Sarah (Product Owner)
**To:** Fred (Architect)
**Date:** 19/06/2025
**Project:** IntelliPost AI MVP
**Status:** PRD Completed & Validated (Quality Score: 8.7/10)
**UX Context:** UX handoff provided in parallel - review both documents

---

## 🎯 **Architecture Mission**

Design and specify the complete technical architecture for IntelliPost AI MVP that enables:
- **90% reduction** in user time/effort for MercadoLibre listing creation
- **Intelligent automation** with AI-powered content generation
- **Modular, maintainable** codebase following "Agent Coding First" principles
- **Scalable foundation** ready for post-MVP enhancements

---

## 🏗️ **Core Technical Requirements**

### **Epic Structure Overview:**
- **Epic 1:** Platform Base (8 stories) - Infrastructure, auth, database, CI/CD
- **Epic 2:** AI Content Generation (6 stories) - Core business logic
- **Epic 3:** Review & Publishing (5 stories) - User interaction, ML API integration

### **Technology Stack Confirmed:**
- **Backend:** Python + FastAPI
- **Frontend:** Svelte + SvelteKit
- **Database:** PostgreSQL + Object Storage (S3)
- **Architecture:** Modular Monolith with Hexagonal Architecture principles
- **AI Integration:** Hybrid approach (3rd party APIs + LLMs)
- **Deployment:** Containerized with CI/CD pipeline

---

## 📐 **Architecture Principles & Patterns**

### **Hexagonal Architecture (Ports & Adapters):**
- **Core Business Logic:** Independent of external concerns
- **Ports:** Consumer-defined interfaces (typing.Protocol)
- **Adapters:** Implementations that satisfy ports via duck typing
- **Static Validation:** Pyright validates interface compliance
- **Convention:** "Accept interfaces, return instances" (Go-style)

### **Agent Coding First Requirements:**
- **Code Quality:** Ruff (linting), Pyright (types), ESLint/Prettier (frontend)
- **Architecture Validation:** Tach (Python boundaries), dependency-cruiser (JS/TS)
- **Documentation:** Self-documenting code, minimal but necessary comments
- **Testing:** TDD mandatory, comprehensive test coverage
- **Modularity:** Clear, independently testable components

### **Key Architectural Constraints:**
- **No explicit adapters:** Duck typing + static validation instead of manual adapter classes
- **Modular design:** Easy to swap AI services, add new platforms
- **Type safety:** Comprehensive static typing throughout
- **Quality gates:** NFR8.1 - nothing merges without passing all automated checks

---

## 🏢 **System Architecture Overview**

### **High-Level Components:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Svelte SPA    │    │  FastAPI Backend │    │  External APIs  │
│                 │    │                  │    │                 │
│ • Mobile UI     │◄──►│ • Business Logic │◄──►│ • AI Services   │
│ • Desktop UI    │    │ • API Gateway    │    │ • MercadoLibre  │
│ • State Mgmt    │    │ • Auth & Security│    │ • Object Storage│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       │                  │
                       │ • User Data      │
                       │ • Product Data   │
                       │ • Generated      │
                       │   Content        │
                       └──────────────────┘
```

### **Data Flow Architecture:**
1. **Input Layer:** Svelte UI → FastAPI endpoints
2. **Processing Layer:** AI services orchestration
3. **Storage Layer:** PostgreSQL + S3 persistence
4. **Integration Layer:** MercadoLibre API publishing
5. **Presentation Layer:** Generated content back to UI

---

## 💾 **Data Architecture & Models**

### **Core Entities:**

#### **User**
```python
class User:
    id: UUID
    email: str
    password_hash: str
    created_at: datetime
    # Future: multi-account support ready
```

#### **Product**
```python
class Product:
    id: UUID
    user_id: UUID
    status: ProductStatus  # uploading, processing, ready, publishing, published, failed
    prompt_text: str  # max 500 chars
    created_at: datetime
    updated_at: datetime
```

#### **ProductImage**
```python
class ProductImage:
    id: UUID
    product_id: UUID
    s3_url: str
    is_primary: bool
    file_size: int
    format: str  # JPG, PNG
    resolution: str  # "1920x1080"
    processing_metadata: JSONB
```

#### **GeneratedContent**
```python
class GeneratedContent:
    id: UUID
    product_id: UUID
    title: str
    category_id: str  # MercadoLibre category
    attributes: JSONB  # ML-specific attributes
    description: str
    confidence_scores: JSONB  # per component
    ml_listing_id: str  # after publication
    ml_listing_url: str
    version: int  # for re-generation
```

#### **MLCredentials**
```python
class MLCredentials:
    id: UUID
    user_id: UUID
    app_id: str
    secret_key: str  # encrypted
    access_token: str  # encrypted
    refresh_token: str  # encrypted
    expires_at: datetime
    # Structure ready for multi-account (not implemented in MVP)
```

### **Product Status State Machine:**
```
uploading → processing → ready → publishing → published
     ↓           ↓         ↓         ↓
   failed ←──failed ←──failed ←──failed
```

---

## 🔧 **Backend Architecture Specifications**

### **FastAPI Application Structure:**
```
src/
├── main.py                 # FastAPI app entry point
├── core/
│   ├── config.py          # Environment configuration
│   ├── database.py        # DB connection & session management
│   ├── security.py        # JWT auth, password hashing
│   └── dependencies.py    # FastAPI dependencies
├── models/                # SQLAlchemy models
│   ├── user.py
│   ├── product.py
│   └── ml_credentials.py
├── services/              # Business logic (ports)
│   ├── ai_service.py      # AI content generation protocols
│   ├── image_service.py   # Image processing protocols
│   ├── ml_service.py      # MercadoLibre API protocols
│   └── storage_service.py # Object storage protocols
├── adapters/              # External integrations (adapters)
│   ├── ai_providers/      # OpenAI, Claude, etc.
│   ├── image_processors/  # Background removal APIs
│   ├── ml_api/           # MercadoLibre API client
│   └── storage/          # S3, MinIO adapters
├── api/                  # FastAPI routers
│   ├── auth.py
│   ├── products.py
│   ├── content.py
│   └── publishing.py
└── tests/
    ├── unit/
    ├── integration/      # Test containers
    └── e2e/
```

### **API Design Patterns:**

#### **RESTful Endpoints:**
```
POST   /auth/login
POST   /auth/register
GET    /auth/me

POST   /products                    # Create new product
GET    /products                    # List user products
GET    /products/{id}               # Get specific product
POST   /products/{id}/images        # Upload images
POST   /products/{id}/generate      # Trigger AI generation
PUT    /products/{id}/content       # Update generated content
POST   /products/{id}/publish       # Publish to MercadoLibre

GET    /ml-credentials              # Get current credentials
PUT    /ml-credentials              # Update credentials
POST   /ml-credentials/validate     # Test credentials

GET    /health                      # Health check
```

#### **WebSocket Endpoints:**
```
/ws/products/{id}/status    # Real-time status updates
```

### **Error Handling Strategy:**
- **Retry Logic:** 3 attempts for AI services, ML API
- **Circuit Breaker:** For external service failures
- **Graceful Degradation:** Clear user feedback when services unavailable
- **Structured Logging:** For debugging and monitoring

---

## 🎨 **Frontend Architecture Specifications**

### **SvelteKit Application Structure:**
```
src/
├── app.html              # App shell
├── routes/
│   ├── auth/
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/        # Product list
│   ├── products/
│   │   ├── [id]/
│   │   │   ├── edit/     # Desktop editing
│   │   │   └── review/   # Mobile review
│   │   └── new/          # Mobile input
│   └── settings/         # ML credentials
├── lib/
│   ├── components/       # Reusable UI components
│   │   ├── forms/
│   │   ├── layout/
│   │   └── product/
│   ├── stores/           # Svelte stores for state
│   │   ├── auth.js
│   │   ├── products.js
│   │   └── ui.js
│   ├── api/              # API client functions
│   │   ├── auth.js
│   │   ├── products.js
│   │   └── ml.js
│   ├── utils/            # Helper functions
│   └── types/            # TypeScript definitions
└── static/               # Static assets
```

### **State Management Pattern:**
- **Svelte Stores:** For global state (auth, products)
- **Component State:** For UI-specific state
- **Real-time Updates:** WebSocket integration for status changes
- **Optimistic Updates:** For better UX during API calls

### **Type Sharing Strategy:**
- **Code Generation:** Automated export of Python models to TypeScript
- **Shared Interfaces:** Consistent typing between backend/frontend
- **API Client:** Auto-generated from OpenAPI spec

---

## 🔌 **External Integrations Architecture**

### **AI Services Integration:**
```python
# Port (Protocol)
class AIContentGenerator(Protocol):
    def generate_content(self, images: List[str], prompt: str) -> GeneratedContent:
        ...

    def get_confidence_score(self, content: GeneratedContent) -> ConfidenceScore:
        ...

# Adapters (Implementations)
class OpenAIAdapter:  # Satisfies AIContentGenerator via duck typing
class ClaudeAdapter:  # Satisfies AIContentGenerator via duck typing
```

### **Image Processing Integration:**
```python
class ImageProcessor(Protocol):
    def remove_background(self, image_url: str) -> ProcessedImage:
        ...

    def enhance_quality(self, image_url: str) -> ProcessedImage:
        ...

# Adapters
class Remove_bgAdapter:  # Third-party background removal
class InternalProcessorAdapter:  # Custom processing if needed
```

### **MercadoLibre API Integration:**
```python
class MLPublisher(Protocol):
    def create_listing(self, content: GeneratedContent, credentials: MLCredentials) -> MLListing:
        ...

    def get_categories(self, title: str) -> List[Category]:
        ...

    def validate_credentials(self, credentials: MLCredentials) -> bool:
        ...
```

### **Object Storage Integration:**
```python
class ObjectStorage(Protocol):
    def upload_image(self, image: bytes, key: str) -> str:  # Returns URL
        ...

    def delete_image(self, key: str) -> bool:
        ...

# Adapters
class S3Adapter:       # Production storage
class MinIOAdapter:    # Local development/testing
```

---

## 🧪 **Testing Architecture**

### **Testing Stack:**
- **Unit Tests:** pytest for Python, Jest for JavaScript
- **Integration Tests:** Test containers (PostgreSQL, MinIO/S3, AI mocks)
- **API Tests:** FastAPI TestClient with full request/response cycle
- **E2E Tests:** Playwright for critical user journeys
- **TDD Requirement:** Tests written before implementation

### **Test Container Strategy:**
```python
# Integration test example
@pytest.fixture
def test_db():
    with TestContainerPostgreSQL() as postgres:
        yield postgres

@pytest.fixture
def test_storage():
    with TestContainerMinIO() as minio:
        yield minio

@pytest.fixture
def mock_ai_service():
    # Mock AI responses for consistent testing
    yield MockAIService()
```

### **CI/CD Pipeline Requirements:**
1. **Quality Gates:** Linting, type checking, security scanning
2. **Test Execution:** Unit, integration, API tests
3. **Build Process:** Docker images for both frontend/backend
4. **Deployment:** Automated deployment pipeline
5. **Monitoring:** Health checks, logging, metrics

---

## 📊 **Performance & Scale Considerations**

### **Performance Targets:**
- **API Response:** < 200ms for standard endpoints
- **AI Processing:** 30-60 seconds (with progress updates)
- **Image Upload:** < 5 seconds for 8 images (50MB total)
- **Database Queries:** < 100ms for dashboard load

### **Concurrency Handling:**
- **Async Processing:** AI generation in background tasks
- **Queue System:** For AI processing jobs (Redis/Celery or FastAPI background tasks)
- **Rate Limiting:** For external API calls
- **Connection Pooling:** Database and HTTP clients

### **MVP Scale Planning:**
- **Users:** 100-500 concurrent users
- **Products:** 10,000 products processed/month
- **Storage:** 100GB initial estimate
- **Monitoring:** Basic health checks, error tracking

---

## 🔒 **Security Architecture**

### **Authentication & Authorization:**
- **JWT Tokens:** Access + refresh token pattern
- **Password Security:** bcrypt hashing
- **API Security:** HTTPS only, CORS properly configured
- **Credential Management:** Encrypted storage of ML API keys

### **Data Security:**
- **Encryption at Rest:** Database and S3 encryption
- **Encryption in Transit:** TLS for all communications
- **Input Validation:** Comprehensive validation on all endpoints
- **File Upload Security:** File type, size, malware scanning

### **Privacy Considerations:**
- **Data Retention:** User can delete products and associated data
- **Image Privacy:** Secure URLs with expiration for S3 access
- **GDPR Readiness:** Data export/deletion capabilities (post-MVP)

---

## 🚀 **Deployment Architecture**

### **Infrastructure Stack:**
- **Containerization:** Docker for both frontend/backend
- **Orchestration:** Docker Compose for development, Kubernetes for production
- **Database:** Managed PostgreSQL service
- **Storage:** Managed S3-compatible service
- **CDN:** For static assets and image delivery

### **Environment Strategy:**
- **Development:** Local containers with test containers
- **Staging:** Production-like environment for testing
- **Production:** Managed services with monitoring

### **Monitoring & Observability:**
- **Health Checks:** Application and service health endpoints
- **Logging:** Structured logging with correlation IDs
- **Metrics:** Basic performance and business metrics
- **Error Tracking:** Exception monitoring and alerting

---

## 📋 **Critical Dependencies & Risks**

### **External Service Dependencies:**
1. **MercadoLibre API:**
   - **Risk:** API changes, rate limits, downtime
   - **Mitigation:** Hexagonal architecture enables easy adapter updates

2. **AI Service Providers:**
   - **Risk:** Cost increases, service limitations, quality changes
   - **Mitigation:** Multiple provider adapters, easy switching capability

3. **Image Processing Services:**
   - **Risk:** Service availability, processing quality
   - **Mitigation:** Fallback providers, quality validation

### **Technical Risks:**
1. **AI Processing Quality:**
   - **Risk:** Inconsistent content generation quality
   - **Mitigation:** Confidence scoring, user review workflow

2. **Mobile/Desktop Sync:**
   - **Risk:** State inconsistency across platforms
   - **Mitigation:** Real-time WebSocket updates, optimistic UI updates

### **PENDING INVESTIGATION:**
- **MercadoLibre Thumbnail Generation:** Does ML auto-generate thumbnails or do we need to provide them?
- **ML API Rate Limits:** Specific limits for categorization and publishing APIs
- **AI Service Costs:** Detailed cost analysis for projected usage

---

## 📚 **Reference Documents & Context**

### **Primary Technical References:**
1. **PRD** - `/docs/prd.md`
   - Section 5: Technical Assumptions (CRITICAL - read in detail)
   - Section 6: Epic Overview with detailed user stories
   - Section 3: Non-Functional Requirements

2. **UX Handoff** - `/docs/handoff/handoff_po_to_ux.md`
   - UI requirements that inform API design
   - State management UX requirements
   - Mobile/desktop optimization strategy

### **Research Context:**
3. **AI Technology Research** - `/docs/reports/image_processing/`
   - Available AI services evaluation
   - Technical capabilities and limitations

4. **MercadoLibre Research** - `/docs/reports/publishing/meli/`
   - API capabilities, publishing requirements
   - Platform-specific technical constraints

---

## ✅ **Architecture Deliverables**

### **Required Outputs:**
1. **System Architecture Document:**
   - Complete component architecture with interfaces
   - Database schema and migrations strategy
   - API specification (OpenAPI/Swagger)

2. **Data Architecture:**
   - Detailed entity relationship diagrams
   - Data flow diagrams for critical processes
   - Migration and backup strategies

3. **Integration Architecture:**
   - External service integration patterns
   - Error handling and retry strategies
   - Authentication and security implementation

4. **Deployment Architecture:**
   - Infrastructure as code specifications
   - CI/CD pipeline configuration
   - Monitoring and observability setup

5. **Development Guidelines:**
   - Code organization and patterns
   - Testing strategies and frameworks
   - Quality gate implementations

### **Success Criteria:**
- **Modular Design:** Easy to test, maintain, and extend
- **Type Safety:** Comprehensive static typing throughout
- **Quality Gates:** Automated validation of code quality
- **Performance:** Meets specified performance targets
- **Security:** Follows security best practices
- **Documentation:** Clear, actionable technical specifications

---

## 🔄 **Next Steps**

1. **Architecture Review:** Review both PO and UX handoffs
2. **Research Deep Dive:** Study technical research reports
3. **Design Phase:** Create comprehensive architecture document
4. **Validation:** Review architecture against all user stories
5. **Developer Handoff:** Prepare technical specifications for development team

---

## 📞 **Contact & Coordination**

**Product Owner:** Sarah - Available for clarification on business requirements and user stories
**UX Context:** Review UX handoff for frontend architecture decisions
**Critical Success Factor:** Architecture must support the 90% time reduction goal through intelligent automation and seamless user experience.

---

*This handoff provides the complete technical context for architecting IntelliPost AI MVP. The architecture should enable rapid development while maintaining high code quality and preparing for future extensibility.*
