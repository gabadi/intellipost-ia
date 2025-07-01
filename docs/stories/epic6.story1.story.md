# Story 6.1: User Authentication & JWT System

## Status: Draft

## Story

- As a user of the IntelliPost AI platform
- I want to securely register, login, and maintain sessions with mobile-optimized JWT tokens
- so that I can safely access my product data and manage my MercadoLibre credentials across multiple devices

## Acceptance Criteria (ACs)

1. **AC1: User Registration & Login**
   - [ ] Users can register with email and password validation (min 8 characters)
   - [ ] Users can login with valid credentials and receive JWT tokens
   - [ ] Failed login attempts provide clear error messages without exposing system information
   - [ ] Registration validates unique emails and provides appropriate feedback
   - [ ] Passwords are hashed using bcrypt before storage

2. **AC2: Mobile-Optimized JWT Strategy**
   - [ ] Access tokens have 15-minute expiry for battery optimization
   - [ ] Refresh tokens have 7-day expiry for user convenience
   - [ ] JWT tokens use HS256 algorithm for MVP security requirements
   - [ ] Token refresh endpoint automatically refreshes tokens before expiry
   - [ ] Secure HTTP-only cookies for web, localStorage for mobile development

3. **AC3: Authentication Middleware Integration**
   - [ ] FastAPI authentication middleware validates JWT tokens on protected endpoints
   - [ ] Protected endpoints require valid Authorization: Bearer <token> header
   - [ ] Authentication service integrates with existing hexagonal architecture
   - [ ] JWT validation errors return standardized error responses
   - [ ] Middleware provides current user context to business logic

4. **AC4: Database User Storage**
   - [ ] Users table with id, email, password_hash, created_at, updated_at fields
   - [ ] User sessions tracking with refresh token storage
   - [ ] Proper database indexes for email lookups and user queries
   - [ ] Foreign key relationships ready for future MercadoLibre credentials
   - [ ] User email uniqueness enforced at database level

5. **AC5: Mobile-First Authentication UI**
   - [ ] Login form with 44px touch targets and mobile-first responsive design
   - [ ] Registration form with real-time validation feedback
   - [ ] Password visibility toggle and auto-fill support
   - [ ] "Remember Me" functionality enabled by default
   - [ ] Authentication error states with actionable recovery messages

6. **AC6: Security Standards Implementation**
   - [ ] Input validation on all authentication endpoints
   - [ ] Rate limiting protection against brute force attacks (basic implementation)
   - [ ] Secure session management with automatic logout on token expiry
   - [ ] No sensitive data logged (passwords, tokens)
   - [ ] Production-ready HTTPS enforcement configuration

## Tasks / Subtasks

- [ ] **Task 1: Backend Authentication Infrastructure** (AC: 1, 3, 4, 6)
  - [ ] Create User entity in domain layer with proper validation
  - [ ] Implement AuthenticationService Protocol for hexagonal architecture
  - [ ] Create user repository with PostgreSQL implementation
  - [ ] Add users table migration with proper indexes and constraints
  - [ ] Implement bcrypt password hashing service

- [ ] **Task 2: JWT Token Management System** (AC: 2, 3)
  - [ ] Create JWT token service with access/refresh token generation
  - [ ] Implement token validation and refresh logic
  - [ ] Create FastAPI authentication middleware for protected routes
  - [ ] Add JWT configuration with mobile-optimized expiry times
  - [ ] Implement secure token storage strategy for different clients

- [ ] **Task 3: Authentication API Endpoints** (AC: 1, 2, 6)
  - [ ] Create POST /auth/register endpoint with validation
  - [ ] Create POST /auth/login endpoint with JWT token response
  - [ ] Create POST /auth/refresh endpoint for token renewal
  - [ ] Create POST /auth/logout endpoint for secure session termination
  - [ ] Add input validation and rate limiting to all endpoints

- [ ] **Task 4: Frontend Authentication Integration** (AC: 5)
  - [ ] Create Login.svelte component with mobile-first design
  - [ ] Create Register.svelte component with real-time validation
  - [ ] Implement authentication store for token management
  - [ ] Create auth API client with automatic token refresh
  - [ ] Add authentication guards for protected routes

- [ ] **Task 5: Security Implementation** (AC: 6)
  - [ ] Configure CORS for authentication endpoints
  - [ ] Implement basic rate limiting for auth endpoints
  - [ ] Add security headers middleware
  - [ ] Create authentication error handling with user-friendly messages
  - [ ] Configure HTTPS enforcement for production

