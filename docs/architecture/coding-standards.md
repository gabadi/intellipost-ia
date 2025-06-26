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

### Tell Don't Ask Pattern Examples

**Core Principle:** Objects should encapsulate behavior and make decisions internally rather than exposing state for external decision-making.

```python
# ✅ Tell Don't Ask - Object makes decisions internally
class ProductPublisher:
    def __init__(self, confidence_threshold: float = 0.85):
        self._confidence_threshold = confidence_threshold

    async def publish_if_ready(self, product: Product) -> PublishResult:
        """Object decides whether to publish based on internal logic."""
        if product.is_ready_for_publication(self._confidence_threshold):
            return await self._publish_to_mercadolibre(product)
        else:
            return PublishResult.needs_review(product.get_review_suggestions())

    async def _publish_to_mercadolibre(self, product: Product) -> PublishResult:
        # Publishing logic encapsulated
        pass

class Product:
    def is_ready_for_publication(self, threshold: float) -> bool:
        """Product decides its own readiness state."""
        return (
            self.confidence_score.value >= threshold and
            self.has_required_content() and
            self.images_are_processed()
        )

    def get_review_suggestions(self) -> List[ReviewSuggestion]:
        """Product provides its own improvement suggestions."""
        suggestions = []
        if self.confidence_score.value < 0.7:
            suggestions.append(ReviewSuggestion.improve_description())
        if not self.has_category():
            suggestions.append(ReviewSuggestion.select_category())
        return suggestions

# ❌ Ask Don't Tell - External code makes decisions
class BadProductPublisher:
    async def publish_product_old_way(self, product: Product) -> PublishResult:
        # External code asking for state and making decisions
        confidence = product.confidence_score.value  # Asking for state
        if confidence >= 0.85:  # External decision making
            if product.images and len(product.images) > 0:  # More asking
                if product.title and product.description:  # More asking
                    return await self._publish(product)
        return PublishResult.failed("Not ready")
```

**Real-World Application Examples:**

```python
# ✅ AI Service encapsulates confidence decision logic
class AIContentGenerator:
    async def generate_with_confidence_handling(self, images: List[ImageData], prompt: str) -> ContentResult:
        """Service decides how to handle confidence internally."""
        content = await self._generate_content(images, prompt)
        confidence = await self._calculate_confidence(content)

        # Internal decision making
        if confidence.requires_manual_review():
            return ContentResult.needs_review(content, confidence.get_improvement_hints())
        elif confidence.is_publication_ready():
            return ContentResult.ready_for_publish(content)
        else:
            return ContentResult.needs_minor_edits(content, confidence.get_quick_fixes())

class ConfidenceScore:
    def __init__(self, value: float, factors: Dict[str, float]):
        self._value = value
        self._factors = factors

    def requires_manual_review(self) -> bool:
        """Score decides its own interpretation."""
        return self._value < 0.7 or self._factors.get('category_match', 1.0) < 0.5

    def is_publication_ready(self) -> bool:
        """Score decides publication readiness."""
        return self._value >= 0.85 and all(f >= 0.7 for f in self._factors.values())

    def get_improvement_hints(self) -> List[str]:
        """Score provides its own improvement suggestions."""
        hints = []
        if self._factors.get('title_quality', 1.0) < 0.7:
            hints.append("Consider improving the title with more descriptive keywords")
        if self._factors.get('description_completeness', 1.0) < 0.7:
            hints.append("Add more details about product condition and features")
        return hints

# ✅ Image processor makes processing decisions internally
class ImageProcessor:
    async def process_for_listing(self, raw_images: List[RawImage]) -> ProcessedImageSet:
        """Processor decides how to handle different image scenarios."""
        result = ProcessedImageSet()

        for image in raw_images:
            # Internal decision making based on image characteristics
            if image.needs_background_removal():
                processed = await self._remove_background(image)
                result.add_main_image(processed)
            elif image.is_suitable_for_thumbnail():
                processed = await self._optimize_for_thumbnail(image)
                result.add_thumbnail(processed)
            else:
                processed = await self._standard_optimization(image)
                result.add_gallery_image(processed)

        return result.ensure_ml_requirements()  # Final validation internally

class RawImage:
    def needs_background_removal(self) -> bool:
        """Image decides if it needs background processing."""
        return self._has_complex_background() and self._is_product_focused()

    def is_suitable_for_thumbnail(self) -> bool:
        """Image decides its own best use case."""
        return self._aspect_ratio_is_square() and self._has_clear_product_focus()
```

**Common Anti-Patterns to Avoid:**

```python
# ❌ Don't expose internal state for external decisions
class BadProduct:
    @property
    def confidence_score(self) -> float:  # Exposing raw state
        return self._confidence

    @property
    def processing_status(self) -> str:  # Exposing raw state
        return self._status

# External code making decisions (violates Tell Don't Ask)
if product.confidence_score > 0.85 and product.processing_status == "completed":
    publisher.publish(product)

# ✅ Instead, encapsulate the decision
class GoodProduct:
    def can_be_published(self) -> bool:
        """Product makes its own publication decision."""
        return self._confidence >= 0.85 and self._status == ProcessingStatus.COMPLETED

    def publish_via(self, publisher: ProductPublisher) -> PublishResult:
        """Product coordinates its own publishing."""
        if self.can_be_published():
            return publisher.execute_publish(self)
        else:
            return PublishResult.not_ready(self._get_readiness_blockers())
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

### Testing Tell Don't Ask Patterns

```python
# ✅ Test behavior, not state exposure
async def test_should_publish_when_product_is_ready():
    # Arrange
    product = create_high_confidence_product()
    publisher = ProductPublisher(confidence_threshold=0.8)

    # Act - Tell the object what to do
    result = await publisher.publish_if_ready(product)

    # Assert - Test the behavior outcome
    assert result.is_successful()
    assert result.listing_id is not None

async def test_should_request_review_when_confidence_low():
    # Arrange
    product = create_low_confidence_product()
    publisher = ProductPublisher(confidence_threshold=0.8)

    # Act
    result = await publisher.publish_if_ready(product)

    # Assert - Test decision behavior
    assert result.needs_review()
    assert "improve_description" in [s.type for s in result.suggestions]

# ❌ Don't test internal state directly
def test_bad_state_testing():
    product = Product()
    # Don't test: assert product._confidence == 0.75
    # Do test: assert product.can_be_published() == True
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
