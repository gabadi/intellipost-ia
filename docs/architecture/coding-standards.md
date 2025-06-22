# IntelliPost AI - Coding Standards

## Document Information
- **Project:** IntelliPost AI MVP
- **Last Updated:** June 22, 2025
- **Scope:** Development Quality Standards
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

### Core Development Principles (SOLID + KISS + DRY + YAGNI)
- **SOLID Principles:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **KISS (Keep It Simple, Stupid):** Simplest solution that works
- **DRY (Don't Repeat Yourself):** Eliminate code duplication
- **YAGNI (You Aren't Gonna Need It):** Don't implement until needed
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

### Error Handling Standards
```python
class AIGenerationError(Exception):
    pass

class MLPublishingError(Exception):
    pass

@dataclass
class ErrorResponse:
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
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

## Testing Standards (SOLID + KISS + DRY + YAGNI)

### Test-Driven Development (TDD)
```python
async def test_should_generate_optimized_title_when_high_quality_images():
    images = [create_test_image(quality="high")]
    prompt = "Samsung Galaxy smartphone"

    content = await ai_service.generate_listing(images, prompt)

    assert content.title is not None
    assert "Samsung Galaxy" in content.title
    assert len(content.title) <= 60

def test_should_raise_error_when_no_images_provided():
    with pytest.raises(ValidationError):
        ai_service.generate_listing([], "test prompt")

@pytest.fixture
def mock_gemini_api():
    import respx
    import httpx

    with respx.mock:
        respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent").mock(
            return_value=httpx.Response(200, json={
                "candidates": [{"content": {"parts": [{"text": "Samsung Galaxy S24 - Excellent condition"}]}}]
            })
        )
        yield

async def test_should_generate_content_via_gemini_api(mock_gemini_api):
    service = GeminiService(api_key="test-key")
    images = [create_test_image()]
    prompt = "Samsung smartphone"

    content = await service.generate_listing(images, prompt)

    assert "Samsung Galaxy" in content.title
```

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

### Coverage Requirements
- **Minimum Coverage:** 80% for domain logic
- **DRY:** Shared test utilities and factories
- **YAGNI:** Don't test getters/setters, test business behavior

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

**Quality Enforcement:** All standards are enforced through automated tooling and code review. Non-compliance blocks story completion per NFR8.1.
