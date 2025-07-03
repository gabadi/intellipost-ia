# IntelliPost AI - System Architecture Overview

## Document Information
- **Project:** IntelliPost AI MVP
- **Architect:** Winston (Fred)
- **Date:** June 22, 2025
- **Phase:** System Architecture Design
- **Scope:** Mobile-Complete MVP with Desktop Post-MVP

---

## Executive Summary

IntelliPost AI is a mobile-first AI-powered platform that transforms the MercadoLibre listing creation process from a 15-20 minute manual task into a **<60 second automated flow**. Users capture photos, provide a prompt, and publish ready-to-sell listings through intelligent AI content generation.

**Core Value Proposition:** Photo + Prompt = Published listing in under 60 seconds

---

## System Architecture Pattern

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL WORLD                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Svelte    │  │   Mobile    │  │    AI Services      │ │
│  │   Desktop   │  │   Native    │  │  (OpenAI/Claude)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                │                     │           │
└─────────┼────────────────┼─────────────────────┼───────────┘
          │                │                     │
    ┌─────▼────────────────▼─────────────────────▼─────┐
    │           PROTOCOLS (Client Interfaces)         │
    │ AIContentGenerator │ ImageProcessor │ MLPublisher│
    └─────────────────────┬───────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────┐
    │                CORE DOMAIN                      │
    │                                                 │
    │  Product Management │ AI Content Generation     │
    │  Publishing Flow    │ Confidence Scoring        │
    │  Image Processing   │ State Management          │
    │                                                 │
    └─────────────────────┬───────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────┐
    │       SERVICES (Duck-type Compatible)           │
    │ GeminiService │ PhotoRoomService │ MLAPIService │
    │ (No explicit adapter classes - direct compatibility) │
    └─────────────────────────────────────────────────┘
```

### Key Architectural Principles

1. **Core Domain Independence**: Business logic isolated from external concerns
2. **Go-Style Protocols**: "Accept interfaces, return instances" - no explicit adapters
3. **Duck Typing + Static Validation**: Pyright validates Protocol compatibility automatically
4. **Tell Don't Ask**: Objects contain behavior and make decisions, not expose state for external decisions
5. **Mobile-First Design**: All components optimized for mobile performance
6. **AI-Service Agnostic**: Easy switching between providers via Protocol compatibility
7. **Real-time Processing**: WebSocket updates during async operations
8. **Module Independence Validated**: PoC research confirms Protocol-based architecture achieves true module independence with zero cross-module imports

---

## Technology Stack Decisions

### Backend Stack
```yaml
Language: Python 3.11+
Framework: FastAPI
  - Rationale: High performance, automatic OpenAPI, excellent async support
  - Async/await for AI processing and real-time updates

Database: PostgreSQL 15+
  - Primary: Structured data (users, products, content)
  - JSONB: Flexible metadata and ML attributes

Object Storage: S3-Compatible
  - Images: Original and processed photos
  - CDN integration for fast mobile delivery

Message Queue: FastAPI Background Tasks (MVP) → Redis/Celery (Post-MVP)
  - AI processing queue
  - MercadoLibre publishing queue

Real-time: WebSocket (FastAPI native)
  - Processing status updates
  - Cross-device sync (mobile ↔ desktop)
```

### Frontend Stack
```yaml
Framework: SvelteKit
  - Rationale: Lightweight, excellent mobile performance, TypeScript support
  - SSR capability for SEO (post-MVP)

State Management: Svelte Stores
  - Global: Auth, products, UI state
  - Real-time: WebSocket integration

Type Safety: TypeScript
  - Shared types with backend
  - Auto-generated API client

Mobile Optimization:
  - Progressive Web App (PWA)
  - Service Worker for offline resilience
  - Touch-optimized UI components
```

### External Integrations
```yaml
AI Services: Multi-provider approach
  - Primary: OpenAI GPT-4 Vision
  - Secondary: Anthropic Claude 3
  - Fallback: Manual editing workflow

Image Processing:
  - Background Removal: Remove.bg API
  - Compression: Sharp.js (client-side)
  - Storage: Auto-WebP conversion

MercadoLibre API:
  - OAuth 2.0 authentication
  - Listing creation and management
  - Category and attribute resolution
```

---

## Core System Components

### 1. Product Lifecycle Engine
**Purpose:** Orchestrates the complete product journey from photo capture to published listing

```python
# Core domain entity
@dataclass
class Product:
    id: UUID
    user_id: UUID
    status: ProductStatus  # uploading → processing → ready → publishing → published
    confidence: ConfidenceScore
    inputs: ProductInputs   # photos, prompt
    outputs: GeneratedContent  # AI-generated content
    metadata: ProductMetadata
