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
├── tests/                         # System-level integration and e2e tests only (module tests are co-located)
├── docs/                          # Project documentation
├── docker-compose.yml             # Local development environment
├── pyproject.toml                 # Python project configuration
├── package.json                   # Monorepo scripts & dependencies
├── README.md                      # Project overview
└── CLAUDE.md                      # Agent instructions
```

---

## Backend Structure (Python/FastAPI)

### Hexagonal Architecture with Independent Modules

**Architecture Pattern**: Each module implements Hexagonal Architecture (Ports & Adapters) while maintaining complete independence from other modules through Protocol-based communication.

**Key Principles**:
- **Hexagonal per Module**: Each module has domain/application/infrastructure/api layers
- **Protocol-Based Communication**: Zero cross-module imports, communication via Protocol interfaces
- **Module Independence**: Each module can be developed, tested, and deployed independently
- **Static Duck Typing**: Pyright validates Protocol compliance at compile-time

```
backend/
├── __init__.py
├── main.py                        # FastAPI application entry point
├── infrastructure/                # Shared infrastructure (database, config, health)
│   ├── __init__.py
│   ├── database.py                # SQLAlchemy setup & session management
│   ├── config/                    # Settings, logging, dependencies
│   │   ├── __init__.py
│   │   └── settings.py
│   └── health/                    # Health checking
│       ├── __init__.py
│       └── health_check.py
├── modules/                       # Independent feature modules
│   ├── user_management/           # User + Auth + ML credentials (unified)
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── entities/          # User, UserProfile, UserAuth entities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py        # Core User entity
│   │   │   │   ├── user_profile.py
│   │   │   │   └── user_auth.py
│   │   │   ├── services/          # Pure business logic (authentication.py, user_registration.py)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── authentication.py  # No "service" suffix
│   │   │   │   └── user_registration.py
│   │   │   └── ports/             # Protocols (client-side interface definitions)
│   │   │       ├── __init__.py
│   │   │       ├── user_repository_protocol.py
│   │   │       ├── password_service_protocol.py
│   │   │       └── jwt_service_protocol.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── use_cases/         # Orchestration only (NO services/ folder)
│   │   │       ├── __init__.py
│   │   │       ├── register_user.py
│   │   │       ├── authenticate_user.py
│   │   │       └── refresh_token.py
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── repositories/      # Protocol implementations (SQLAlchemy, etc.)
│   │   │   │   ├── __init__.py
│   │   │   │   └── sqlalchemy_user_repository.py
│   │   │   ├── services/          # External service adapters (HTTP clients, etc.)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── bcrypt_password_service.py
│   │   │   │   └── jose_jwt_service.py
│   │   │   └── models/            # External resource models (SQLAlchemy, etc.)
│   │   │       ├── __init__.py
│   │   │       └── user_model.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routers/           # HTTP endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth_router.py
│   │   │   │   └── user_router.py
│   │   │   └── schemas/           # Request/Response DTOs
│   │   │       ├── __init__.py
│   │   │       ├── auth_schemas.py
│   │   │       └── user_schemas.py
│   │   └── tests/                 # Tests INSIDE module (not global /tests/)
│   │       ├── __init__.py
│   │       ├── test_entities.py   # Unit tests for domain entities
│   │       ├── test_use_cases.py  # Unit tests for application use cases
│   │       └── test_integration.py # Integration tests with real infrastructure
│   ├── product_management/        # Core product domain
│   │   ├── [same structure as user_management]
│   │   └── # Entities: Product, ProductCore, ProductStatus, ProductBusinessRules
│   ├── content_generation/        # AI content creation
│   │   ├── [same structure as user_management]
│   │   └── # Entities: GeneratedContent, ConfidenceScore, AIGeneration, ContentVersion
│   ├── image_processing/          # Image handling
│   │   ├── [same structure as user_management]
│   │   └── # Entities: ProductImage, ImageData, ProcessedImage, ImageProcessingMetadata
│   ├── marketplace_integration/   # External marketplace publishing
│   │   ├── [same structure as user_management]
│   │   └── # Entities: MLCredentials, MLListing, MLCategory, MLAttributes, MLSaleTerms
│   └── notifications/             # User communications
│       ├── [same structure as user_management]
│       └── # Entities: Notification, EmailNotification, NotificationPreferences
├── application/                   # Global orchestration (cross-module use cases)
│   ├── __init__.py
│   ├── orchestration/             # Cross-module workflows
│   │   ├── __init__.py
│   │   ├── product_creation_orchestrator.py  # Coordinates user_management + product_management
│   │   └── publishing_orchestrator.py        # Coordinates multiple modules for publishing
│   └── dependencies.py           # Global dependency injection setup
└── api/                           # Global HTTP interface layer
    ├── __init__.py
    ├── main.py                    # API router setup & module router aggregation
    ├── dependencies.py            # Global FastAPI dependencies & DI setup
    ├── middleware.py              # Global middleware (CORS, auth, etc.)
    ├── routers/                   # Global API route aggregation
    │   ├── __init__.py
    │   └── router_aggregator.py   # Combines all module routers
    ├── schemas/                   # Global API schemas
    │   ├── __init__.py
    │   ├── common.py              # Shared response schemas
    │   └── error.py               # Global error response schemas
    └── websocket/                 # Global WebSocket handlers
        ├── __init__.py
        └── connection_manager.py  # Cross-module real-time updates
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

