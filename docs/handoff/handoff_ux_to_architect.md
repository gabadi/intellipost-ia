# UX to Architecture Handoff Document
## IntelliPost AI - Technical Architecture Requirements

### Document Information
- **From:** Sally (UX Expert)
- **To:** Fred (Architect)
- **Date:** June 20, 2025
- **Phase:** UX Complete → Architecture Design

---

## Architecture Overview

IntelliPost AI implements a **mobile-complete, desktop-optional** architecture supporting AI-powered MercadoLibre listing generation with cross-platform state synchronization and adaptive user interfaces based on AI confidence scoring.

---

## Core Technical Requirements

### 1. Mobile-First Responsive Architecture

**Breakpoint Strategy:**
- **Mobile:** 320px - 767px (primary target, mobile-complete functionality)
- **Tablet:** 768px - 1023px (mobile interface with enhanced touch targets)
- **Desktop:** 1024px+ (full desktop interface with image management)

**Performance Targets:**
- **Mobile load time:** <3 seconds for review screens
- **Interaction response:** <100ms for all user interactions
- **Image processing feedback:** Real-time progress indicators
- **Auto-save frequency:** Every 30 seconds during editing

### 2. AI Integration Architecture

**Processing Pipeline:**
```
User Input (Images + Prompt) 
    ↓
AI Processing Service
    ↓
Confidence Scoring Engine
    ↓
Content Generation (Title, Category, Attributes, Description)
    ↓
Image Processing (Background removal, Enhancement)
    ↓
State Management & Persistence
```

**Auto-Reprocessing Triggers:**
- **Add Image:** Reprocess all content and images
- **Delete Image:** Reprocess remaining images and update content
- **Edit Prompt:** Reprocess content generation only
- **Timeout:** 2-minute maximum processing time

**Confidence Scoring System:**
- **Overall Confidence:** Weighted average of component scores
- **Component Confidence:** Individual scores for images, title, category, attributes
- **Threshold-Based UI:** >85% (green), 70-85% (yellow), <70% (red)

### 3. State Management Architecture

**Cross-Platform Synchronization:**
- **Real-time sync:** User account-based state persistence
- **Conflict resolution:** Last-write-wins with timestamp validation
- **Offline capability:** Local state with sync on reconnection
- **Session persistence:** 24-hour draft state retention

**State Entities:**
```typescript
interface ProductState {
  id: string;
  userId: string;
  status: 'uploading' | 'processing' | 'ready' | 'publishing' | 'published' | 'failed';
  confidence: {
    overall: number;
    images: number;
    title: number;
    category: number;
    attributes: number;
    description: number;
  };
  inputs: {
    prompt: string;
    originalImages: ImageData[];
  };
  outputs: {
    processedImages: ImageData[];
    mainImage: string;
    title: string;
    category: CategoryData;
    attributes: AttributeData[];
    description: string;
  };
  metadata: {
    createdAt: timestamp;
    updatedAt: timestamp;
    lastProcessedAt: timestamp;
  };
}
```

### 4. Image Management System

**Storage Architecture:**
- **Original Images:** Secure object storage (S3-compatible)
- **Processed Images:** CDN-enabled storage with multiple resolutions
- **Temporary Processing:** Ephemeral storage with automatic cleanup

**Processing Pipeline:**
```
Original Image Upload
    ↓
Validation (format, size, resolution)
    ↓
AI Processing (background removal, enhancement)
    ↓
Multi-resolution generation
    ↓
CDN distribution
    ↓
Database reference storage
```

**CRUD Operations:**
- **Create:** Multi-file upload with progress tracking
- **Read:** Optimized delivery with lazy loading
- **Update:** Main image selection and reordering
- **Delete:** Soft delete with cleanup jobs

### 5. API Architecture Requirements

**Core API Endpoints:**

```
POST /api/products
GET /api/products
GET /api/products/{id}
PUT /api/products/{id}
DELETE /api/products/{id}

POST /api/products/{id}/images
DELETE /api/products/{id}/images/{imageId}
PUT /api/products/{id}/images/reorder

POST /api/products/{id}/process
GET /api/products/{id}/confidence

POST /api/products/{id}/publish
GET /api/products/{id}/preview

GET /api/categories
GET /api/categories/{id}/attributes
```

**Real-time Updates:**
- **WebSocket connection** for processing status
- **Server-sent events** for confidence score updates
- **Push notifications** for cross-platform sync

### 6. External Service Integration

**MercadoLibre API Integration:**
- **Category API:** Real-time category validation and suggestions
- **Publishing API:** Automated listing creation and updates
- **Preview API:** Generate ML listing previews
- **Error Handling:** Robust retry logic with exponential backoff

**AI Service Integration:**
- **Image Processing:** Background removal and enhancement services
- **Content Generation:** LLM integration for title, description, attributes
- **Confidence Scoring:** Machine learning model for quality assessment
- **Rate Limiting:** Intelligent queuing and throttling

### 7. Database Schema Requirements

**Core Tables:**
```sql
-- Users
users (id, email, created_at, updated_at, preferences)

-- Products
products (id, user_id, status, confidence_data, created_at, updated_at)

-- Product Content
product_content (product_id, title, category_id, attributes, description, confidence_scores)

-- Images
images (id, product_id, type, url, metadata, is_main, sort_order)

-- Processing Jobs
processing_jobs (id, product_id, type, status, started_at, completed_at, error_data)

-- ML Integration
ml_listings (id, product_id, ml_listing_id, status, published_at, url)
```