```

**State Machine:**
```
Photo Upload → AI Processing → Content Ready → User Review → Publishing → Published
     ↓              ↓              ↓             ↓            ↓
   Failed ←────── Failed ←────── Failed ←──── Failed ←──── Failed
```

### 2. AI Content Generation Service
**Purpose:** Multi-provider AI orchestration with confidence scoring

```python
# Protocol defines CLIENT interface (what the business logic expects)
class AIContentGenerator(Protocol):
    async def generate_listing(
        self,
        images: List[ImageData],
        prompt: str,
        ml_category_hint: Optional[str] = None
    ) -> GeneratedContent:
        ...

    async def calculate_confidence(
        self,
        content: GeneratedContent
    ) -> ConfidenceScore:
        ...

# Services are duck-type compatible (NO explicit implementation)
# Pyright validates compatibility automatically
class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel("gemini-2.5-flash")

    # Duck-type compatible with AIContentGenerator
    async def generate_listing(self, images: List[ImageData], prompt: str, ml_category_hint: Optional[str] = None) -> GeneratedContent:
        # Returns GeneratedContent instance
        pass

    async def calculate_confidence(self, content: GeneratedContent) -> ConfidenceScore:
        # Returns ConfidenceScore instance
        pass

# Business logic accepts interface, returns instances (Go principle)
async def process_product_content(product_id: UUID, ai_service: AIContentGenerator) -> GeneratedContent:
    # Accepts interface (Protocol)
    content = await ai_service.generate_listing(...)  # Returns instance
    return content  # Returns instance
```

**Confidence Scoring:**
- **High (>85%)**: Quick Approval flow - Big "PUBLISH NOW" button
- **Medium (70-85%)**: Balanced Review flow - Edit interface shown
- **Low (<70%)**: Manual editing required with AI assistance

### 3. Real-time Processing Service
**Purpose:** WebSocket-based status updates during AI processing

```python
class ProcessingNotifier(Protocol):
    async def notify_status_change(
        self,
        product_id: UUID,
        status: ProductStatus,
        progress: Optional[int] = None
    ) -> None:
        ...

    async def notify_completion(
        self,
        product_id: UUID,
        result: GeneratedContent
    ) -> None:
        ...
```

### 4. MercadoLibre Integration Service
**Purpose:** Publishing and category management

```python
class MLPublisher(Protocol):
    async def publish_listing(
        self,
        content: GeneratedContent,
        credentials: MLCredentials
    ) -> PublishedListing:
        ...

    async def suggest_categories(
        self,
        title: str,
        description: str
    ) -> List[MLCategory]:
        ...
```

---

## Performance Architecture

### Mobile-First Performance Targets
```yaml
Critical Metrics:
  - App Load Time: <3 seconds on 3G
  - Photo Upload: <5 seconds for 8 photos (50MB total)
  - AI Processing: 10-15 seconds typical, 30 seconds max
  - UI Responsiveness: <100ms for all interactions
  - End-to-End Flow: <60 seconds photo to published

Optimization Strategies:
  - Image Compression: Client-side before upload
  - Progressive Loading: Show UI while processing
  - Optimistic Updates: Immediate UI feedback
  - CDN Integration: Fast image delivery
  - Connection Pooling: Efficient API calls
```

### Concurrency & Scaling
```python
# Async processing with FastAPI background tasks
@router.post("/products/{product_id}/generate")
async def generate_content(
    product_id: UUID,
    background_tasks: BackgroundTasks,
    ai_service: AIContentGenerator = Depends()
):
    background_tasks.add_task(
        process_product_content,
        product_id,
        ai_service
    )
    return {"status": "processing_started"}

# Real-time updates via WebSocket
@app.websocket("/ws/products/{product_id}")
async def product_updates(websocket: WebSocket, product_id: UUID):
    # Stream processing updates
```

---

## Security Architecture

### Authentication & Authorization
```yaml
Strategy: JWT-based with refresh tokens
  - Access Token: 15 minutes expiry
  - Refresh Token: 7 days expiry
  - Secure HTTP-only cookies for web
  - Encrypted storage for mobile

API Security:
  - HTTPS only (TLS 1.3)
  - CORS properly configured
  - Rate limiting per user/IP
  - Input validation on all endpoints

Data Security:
  - Passwords: bcrypt hashing
  - ML Credentials: AES-256 encryption at rest
  - Images: Signed URLs with expiration
  - Database: Connection encryption
```

### Privacy & Data Handling
```yaml
User Data:
  - Images: User-owned, deletable on demand
  - Generated Content: User-owned, exportable
  - ML Credentials: Encrypted, never logged