### Backend Test Organization

**Module Tests (Co-located)**: Each module contains its own tests in `modules/{module}/tests/`
```
modules/user_management/tests/
├── __init__.py
├── conftest.py                    # Module-specific fixtures
├── test_user_entity.py            # Domain entity tests (fast, isolated)
├── test_authentication.py         # Domain service tests
├── test_use_cases.py              # Application layer tests (mock external services)
├── test_repositories.py           # Infrastructure tests with test containers
└── test_integration.py            # Module integration tests
```

**System Tests (Global)**: Cross-module integration and end-to-end tests
```
tests/
├── __init__.py
├── conftest.py                    # Global pytest configuration & fixtures
├── integration/                   # Cross-module integration tests
│   ├── test_cross_module_workflows.py  # Multi-module workflows
│   ├── test_database_integration.py    # Full database integration
│   └── test_external_services.py       # Third-party service integration
├── api/                          # Full API endpoint tests
│   ├── test_api_integration.py    # Cross-module API flows
│   └── test_websocket.py          # Real-time communication tests
└── e2e/                          # End-to-end user journeys
    ├── test_product_creation_flow.py   # Complete product creation workflow
    └── test_publishing_workflow.py     # Full publishing process
```

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

## Project Module Organization

### Current Module Structure

**6 Independent Modules:**
- **user_management**: User + Auth + ML credentials (unified bounded context)
- **product_management**: Core product domain
- **content_generation**: AI content creation
- **image_processing**: Image handling
- **marketplace_integration**: External marketplace publishing
- **notifications**: User communications

### Module Responsibilities

#### user_management (Unified Module)
**Entities**: User, UserProfile, UserAuth, UserMLIntegration, UserStatus
**Rationale**: Auth without User makes no sense - same bounded context
**Responsibilities**: User account lifecycle, authentication, MercadoLibre OAuth integration

#### product_management
**Entities**: Product, ProductCore, ProductStatus, ProductBusinessRules
**Responsibilities**: Product creation, lifecycle management, business rule validation

#### content_generation
**Entities**: GeneratedContent, ConfidenceScore, AIGeneration, ContentVersion
**Responsibilities**: AI-powered content creation, confidence scoring, content versioning

#### image_processing
**Entities**: ProductImage, ImageData, ProcessedImage, ImageProcessingMetadata
**Responsibilities**: Image upload, transformation, optimization, metadata extraction

#### marketplace_integration
**Entities**: MLCredentials, MLListing, MLCategory, MLAttributes, MLSaleTerms
**Responsibilities**: External marketplace publishing, credential management, listing synchronization

#### notifications
**Entities**: Notification, EmailNotification, NotificationPreferences
**Responsibilities**: User communication, notification delivery, preference management

### Protocol Placement Guidelines

**Within Each Module:**
```
modules/{module_name}/domain/ports/
├── {entity}_repository_protocol.py     # Data persistence interfaces
├── {external_service}_protocol.py      # External service interfaces
└── {cross_module}_protocol.py          # Cross-module communication interfaces
```

**Protocol Definition Rules:**
- Protocols defined in CONSUMER module's domain/ports/
- Producer modules implement via structural subtyping (no imports)
- Validated statically by Pyright during development
- Cross-module communication ONLY via protocols + dependency injection

### Module Independence Validation

**Zero Cross-Module Dependencies:**
- No imports between modules
- Communication via protocols only
- Each module developable independently
- Pyright validates Protocol compliance automatically

## File Organization Principles

### Module Architecture Enforcement
1. **Domain** → Pure Python, defines Protocol interfaces, no external dependencies
2. **Application** → Use cases only, accepts protocol interfaces via DI
3. **Infrastructure** → External resource implementations (SQLAlchemy, HTTP clients, etc.)
4. **API** → HTTP endpoints + schemas specific to module
5. **Tests** → Inside each module, tests module isolation

### Protocol-Based Communication Pattern
- **Protocols in domain/ports/**: Define what module needs from external dependencies
- **Static compatibility via Pyright**: Compile-time validation, zero runtime overhead
- **NO adapter classes**: Services implement Protocol signatures automatically
- **"Accept interfaces, return instances"**: Modules never depend on concrete implementations
- **Module Independence**: Zero imports between modules, communication via DI only

### Mobile-First Frontend
1. **Components** → Mobile-optimized by default
2. **Routes** → Progressive enhancement for desktop
3. **Stores** → Reactive state for real-time updates
4. **Utils** → Performance-focused helpers

### Quality Standards
1. **Testing** → Co-located within modules for isolation, global tests for cross-module workflows
2. **Configuration** → Centralized at appropriate levels (global/infrastructure, module-specific)
3. **Documentation** → Maintained alongside code changes
4. **Types** → Protocol interfaces for module communication, shared DTOs where applicable
5. **Architecture Compliance** → Tach validates module boundaries, Pyright validates Protocol compliance

---

**Structure Validation:** All directory structures support the hexagonal architecture pattern, mobile-first development, and agent-friendly development workflows defined in the project requirements.
