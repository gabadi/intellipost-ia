# Performance Testing

## Overview

Performance tests validate non-functional requirements such as response times, throughput, and scalability. These tests are separate from integration tests and focus specifically on performance metrics.

## Test Categories

### Authentication Performance (`test_auth_timing.py`)

Validates that authentication endpoints meet the <200ms response time requirement for mobile-first user experience.

**Endpoints Tested:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Protected endpoint access

**Performance Criteria:**
- Average response time: <200ms
- 95th percentile response time: <200ms
- Statistical significance with multiple requests

## Running Performance Tests

### Manual Execution (Recommended)

Performance tests are designed for manual execution to avoid impacting CI/CD pipeline performance:

```bash
# Run authentication performance tests
cd tests/performance
python test_auth_timing.py

# With custom parameters
python test_auth_timing.py --url http://localhost:8000 --requests 50

# Save results to JSON
python test_auth_timing.py --output results.json

# Verbose output
python test_auth_timing.py --verbose
```

### Prerequisites

1. **Backend running**: Ensure the FastAPI backend is running on the target URL
2. **Database available**: Performance tests create real users and require database access
3. **Clean state**: Tests create unique users but may impact database performance

### Example Output

```
🚀 Starting Authentication Performance Tests
📍 Target URL: http://localhost:8000
📊 Requests per test: 100
============================================================

✅ PASS POST /auth/register
  Total Requests: 50
  Successful: 50
  Failed: 0
  Average Response Time: 145.23ms
  Median Response Time: 142.10ms
  95th Percentile: 178.45ms
  99th Percentile: 195.20ms
  Min/Max: 98.12ms / 198.45ms

✅ PASS POST /auth/login
  Total Requests: 100
  Successful: 100
  Failed: 0
  Average Response Time: 98.76ms
  Median Response Time: 95.30ms
  95th Percentile: 142.18ms
  99th Percentile: 167.89ms
  Min/Max: 67.23ms / 178.92ms
  Requests/Second: 45.67
```

## Why Separate from Integration Tests?

### Integration Tests Focus
- **Purpose**: Verify functionality and feature correctness
- **Assertions**: `assert response.status_code == 200`
- **Environment**: Test databases with mocked external services
- **Speed**: Fast execution for CI/CD pipelines

### Performance Tests Focus
- **Purpose**: Verify non-functional requirements (speed, load)
- **Assertions**: `assert response_time < 200ms`
- **Environment**: Production-like conditions with real load
- **Speed**: Slower execution with statistical analysis

## Test Structure

### Directory Organization
```
backend/modules/                   # Unit tests co-located with source code
├── auth/domain/authentication_service_test.py
├── auth/infrastructure/jwt_service_test.py
└── user/domain/user_test.py

tests/                            # Integration, performance, e2e only
├── integration/                  # Module interactions and API workflows
├── performance/                  # Non-functional requirements testing
└── e2e/                         # User journey testing
```

### Performance Test Categories

1. **Response Time Tests**: Validate API response times under normal load
2. **Load Tests**: Validate system behavior under expected traffic
3. **Stress Tests**: Determine system limits and breaking points
4. **Spike Tests**: Validate behavior during traffic spikes

## Statistical Analysis

Performance tests use statistical analysis to ensure reliable results:

- **Multiple Requests**: 50-100 requests per endpoint for statistical significance
- **Percentiles**: P95 and P99 response times for outlier analysis
- **Concurrent Load**: Configurable concurrent request simulation
- **Statistical Validation**: Requirements must pass for both average and P95

## Adding New Performance Tests

### 1. Create Test Function
```python
async def test_new_endpoint_performance(self, num_requests: int = 100) -> PerformanceResult:
    """Test new endpoint performance."""
    return await self.test_endpoint_performance(
        endpoint="/api/new-endpoint",
        method="POST",
        payload={"test": "data"},
        num_requests=num_requests
    )
```

### 2. Add to Main Test Suite
```python
# In main() function
new_result = await tester.test_new_endpoint_performance(args.requests)
results.append(new_result)
tester.print_result(new_result)
```

### 3. Define Performance Requirements
Document the performance requirement and rationale:
- Source of requirement (UX spec, business need)
- Target metrics (response time, throughput)
- Test conditions (load, environment)

## Best Practices

### Test Environment
- **Dedicated Environment**: Run on dedicated hardware when possible
- **Consistent Conditions**: Minimize other processes during testing
- **Real Dependencies**: Use real databases and external services
- **Network Conditions**: Consider network latency in targets

### Test Design
- **Realistic Load**: Simulate actual user patterns
- **Statistical Significance**: Use sufficient request volumes
- **Cleanup**: Clean up test data after execution
- **Monitoring**: Track resource usage during tests

### Result Analysis
- **Trends**: Track performance over time
- **Regression Detection**: Compare against baseline metrics
- **Root Cause**: Investigate performance degradations
- **Optimization**: Use results to guide performance improvements

## Integration with Development Workflow

### When to Run Performance Tests
- **Manual**: During performance optimization work
- **Pre-release**: Before major releases or deployments
- **Regression**: When performance issues are suspected
- **Baseline**: After significant architecture changes

### Performance Requirements Source
Performance requirements should be:
- **Documented**: Clearly specified in requirements documents
- **Traceable**: Linked to business or user experience needs
- **Testable**: Measurable with automated tools
- **Realistic**: Achievable given system constraints

### CI/CD Integration (Future)
While currently manual, performance tests can be integrated into CI/CD:
- **Nightly Builds**: Run comprehensive performance suites
- **Release Gates**: Block releases that fail performance criteria
- **Trend Analysis**: Track performance metrics over time
- **Alert Systems**: Notify teams of performance regressions
