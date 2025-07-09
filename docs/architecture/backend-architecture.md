# Backend Architecture

## 1. Architecture Overview

This document provides the implementation guide for the backend architecture of IntelliPost-IA, focusing on how the hexagonal architecture pattern (defined in [system-overview.md](./system-overview.md)) is actually implemented across the 5 backend modules.

### Real Module Implementation

IntelliPost-IA implements a **Modular Monolith** with strict hexagonal boundaries enforced by **Tach** (boundary validation tool). The actual modules are:

1. **user_management** - Authentication, MercadoLibre OAuth, user profiles
2. **product_management** - Product lifecycle, images, file storage
3. **content_generation** - AI content generation (skeleton)
4. **marketplace_integration** - MercadoLibre API integration (skeleton)
5. **notifications** - Email and notification services (skeleton)

### Core Principles Implementation

The backend implements the following architectural principles:

- **Hexagonal Architecture**: Each module implements ports & adapters with **Tach-enforced** boundaries
- **Protocol-Based Communication**: Python `typing.Protocol` for zero cross-module dependencies
- **Module Independence**: True independence validated by Tach.toml with zero dependencies between modules
- **Domain-Driven Design**: Pure business logic in domain layers, composition over inheritance

### Actual Module Architecture Pattern

```
backend/modules/{module_name}/
├── domain/           # Pure business logic, no external dependencies
│   ├── entities/     # Domain entities (Product, User, ConfidenceScore)
│   ├── ports/        # Protocol interfaces (UserRepositoryProtocol)
│   ├── services/     # Domain services (AuthenticationService)
│   └── exceptions.py # Domain-specific exceptions
├── application/      # Use cases orchestrating domain logic
│   └── use_cases/    # Use case implementations (CreateProductUseCase)
├── infrastructure/   # External adapters and implementations
│   ├── repositories/ # Database implementations (SQLAlchemyUserRepository)
│   ├── services/     # External service adapters (BcryptPasswordService)
│   └── models/       # SQLAlchemy ORM models
├── api/             # FastAPI controllers and schemas
│   ├── routers/      # FastAPI route handlers
│   └── schemas/      # Pydantic request/response models
└── tests/           # Co-located module tests with pytest marks
```

## 2. Module Architecture Deep Dive

### Domain Layer Implementation

The domain layer contains pure business logic without external dependencies. Real examples from the codebase:

```python
# Real example: User entity from user_management module
@dataclass
class User:
    """Unified User domain entity with authentication and ML integration."""

    # Core identity
    id: UUID
    email: str
    password_hash: str
    created_at: datetime

    # User profile
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus = UserStatus.PENDING_VERIFICATION

    # MercadoLibre integration
    ml_user_id: str | None = None
    ml_access_token: str | None = None
    ml_refresh_token: str | None = None
    ml_token_expires_at: datetime | None = None

    def activate(self) -> None:
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    @property
    def is_ml_connected(self) -> bool:
        """Check if user has valid MercadoLibre connection."""
        return (
            self.ml_user_id is not None
            and self.ml_access_token is not None
            and self.ml_token_expires_at is not None
            and self.ml_token_expires_at > datetime.now(UTC)
        )
```

```python
# Real example: Product entity with composition pattern
class Product(ProductCore):
    """Product domain entity with business logic composition."""

    def is_ready_for_processing(self) -> bool:
        """Check if product is ready for AI processing."""
        return ProductBusinessRules.is_ready_for_processing(self)

    def has_high_confidence(self) -> bool:
        """Check if AI-generated content has high confidence."""
        return ProductBusinessRules.has_high_confidence(self)

    def mark_as_processed(self, confidence: ConfidenceScore) -> None:
        """Mark product as processed with confidence score."""
        ProductStatusManager.mark_as_processed(self, confidence)
```

