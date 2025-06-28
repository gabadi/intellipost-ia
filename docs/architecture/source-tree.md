# IntelliPost AI - Source Tree Structure

## Document Information
- **Project:** IntelliPost AI MVP
- **Last Updated:** June 22, 2025
- **Scope:** Codebase Organization & File Structure
- **Reference:** Hexagonal Architecture + Frontend Architecture docs

---

## Project Root Structure

```
intellipost-ia/                    # Root monorepo
├── .bmad-core/                    # Agent workflow configuration
├── .ai/                           # AI development artifacts
├── backend/                       # Python/FastAPI backend
├── frontend/                      # TypeScript/SvelteKit frontend
├── tests/                         # Cross-project tests (unit, integration, performance, e2e)
├── docs/                          # Project documentation
├── docker-compose.yml             # Local development environment
├── pyproject.toml                 # Python project configuration
├── package.json                   # Monorepo scripts & dependencies
├── README.md                      # Project overview
└── CLAUDE.md                      # Agent instructions
```

---

## Backend Structure (Python/FastAPI)

### Hexagonal Architecture Layout
```
backend/
├── __init__.py
├── main.py                        # FastAPI application entry point
├── domain/                        # Core business logic (no external deps)
│   ├── __init__.py
│   ├── entities/                  # Business entities
│   │   ├── __init__.py
│   │   ├── product.py             # Product aggregate root
│   │   ├── user.py                # User entity
│   │   ├── generated_content.py   # AI-generated content entity
│   │   └── confidence.py          # Confidence scoring value objects
│   ├── repositories/              # Repository interfaces (Protocols)
│   │   ├── __init__.py
│   │   ├── product_repository.py  # Product persistence interface
│   │   └── user_repository.py     # User persistence interface
│   ├── services/                  # Domain services (business logic)
│   │   ├── __init__.py
│   │   ├── ai_content_generator.py # AI generation interface
│   │   ├── image_processor.py     # Image processing interface
│   │   └── ml_publisher.py        # MercadoLibre publishing interface
│   └── exceptions.py              # Domain-specific exceptions
├── application/                   # Use cases & orchestration
│   ├── __init__.py
│   ├── use_cases/                 # Application use cases
│   │   ├── __init__.py
│   │   ├── create_product.py      # Product creation workflow
│   │   ├── generate_content.py    # AI content generation workflow
│   │   ├── process_images.py      # Image processing workflow
│   │   └── publish_listing.py     # MercadoLibre publishing workflow
│   ├── dto/                       # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── product_dto.py         # Product-related DTOs
│   │   └── content_dto.py         # Content-related DTOs
│   └── services/                  # Application services
│       ├── __init__.py
│       └── product_service.py     # Product orchestration service
├── infrastructure/                # External concerns (duck-type compatible services)
│   ├── __init__.py
│   ├── database/                  # Database implementations
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── repositories/          # Repository duck-type implementations
│   │   │   ├── __init__.py
│   │   │   ├── product_repository_impl.py  # Duck-type compatible with domain Protocol
│   │   │   └── user_repository_impl.py     # Duck-type compatible with domain Protocol
│   │   └── migrations/            # Database migrations
│   ├── ai_services/               # AI service implementations (NO explicit adapters)
│   │   ├── __init__.py
│   │   ├── gemini_service.py      # Statically compatible with AIContentGenerator Protocol
│   │   ├── claude_service.py      # Statically compatible with AIContentGenerator Protocol
│   │   └── photoroom_service.py   # Statically compatible with ImageProcessor Protocol
│   ├── storage/                   # Object storage implementations
│   │   ├── __init__.py
│   │   ├── s3_storage.py          # S3-compatible storage
│   │   └── local_storage.py       # Local development storage
│   ├── ml_api/                    # MercadoLibre API integration
│   │   ├── __init__.py
│   │   ├── ml_client.py           # ML API client
│   │   └── ml_publisher_impl.py   # ML publishing implementation
│   └── config/                    # Configuration management
│       ├── __init__.py
│       ├── settings.py            # Application settings
│       └── database.py            # Database configuration
└── api/                           # HTTP interface layer
    ├── __init__.py
    ├── main.py                    # API router setup
    ├── dependencies.py            # FastAPI dependencies
    ├── middleware.py              # Custom middleware
    ├── routers/                   # API route handlers
    │   ├── __init__.py
    │   ├── auth.py                # Authentication endpoints
    │   ├── products.py            # Product management endpoints
    │   ├── images.py              # Image upload/management endpoints
    │   └── ml_credentials.py      # MercadoLibre credential endpoints
    ├── schemas/                   # Pydantic request/response models
    │   ├── __init__.py
    │   ├── auth.py                # Auth-related schemas
    │   ├── product.py             # Product-related schemas
    │   └── error.py               # Error response schemas
    └── websocket/                 # WebSocket handlers
        ├── __init__.py
        └── product_updates.py     # Real-time product updates
```