- [ ] **Task 6: Testing & Integration** (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Unit tests for authentication service and JWT validation
  - [ ] Integration tests for auth endpoints with database
  - [ ] Frontend component tests for login/register forms
  - [ ] End-to-end authentication flow testing
  - [ ] Security testing for token validation and session management

## Dev Technical Guidance

### Previous Story Insights
From Epic1.Story3 completion:
- SvelteKit frontend is running on localhost:3001 with mobile-first design system
- FastAPI backend is running on localhost:8080 with hexagonal architecture
- PostgreSQL database is configured with proper connection pooling
- CORS is configured between frontend and backend
- Quality tools (Ruff, Pyright, ESLint) are enforced with strict standards
- Mobile-first CSS design system with 44px touch targets is implemented

### Data Models
**User Entity** [Source: architecture/database-schema.md#users-table]:
```python
@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
```

**Authentication DTOs** [Source: architecture/source-tree.md#backend-dto]:
```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    first_name: Optional[str] = Field(max_length=100)
    last_name: Optional[str] = Field(max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
```

### API Specifications
**Authentication Endpoints** [Source: architecture/api-specification.md#authentication]:
```http
POST /auth/register
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}

POST /auth/login
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepass123"
}

POST /auth/refresh
Content-Type: application/json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

POST /auth/logout
Authorization: Bearer <access_token>
```

**JWT Configuration** [Source: epics/epic6-security-authentication.md#jwt-strategy]:
```python
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15    # Battery optimization
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7       # User convenience
JWT_ALGORITHM = "HS256"                 # Sufficient for MVP
JWT_SECRET_KEY = "your-secret-key"      # From environment variable
```

### Component Specifications
**Protocol-Based Architecture Implementation** [Source: architecture/coding-standards.md#module-independence]:
```python
# Consumer defines what they need via protocols
class UserRepositoryProtocol(Protocol):
    async def save(self, user: User) -> None
    async def find_by_id(self, user_id: UUID) -> User | None
    async def find_by_email(self, email: str) -> User | None

class PasswordServiceProtocol(Protocol):
    def hash_password(self, password: str) -> str
    def verify_password(self, password: str, hashed_password: str) -> bool

class JWTServiceProtocol(Protocol):
    def create_access_token(self, user_id: UUID, expires_delta: timedelta) -> str
    def create_refresh_token(self, user_id: UUID, expires_delta: timedelta) -> str
    def verify_token(self, token: str) -> dict[str, str] | None

# Implementation satisfies protocols automatically (no imports)
class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        # Implementation automatically satisfies UserRepositoryProtocol
        pass
```

**Frontend Authentication Store** [Source: architecture/source-tree.md#frontend-stores]:
```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Svelte store for authentication state
function createAuthStore() {
  const { subscribe, update } = writable<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  });

  return {
    subscribe,
    login: async (credentials: LoginRequest) => Promise<void>,
    register: async (userData: RegisterRequest) => Promise<void>,
    logout: () => void,
    refreshToken: () => Promise<void>
  };
}
```

### File Locations
**Backend User Management Module** [Source: architecture/source-tree.md#backend-structure]:
**NOTE**: Following new module independence architecture with protocol-based communication

- User entities: `backend/modules/user_management/domain/entities/user.py`
- Authentication service: `backend/modules/user_management/domain/services/authentication.py`
- User repository protocol: `backend/modules/user_management/domain/ports/user_repository_protocol.py`
- Password service protocol: `backend/modules/user_management/domain/ports/password_service_protocol.py`
- JWT service protocol: `backend/modules/user_management/domain/ports/jwt_service_protocol.py`
- Use cases: `backend/modules/user_management/application/use_cases/`
  - `register_user.py`
  - `authenticate_user.py`
  - `refresh_token.py`
- Repository implementation: `backend/modules/user_management/infrastructure/repositories/sqlalchemy_user_repository.py`
- Service implementations: `backend/modules/user_management/infrastructure/services/`
  - `bcrypt_password_service.py`
  - `jose_jwt_service.py`
- SQLAlchemy models: `backend/modules/user_management/infrastructure/models/user_model.py`
- Auth endpoints: `backend/modules/user_management/api/routers/auth_router.py`
- Auth schemas: `backend/modules/user_management/api/schemas/auth_schemas.py`
- Module tests: `backend/modules/user_management/tests/`

**Frontend Authentication** [Source: architecture/source-tree.md#frontend-structure]:
- Login component: `frontend/src/routes/auth/login/+page.svelte`
- Register component: `frontend/src/routes/auth/register/+page.svelte`
- Auth store: `frontend/src/lib/stores/auth.ts`
- Auth API client: `frontend/src/lib/api/auth.ts`
- Auth types: `frontend/src/lib/types/auth.ts`

**Database Migration**:
- Migration file: `backend/migrations/versions/create_users_table.py`

### Testing Requirements
**Backend Testing** [Source: architecture/coding-standards.md#module-independence-testing]:
```python
# Unit tests - Inside module (modules/user_management/tests/)
def test_user_entity_validation():
    # Test pure domain logic, no external dependencies
    pass

def test_authenticate_user_use_case():
    # Mock protocol interfaces, not implementations
    mock_user_repo = AsyncMock(spec=UserRepositoryProtocol)
    mock_password_service = AsyncMock(spec=PasswordServiceProtocol)
    # Test business logic with mocked protocols
    pass

# Integration tests - Test protocol compliance
def test_user_satisfies_owner_protocol():
    user = User.create(email="test@example.com", name="Test User")
    # Type checker validates this assignment
    owner: OwnerProtocol = user  # If other modules need User as Owner
    assert owner.get_email() == "test@example.com"

# API tests - Full request/response with real implementations
def test_auth_endpoints_with_real_database():
    # Real SQLAlchemy repository, real bcrypt service
    # Test actual protocol compliance at runtime
    pass
```

**Frontend Testing** [Source: architecture/source-tree.md#frontend-tests]:
```typescript
// Component tests
test('Login form validates input and submits correctly')
test('Register form provides real-time validation feedback')
test('Authentication state updates correctly on login')

// Integration tests
test('Auth store manages tokens correctly')
test('API client handles authentication errors')
test('Route guards protect authenticated pages')
```

### Technical Constraints
**Security Requirements** [Source: architecture/tech-stack.md#security-stack]:
- Passwords: bcrypt hashing with salt rounds = 12
- JWT tokens: HS256 algorithm for MVP simplicity
- HTTPS only: TLS 1.3 for production
- Rate limiting: 5 attempts per minute per IP for auth endpoints
- Input validation: Email regex, password strength, SQL injection protection

**Mobile Performance** [Source: architecture/tech-stack.md#mobile-optimization]:
- Touch targets: 44px minimum for all authentication form elements
- Bundle impact: Authentication module should add <10KB to frontend bundle
- Token storage: Secure storage with automatic cleanup on expiry
- Network optimization: Minimize token refresh requests through intelligent timing

**Architecture Integration** [Source: architecture/coding-standards.md#module-independence]:
- **Module Independence**: Zero cross-module imports, communication via protocols only
- **Protocol-Based Implementation**: Static duck typing validated by Pyright
- **user_management Module**: Unified User + Auth bounded context (no artificial separation)
- **External Resources**: SQLAlchemy, bcrypt, JWT libraries ONLY in infrastructure layer
- **Tests Inside Module**: All tests in modules/user_management/tests/ directory
- **No Performance Tests**: Focus on unit, integration, and API testing for MVP
- **Critical Problem Prevention**:
  - SQLAlchemy ONLY in infrastructure (not application/domain)
  - Real protocol implementation (no ServiceImpl without Protocol)
  - Client-side protocols in domain/ports/
  - No unnecessary performance testing

## Testing

Dev Note: Story Requires the following tests:

- [ ] **pytest Unit Tests**: location: `modules/user_management/tests/test_*.py` (inside module), coverage requirement: 80%
- [ ] **pytest Integration Tests**: location: `modules/user_management/tests/test_integration.py` (inside module)
- [ ] **Vitest Component Tests**: location: `frontend/tests/unit/auth/`
- [ ] **Playwright E2E**: location: `frontend/tests/e2e/auth-flow.spec.ts`
- [ ] **NO Performance Tests**: Per MVP architecture standards

Manual Test Steps:
- Register new user through frontend form and verify account creation
- Login with valid credentials and verify JWT tokens are received
- Access protected route with valid token and verify access granted
- Test token refresh before expiry and verify seamless user experience
- Test logout functionality and verify tokens are invalidated
- Verify mobile responsive design on authentication forms (320px viewport)
- Test authentication error states with invalid credentials

## Dev Agent Record

### Agent Model Used: {{Agent Model Name/Version}}

### Debug Log References

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update]]
[[LLM: (Dev Agent) If the debug is logged to during the current story progress, create a table with the debug log and the specific task section in the debug log - do not repeat all the details in the story]]

### Completion Notes List

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update - remove this line to the SM]]
[[LLM: (Dev Agent) Anything the SM needs to know that deviated from the story that might impact drafting the next story.]]

### Change Log

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update- remove this line to the SM]]
[[LLM: (Dev Agent) Track document versions and changes during development that deviate from story dev start]]

| Date | Version | Description | Author |
| :--- | :------ | :---------- | :----- |
