# Content Generation Tests

This directory contains comprehensive tests for the content generation module, implementing Epic 2 Story 3 ("AI for ML Text Content Generation").

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_runner.py                 # Test runner utility
├── test_performance.py            # Performance and load tests
├── README.md                      # This documentation
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_domain_entities.py    # Domain entity tests
│   └── test_services.py           # Service layer tests
├── integration/                   # Integration tests
│   ├── __init__.py
│   └── test_ai_ml_integration.py  # AI/ML service integration tests
└── api/                          # API tests
    ├── __init__.py
    └── test_content_generation_api.py  # FastAPI endpoint tests
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Domain Entities** (`test_domain_entities.py`):
- `GeneratedContent` entity validation and business rules
- `ConfidenceScore` calculation and thresholds
- `AIGeneration` status management and progress tracking
- Input validation and error handling
- Quality threshold enforcement

**Services** (`test_services.py`):
- `GeminiAIService` content generation and API integration
- `MLCategoryService` category detection and caching
- `TitleGenerationService` SEO optimization and character limits
- `DescriptionGenerationService` mobile-first formatting
- `AttributeMappingService` category-specific attribute mapping
- Mock-based testing for external dependencies

### 2. Integration Tests (`tests/integration/`)

**AI/ML Integration** (`test_ai_ml_integration.py`):
- Google Gemini 2.5 Flash API integration
- MercadoLibre category detection API integration
- Multimodal image processing workflow
- Error recovery and retry mechanisms
- Rate limiting and timeout handling
- Complete workflow orchestration

### 3. API Tests (`tests/api/`)

**FastAPI Endpoints** (`test_content_generation_api.py`):
- POST `/products/{id}/generate` endpoint
- GET `/processing/{id}/status` endpoint
- WebSocket real-time updates
- Request/response validation
- Authentication and authorization
- Error handling and HTTP status codes
- Content validation and enhancement endpoints

### 4. Performance Tests (`test_performance.py`)

**Performance Metrics**:
- Single content generation performance (<5s)
- Concurrent request handling (5+ concurrent)
- Load testing (10+ requests with metrics)
- Memory usage monitoring
- Error handling performance
- Caching effectiveness
- System throughput measurement
- Scalability testing

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx psutil
```

### Using the Test Runner

The test runner provides a convenient interface for running different test types:

```bash
# Run all tests
python tests/test_runner.py --type all

# Run unit tests only
python tests/test_runner.py --type unit

# Run integration tests
python tests/test_runner.py --type integration

# Run API tests
python tests/test_runner.py --type api

# Run performance tests
python tests/test_runner.py --type performance

# Run with coverage
python tests/test_runner.py --type all --coverage

# Run specific test
python tests/test_runner.py --test tests/unit/test_domain_entities.py::TestGeneratedContent::test_create_generated_content_success

# Run tests with markers
python tests/test_runner.py --markers "unit and not slow"

# Generate comprehensive report
python tests/test_runner.py --report
```

### Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run specific test type
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
pytest tests/api/ -m api
pytest tests/test_performance.py -m performance

# Run with coverage
pytest tests/ --cov=modules.content_generation --cov-report=html

# Run specific test
pytest tests/unit/test_domain_entities.py::TestGeneratedContent::test_create_generated_content_success -v

# Run with markers
pytest tests/ -m "unit and not slow"
pytest tests/ -m "integration" --tb=short
```

## Test Markers

Tests are organized with pytest markers for selective execution:

- `unit`: Unit tests (fast, isolated)
- `integration`: Integration tests (external dependencies)
- `api`: API endpoint tests
- `performance`: Performance and load tests
- `slow`: Slow-running tests
- `external`: Tests requiring external services

## Test Configuration

### Environment Variables

For integration tests requiring external services:

```bash
# Google Gemini API
export GEMINI_API_KEY="your_gemini_api_key"

# MercadoLibre API
export ML_API_BASE_URL="https://api.mercadolibre.com"

# Test flags
export RUN_SLOW_TESTS="true"
export RUN_EXTERNAL_TESTS="true"
```

### pytest.ini Configuration

The `pytest.ini` file configures:
- Test discovery patterns
- Markers registration
- Coverage settings
- Output formatting
- Strict mode enforcement

## Test Data and Fixtures

### Shared Fixtures (`conftest.py`)

