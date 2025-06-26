# IntelliPost AI - Coding Standards

## Document Information
- **Project:** IntelliPost AI MVP
- **Last Updated:** 2024-12-26
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

### Tell Don't Ask Pattern (Domain-Specific)

**Core Principle:** Objects encapsulate behavior and make decisions internally

#### Publication Decision Pattern
```python
# ✅ DO: Object makes decision
class Product:
    def can_be_published(self) -> bool:
        return self._confidence >= 0.85 and self._has_required_content()

    def publish_via(self, publisher: ProductPublisher) -> PublishResult:
        return publisher.execute_publish(self) if self.can_be_published() else PublishResult.not_ready()

# ❌ DON'T: External decision making
if product.confidence_score > 0.85 and product.processing_status == "completed":
    publisher.publish(product)
```
**WHY:** Eliminates scattered business logic, improves testability

#### AI Confidence Handling Pattern
```python
# ✅ DO: Service decides confidence handling
class AIContentGenerator:
    async def generate_with_confidence_handling(self, images: List[ImageData]) -> ContentResult:
        content = await self._generate_content(images)
        confidence = await self._calculate_confidence(content)
        return confidence.create_result(content)  # Confidence decides result type

class ConfidenceScore:
    def create_result(self, content: GeneratedContent) -> ContentResult:
        if self._value >= 0.85: return ContentResult.ready_for_publish(content)
        if self._value >= 0.7: return ContentResult.needs_minor_edits(content)
        return ContentResult.needs_review(content, self._get_improvement_hints())

# ❌ DON'T: External confidence interpretation
confidence = await ai_service.calculate_confidence(content)
if confidence.value >= 0.85:
    result = ContentResult.ready_for_publish(content)
elif confidence.value >= 0.7:
    result = ContentResult.needs_minor_edits(content)
```
**WHY:** Centralizes confidence interpretation logic, prevents inconsistent thresholds

#### Image Processing Decision Pattern
```python
# ✅ DO: Image decides its processing needs
class RawImage:
    def process_for_listing(self, processor: ImageProcessor) -> ProcessedImage:
        if self._needs_background_removal():
            return processor.remove_background(self)
        elif self._is_suitable_for_thumbnail():
            return processor.optimize_for_thumbnail(self)
        return processor.standard_optimization(self)

# ❌ DON'T: External processing decisions
if image.has_complex_background() and image.is_product_focused():
    processed = processor.remove_background(image)
elif image.aspect_ratio == 1.0 and image.has_clear_focus():
    processed = processor.optimize_for_thumbnail(image)
```
**WHY:** Image characteristics determine processing needs, not external logic

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

## Testing Standards

### Testing Strategy by Layer
```yaml
Unit Tests:
  Domain: Pure functions, no mocks
  Application: Mock external services only
  Coverage: 80%+ for domain logic

Integration Tests:
  Database: Real DB (test containers)
  External APIs: httpx-mock + respx (Gemini, PhotoRoom, MercadoLibre)

E2E Tests:
  Focus: Critical user journeys only
  Mock: External services only
```

### Test Behavior, Not State
```python
# ✅ DO: Test behavior outcomes
async def test_should_publish_when_ready():
    product = create_high_confidence_product()
    result = await publisher.publish_if_ready(product)
    assert result.is_successful()

# ❌ DON'T: Test internal state
def test_confidence_value():
    assert product._confidence == 0.85  # Internal state exposure
```

### Domain-Specific Test Patterns
```python
# AI Content Generation
async def test_ai_should_generate_title_from_images():
    content = await ai_service.generate_listing(images, "Samsung Galaxy")
    assert "Samsung Galaxy" in content.title and len(content.title) <= 60

# Product Publishing Decision
async def test_product_should_reject_low_confidence():
    product = create_low_confidence_product()
    result = await publisher.publish_if_ready(product)
    assert result.needs_review()

# Image Processing Decision
def test_image_should_choose_background_removal():
    image = create_complex_background_image()
    result = image.process_for_listing(processor)
    assert isinstance(result, BackgroundRemovedImage)
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

**Quality Enforcement:** All standards are enforced through automated tooling and code review. Non-compliance blocks story completion per NFR8.1.
