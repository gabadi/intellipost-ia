# IntelliPost AI - Technology Stack

## Document Information
- **Project:** IntelliPost AI MVP
- **Last Updated:** June 22, 2025
- **Scope:** Technical Stack Decisions & Rationale
- **Reference:** PRD Section 8.2 & System Overview Architecture

---

## Stack Overview

IntelliPost AI uses a **mobile-first, AI-powered monorepo** architecture designed for rapid development, high performance, and seamless AI integration.

### Core Architecture Pattern
**Hexagonal Architecture (Ports & Adapters)** with modular monolith structure for MVP scalability.

---

## Backend Technology Stack

### Core Framework
```yaml
Language: Python 3.11+
Framework: FastAPI
Rationale:
  - High performance async/await support
  - Automatic OpenAPI documentation
  - Excellent ecosystem for AI/ML integration
  - Native support for type hints (Pyright compatible)
  - "Agent Coding First" friendly syntax
```

### Database & Storage
```yaml
Primary Database: PostgreSQL 15+
  Purpose: Structured data (users, products, content metadata)
  Features: JSONB for flexible metadata, ACID compliance
  Performance: Connection pooling, query optimization

Object Storage: S3-Compatible (MinIO for development)
  Purpose: Image storage (original and processed)
  Features: CDN integration, signed URLs, lifecycle policies
  Rationale: Scalable, cost-effective, mobile-optimized delivery
```

### AI & External Services
```yaml
Primary AI Provider: Google Gemini 2.5 Flash
  Purpose: Multimodal content generation
  Cost: ~$0.02 per listing (optimal for MVP)
  Performance: 5-10 seconds processing time

Image Processing: PhotoRoom API
  Purpose: Professional background removal
  Cost: ~$0.02 per image processed
  Performance: 350ms API response time

MercadoLibre Integration: Official ML API
  Purpose: Category detection, listing publication
  Features: OAuth 2.0, rate limiting, error handling
```

### Development Tools
```yaml
Package Management: UV (Python dependency management)
Linting & Formatting: Ruff (replaces Black, isort, flake8)
Type Checking: Pyright
Architecture Validation: Tach (boundary enforcement)
Testing Framework: pytest with coverage >80%
HTTP Mocking: httpx-mock + respx for external API testing
```

---

## Frontend Technology Stack

### Core Framework
```yaml
Framework: SvelteKit
Rationale:
  - Lightweight bundle size (mobile-first)
  - Excellent performance characteristics
  - TypeScript support out of the box
  - SSR capability for future SEO needs
  - Developer experience optimized for rapid iteration
```

### State Management
```yaml
Global State: Svelte Stores
  Purpose: Authentication, products, UI state
  Pattern: Reactive stores with TypeScript interfaces

Real-time Updates: WebSocket integration
  Purpose: AI processing status, cross-device sync
  Implementation: Native WebSocket with reconnection logic

Local State: Component-level reactive variables
  Purpose: UI interactions, form validation
```

### Development Tools
```yaml
Type Safety: TypeScript (strict mode)
Linting: ESLint + Prettier
Build Tool: Vite (SvelteKit default)
Architecture: dependency-cruiser (module boundaries)
Testing: Jest + Testing Library + Playwright (E2E)
```

### Mobile Optimization
```yaml
Progressive Web App (PWA): Service Worker support
Touch Optimization: 44px minimum touch targets
Performance: <100KB gzipped bundles
Image Handling: Client-side compression with Sharp.js
Offline Support: Basic offline resilience for critical flows
```

---

## Infrastructure & DevOps Stack

### Development Environment
```yaml
Container Platform: Docker + Docker Compose
  Purpose: Consistent development environment
  Services: PostgreSQL, MinIO, FastAPI, SvelteKit

Repository Structure: Monorepo
  Benefits: Atomic commits, unified tooling, simplified CI/CD

Package Management:
  - Backend: UV for Python dependencies
  - Frontend: npm for Node.js dependencies
```

### Quality Assurance
```yaml
CI/CD Platform: GitHub Actions (configurable)
Quality Gates:
  - ✅ Ruff linting (Python)
  - ✅ Pyright type checking (Python)
  - ✅ ESLint + Prettier (TypeScript/Svelte)
  - ✅ Tach architecture boundaries (Python)
  - ✅ dependency-cruiser (Frontend)
  - ✅ pytest with 80%+ coverage
  - ✅ Security scanning

Pre-commit Hooks: Automated quality checks before commit
```