**Domain Entities**:
- `sample_generated_content`: Complete generated content instance
- `sample_ai_generation`: AI generation with processing status
- `sample_confidence_score`: Confidence score with breakdown
- `sample_image_data`: Multi-image product data

**Service Mocks**:
- `mock_ai_service`: Gemini AI service mock
- `mock_category_service`: ML category service mock
- `mock_title_service`: Title generation service mock
- `mock_description_service`: Description generation service mock
- `mock_attribute_service`: Attribute mapping service mock

**Repository Mocks**:
- `mock_content_repository`: Content persistence mock
- `mock_generation_repository`: Generation tracking mock

**Test Data**:
- `sample_product_data`: Complete product information
- `sample_ml_category_data`: MercadoLibre category structure
- `sample_gemini_response`: AI service response format

### Test Utilities

**Performance Assertions**:
- `assert_performance`: Execution time validation
- `assert_content_quality`: Content quality validation

**Conditional Skipping**:
- `skip_if_no_api_key`: Skip tests without API keys
- `skip_if_slow`: Skip slow tests conditionally
- `skip_if_no_external_deps`: Skip external dependency tests

## Coverage Requirements

### Minimum Coverage Targets

- **Overall Coverage**: 80%
- **Domain Entities**: 95%
- **Services**: 85%
- **Use Cases**: 90%
- **API Endpoints**: 80%

### Coverage Reports

Generate coverage reports:
```bash
# HTML report
pytest tests/ --cov=modules.content_generation --cov-report=html

# Terminal report
pytest tests/ --cov=modules.content_generation --cov-report=term-missing

# XML report (for CI/CD)
pytest tests/ --cov=modules.content_generation --cov-report=xml
```

## Continuous Integration

### Test Pipeline

1. **Unit Tests**: Fast feedback on code changes
2. **Integration Tests**: External service validation
3. **API Tests**: Endpoint functionality verification
4. **Performance Tests**: Performance regression detection
5. **Coverage Analysis**: Code coverage enforcement

### Quality Gates

Tests must pass with:
- 100% unit test success rate
- 90% integration test success rate
- 80% overall code coverage
- No performance regressions (>20% slower)
- All API endpoints returning correct status codes

## Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to appropriate test class in `tests/unit/`
2. **Integration Tests**: Add to relevant integration test module
3. **API Tests**: Add to endpoint test classes
4. **Performance Tests**: Add to performance test module

### Test Organization

- Group related tests in classes
- Use descriptive test names
- Include docstrings for complex tests
- Add appropriate markers
- Use fixtures for common setup

### Mock Strategy

- Mock external dependencies in unit tests
- Use real services in integration tests (when possible)
- Provide realistic mock responses
- Test error conditions with mocks
- Verify mock calls for behavior testing

## Debugging Tests

### Common Issues

1. **Async Test Failures**: Ensure proper `@pytest.mark.asyncio` usage
2. **Mock Configuration**: Verify mock setup matches service interfaces
3. **Environment Variables**: Check required environment variables
4. **Dependency Injection**: Ensure proper service wiring in tests

### Debug Commands

```bash
# Run with verbose output
pytest tests/ -v -s

# Run with pdb on failure
pytest tests/ --pdb

# Run with detailed traceback
pytest tests/ --tb=long

# Run single test with debugging
pytest tests/unit/test_domain_entities.py::TestGeneratedContent::test_create_generated_content_success -v -s --tb=long
```

## Performance Benchmarks

### Expected Performance

- **Single Content Generation**: <5 seconds
- **Concurrent Requests (5)**: <10 seconds total
- **Average Response Time**: <3 seconds
- **Memory Usage**: <50MB increase per generation
- **Error Handling**: <2 seconds response time

### Performance Monitoring

Performance tests automatically measure:
- Response times (avg, median, min, max)
- Memory usage patterns
- Throughput (requests per second)
- Error recovery times
- Cache effectiveness

## Contributing

### Test Guidelines

1. **Write tests first** (TDD approach)
2. **Test behavior, not implementation**
3. **Use meaningful test names**
4. **Test edge cases and error conditions**
5. **Maintain test independence**
6. **Keep tests fast and reliable**

### Review Checklist

- [ ] All test types covered (unit, integration, API, performance)
- [ ] Appropriate markers applied
- [ ] Fixtures used for common setup
- [ ] Error conditions tested
- [ ] Performance benchmarks met
- [ ] Documentation updated
