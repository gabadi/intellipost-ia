# IntelliPost AI - Coding Standards

## Document Information
- **Project:** IntelliPost AI MVP
- **Last Updated:** 2025-01-26
- **Scope:** LLM-Optimized Development Standards
- **Reference:** PRD Section 8.3 - Agent Coding First Principles

---

## Core Development Principles

### Agent Coding First Philosophy
- **Self-Documenting Code:** Clean Code principles - code should be autoexplicative
- **Minimal Comments:** Use comments sparingly, only when code cannot express intent
- **English Only:** All comments and documentation must be in English
- **Explicit Typing:** All functions and classes must have complete type annotations
- **Consistent Structure:** Follow established patterns for LLM comprehension
- **Modular Design:** Components must be independently testable and replaceable
- **Tell Don't Ask:** Objects should encapsulate behavior and make decisions internally

### Core Development Principles (SOLID + KISS + DRY + YAGNI + Tell Don't Ask)
- **SOLID Principles:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **KISS (Keep It Simple, Stupid):** Simplest solution that works
- **DRY (Don't Repeat Yourself):** Eliminate code duplication
- **YAGNI (You Aren't Gonna Need It):** Don't implement until needed
- **Tell Don't Ask:** Objects should do work rather than expose state for external manipulation
- **Applied to:** Code, tests, documentation, architecture decisions

---

## Python Backend Standards

### Code Style & Formatting
```yaml
Linter: Ruff (replaces Black, isort, flake8)
Type Checker: Pyright
Line Length: 88 characters
Import Style: Absolute imports preferred
Docstring Style: Google format for public APIs only
```

### Type Safety Requirements

**Pyright Configuration: STRICT Mode**
```toml
typeCheckingMode = "strict"
```

**Architectural Decision:** We use pyright in `strict` mode to enforce the highest level of type safety from the start. This ensures:
- All functions require complete type annotations
- No unused imports or variables survive
- Optional access is properly handled
- Runtime type errors are caught at development time

**Impact:** Code generation and development must meet strict typing standards from day one. This prevents technical debt accumulation and ensures consistent code quality.

**Code Standards:**
```python
# ✅ Required: Complete type annotations
async def generate_listing(
    images: List[ImageData],
    prompt: str,
    ml_category_hint: Optional[str] = None
) -> GeneratedContent:
    """Generate MercadoLibre listing content from images and prompt."""
    pass

# ❌ Forbidden: Missing types
def process_data(input_data):
    return result

# ❌ Forbidden: Unused imports (strict mode catches these)
import unused_module  # Will fail type checking

# ❌ Forbidden: Unused variables (strict mode catches these)
def process_data(data: str) -> str:
    unused_var = "temporary"  # Will fail type checking
    return data.upper()
```

### Hexagonal Architecture Patterns (Go-Style + Static Duck-Typing)

**Core Principle:** "Accept interfaces, return instances" - NO explicit adapters
**Type Safety:** Static duck-typing via Pyright (NOT runtime duck-typing)

```python
class AIContentGenerator(Protocol):
    async def generate_listing(
        self,
        images: List[ImageData],
        prompt: str,
        ml_category_hint: Optional[str] = None
    ) -> GeneratedContent: ...

    async def calculate_confidence(
        self,
        content: GeneratedContent
    ) -> ConfidenceScore: ...

class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_listing(
        self,
        images: List[ImageData],
        prompt: str,
        ml_category_hint: Optional[str] = None
    ) -> GeneratedContent:
        return await self._process_with_gemini(images, prompt, ml_category_hint)

    async def calculate_confidence(self, content: GeneratedContent) -> ConfidenceScore:
        return ConfidenceScore(self._analyze_content_quality(content))

async def process_product_content(
    product_id: UUID,
    ai_service: AIContentGenerator
) -> GeneratedContent:
    product = await get_product_by_id(product_id)
    content = await ai_service.generate_listing(product.images, product.prompt)
    return content

class AIServiceWithFallback:
    def __init__(self, primary: AIContentGenerator, secondary: AIContentGenerator):
        self.primary = primary
        self.secondary = secondary

    async def generate_listing(self, images: List[ImageData], prompt: str) -> GeneratedContent:
        try:
            return await self.primary.generate_listing(images, prompt)
        except AIServiceError:
            return await self.secondary.generate_listing(images, prompt)
```

### Tell Don't Ask Pattern

**Core:** Objects decide internally, don't expose state for external decisions

```python
# ✅ Product Publishing
product.can_be_published() → publisher.execute_publish(product)
# ❌ External decisions
if product.confidence > 0.85 and product.status == "ready": publisher.publish()

# ✅ AI Confidence
confidence.create_result(content) → ContentResult
# ❌ Threshold logic outside
if confidence.value >= 0.85: result = ContentResult.ready_for_publish()

# ✅ Image Processing
image.process_for_listing(processor) → ProcessedImage
# ❌ External analysis
if image.has_complex_bg(): processor.remove_background()
```

**WHY:** Centralized business logic, consistent decisions, improved testability

### Error Handling Standards

#### Domain-Specific Exception Hierarchy

**Core Principle:** Every module MUST define its own exception hierarchy. Generic exceptions (ValueError, RuntimeError) are FORBIDDEN in domain and application layers.

```python
# ✅ Required: Module-specific exception hierarchy
class UserManagementError(Exception):
    """Base exception for all user management domain errors."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class UserAlreadyExistsError(UserManagementError):
    """Raised when attempting to register a user with an email that already exists."""

    def __init__(self, email: str):
        super().__init__(
            f"User with email '{email}' already exists",
            error_code="USER_ALREADY_EXISTS"
        )
        self.email = email

class AccountLockedError(UserManagementError):
    """Raised when attempting to authenticate with a locked account."""

    def __init__(self, failed_attempts: int, max_attempts: int):
        super().__init__(
            f"Account locked due to {failed_attempts} failed login attempts. "
            f"Maximum allowed attempts: {max_attempts}",
            error_code="ACCOUNT_LOCKED"
        )
        self.failed_attempts = failed_attempts
        self.max_attempts = max_attempts
```

#### Exception Design Patterns

**Pattern 1: Base Domain Exception**
```python
# modules/{module}/domain/exceptions.py
class {Module}Error(Exception):
    """Base exception for {module} domain errors."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
```

**Pattern 2: Specific Business Rule Violations**
```python
class WeakPasswordError(UserManagementError):
    """Raised when a password does not meet strength requirements."""

    def __init__(self, requirements: str | None = None):
        message = (
            requirements or
            "Password must be at least 8 characters long and contain "
            "uppercase, lowercase, number and special character"
        )
        super().__init__(message, error_code="WEAK_PASSWORD")

class InvalidConfidenceScoreError(ProductManagementError):
    """Raised when confidence score is invalid or out of range."""

    def __init__(self, score: float, product_id: str | None = None):
        message = f"Invalid confidence score: {score}. Must be between 0.0 and 1.0"
        super().__init__(message, product_id)
        self.score = score
```

**Pattern 3: Operation Not Allowed**
```python
class OperationNotAllowedError(UserManagementError):
    """Raised when an operation is not allowed due to business rules."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Operation '{operation}' not allowed: {reason}",
            error_code="OPERATION_NOT_ALLOWED"
        )
        self.operation = operation
        self.reason = reason
```

#### Exception Usage Rules

**FORBIDDEN: Generic Exceptions in Domain/Application**
```python
# ❌ NEVER use generic exceptions
raise ValueError("User already exists")
raise RuntimeError("Account is locked")
raise Exception("Password too weak")
```

**REQUIRED: Domain-Specific Exceptions**
```python
# ✅ Always use domain-specific exceptions
raise UserAlreadyExistsError(email)
raise AccountLockedError(failed_attempts, max_attempts)
raise WeakPasswordError()
```

**Exception Location Requirements:**
- **Domain Layer:** `modules/{module}/domain/exceptions.py`
- **Cross-Module:** Each module defines its own exceptions (NO sharing)
- **Infrastructure:** Can raise domain exceptions via protocol interfaces
- **API Layer:** Convert domain exceptions to HTTP responses

#### Testing Exception Patterns

```python
# ✅ Test specific exception types and properties
def test_user_already_exists_error():
    email = "test@example.com"
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await authentication_service.register_user(email, password)

    assert exc_info.value.email == email
    assert exc_info.value.error_code == "USER_ALREADY_EXISTS"

# ✅ Test exception message content for business clarity
def test_account_locked_error_message():
    with pytest.raises(AccountLockedError) as exc_info:
        await authentication_service.authenticate_user(email, password)

    error = exc_info.value
    assert str(error.failed_attempts) in str(error)
    assert str(error.max_attempts) in str(error)
```

#### Error Response Standardization

```python
@dataclass
class ErrorResponse:
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None

# API layer converts domain exceptions
def convert_domain_exception(exc: Exception) -> ErrorResponse:
    if isinstance(exc, UserManagementError):
        return ErrorResponse(
            error_code=exc.error_code or "USER_MANAGEMENT_ERROR",
            message=exc.message,
            details={"module": "user_management"}
        )
    # Handle other domain exceptions...
```

---

## TypeScript Frontend Standards

### Code Style
```yaml
Linter: ESLint + Prettier
Type Safety: TypeScript strict mode
Component Style: Functional components with hooks
File Naming: kebab-case for components, PascalCase for types
```

### Component Standards
```typescript
// ✅ Required: Props interface + component export
interface PhotoCollectionProps {
  images: ImageData[];
  maxImages?: number;
  onImagesChange: (images: ImageData[]) => void;
}

export default function PhotoCollection({
  images,
  maxImages = 10,
  onImagesChange
}: PhotoCollectionProps) {
  // Implementation
}
```

### State Management Patterns
```typescript
// ✅ Svelte stores with typed interfaces
interface ProductsState {
  items: Record<string, Product>;
  loading: boolean;
  error: string | null;
}

function createProductsStore() {
  const { subscribe, update } = writable<ProductsState>({
    items: {},
    loading: false,
    error: null
  });

  return { subscribe, /* methods */ };
}
```

---

## Naming Conventions

### File Structure
```
Backend:
  - Classes: PascalCase (class ProductService)
  - Functions: snake_case (def generate_content)
  - Variables: snake_case (user_prompt)
  - Constants: UPPER_SNAKE_CASE (MAX_IMAGES)
  - Files: snake_case (product_service.py)

Frontend:
  - Components: PascalCase (PhotoCollection.svelte)
  - Functions: camelCase (handleSubmit)
  - Variables: camelCase (userPrompt)
  - Constants: UPPER_SNAKE_CASE (MAX_IMAGES)
  - Files: kebab-case (photo-collection.svelte)
```

### Domain Language
```yaml
Consistent Terms:
  - "Product" not "Item" or "Listing"
  - "Generated Content" not "AI Output"
  - "Confidence Score" not "Quality Score"
  - "MercadoLibre" not "ML" in user-facing text
  - "Processing" not "Loading" for AI operations
```

---

## Testing Standards

### Testing Strategy by Layer

**Unit Tests:**
- **Domain Logic:** Pure functions, no mocks needed
- **Application Use Cases:** Mock external services only (AIContentGenerator, ImageProcessor)
- **SOLID:** Each test has single responsibility

**Integration Tests:**
- **Database:** Real database (test containers), no mocking
- **Internal Services:** Real implementations, no mocking
- **External APIs:** httpx-mock + respx for external services (Gemini, PhotoRoom, MercadoLibre)

**E2E Tests:**
- **External Services:** httpx-mock + respx for Gemini API, PhotoRoom API, MercadoLibre API
- **Internal Services:** Real database, real application logic, real infrastructure
- **Focus:** Critical user journeys only

### Test Organization Architecture

**Core Principle:** Tests are co-located with implementation for better maintainability and module independence.

#### Test Location Strategy

**Co-located Unit Tests:** `modules/{module}/domain/entities/test_*.py`
```
modules/user_management/
├── domain/
│   ├── entities/
│   │   ├── user.py
│   │   └── test_user.py           # ✅ Co-located with entity
│   └── services/
│       ├── authentication.py
│       └── test_authentication.py  # ✅ Co-located with service
└── tests/                         # ✅ Module-level integration tests
    ├── test_user_integration.py
    └── conftest.py
```

**Centralized Integration/E2E Tests:** `/tests/`
```
tests/
├── integration/
│   └── api/
│       └── test_health.py          # ✅ Cross-module integration tests
├── infrastructure/
│   └── test_settings.py           # ✅ Infrastructure tests
└── modules/
    └── shared/                     # ✅ Shared/common functionality tests
        ├── test_health.py
        └── test_main.py
```

#### Test Discovery Configuration

**pytest Configuration Updates:**
```toml
[tool.pytest.ini_options]
testpaths = ["../tests", "modules"]    # Discovers both locations
addopts = [
    "--strict-markers",
    "--strict-config",
]
```

**Coverage Configuration:**
```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/test_*.py",          # Excludes co-located tests
    "*/migrations/*",
    "*/__pycache__/*",
]
```

### Coverage Requirements
- **Minimum Coverage:** 80% for domain logic
- **DRY:** Shared test utilities and factories
- **YAGNI:** Don't test getters/setters, test business behavior

### Test Behavior, Not State
```python
# ✅ Test behavior outcomes
result = await publisher.publish_if_ready(product)
assert result.is_successful()

# ❌ Test internal state
assert product._confidence == 0.85  # State exposure
```

---

## Security Standards

### Data Protection
```python
logger.info(f"Processing product {product_id}")
logger.info(f"ML credentials: {credentials}")    # Forbidden

@dataclass
class MLCredentials:
    app_id: str
    secret_key: str = field(repr=False)
    access_token: str = field(repr=False)
```

### Input Validation
```python
def validate_prompt(prompt: str) -> str:
    if len(prompt.strip()) < 10:
        raise ValidationError("Prompt must be at least 10 characters")
    if len(prompt) > 500:
        raise ValidationError("Prompt must be less than 500 characters")
    return prompt.strip()
```

---

## Git Workflow Standards

### Commit Messages
```
Format: type(scope): description

Examples:
feat(product): add AI content generation service
fix(image): resolve background processing error
docs(api): update endpoint documentation
test(product): add integration tests for ML publishing
```

### Branch Strategy
```yaml
Main Branch: main
Feature Branches: feature/story-number-brief-description
Hotfix Branches: hotfix/brief-description
Protection: No direct commits to main
Required: Pull request with review
```

---

## Quality Gates (NFR8.1)

### Automated Checks Required
```yaml
Before Story Completion:
  - ✅ Ruff linting passes
  - ✅ Pyright type checking passes
  - ✅ ESLint + Prettier passes
  - ✅ Tach boundary validation passes
  - ✅ All tests pass (80%+ coverage)
  - ✅ Build succeeds
  - ✅ Security scan passes
```

### Code Review Checklist
- [ ] Follows hexagonal architecture patterns
- [ ] Complete type annotations
- [ ] Proper error handling
- [ ] Security considerations addressed
- [ ] Tests written (TDD)
- [ ] No hardcoded secrets
- [ ] Follows naming conventions
- [ ] **Tell Don't Ask:** Objects make decisions internally, don't expose state for external decisions
- [ ] **Tell Don't Ask:** Methods return behavior results, not raw data for external processing

---

## Performance Standards

### Mobile-First Optimization
- **Bundle Size:** Frontend chunks < 100KB gzipped
- **API Response:** < 200ms for simple endpoints
- **Image Processing:** Progress feedback every 2 seconds
- **Real-time Updates:** WebSocket latency < 100ms

### Backend Performance
- **Database Queries:** N+1 queries forbidden
- **AI API Calls:** Implement retry with exponential backoff
- **File Uploads:** Chunked upload for images > 5MB
- **Memory Usage:** Monitor and limit per request

---

## Module Independence & Protocol Standards

### Protocol-First Architecture (Validated via PoC)

**Core Principle:** Modules must be 100% independent with zero cross-module imports.

- **Zero Import Rule:** Modules MUST NOT import from other domain modules
- **Interface Contracts:** All cross-module communication via Protocol interfaces only
- **Static Validation:** Pyright validates Protocol compliance without runtime overhead
- **Research Validation:** Static duck typing with Protocols achieves true module independence

### Protocol Design Patterns

#### Pattern 1: Protocol @property ↔ Entity field
```python
# Consumer module defines protocol
class ManagerProtocol(Protocol):
    @property
    def is_active(self) -> bool: ...

# Producer module satisfies automatically
@dataclass
class User:
    is_active: bool = True  # ✅ Field satisfies @property automatically
```

#### Pattern 2: Protocol method ↔ Entity field + method
```python
# Consumer module defines interface
class OwnerProtocol(Protocol):
    def get_email(self) -> str: ...

# Producer module implements via field + accessor
@dataclass
class User:
    email: str

    def get_email(self) -> str:
        return self.email  # ✅ Method satisfies protocol
```

#### Pattern 3: Runtime checkable protocols
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProcessorProtocol(Protocol):
    def process(self, data: Any) -> Any: ...

# Enables isinstance checks when needed
if isinstance(service, ProcessorProtocol):
    result = service.process(data)
```

### External Resource Placement Rules

**Infrastructure Layer Only:**
- **Database Access:** SQLAlchemy models, sessions, repositories
- **HTTP Clients:** External API clients (MercadoLibre, Gemini, PhotoRoom)
- **File Systems:** File storage, image processing services
- **Message Queues:** Redis, RabbitMQ, task queues
- **Caching:** Redis clients, memory caches

**Domain Layer:**
- **Pure Python:** No external dependencies
- **Business Logic:** Entities, services, value objects
- **Interfaces:** Protocol definitions for external dependencies

```python
# ✅ Correct: Repository protocol in domain
class UserRepositoryProtocol(Protocol):
    async def save(self, user: User) -> None: ...
    async def find_by_id(self, user_id: UUID) -> User | None: ...

# ✅ Correct: SQLAlchemy implementation in infrastructure
class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        # SQLAlchemy implementation details
        pass
```

### Module Structure Standards

```
modules/{module_name}/
├── domain/
│   ├── entities/          # Domain entities (dataclasses, pure Python)
│   ├── services/          # Pure business logic ({name}.py - no "service" suffix)
│   └── ports/            # Protocols (client-side interface definitions)
├── application/
│   └── use_cases/        # Orchestration only (NO services/ folder)
├── infrastructure/
│   ├── repositories/     # Protocol implementations (SQLAlchemy, etc.)
│   ├── services/        # External service adapters (HTTP clients, etc.)
│   └── models/          # External resource models (SQLAlchemy, etc.)
├── api/
│   ├── routers/         # HTTP endpoints
│   └── schemas/         # Request/Response DTOs
└── tests/               # Tests INSIDE module (not global /tests/)
    ├── test_entities.py  # Unit tests for domain entities
    ├── test_use_cases.py # Unit tests for application use cases
    └── test_integration.py # Integration tests with real infrastructure
```

### Module Communication Patterns

```python
# ✅ Correct: Define protocols in consumer module
# modules/product_management/domain/ports/owner_service.py
class OwnerServiceProtocol(Protocol):
    def get_owner_info(self, owner_id: UUID) -> OwnerInfo: ...

# ✅ Correct: Producer satisfies protocol without importing it
# modules/user_management/domain/entities/user.py
class User:
    def get_owner_info(self, owner_id: UUID) -> OwnerInfo:
        # Implementation automatically satisfies protocol
        pass

# ✅ Correct: Application layer uses dependency injection
# application/use_cases/create_product.py
async def create_product(
    product_data: ProductData,
    owner_service: OwnerServiceProtocol  # Injected, no imports
) -> Product:
    owner_info = await owner_service.get_owner_info(product_data.owner_id)
    return Product.create(owner_info, product_data)
```

### Testing Strategy for Module Independence

#### Test Location
- **Module Tests:** `modules/{module}/tests/` (inside each module)
- **Integration Tests:** Can be global for cross-module scenarios
- **NO Global Module Tests:** No `/tests/modules/` directory

#### Testing Patterns
```python
# ✅ Unit Test: Mock protocol interfaces
async def test_create_product_use_case():
    # Mock the protocol, not the implementation
    mock_owner_service = AsyncMock(spec=OwnerServiceProtocol)
    mock_owner_service.get_owner_info.return_value = OwnerInfo(...)

    result = await create_product(product_data, mock_owner_service)
    assert result.owner_id == product_data.owner_id

# ✅ Integration Test: Test protocol compliance
def test_user_satisfies_owner_protocol():
    user = User.create(email="test@example.com", name="Test User")
    # Type checker validates this assignment
    owner: OwnerServiceProtocol = user
    owner_info = owner.get_owner_info(user.id)
    assert owner_info.name == "Test User"

# ✅ Cross-Module Test: Real implementations via DI
async def test_product_creation_integration():
    # Real implementations, no mocks
    user_repository = SQLAlchemyUserRepository(session)
    user_service = UserService(user_repository)

    product = await create_product(product_data, user_service)
    # Validates actual protocol compliance
```

### Critical Implementation Rules (Problem Prevention)

**Rule 1: External Resources ONLY in Infrastructure**
```python
# ❌ Forbidden: SQLAlchemy in application/domain
from sqlalchemy.orm import Session  # In application layer

# ✅ Required: External resources in infrastructure only
# modules/{module}/infrastructure/repositories/{name}_repository.py
```

**Rule 2: NO Cross-Module Imports**
```python
# ❌ Forbidden: Direct module imports
from modules.user_management.domain.entities.user import User

# ✅ Required: Protocol-based communication only
from modules.product_management.domain.ports.owner_service import OwnerServiceProtocol
```

**Rule 3: Tests Inside Modules**
```python
# ❌ Forbidden: Global test directory
/tests/modules/user_management/test_user.py

# ✅ Required: Tests inside module
modules/user_management/tests/test_user.py
```

**Rule 4: NO Performance Tests for MVP**
```python
# ❌ Forbidden: Performance testing for MVP features
@pytest.mark.performance
def test_user_creation_performance():
    # Not needed for MVP

# ✅ Required: Functional testing only
def test_user_creation():
    user = User.create(...)
    assert user.is_valid()
```

**Rule 5: Real Protocol Implementation (No ServiceImpl)**
```python
# ❌ Forbidden: ServiceImpl without Protocol
class UserServiceImpl:  # What protocol does this implement?
    pass

# ✅ Required: Clear protocol implementation
class DatabaseUserRepository:  # Implements UserRepositoryProtocol
    def save(self, user: User) -> None:
        # Implementation
```

### Naming Conventions

- **Protocols:** `{Purpose}Protocol` (e.g., `UserRepositoryProtocol`, `EmailServiceProtocol`)
- **Implementations:** `{Technology}{Purpose}` (e.g., `SQLAlchemyUserRepository`, `SMTPEmailService`)
- **Domain Services:** `{name}.py` (e.g., `authentication.py`, not `authentication_service.py`)
- **Use Cases:** `{verb}_{noun}.py` (e.g., `create_user.py`, `authenticate_user.py`)

---

**Quality Enforcement:** All standards are enforced through automated tooling and code review. Non-compliance blocks story completion per NFR8.1.