### Production Infrastructure
```yaml
Deployment Strategy: Docker containers
Database: Managed PostgreSQL (cloud provider)
Object Storage: S3 or compatible service
CDN: CloudFlare or equivalent for image delivery
Monitoring: Application and infrastructure monitoring
SSL/TLS: Automatic certificate management
```

---

## AI & External Integration Stack

### AI Service Architecture
```yaml
Primary: Google Gemini 2.5 Flash
  - Multimodal image + text processing
  - MercadoLibre-optimized content generation
  - Confidence scoring and quality assessment

Secondary: Anthropic Claude 3 (fallback)
  - Backup for content generation
  - Alternative for specific use cases

Image Processing: PhotoRoom API
  - Professional background removal
  - Quality enhancement and optimization
  - Mobile-optimized output formats
```

### Integration Patterns
```yaml
Hexagonal Architecture Implementation:
  - Protocols define client interfaces (Ports)
  - Services implement duck-type compatibility (Adapters)
  - No explicit adapter classes needed
  - Easy provider switching and testing

Error Handling:
  - Automatic retry with exponential backoff
  - Graceful degradation for service failures
  - Circuit breaker pattern for unreliable services
```

---

## Performance & Scalability Stack

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
```yaml
Backend:
  - FastAPI async/await for non-blocking operations
  - Background tasks for AI processing
  - WebSocket for real-time updates
  - Database connection pooling

Frontend:
  - Lazy loading for non-critical components
  - Image optimization and WebP conversion
  - Service worker for offline capabilities
  - Efficient state management with Svelte stores
```

---

## Security Stack

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
```

### Data Security
```yaml
Encryption:
  - Passwords: bcrypt hashing
  - ML Credentials: AES-256 encryption at rest
  - Database: Connection encryption (TLS)
  - File Storage: Encryption at rest and in transit

Privacy:
  - Images: User-owned, deletable on demand
  - Generated Content: User-owned, exportable
  - ML Credentials: Encrypted, never logged
  - Audit logging for sensitive operations
```

---

## Development Workflow Stack

### Code Quality
```yaml
Testing Strategy: Test-Driven Development (TDD)
  - Unit tests: Domain logic isolation
  - Integration tests: External service mocking
  - API tests: Full request/response testing
  - E2E tests: Critical user journeys

Documentation:
  - Self-documenting code prioritized
  - API documentation auto-generated (FastAPI)
  - Architecture documentation in Markdown
  - Minimal but necessary comments
```

### Team Collaboration
```yaml
Version Control: Git with conventional commits
Branch Strategy: Feature branches with PR reviews
Code Review: Automated + manual quality gates
Communication: English for all technical documentation

Agent Coding Support:
  - Consistent patterns for LLM comprehension
  - Complete type annotations for inference
  - Modular architecture for independent testing
  - Clear separation of concerns
```

---

## Cost & Resource Management

### MVP Cost Structure
```yaml
AI Services: ~$0.04 per listing
  - Gemini 2.5 Flash: ~$0.02
  - PhotoRoom API: ~$0.02

Infrastructure: ~$0.03-0.05 per listing
  - Database operations
  - Object storage
  - CDN delivery
  - Computing resources

Total: ~$0.13-0.17 per listing
Monthly MVP Target: ~$150 for 1000 listings
```

### Resource Optimization
```yaml
Development:
  - Local development with Docker Compose
  - Efficient CI/CD pipelines
  - Automated testing to prevent regressions

Production:
  - Auto-scaling based on demand
  - Efficient resource utilization
  - Cost monitoring and optimization
```

---

## Technology Decision Rationale

### Key Trade-offs Made
1. **Python + FastAPI:** AI ecosystem access vs. raw performance
2. **SvelteKit:** Modern DX vs. larger ecosystem (React/Vue)
3. **Monorepo:** Development simplicity vs. deployment complexity
4. **PostgreSQL:** SQL reliability vs. NoSQL flexibility
5. **Docker:** Consistency vs. native performance

### Future Evolution Path
- **Microservices:** When team size and complexity justify splitting
- **Native Mobile:** If PWA limitations become significant
- **Multi-cloud:** For redundancy and cost optimization
- **Advanced AI:** As models and capabilities improve

---

**Stack Validation:** All technology choices align with PRD requirements for mobile-first, AI-powered, rapid development with high quality standards.