### Backend File Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

---

## Frontend Structure (SvelteKit)

### Mobile-First Architecture
```
frontend/
├── package.json                   # Frontend dependencies
├── svelte.config.js               # SvelteKit configuration
├── vite.config.js                 # Vite build configuration
├── tsconfig.json                  # TypeScript configuration
├── src/
│   ├── app.html                   # HTML shell with PWA meta
│   ├── app.css                    # Global styles
│   ├── routes/                    # File-based routing
│   │   ├── +layout.svelte         # Global layout with navigation
│   │   ├── +layout.ts             # Global layout data loading
│   │   ├── +page.svelte           # Dashboard (product list)
│   │   ├── auth/                  # Authentication flows
│   │   │   ├── login/
│   │   │   │   └── +page.svelte   # Login page
│   │   │   └── register/
│   │   │       └── +page.svelte   # Registration page
│   │   ├── products/              # Product management
│   │   │   ├── +layout.svelte     # Product-specific layout
│   │   │   ├── new/
│   │   │   │   └── +page.svelte   # Photo + Prompt input
│   │   │   ├── [id]/
│   │   │   │   ├── +page.svelte   # Product detail view
│   │   │   │   ├── +page.ts       # Product data loading
│   │   │   │   ├── review/
│   │   │   │   │   └── +page.svelte # Balanced Review flow
│   │   │   │   └── edit/
│   │   │   │       └── +page.svelte # Edit interface
│   │   │   └── +page.svelte       # Product list
│   │   ├── ml-setup/
│   │   │   └── +page.svelte       # MercadoLibre OAuth setup
│   │   └── api/                   # API routes (if needed)
│   ├── lib/                       # Reusable components & utilities
│   │   ├── components/            # UI components
│   │   │   ├── core/              # Core mobile components
│   │   │   │   ├── MobileNavigation.svelte
│   │   │   │   ├── LoadingSpinner.svelte
│   │   │   │   └── ActionButton.svelte
│   │   │   ├── product/           # Product-specific components
│   │   │   │   ├── PhotoCollectionComponent.svelte
│   │   │   │   ├── PromptInputComponent.svelte
│   │   │   │   ├── ProcessingSpinner.svelte
│   │   │   │   ├── GeneratedListingPreview.svelte
│   │   │   │   └── ConfidenceIndicator.svelte
│   │   │   ├── ui/                # Generic UI components
│   │   │   │   ├── Button.svelte
│   │   │   │   ├── Input.svelte
│   │   │   │   ├── Modal.svelte
│   │   │   │   └── Card.svelte
│   │   │   └── forms/             # Form components
│   │   │       ├── FormField.svelte
│   │   │       ├── ImageUpload.svelte
│   │   │       └── ValidationMessage.svelte
│   │   ├── stores/                # Svelte stores for state
│   │   │   ├── auth.ts            # Authentication state
│   │   │   ├── products.ts        # Product management
│   │   │   ├── realtime.ts        # WebSocket management
│   │   │   └── ui.ts              # UI state (loading, errors)
│   │   ├── api/                   # API client functions
│   │   │   ├── client.ts          # Base API client
│   │   │   ├── auth.ts            # Authentication API calls
│   │   │   ├── products.ts        # Product API calls
│   │   │   └── ml.ts              # MercadoLibre API calls
│   │   ├── utils/                 # Helper functions
│   │   │   ├── image.ts           # Image compression/processing
│   │   │   ├── validation.ts      # Form validation
│   │   │   ├── formatting.ts      # Data formatting
│   │   │   └── websocket.ts       # WebSocket utilities
│   │   └── types/                 # TypeScript definitions
│   │       ├── api.ts             # API response types
│   │       ├── product.ts         # Product entity types
│   │       ├── ui.ts              # UI component types
│   │       └── websocket.ts       # WebSocket message types
│   ├── static/                    # Static assets
│   │   ├── favicon.ico
│   │   ├── app-icons/             # PWA icons
│   │   └── images/                # Static images
│   └── service-worker.js          # PWA service worker (future)
├── tests/                         # Frontend tests
│   ├── unit/                      # Component unit tests
│   ├── integration/               # Store integration tests
│   └── e2e/                       # Playwright E2E tests
└── playwright.config.ts          # E2E test configuration
```