```python
# Real example: ConfidenceScore value object
@dataclass(frozen=True)
class ConfidenceScore:
    """Numeric confidence score for AI-generated content (0.0-1.0)."""

    score: float

    # Threshold constants
    HIGH_THRESHOLD: ClassVar[float] = 0.8
    MEDIUM_THRESHOLD: ClassVar[float] = 0.5

    @property
    def is_high(self) -> bool:
        return self.score >= self.HIGH_THRESHOLD

    @classmethod
    def high(cls) -> "ConfidenceScore":
        return cls(0.9)
```

### Application Layer Patterns

Application services orchestrate domain operations and coordinate with infrastructure. Real use case implementations:

```python
# Real example: CreateProductUseCase orchestrates domain + infrastructure
class CreateProductUseCase:
    """Use case for creating a new product with images."""

    def __init__(
        self,
        product_repository: ProductRepositoryProtocol,
        file_storage_service: FileStorageService,
    ):
        self.product_repository = product_repository
        self.file_storage_service = file_storage_service

    async def execute(
        self,
        user_id: UUID,
        prompt_text: str,
        images: list[UploadFile],
    ) -> dict[str, Any]:
        """Execute the create product use case."""
        # Business validation
        if len(images) > 8:  # PRD business rule
            raise ValueError("Maximum 8 images allowed")

        # Create domain entity
        product = Product(
            id=uuid4(),
            user_id=user_id,
            status=ProductStatus.UPLOADING,
            prompt_text=prompt_text.strip(),
        )

        # Orchestrate: Domain + Infrastructure
        created_product = await self.product_repository.create(product)

        # Process images (simplified)
        for i, image_file in enumerate(images):
            upload_metadata = await self.file_storage_service.upload_product_image(
                user_id, product.id, image_file
            )
            await self.product_repository.create_product_image(
                product.id, upload_metadata["s3_key"], is_primary=(i == 0)
            )

        return {"product_id": str(created_product.id), "images_uploaded": len(images)}
```

```python
# Real example: AuthenticateUserUseCase coordinates domain + infrastructure
class AuthenticateUserUseCase:
    """Use case for user authentication."""

    def __init__(
        self,
        authentication_service: AuthenticationService,
        jwt_service: JWTServiceProtocol,
    ):
        self._authentication_service = authentication_service
        self._jwt_service = jwt_service

    async def execute(self, email: str, password: str) -> tuple[str, str, User]:
        """Execute user authentication use case."""
        # Domain: Authenticate user
        user = await self._authentication_service.authenticate_user(email, password)
        if not user:
            raise InvalidCredentialsError()

        # Infrastructure: Generate tokens
        access_token = self._jwt_service.create_access_token(user.id)
        refresh_token = self._jwt_service.create_refresh_token(user.id)

        return access_token, refresh_token, user
```

### Infrastructure Layer Design

Infrastructure adapters implement domain interfaces through structural subtyping (duck typing):

```python
# Real Adapter: SQLAlchemyUserRepository implementation
class SQLAlchemyUserRepository:
    """SQLAlchemy implementation automatically satisfies UserRepositoryProtocol."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user in database."""
        db_user = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            # ... other fields
        )
        self.session.add(db_user)
        await self.session.commit()
        return self._model_to_entity(db_user)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        return self._model_to_entity(db_user) if db_user else None

    def _model_to_entity(self, db_user: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=db_user.id,
            email=db_user.email,
            password_hash=db_user.password_hash,
            status=UserStatus(db_user.status)
        )
```

### API Layer Organization

FastAPI endpoints handle HTTP concerns and delegate to application services using dependency injection:

```python
# Real API endpoint from product_management module
@router.post("/products", response_model=CreateProductResponse)
async def create_product(
    prompt_text: str = Form(...),
    images: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    create_product_use_case: CreateProductUseCase = Depends(get_create_product_use_case),
) -> CreateProductResponse:
    """Create a new product with images."""
    try:
        result = await create_product_use_case.execute(
            user_id=current_user.id,
            prompt_text=prompt_text,
            images=images,
        )
        return CreateProductResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

```python
# Real API endpoint from user_management module
@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    authenticate_use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> LoginResponse:
    """Authenticate user and return JWT tokens."""
    try:
        access_token, refresh_token, user = await authenticate_use_case.execute(
            email=request.email,
            password=request.password
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
            email=user.email
        )
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