**Indexes and Performance:**
- **User products:** Composite index on (user_id, status, updated_at)
- **Image lookups:** Index on (product_id, type, sort_order)
- **Processing queue:** Index on (status, created_at)

### 8. Security Requirements

**Authentication & Authorization:**
- **JWT-based authentication** with refresh tokens
- **Role-based access control** (user, admin)
- **API rate limiting** per user and endpoint
- **CORS configuration** for web application

**Data Protection:**
- **Encryption at rest** for sensitive data
- **HTTPS enforcement** for all communications
- **Secure file upload** with virus scanning
- **Data retention policies** with automatic cleanup

**MercadoLibre Integration Security:**
- **OAuth 2.0 flow** for ML API access
- **Encrypted credential storage** with key rotation
- **Scope-limited permissions** for ML operations
- **Audit logging** for all ML API interactions

### 9. Error Handling and Resilience

**Error Categories:**
- **User Input Errors:** Validation failures, format issues
- **Processing Errors:** AI service failures, timeout errors
- **Integration Errors:** ML API failures, network issues
- **System Errors:** Database failures, storage issues

**Resilience Patterns:**
- **Circuit breaker** for external service calls
- **Retry with exponential backoff** for transient failures
- **Graceful degradation** when AI services are unavailable
- **Fallback mechanisms** for critical path operations

**User Experience During Errors:**
```
Processing Failure → Clear error message → Retry options → Manual editing fallback
ML API Failure → Cached categories → Manual category selection
Image Processing Failure → Original image use → Processing retry option
```

### 10. Monitoring and Observability

**Performance Metrics:**
- **API response times** by endpoint and user
- **Image processing duration** and success rates
- **AI confidence score distributions** over time
- **User workflow completion rates** by platform

**Business Metrics:**
- **Listing publication success rates**
- **User engagement** by platform (mobile vs desktop)
- **Processing accuracy** via user feedback
- **Cross-platform usage patterns**

**Alerting:**
- **High error rates** in AI processing
- **Performance degradation** alerts
- **External service** availability monitoring
- **Database performance** and capacity alerts

---

## Technical Constraints and Considerations

### Scalability Requirements:
- **Concurrent users:** Support 100+ simultaneous users for MVP
- **Image processing:** Queue-based processing with auto-scaling
- **Database scaling:** Read replicas for query performance
- **CDN usage:** Global image delivery optimization

### Technology Stack Alignment:
- **Backend:** Python with FastAPI (per PRD requirements)
- **Frontend:** Svelte with SvelteKit (per PRD requirements)
- **Database:** PostgreSQL with JSONB for flexible schema
- **Storage:** S3-compatible object storage
- **Cache:** Redis for session and temporary data

### Development Considerations:
- **TDD methodology:** Test-first development approach
- **API-first design:** Well-documented API contracts
- **Component isolation:** Testable, modular architecture
- **Performance testing:** Load testing for critical paths

---

## Implementation Phases

### Phase 1: Core Infrastructure
- User authentication and basic API framework
- Database schema and migration system
- Basic image upload and storage
- Simple AI processing pipeline

### Phase 2: Mobile Interface Implementation
- Three-tier mobile interface development
- Cross-platform state synchronization
- Basic editing capabilities
- Auto-reprocessing implementation

### Phase 3: Desktop Enhancement
- Image management interface
- Advanced editing capabilities
- Before/after comparison tools
- MercadoLibre preview integration

### Phase 4: Optimization and Polish
- Performance optimization
- Advanced error handling
- Monitoring and alerting setup
- User experience refinements

---

## Architecture Validation Points

### Critical Technical Decisions Needed:
1. **Auto-reprocessing feasibility:** Confirm AI service integration approach
2. **Real-time sync implementation:** WebSocket vs polling vs hybrid approach
3. **Image processing pipeline:** In-house vs external service integration
4. **State management complexity:** Client-side state vs server-driven approach

### Integration Validation Required:
- **MercadoLibre API capabilities** and limitations
- **AI service performance** and reliability
- **Image processing services** quality and speed
- **Database performance** under concurrent load

### Security Review Points:
- **File upload security** and virus scanning
- **API security** and rate limiting implementation
- **Cross-platform authentication** token management
- **External service** credential security

---

## Handoff Artifacts

### Available Documentation:
- **Frontend Specification:** `/docs/front-end-spec.md` (comprehensive UI/UX specs)
- **Product Requirements:** `/docs/prd.md` (updated with mobile-complete strategy)
- **UX Research:** `/mobile-ai-content-review-ux-research.md` (user behavior insights)

### Design System Resources:
- **Component specifications** in frontend documentation
- **Interaction patterns** defined with technical requirements
- **Responsive behavior** detailed by breakpoint
- **Accessibility requirements** (WCAG 2.1 AA compliance)

### User Flow Documentation:
- **Mermaid diagrams** for all critical flows
- **Error handling flows** for failure scenarios
- **Cross-platform transition** specifications
- **State management flows** for synchronization

---

*This handoff document provides the technical foundation for implementing the IntelliPost AI architecture, ensuring UX design decisions are properly supported by robust, scalable technical infrastructure.*