### Frontend File Naming Conventions
- **Components:** `PascalCase.svelte`
- **Pages:** `+page.svelte`, `+layout.svelte`
- **TypeScript:** `camelCase.ts`
- **CSS:** `kebab-case.css`
- **Assets:** `kebab-case.ext`

---

## Documentation Structure

```
docs/
├── README.md                      # Project overview
├── prd.md                         # Product Requirements Document
├── project-brief.md               # Initial project brief
├── architecture/                  # Architecture documentation
│   ├── system-overview.md         # High-level system design
│   ├── frontend-architecture.md   # Frontend-specific architecture
│   ├── database-schema.md         # Database design
│   ├── api-specification.md       # API documentation
│   ├── deployment-strategy.md     # Deployment guidelines
│   ├── external-integrations.md   # Third-party integrations
│   ├── coding-standards.md        # Development standards
│   ├── tech-stack.md             # Technology decisions
│   └── source-tree.md            # This document
├── front-end-spec/               # UI/UX specifications
│   ├── index.md                  # Overview
│   ├── user-flows.md             # User journey documentation
│   ├── wireframes-mockups.md     # Visual design specs
│   ├── component-library-design-system.md
│   ├── responsiveness-strategy.md
│   ├── accessibility-requirements.md
│   └── performance-considerations.md
├── epics/                        # Epic progress tracking
├── stories/                      # User story details
├── handoff/                      # Team handoff documentation
└── reports/                      # Research and analysis
    ├── competitors/              # Competitive analysis
    ├── image_processing/         # AI service research
    └── publishing/               # MercadoLibre best practices
```

---

## Test Structure

### Backend Tests
```
tests/
├── __init__.py
├── conftest.py                    # pytest configuration & fixtures
├── modules/                       # Unit tests organized by backend module
│   ├── auth/
│   │   ├── test_jwt_service.py    # JWT token generation and validation (future)
│   │   ├── test_password_service.py  # Password hashing and verification (future)
│   │   └── test_authentication_service.py  # Authentication business logic (future)
│   ├── user/
│   │   ├── test_user.py           # User domain entity tests
│   │   ├── test_user_auth.py      # User authentication integration
│   │   ├── test_user_profile.py   # User profile management
│   │   └── test_user_status.py    # User status management
│   ├── product/
│   │   ├── test_product.py        # Product domain entity tests
│   │   ├── test_confidence_score.py  # Confidence scoring logic
│   │   └── test_product_business_rules.py  # Product validation rules
│   └── shared/
│       ├── test_health.py         # Health check functionality
│       └── infrastructure/
│           └── config/
│               ├── test_settings.py      # Application configuration
│               ├── test_dependencies.py  # Dependency injection
│               └── test_logging.py       # Logging configuration
├── integration/                   # Module interaction and API endpoint tests
│   └── api/
│       ├── test_auth_flow.py      # Authentication API integration workflows
│       └── test_health.py         # Health check and status endpoints
├── performance/                   # Non-functional requirements testing (manual execution)
│   ├── README.md                  # Performance testing guide and documentation
│   ├── test_auth_timing.py        # Authentication endpoint performance tests
│   └── test_api_performance.py   # General API performance tests (future)
└── e2e/                          # End-to-end user journeys (KISS: critical paths only)
    ├── test_user_registration_flow.py  # Complete user registration workflow
    └── test_authentication_flow.py     # Complete authentication user journey
```

### Testing Category Guidelines

**Unit Tests**: Isolated component logic testing by module
- Focus: Individual module functionality and business logic
- Structure: Organized by backend module hierarchy (auth, user, shared)
- Mocking: Minimal, only for external dependencies
- Speed: Fast execution for CI/CD

