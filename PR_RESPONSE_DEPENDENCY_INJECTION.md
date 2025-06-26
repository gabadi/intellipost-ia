# PR Comment Response: Dependency Injection Architecture

## Comment Location
`backend/infrastructure/config/dependencies.py:104` - "Is this OK? why not directly the fastapi depends for everything?"

## Current Implementation Analysis

The current implementation uses a custom `DependencyContainer` class instead of relying solely on FastAPI's built-in `Depends()` mechanism. Here's the architectural justification:

## Why Custom Container vs. Pure FastAPI Depends

### 1. **Hexagonal Architecture Enforcement**
```python
# Current approach - Protocol-based with explicit registration
def register_user_repository(self, repository: UserRepository):
    """Register user repository implementation."""
    self._user_repository = repository

# vs Pure FastAPI - Direct instantiation coupling
def get_user_repository() -> SQLUserRepository:  # Breaks abstraction
    return SQLUserRepository(get_db_connection())
```

**Benefits:**
- Forces infrastructure layer to register Protocol implementations
- Application layer remains decoupled from infrastructure details
- Clear contract boundaries between layers

### 2. **Startup-Time Dependency Validation**
```python
# Current approach - Fail fast at startup
def get_user_repository(self):
    if self._user_repository is None:
        raise RuntimeError("User repository not registered")  # Clear error
    return self._user_repository

# vs Pure FastAPI - Runtime failures
@app.get("/users")
def get_users(repo: UserRepository = Depends(get_user_repo)):
    # Could fail here if dependency not properly configured
```

**Benefits:**
- Application fails fast if dependencies aren't properly registered
- Clear error messages for missing dependencies
- Prevents runtime surprises in production

### 3. **Testing Flexibility**
```python
# Current approach - Easy mocking
def test_user_service():
    container.register_user_repository(MockUserRepository())
    # Test runs with mock

# vs Pure FastAPI - Requires dependency override machinery
def test_user_service():
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()
    # More complex setup
```

**Benefits:**
- Simpler test setup
- No need for FastAPI app instance in unit tests
- Clear dependency substitution

### 4. **Centralized Dependency Management**
The container acts as a registry that makes it explicit what dependencies exist and how they're wired together, improving maintainability.

## Potential Concerns & Responses

### "Isn't this over-engineering?"
**Response:** For a simple CRUD app, yes. But for a modular system with:
- Multiple domain modules (product, user, ai_content, etc.)
- External service integrations (MercadoLibre, AI services)
- Protocol-based architecture for testability

The container provides clear benefits in managing complexity.

### "FastAPI's Depends() is more idiomatic"
**Response:** True, but we use both:
- Container for Protocol registration and lifecycle management
- FastAPI Depends() for actual dependency injection in routes
- Best of both worlds: FastAPI integration + architectural control

## Recommendation

**Keep current approach** because:
1. It properly implements hexagonal architecture principles
2. Provides clear separation of concerns
3. Makes testing easier
4. Follows Domain-Driven Design patterns
5. The complexity is justified by the modular architecture

However, we should:
1. Add proper Protocol type annotations (currently using `Any`)
2. Document the architectural decision in code comments
3. Consider if any dependencies could be simplified for truly simple cases

## Alternative Considered
Pure FastAPI Depends() with Protocol factory functions, but this would:
- Lose startup-time validation
- Make Protocol registration less explicit
- Complicate test setup
- Reduce architectural boundary enforcement

The current approach is appropriate for the application's complexity and architectural goals.
