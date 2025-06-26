# Hexagonal Architecture (Ports and Adapters)

## Overview

This project implements **Hexagonal Architecture** (also known as "Ports and Adapters" pattern) to achieve clean separation between business logic and external concerns.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│                  (FastAPI routes, DTOs)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Domain Layer                           │
│              (Business Logic & Ports)                     │
│                                                            │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │    Entities     │  │    Protocols    │                │
│  │   (Product,     │  │   (Ports for    │                │
│  │    User, etc)   │  │   external      │                │
│  │                 │  │   services)     │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Infrastructure Layer                        │
│              (Adapters & Implementations)                 │
│                                                            │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Repositories  │  │    Services     │                │
│  │ (Database impl) │  │  (Email, API    │                │
│  │                 │  │   implementations) │               │
│  └─────────────────┘  └─────────────────┘                │
└────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Ports (Protocols)
**Definition**: Interfaces defined by the domain that specify what external services the business logic needs.

**Location**: `modules/{module}/domain/` directory
**Examples**:
- `EmailServiceProtocol`: Domain needs email capabilities
- `MercadoLibreServiceProtocol`: Domain needs marketplace integration
- `UserRepositoryProtocol`: Domain needs user persistence

### Adapters (Implementations)
**Definition**: Concrete implementations of ports that handle external system integration.

**Location**: `modules/{module}/infrastructure/` directory
**Examples**:
- `SmtpEmailService`: Implements `EmailServiceProtocol` using SMTP
- `MercadoLibreApiService`: Implements `MercadoLibreServiceProtocol` using HTTP API
- `SqlUserRepository`: Implements `UserRepositoryProtocol` using PostgreSQL

## Why Protocols in Domain?

### 1. Dependency Inversion Principle
```python
# Wrong: Domain depends on infrastructure
from infrastructure.email import SmtpEmailService  # Domain → Infrastructure

class UserService:
    def __init__(self):
        self.email_service = SmtpEmailService()  # Tight coupling
```

```python
# Correct: Infrastructure depends on domain
from domain.email_service_protocol import EmailServiceProtocol  # Infrastructure → Domain

class UserService:
    def __init__(self, email_service: EmailServiceProtocol):
        self.email_service = email_service  # Loose coupling
```

### 2. Business-Driven Design
The domain defines **what** it needs, not **how** it's implemented:

```python
# Domain defines business requirements
class EmailServiceProtocol(Protocol):
    async def send_verification_email(self, user: User, link: str) -> bool:
        """Send email verification - WHAT we need"""
        ...

# Infrastructure provides implementation
class SendGridEmailService:
    async def send_verification_email(self, user: User, link: str) -> bool:
        """HOW we implement it using SendGrid"""
        # Implementation details...
```

### 3. Testing Benefits
```python
# Easy to test with mock implementations
class MockEmailService:
    async def send_verification_email(self, user: User, link: str) -> bool:
        return True  # Always succeeds in tests

def test_user_registration():
    user_service = UserService(MockEmailService())
    # Test business logic without external dependencies
```

## File Organization

```
backend/modules/
├── user/
│   ├── domain/
│   │   ├── user.py                    # Entity
│   │   ├── user_repository_protocol.py # Port
│   │   └── user_service.py            # Business Logic
│   ├── infrastructure/
│   │   ├── user_repository.py         # Adapter
│   │   └── user_dto.py               # Data Transfer Objects
│   └── application/
│       └── user_routes.py            # HTTP endpoints
└── communications/
    ├── domain/
    │   └── email_service_protocol.py  # Port
    └── infrastructure/
        └── email_service.py          # Adapter
```

## Benefits of This Architecture

### 1. **Testability**
- Business logic can be tested in isolation
- Easy to mock external dependencies
- Faster test execution

### 2. **Flexibility**
- Can swap implementations without changing business logic
- Support multiple implementations simultaneously
- Easy to add new external services

### 3. **Maintainability**
- Clear separation of concerns
- Changes to external services don't affect business logic
- Easier to understand and modify

### 4. **Development Speed**
- Can develop business logic before external integrations
- Parallel development of domain and infrastructure
- Reduced coupling between teams

## Common Patterns

### Repository Pattern
```python
# Domain defines what persistence is needed
class UserRepositoryProtocol(Protocol):
    async def save(self, user: User) -> User: ...
    async def find_by_email(self, email: str) -> User | None: ...

# Infrastructure provides the implementation
class SqlUserRepository:
    async def save(self, user: User) -> User:
        # SQL implementation
    async def find_by_email(self, email: str) -> User | None:
        # SQL implementation
```

### Service Pattern
```python
# Domain defines external service needs
class PaymentServiceProtocol(Protocol):
    async def process_payment(self, amount: Money, card: Card) -> PaymentResult: ...

# Infrastructure provides implementations
class StripePaymentService: ...
class PayPalPaymentService: ...
```

## Response to PR Comments

### "this is not a protocol? why in domain?"
**Answer**:
1. It IS a Python `typing.Protocol`
2. It belongs in domain because it defines business requirements
3. Infrastructure implements these protocols
4. This follows hexagonal architecture principles

### "This is not a port? why in domain?"
**Answer**:
1. The protocol IS the port
2. Ports are interfaces defined by the domain
3. Domain specifies what it needs from external world
4. Infrastructure provides adapters that implement these ports

## Evolution Strategy

As the application grows:

1. **Phase 1** (Current): Modular monolith with hexagonal architecture
2. **Phase 2**: Extract modules to separate libraries
3. **Phase 3**: Deploy modules as microservices
4. **Phase 4**: Each service maintains its own domain protocols

The hexagonal architecture enables this evolution without major refactoring.