Compliance Ready:
  - Data export functionality
  - Data deletion on user request
  - Audit logging for sensitive operations
```

---

## Error Handling & Resilience

### Retry & Fallback Strategy
```python
# Fallback service - also duck-type compatible with AIContentGenerator
class AIServiceWithFallback:
    def __init__(self, primary: AIContentGenerator, secondary: AIContentGenerator):
        # Accept interfaces (Protocols)
        self.primary = primary
        self.secondary = secondary

    # Duck-type compatible with AIContentGenerator Protocol
    async def generate_listing(self, images: List[ImageData], prompt: str) -> GeneratedContent:
        try:
            # Call interface, get instance
            return await self.primary.generate_listing(images, prompt)
        except AIServiceError:
            logger.warning("Primary AI service failed, trying secondary")
            # Call interface, get instance
            return await self.secondary.generate_listing(images, prompt)
        except Exception:
            logger.error("All AI services failed, falling back to manual editing")
            raise AIGenerationFailedError("Manual editing required")

# Business logic doesn't know or care about concrete implementations
# Only works with Protocol interfaces, gets back concrete instances
async def process_product(product_id: UUID, ai_service: AIContentGenerator):
    # Accept interface, return instance pattern
    content = await ai_service.generate_listing(...)  # Returns GeneratedContent instance
    return content
```

### Network Resilience (Mobile-Critical)
```yaml
Upload Resilience:
  - Chunked upload for large images
  - Resume capability on connection loss
  - Offline queue with sync on reconnect

Processing Resilience:
  - Timeout handling (30s max for AI)
  - Progress preservation during errors
  - Clear user feedback with retry options

UI Resilience:
  - Optimistic updates with rollback
  - Loading states for all async operations
  - Graceful degradation when services unavailable
```

---

## Development & Quality Architecture

### Code Quality Gates
```yaml
Backend (Python):
  - Linting: Ruff (replaces Black, isort, flake8)
  - Type Checking: Pyright
  - Architecture: Tach (boundary validation)
  - Testing: pytest with coverage >90%

Frontend (TypeScript):
  - Linting: ESLint + Prettier
  - Type Checking: TypeScript strict mode
  - Architecture: dependency-cruiser
  - Testing: Jest + Testing Library

CI/CD Pipeline:
  1. Code Quality: Linting, type checking, security scan (Bandit)
  2. Testing: Unit, integration, API tests with consistent environment config
  3. Build: Docker images for both services
  4. Deploy: Automated to staging, manual to production

Environment Configuration:
  - Port standardization: Backend internal port 8000, Docker exposes on 8080
  - Frontend API URL configured via VITE_API_BASE_URL environment variable
  - CI/CD uses .env.testing for consistent test environment setup
```

### Testing Strategy
```python
# Test structure
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Test containers (PostgreSQL, MinIO, Redis)
├── api/           # FastAPI TestClient full request/response
└── e2e/           # Playwright critical user journeys

# Example integration test with containers
@pytest.fixture
def test_environment():
    with TestContainerPostgreSQL() as db, \
         TestContainerMinIO() as storage, \
         MockAIService() as ai:
        yield TestEnvironment(db, storage, ai)
```

---

## Final Architecture Decisions ✅

### 1. AI Provider Strategy - **CONFIRMED**
**Decision:** Gemini 2.5 Flash as primary provider
- **Cost:** ~$0.02 per listing (optimal for MVP budget)
- **Performance:** 5-10 seconds processing (meets <15s target)
- **Capabilities:** Best-in-class 2025 multimodal vision + text generation

### 2. Image Processing - **CONFIRMED**
**Decision:** PhotoRoom API for background removal + optimization
- **Cost:** $0.02 per image (~$0.06-0.08 per listing)
- **Performance:** 350ms API response (meets <5s upload target)
- **Mobile optimized:** WebP/AVIF support, CDN integration

### 3. Database & Deployment - **CONFIRMED**
**Decision:** Full Docker Compose stack (PostgreSQL + MinIO + FastAPI + Svelte)
- **Simplicity:** Single docker-compose.yml for all environments
- **Cost:** ~$0.05-0.07 per listing in infrastructure
- **Development:** Consistent environment across team

### 4. Mobile Strategy - **CONFIRMED**
**Decision:** Web responsive → PWA if camera UX works well
- **MVP:** Start with mobile-optimized web app
- **Evolution:** PWA features if needed, native wrapper as fallback

### 5. **Total Cost per Listing: ~$0.13-0.17**
**Monthly MVP Cost: ~$150 for 1000 listings**

---

**✅ Architecture Overview Approved - Ready for Database Schema Design**
