# Testing Architecture

This document explains the testing strategy and organization for the IntelliPost AI backend.

## Test Classification

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions, classes, or methods in isolation
- **Characteristics**:
  - No external dependencies (database, HTTP requests, file system)
  - Fast execution (< 1ms per test)
  - Use mocks/stubs for dependencies
  - Test business logic and domain rules
- **Example**: Testing `Product.calculate_confidence_score()` with mocked data

### Integration Tests (`tests/integration/`)
- **Purpose**: Test interactions between components and external systems
- **Characteristics**:
  - Use TestClient for HTTP endpoint testing
  - May use real database connections (test database)
  - Test complete request-response cycles
  - Verify middleware, routing, and serialization
- **Example**: Testing `/health` endpoint with actual HTTP requests

### Module Tests (`tests/modules/`)
- **Purpose**: Test module-specific functionality at various integration levels
- **Structure**:
  - `tests/modules/{module_name}/` - Module-specific tests
  - `tests/modules/shared/` - Cross-module integration tests
- **Mixed Classification**:
  - Some files contain integration tests (using TestClient)
  - Some files contain unit tests (testing domain objects)
  - Classification is determined by test implementation, not location

## Current Test Organization

### Integration Tests (using TestClient)
- `tests/integration/api/test_health.py` - API endpoint integration tests
- `tests/modules/shared/test_main.py` - Application setup integration tests
- `tests/modules/shared/test_health.py` - Health endpoint integration tests

### Unit Tests (testing isolated logic)
- `tests/modules/product/test_*.py` - Product domain logic tests
- `tests/modules/user/test_*.py` - User domain logic tests
- `tests/modules/shared/infrastructure/config/test_*.py` - Configuration tests

## TestClient Usage Clarification

**Question**: "Si corre un TestClient, no es de integración?" (If it runs TestClient, isn't it integration?)

**Answer**: **Yes, absolutely correct!** Any test using `TestClient` is an integration test because:

1. **Full Application Stack**: TestClient instantiates the complete FastAPI application
2. **HTTP Layer**: Tests actual HTTP request/response cycles
3. **Middleware Execution**: All middleware runs during the test
4. **Routing Logic**: Tests complete routing and path resolution
5. **Serialization**: Tests request/response serialization/deserialization

### Proper Classification
- **Integration Tests**: Use `TestClient` to test HTTP endpoints
- **Unit Tests**: Test individual functions/classes with direct method calls

## Best Practices

### For Unit Tests
```python
# Good: Direct method call, testing isolated logic
def test_product_confidence_calculation():
    product = Product(title="Test", price=100)
    score = product.calculate_confidence_score()
    assert score == 0.85

# Good: Testing domain rules in isolation
def test_user_can_create_product():
    user = User(status=UserStatus.VERIFIED)
    assert user.can_create_products() is True
```

### For Integration Tests
```python
# Good: Testing complete HTTP endpoint
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Good: Testing authentication flow
def test_login_endpoint(client):
    response = client.post("/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 200
```

## Migration Plan

To align with proper test classification:

1. **Keep TestClient tests** in integration folders
2. **Create pure unit tests** for domain logic
3. **Move misclassified tests** to appropriate folders
4. **Add pytest markers** to distinguish test types

## Pytest Fixture Best Practices

### TestClient Fixtures
```python
@pytest.fixture
def client():
    """Create test client with proper lifecycle management."""
    with TestClient(app) as test_client:
        yield test_client  # Use yield, not return
```

### Why `yield` over `return`?
- **Resource Management**: Ensures proper cleanup after tests
- **Context Manager Support**: Leverages TestClient's context manager
- **Connection Handling**: Properly closes HTTP connections
- **Memory Management**: Prevents resource leaks in test suites