## 3. Inter-Module Communication

### Protocol-Based Communication (Go-Style Pattern)

**Core Principle**: "Accept interfaces, return instances" with zero cross-module dependencies.

Modules communicate through Protocol interfaces defined in the **CONSUMER** module:

```python
# ✅ Protocol defined in CONSUMER module (product_management/domain/ports/)
class UserServiceProtocol(Protocol):
    """Protocol for user operations needed by product management."""
    async def get_user(self, user_id: UUID) -> User: ...
    async def is_user_active(self, user_id: UUID) -> bool: ...

# ✅ Use case accepts Protocol, returns concrete instance
async def create_product(
    user_service: UserServiceProtocol,  # ← Accept interface
    product_data: ProductData
) -> Product:  # ← Return concrete instance
    user = await user_service.get_user(product_data.user_id)
    return Product.create(user, product_data)

# ✅ Producer module satisfies Protocol WITHOUT importing it
# (user_management/domain/services/user_service.py)
class UserService:  # ← Automatically satisfies UserServiceProtocol
    async def get_user(self, user_id: UUID) -> User:
        return await self.repository.find(user_id)

    async def is_user_active(self, user_id: UUID) -> bool:
        user = await self.get_user(user_id)
        return user.status == UserStatus.ACTIVE
```

**Static Validation with Pyright:**
- **Zero runtime overhead**: Type checking at compile-time only
- **No explicit Protocol inheritance**: Duck typing with static validation
- **Module independence**: Producer never imports consumer's Protocol
- **Automatic compatibility**: Pyright validates method signatures match

```python
# Real Protocols from the codebase:
class AIContentServiceProtocol(Protocol):
    async def generate_title(self, product_info: str) -> str: ...
    async def calculate_confidence(self, content: dict[str, Any]) -> ConfidenceScore: ...

class MercadoLibreServiceProtocol(Protocol):
    async def publish_listing(self, listing_data: dict[str, Any]) -> str: ...
    async def get_categories(self, query: str) -> list[dict[str, Any]]: ...
```

### Tach Boundary Enforcement

Zero cross-module dependencies enforced by Tach:

```toml
# Modules are completely independent
[[modules]]
path = "modules.user_management.domain"
depends_on = []  # No module dependencies

[[modules]]
path = "modules.product_management.domain"
depends_on = []  # Protocols define needed interfaces only
```

### Dependency Injection Pattern

FastAPI native dependency injection with type aliases:

```python
# Real DI configuration (api/dependencies.py)
def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

def get_authentication_service(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> AuthenticationService:
    return AuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        max_login_attempts=5
    )

# Clean type aliases for endpoints
UserRepositoryDep = Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)]
AuthServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
```

### Cross-Module Orchestration

Complex workflows use Protocol interfaces to coordinate modules:

```python
# Future: Product publishing workflow
class ProductPublishingWorkflow:
    """Orchestrate publishing across multiple modules via Protocols."""

    def __init__(
        self,
        ai_content_service: AIContentServiceProtocol,
        ml_service: MercadoLibreServiceProtocol,
        notification_service: NotificationServiceProtocol,
    ):
        self.ai_content_service = ai_content_service
        self.ml_service = ml_service
        self.notification_service = notification_service

    async def process_and_publish_product(self, product_id: UUID) -> None:
        """Complete workflow: AI → MercadoLibre → Notifications."""
        ai_content = await self.ai_content_service.generate_content(product_id)
        ml_listing_id = await self.ml_service.publish_listing(ai_content)
        await self.notification_service.notify_product_published(product_id)
        # Modules remain independent via Protocol interfaces
```

## 4. Data Architecture

### Repository Pattern Implementation

