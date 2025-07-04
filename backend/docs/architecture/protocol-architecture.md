# Protocol Architecture: Correct Dependency Management

## Overview

This document describes the correct protocol architecture for the IntelliPost application, where each module owns its protocols and the API defines what it needs from modules.

## Core Principles

### 1. Protocol Ownership
- **API protocols**: Owned by the API layer (`api/protocols/`)
- **Module protocols**: Owned by individual modules (`modules/xxx/domain/ports/`)
- **No shared protocol directories**: No `api.protocols` or shared protocol modules

### 2. Dependency Direction
- **API defines what it needs**: API creates protocols for capabilities it requires
- **Modules implement API protocols**: Modules provide implementations of API protocols
- **No module-to-module protocol sharing**: Modules don't share protocols with each other

### 3. Clean Boundaries
- **API layer**: Only knows about its own protocols and schemas
- **Modules**: Only know about their own internal protocols and API protocols they implement
- **No cross-module dependencies**: Modules are independent of each other

## Architecture Structure

```
backend/
├── api/
│   ├── protocols/           # API-owned protocols
│   │   ├── authentication_provider.py
│   │   ├── product_provider.py
│   │   └── content_provider.py
│   ├── routers/            # API routes using API protocols
│   ├── schemas/            # API request/response models
│   └── container.py        # API dependency injection
├── modules/
│   ├── user_management/
│   │   ├── domain/ports/   # Module-owned protocols
│   │   │   ├── user_repository_protocol.py
│   │   │   ├── jwt_service_protocol.py
│   │   │   └── password_service_protocol.py
│   │   ├── domain/services/ # Enhanced services that naturally satisfy API protocols
│   │   │   └── enhanced_authentication.py
│   │   └── ...
│   ├── product_management/
│   │   ├── domain/ports/   # Module-owned protocols
│   │   │   └── product_repository_protocol.py
│   │   ├── api/            # API protocol implementations
│   │   │   └── product_provider_impl.py
│   │   └── ...
│   └── ...
└── di/
    └── module_discovery.py  # Automatic provider registration
```

## Protocol Types

### API Protocols
**Purpose**: Define what the API needs from modules
**Location**: `api/protocols/`
**Owned by**: API layer
**Implemented by**: Modules

```python
# api/protocols/authentication_provider.py
class AuthenticationProviderProtocol(Protocol):
    async def authenticate_user(self, credentials: AuthenticationCredentials) -> AuthenticationResult | None:
        ...

    async def register_user(self, registration_data: UserRegistrationData) -> AuthenticationResult:
        ...
```

### Module Internal Protocols
**Purpose**: Define module's internal architecture (repository, services, etc.)
**Location**: `modules/xxx/domain/ports/`
**Owned by**: Individual modules
**Implemented by**: Module's infrastructure layer

```python
# modules/user_management/domain/ports/user_repository_protocol.py
class UserRepositoryProtocol(Protocol):
    async def create(self, user: User) -> User:
        ...

    async def get_by_email(self, email: str) -> User | None:
        ...
```

## Implementation Pattern

### 1. API Protocol Definition
The API layer defines what capabilities it needs:

```python
# api/protocols/authentication_provider.py
class AuthenticationProviderProtocol(Protocol):
    """What the API needs for authentication functionality."""

    async def authenticate_user(self, credentials: AuthenticationCredentials) -> AuthenticationResult | None:
        """API needs: authenticate a user with credentials."""
        ...
```

### 2. Module Implementation
Modules implement the API protocols naturally through duck typing in their domain services:

```python
# modules/user_management/domain/services/enhanced_authentication.py
class EnhancedAuthenticationService:
    """Enhanced authentication service that naturally satisfies API protocols."""

    def __init__(self, repositories_and_services):
        # Wire internal module dependencies
        self._user_repository = user_repository
        self._jwt_service = jwt_service
        # ...

    async def authenticate_user(self, credentials: AuthenticationCredentials) -> AuthenticationResult | None:
        """This signature naturally satisfies the API protocol via duck typing."""
        # Implement business logic using domain methods
        user = await self._authenticate_user_domain(credentials.email, credentials.password)
        # Convert and return API-compatible result
        return self._create_authentication_result(user)
```

### 3. Dependency Injection
API container manages API protocol implementations:

```python
# api/container.py
class APIContainer:
    """API-owned dependency container."""

    def __init__(self):
        self._authentication_provider: AuthenticationProviderProtocol | None = None

    def register_authentication_provider(self, provider: AuthenticationProviderProtocol):
        self._authentication_provider = provider

    def get_authentication_provider(self) -> AuthenticationProviderProtocol:
        return self._authentication_provider
```

### 4. Module Discovery
Automatic discovery and registration of implementations:

```python
# di/module_discovery.py
module_discovery.register_authentication_provider(
    "modules.user_management.domain.services.authentication_factory",
    "EnhancedAuthenticationService",
    "create_enhanced_authentication_service"
)
```

## Benefits

### 1. Clean Separation of Concerns
- API layer focuses on HTTP concerns and API contracts
- Modules focus on business logic and domain concerns
- Clear boundaries between layers

### 2. Independent Module Development
- Each module can be developed independently
- No shared protocol dependencies between modules
- Modules can evolve their internal architecture freely

### 3. Testability
- Easy to mock API protocols for testing
- Modules can be tested in isolation
- Clear test boundaries

### 4. Maintainability
- Protocol changes are localized to their owners
- No cascading changes across modules
- Easy to understand dependencies

## Anti-Patterns to Avoid

### ❌ Shared Protocol Directories
```
# DON'T DO THIS
api/
├── protocols/
│   ├── shared/          # ❌ Shared protocols
│   │   ├── user_protocols.py
│   │   └── product_protocols.py
```

### ❌ Module-to-Module Protocol Sharing
```python
# DON'T DO THIS
# modules/product_management/domain/ports/user_service_protocol.py
from modules.user_management.domain.ports.user_repository_protocol import UserRepositoryProtocol  # ❌
```

### ❌ API Importing Module Protocols
```python
# DON'T DO THIS
# api/container.py
from modules.user_management.domain.ports.user_repository_protocol import UserRepositoryProtocol  # ❌
```

### ❌ Cross-Module Dependencies
```python
# DON'T DO THIS
# modules/product_management/application/use_cases/create_product.py
from modules.user_management.domain.services.authentication import AuthenticationService  # ❌
```

## Migration from Current Architecture

### Step 1: Move API Protocols
1. Create `api/protocols/` directory
2. Define API-owned protocols based on what API needs
3. Move relevant protocol definitions from DI container

### Step 2: Create Module Implementations
1. Create `modules/xxx/api/` directories
2. Implement API protocols using module's internal architecture
3. Create factory functions for dependency injection

### Step 3: Update DI Container
1. Create API-owned container (`api/container.py`)
2. Remove module protocol imports from DI
3. Use module discovery for automatic registration

### Step 4: Update API Routes
1. Use API protocols instead of module protocols
2. Remove direct module imports from routes
3. Use dependency injection for protocol implementations

## Examples

### Complete Authentication Flow
1. **API defines**: `AuthenticationProviderProtocol` in `api/protocols/`
2. **Module implements**: `EnhancedAuthenticationService` naturally satisfies protocol via duck typing
3. **DI discovers**: Implementation via `module_discovery`
4. **API uses**: Protocol via dependency injection
5. **No coupling**: API doesn't know about module internals, no adapter classes needed

This architecture ensures clean boundaries, independent modules, and maintainable code while following hexagonal architecture principles.