**Integration Tests**: Module interaction and API endpoint testing
- Focus: Module integration and complete API workflows
- Structure: Organized by module interactions and API endpoints
- Mocking: External services only (AI APIs, external APIs)
- Speed: Moderate execution for CI/CD

**Performance Tests**: Non-functional requirements testing
- Focus: Response times, throughput, scalability metrics
- Environment: Production-like conditions with real dependencies
- Execution: Manual only (not included in CI/CD pipelines)

**E2E Tests**: Complete user journey validation
- Focus: Critical user workflows from start to finish
- Environment: Full application stack with mocked external services
- Speed: Slower execution, run before releases

### Frontend Tests
```
frontend/tests/
├── unit/                          # Component unit tests
│   ├── components/
│   │   ├── PhotoCollection.test.ts
│   │   └── PromptInput.test.ts
│   └── utils/
│       └── validation.test.ts
├── integration/                   # Store integration tests
│   ├── products.store.test.ts
│   └── realtime.store.test.ts
└── e2e/                          # Playwright end-to-end tests
    ├── auth.spec.ts               # Authentication flows
    ├── product-creation.spec.ts   # Product creation journey
    └── mobile-workflow.spec.ts    # Mobile-specific workflows
```

---

## Configuration Files

### Root Level Configuration
```
intellipost-ia/
├── .gitignore                     # Git ignore patterns
├── .pre-commit-config.yaml        # Pre-commit hooks
├── .github/                       # GitHub workflows
│   └── workflows/
│       ├── ci.yml                 # Continuous integration
│       └── deploy.yml             # Deployment pipeline
├── docker-compose.yml             # Local development environment
├── docker-compose.prod.yml        # Production configuration
├── pyproject.toml                 # Python project + tool configuration
├── package.json                   # Monorepo scripts + frontend deps
├── uv.lock                        # Python dependency lock file
└── package-lock.json              # Frontend dependency lock file
```

### Tool Configuration Details
```yaml
pyproject.toml:
  - Python dependencies (UV managed)
  - Ruff configuration (linting/formatting)
  - Pyright configuration (type checking)
  - Tach configuration (architecture boundaries)
  - pytest configuration
  - Project metadata

package.json:
  - Monorepo build scripts
  - Frontend dependencies
  - Quality scripts (lint, test, typecheck)
  - Development workflow commands
```

---

## Development Workflow Files

### Agent Support Files
```
.bmad-core/
├── core-config.yml               # Agent configuration
├── tasks/                        # Development tasks
├── templates/                    # Code templates
└── checklists/                   # Quality checklists

.ai/
├── debug-log.md                  # Development debug log
└── core-dump*.md                 # Agent state snapshots
```

### IDE Support
```
.vscode/                          # VS Code configuration
├── settings.json                 # Editor settings
├── extensions.json               # Recommended extensions
└── launch.json                   # Debug configurations

intellipost-ia/
├── CLAUDE.md                     # Agent instructions
└── README.md                     # Developer onboarding
```

---

## File Organization Principles

### Hexagonal Architecture Enforcement (Go-Style)
1. **Domain** → No external dependencies, defines Protocol interfaces
2. **Application** → Depends only on Domain, accepts interfaces, returns instances
3. **Infrastructure** → Duck-type compatible services (NO explicit adapters)
4. **API** → Orchestrates Application use cases

### Go-Style Pattern Implementation (Static Duck-Typing)
- **Protocols in domain/services/**: Define what business logic expects
- **Static compatibility via Pyright**: Compile-time validation, not runtime duck-typing
- **NO adapter classes**: Services implement Protocol signatures by convention
- **"Accept interfaces, return instances"**: Business logic never depends on concrete types
- **SOLID Principles**: Dependency Inversion through Protocol abstractions

### Mobile-First Frontend
1. **Components** → Mobile-optimized by default
2. **Routes** → Progressive enhancement for desktop
3. **Stores** → Reactive state for real-time updates
4. **Utils** → Performance-focused helpers

### Quality Standards
1. **Testing** → Co-located with source code where possible
2. **Configuration** → Centralized at appropriate levels
3. **Documentation** → Maintained alongside code changes
4. **Types** → Shared between frontend and backend where applicable

---

**Structure Validation:** All directory structures support the hexagonal architecture pattern, mobile-first development, and agent-friendly development workflows defined in the project requirements.