Data access abstracted through Protocol interfaces defined in consumer modules:

```python
# Protocol defined in consumer module (product_management/domain/ports/)
class ProductRepositoryProtocol(Protocol):
    async def create(self, product: Product) -> Product: ...
    async def get_by_user_id(self, user_id: UUID) -> list[Product]: ...

# Infrastructure implementation satisfies Protocol
class SQLAlchemyProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product: Product) -> Product:
        db_product = ProductModel(id=product.id, user_id=product.user_id)
        self.session.add(db_product)
        await self.session.commit()
        return self._model_to_entity(db_product)
```

### Transaction Management

Transactions at application layer with shared database:

```python
class CreateProductUseCase:
    async def execute(self, user_id: UUID, data: ProductData) -> Product:
        async with self.session.begin():  # Transaction boundary
            product = await self.product_repository.create(Product(...))
            await self.image_repository.create_images(product.id, data.images)
            return product
```

## 5. Service Layer Architecture

### Domain Service Composition

Domain services handle pure business logic:

```python
class AuthenticationService:
    """Pure domain service for user authentication."""

    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordServiceProtocol,
    ):
        self.user_repository = user_repository
        self.password_service = password_service

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repository.get_by_email(email)
        if not user or not self.password_service.verify(password, user.password_hash):
            raise InvalidCredentialsError()
        return user
```

### Error Handling Patterns

Domain-specific exceptions with structured handling:

```python
# Domain exceptions (user_management/domain/exceptions.py)
class UserManagementError(Exception):
    pass

class InvalidCredentialsError(UserManagementError):
    pass

# API layer converts to HTTP responses
@router.post("/auth/login")
async def login(request: LoginRequest, ...):
    try:
        return await authenticate_use_case.execute(request.email, request.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

## 6. Security Architecture

### Authentication & Authorization

JWT-based auth with domain validation:

```python
# JWT service (infrastructure)
class JoseJWTService:
    def create_access_token(self, user_id: UUID) -> str:
        payload = {"user_id": str(user_id), "exp": datetime.utcnow() + timedelta(minutes=15)}
        return jwt.encode(payload, self.secret_key)

# Auth middleware
async def get_current_user(
    credentials: HTTPAuthorizationCredentials,
    jwt_service: JoseJWTService = Depends(get_jwt_service)
) -> User:
    token = credentials.credentials
    payload = jwt_service.decode_token(token)
    return await user_repository.get_by_id(UUID(payload["user_id"]))
```

### Input Validation

Pydantic schemas with business rules:

```python
class CreateProductRequest(BaseModel):
    prompt_text: str = Field(..., min_length=10, max_length=500)

    @field_validator('prompt_text')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
```

## 7. Performance Architecture

### Performance Patterns

Async I/O with concurrent operations:

```python
class ProductService:
    async def get_product_with_images(self, product_id: UUID) -> ProductWithImages:
        # Concurrent database operations
        product_task = self.product_repository.get_by_id(product_id)
        images_task = self.image_repository.get_by_product_id(product_id)

        product, images = await asyncio.gather(product_task, images_task)
        return ProductWithImages(product, images)
```

### Database Optimization

Optimized queries with proper joins:

```python
class SQLAlchemyProductRepository:
    async def get_products_with_images(self, user_id: UUID) -> list[ProductWithImages]:
        # Single query with join
        query = (
            select(ProductModel, ProductImageModel)
            .outerjoin(ProductImageModel)
            .where(ProductModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return self._group_products_with_images(result)
```

## 8. Testing Architecture

### Co-located Testing Strategy

IntelliPost-IA uses **co-located tests** within each module, marked with pytest marks for test separation:

```python
# Real example: backend/modules/product_management/tests/test_product_entity.py
import pytest
from modules.product_management.domain.entities.product import Product
from modules.product_management.domain.entities.confidence_score import ConfidenceScore

pytestmark = pytest.mark.unit

class TestProduct:
    def test_product_creation(self):
        product = Product(
            id=uuid4(),
            user_id=uuid4(),
            status=ProductStatus.DRAFT,
            prompt_text="iPhone 13 Pro usado, excelente estado",
        )
        assert product.status == ProductStatus.DRAFT
        assert product.is_ready_for_processing() is False

    def test_confidence_score_validation(self):
        high_confidence = ConfidenceScore(0.9)
        assert high_confidence.is_high is True

        with pytest.raises(InvalidConfidenceScoreError):
            ConfidenceScore(1.5)  # Invalid score
```

### Integration Testing with TestContainers

Real integration testing using database test containers:

```python
# Real example: backend/modules/user_management/tests/test_integration.py
import pytest
from testcontainers.postgres import PostgresContainer
from modules.user_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.user_management.domain.entities.user import User, UserStatus

pytestmark = pytest.mark.integration

class TestUserIntegration:
    @pytest.fixture
    async def test_db_session(self):
        """Create test database session with PostgreSQL container."""
        with PostgresContainer("postgres:15") as postgres:
            engine = create_async_engine(postgres.get_connection_url())
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async_session = sessionmaker(engine, class_=AsyncSession)
            async with async_session() as session:
                yield session

    async def test_user_creation_and_retrieval(self, test_db_session):
        repository = SQLAlchemyUserRepository(test_db_session)

        user = User(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE
        )

        created_user = await repository.create(user)
        retrieved_user = await repository.get_by_email("test@example.com")

        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.status == UserStatus.ACTIVE
```

### Test Organization and Marks

Tests are organized using pytest marks for different test types:

```python
# Test marks configuration in pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: marks tests as unit tests (fast, isolated)",
    "integration: marks tests as integration tests (with external dependencies)",
    "api: marks tests as API endpoint tests (full request/response cycle)",
    "slow: marks tests as slow running tests",
]

# Test execution examples:
# pytest -m unit                    # Run only unit tests
# pytest -m "integration or api"    # Run integration and API tests
# pytest -m "not slow"              # Skip slow tests
```

```python
# Module-specific fixtures (backend/modules/user_management/tests/conftest.py)
import pytest
from modules.user_management.domain.entities.user import User, UserStatus

@pytest.fixture
def sample_user() -> User:
    return User(
        id=uuid4(),
        email="test@intellipost.ai",
        password_hash="$2b$12$hashed_password",
        status=UserStatus.ACTIVE
    )

@pytest.fixture
def mock_user_repository():
    return AsyncMock(spec=UserRepositoryProtocol)
```

## 9. Development Patterns

### Actual Code Organization Principles

Based on the real IntelliPost-IA implementation:

- **Composition over Inheritance**: Product entity uses composition with ProductBusinessRules, ProductStatusManager
- **Protocol-based Interfaces**: Zero cross-module dependencies via typing.Protocol
- **Co-located Testing**: Tests reside within modules, not separate test directories
- **Domain-Driven Design**: Pure domain logic isolated from infrastructure concerns
- **Tell Don't Ask**: Entities encapsulate behavior, avoid anemic domain models

### Dependency Injection Implementation

Actual FastAPI DI setup (backend/api/dependencies.py):

```python
def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

def get_jwt_service(settings: Settings = Depends(get_settings)) -> JoseJWTService:
    return JoseJWTService(
        secret_key=settings.user_jwt_secret_key,
        algorithm=settings.user_jwt_algorithm
    )

# Authentication chain
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    jwt_service: JoseJWTService = Depends(get_jwt_service),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    auth_middleware = AuthMiddleware(jwt_service, user_repository)
    return await auth_middleware.get_current_user(credentials)
```

### Domain Exception Hierarchy

Module-specific exception patterns:

```python
# user_management/domain/exceptions.py
class UserManagementError(Exception):
    pass

class UserAlreadyExistsError(UserManagementError):
    pass

class InvalidCredentialsError(UserManagementError):
    pass

# product_management/domain/exceptions.py
class ProductManagementError(Exception):
    pass

class InvalidConfidenceScoreError(ProductManagementError):
    def __init__(self, score: float):
        super().__init__(f"Score {score} must be between 0.0 and 1.0")
        self.score = score

# API layer converts domain exceptions to HTTP responses
@router.post("/auth/login")
async def login(request: LoginRequest, ...):
    try:
        return await authenticate_use_case.execute(request.email, request.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Structured Logging System

Enterprise-grade JSON structured logging with correlation tracking:

```python
# infrastructure/config/logging.py - Advanced structured logging
class StructuredLogger:
    """Enhanced logger with structured data support."""

    def performance(self, message: str, duration: float, **kwargs):
        """Log performance metrics with structured data."""
        self._log("INFO", message, extra={
            "event_type": "performance",
            "duration_ms": duration * 1000,
            **kwargs
        })

    def security_event(self, event_type: str, message: str, **kwargs):
        """Log security events with correlation context."""
        self._log("WARNING", message, extra={
            "event_type": "security",
            "security_event_type": event_type,
            **kwargs
        })

def get_logger(name: str) -> StructuredLogger:
    """Get structured logger with context correlation."""
    return StructuredLogger(name)

# Usage with structured data and correlation
from infrastructure.config.logging import get_logger

logger = get_logger(__name__)

class CreateProductUseCase:
    async def execute(self, user_id: UUID, prompt_text: str, images: list[UploadFile]):
        logger.info("Creating product", extra={
            "user_id": str(user_id),
            "image_count": len(images),
            "prompt_length": len(prompt_text)
        })

        start_time = time.time()
        try:
            created_product = await self.product_repository.create(product)
            logger.performance(
                "Product created successfully",
                time.time() - start_time,
                product_id=str(created_product.id)
            )
            return result
        except Exception as e:
            logger.error("Product creation failed", extra={
                "error_type": type(e).__name__,
                "user_id": str(user_id)
            })
            raise
```

**Features:**
- **JSON Format**: Structured data for log aggregation
- **Correlation Context**: `correlation_id`, `request_id`, `user_id` tracking
- **Sensitive Data Filtering**: Automatic removal of passwords, tokens
- **Performance Logging**: Built-in timing and metrics
- **Security Event Detection**: Specialized security logging
- **Request Middleware**: Automatic HTTP request/response logging

⚠️ **Current Issue**: The sophisticated logging system exists but requires initialization via `setup_logging(settings)` during application startup to activate structured features.

## References

### Architecture Documentation
- [System Overview](./system-overview.md) - Hexagonal architecture principles and AI service decisions
- [Database Schema](./database-schema.md) - PostgreSQL schema with User/Product/ML entities
- [Tech Stack](./tech-stack.md) - Python 3.11+, FastAPI, PostgreSQL, MinIO technology choices
- [API Specification](./api-specification.md) - REST endpoints and WebSocket real-time updates
- [External Integrations](./external-integrations.md) - MercadoLibre OAuth, AI services integration

### Implementation References
- **Tach Configuration**: `backend/tach.toml` - Module boundary enforcement
- **Dependency Injection**: `backend/api/dependencies.py` - FastAPI DI setup
- **User Management**: `backend/modules/user_management/` - Authentication and ML OAuth
- **Product Management**: `backend/modules/product_management/` - Product lifecycle and file storage
- **Domain Entities**: Real examples in `domain/entities/` across modules
- **Use Cases**: Application logic in `application/use_cases/` directories
- **Testing**: Co-located tests with pytest marks in `tests/` directories

### Business Context
- [PRD](../prd.md) - Mobile-first AI-powered MercadoLibre listing generation requirements
- **Epic Structure**: 5 modules supporting photo-to-published-listing in <60 seconds
- **AI Integration**: Multi-provider AI strategy with confidence scoring (high/medium/low thresholds)
- **MercadoLibre Focus**: OAuth integration, category detection, automated publishing
