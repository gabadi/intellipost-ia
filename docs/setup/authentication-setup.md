# Authentication System Setup Guide

## Overview

This guide covers the complete setup of the IntelliPost AI authentication system, including backend JWT services, frontend authentication components, database configuration, and security considerations.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+ with uv package manager
- PostgreSQL 15+
- Git

## Environment Setup

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example environment file
cp .env.example .env
```

Required authentication environment variables:

```bash
# Application Environment
INTELLIPOST_ENVIRONMENT=development
INTELLIPOST_DEBUG=true

# Database Configuration
INTELLIPOST_DATABASE_URL=postgresql+asyncpg://intellipost_user:intellipost_password@localhost:5443/intellipost_dev

# JWT Configuration
INTELLIPOST_SECRET_KEY=your-secret-key-change-in-production
INTELLIPOST_JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
INTELLIPOST_JWT_ALGORITHM=HS256
INTELLIPOST_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
INTELLIPOST_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
INTELLIPOST_API_HOST=127.0.0.1
INTELLIPOST_API_PORT=8000

# CORS Configuration
INTELLIPOST_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### 2. Security Configuration

For production environments, ensure:

```bash
# Production Security (REQUIRED)
INTELLIPOST_ENVIRONMENT=production
INTELLIPOST_DEBUG=false
INTELLIPOST_SECRET_KEY=your-secure-random-256-bit-key
INTELLIPOST_JWT_SECRET_KEY=your-secure-random-256-bit-jwt-key
```

Generate secure keys:
```bash
# Generate secure secret keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Database Setup

Start PostgreSQL (using Docker Compose):
```bash
docker-compose up -d postgres
```

Run database migrations:
```bash
cd backend
uv run alembic upgrade head
```

Verify migration:
```bash
# Check users table exists
psql postgresql://intellipost_user:intellipost_password@localhost:5443/intellipost_dev -c "\\dt"
```

### 3. Start Backend Server

```bash
cd backend
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

### 4. Test Authentication Endpoints

```bash
# Test registration
curl -X POST http://localhost:8000/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Test login
curl -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API Client

Verify `src/lib/api/client.ts` points to correct backend:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Verify frontend is running: http://localhost:3000

### 4. Test Authentication Flow

1. Navigate to http://localhost:3000/auth/register
2. Register a new user account
3. Verify redirection and authentication state
4. Test login/logout functionality

## Authentication Components

### Backend Components

```
backend/modules/auth/
├── api/
│   ├── auth_router.py          # Authentication endpoints
│   └── schemas.py              # Request/response schemas
├── application/
│   └── authentication_service_impl.py  # Business logic
├── domain/
│   ├── authentication_service.py       # Service interface
│   └── user_domain_service.py         # User domain logic
└── infrastructure/
    ├── jwt_service.py          # JWT token management
    ├── middleware.py           # Authentication middleware
    └── password_service.py     # Password hashing
```

### Frontend Components

```
frontend/src/lib/
├── components/auth/
│   ├── AuthModal.svelte       # Authentication modal
│   ├── LoginForm.svelte       # Login form component
│   ├── RegisterForm.svelte    # Registration form component
│   └── PasswordInput.svelte   # Password input with toggle
├── stores/
│   └── auth.ts               # Authentication state management
├── api/
│   └── auth.ts               # Authentication API client
├── types/
│   └── auth.ts               # TypeScript type definitions
└── utils/
    ├── auth-guards.ts        # Route protection utilities
    └── auth-validation.ts    # Form validation utilities
```

## Database Schema

The authentication system uses the `users` table:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VERIFICATION',
    ml_user_id VARCHAR(100),
    ml_access_token VARCHAR(1000),
    ml_refresh_token VARCHAR(1000),
    ml_token_expires_at TIMESTAMPTZ,
    default_ml_site VARCHAR(10) NOT NULL DEFAULT 'MLA',
    auto_publish BOOLEAN NOT NULL DEFAULT FALSE,
    ai_confidence_threshold VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at TIMESTAMPTZ,
    email_verified_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX ix_users_email ON users(email);
```

## Testing Setup

### 1. Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run authentication-specific tests
uv run pytest tests/modules/user/
uv run pytest tests/integration/api/test_auth_flow.py

# Run with coverage
uv run pytest --cov=backend.modules.auth
```

### 2. Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Run authentication E2E tests specifically
npm run test:e2e -- auth-flow.spec.ts
```

## Security Configuration

### 1. Password Security

- **Hashing**: bcrypt with 12 salt rounds
- **Requirements**: Minimum 8 characters, mixed case, numbers
- **Validation**: Client-side and server-side validation

### 2. JWT Security

- **Algorithm**: HS256 (sufficient for MVP)
- **Access Token Expiry**: 15 minutes (mobile battery optimization)
- **Refresh Token Expiry**: 7 days (user convenience)
- **Storage**: HTTP-only cookies (web security)

### 3. API Security

- **CORS**: Configured for allowed origins
- **Rate Limiting**: 5 failed login attempts per email per 15 minutes
- **HTTPS**: Required in production
- **Security Headers**: CSP, XSS protection, frame denial

### 4. Environment Security

Production checklist:
- [ ] Change default secret keys
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring
- [ ] Configure firewall rules

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql postgresql://intellipost_user:intellipost_password@localhost:5443/intellipost_dev -c "SELECT 1;"
```

**2. JWT Token Errors**
```bash
# Verify secret keys are set
echo $INTELLIPOST_JWT_SECRET_KEY

# Check token expiry in logs
tail -f backend/logs/app.log | grep JWT
```

**3. CORS Errors**
```bash
# Verify CORS configuration
curl -H "Origin: http://localhost:3000" \\
     -H "Access-Control-Request-Method: POST" \\
     -X OPTIONS http://localhost:8000/auth/login
```

**4. Frontend Authentication State Issues**
```javascript
// Clear authentication state
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');

// Check browser console for errors
// Verify API endpoints in Network tab
```

### Health Checks

**Backend Health**:
```bash
curl http://localhost:8000/health
```

**Database Health**:
```bash
curl http://localhost:8000/health/db
```

**Authentication Health**:
```bash
# Register test user
curl -X POST http://localhost:8000/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email":"health@example.com","password":"HealthCheck123!","first_name":"Health","last_name":"Check"}'
```

## Performance Monitoring

### Response Time Requirements

All authentication endpoints must respond within 200ms:

```bash
# Test endpoint performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/auth/login

# curl-format.txt content:
#     time_namelookup:  %{time_namelookup}\\n
#        time_connect:  %{time_connect}\\n
#     time_appconnect:  %{time_appconnect}\\n
#    time_pretransfer:  %{time_pretransfer}\\n
#       time_redirect:  %{time_redirect}\\n
#  time_starttransfer:  %{time_starttransfer}\\n
#                     ----------\\n
#          time_total:  %{time_total}\\n
```

### Load Testing

```bash
# Install Apache Bench
brew install httpd

# Test registration endpoint
ab -n 100 -c 10 -H "Content-Type: application/json" \\
   -p registration.json http://localhost:8000/auth/register
```

## Deployment Considerations

### 1. Environment-Specific Configuration

**Development**:
- Debug mode enabled
- Local database
- Permissive CORS
- Short token expiry for testing

**Production**:
- Debug mode disabled
- Secure database connection
- Strict CORS policy
- Production-appropriate token expiry
- HTTPS only
- Rate limiting enabled

### 2. CI/CD Integration

Authentication system should be tested in CI/CD pipeline:

```yaml
# Example GitHub Actions step
- name: Test Authentication System
  run: |
    # Start services
    docker-compose up -d postgres

    # Run backend tests
    cd backend && uv run pytest tests/integration/api/test_auth_flow.py

    # Run frontend tests
    cd frontend && npm run test:e2e -- auth-flow.spec.ts
```

### 3. Monitoring and Alerting

Set up monitoring for:
- Authentication endpoint response times
- Failed login attempt rates
- JWT token validation errors
- Database connection health
- User registration/login metrics

## Support

For authentication system issues:

1. Check logs: `backend/logs/app.log`
2. Verify environment variables are set correctly
3. Test database connectivity
4. Review API documentation: `docs/api/authentication-endpoints.md`
5. Run test suite to identify specific failures

## Migration Guide

If upgrading from a previous authentication system:

1. **Backup existing user data**
2. **Run database migrations**: `uv run alembic upgrade head`
3. **Update environment variables** with new JWT settings
4. **Test authentication flow** with existing users
5. **Update frontend components** to use new API endpoints
6. **Run full test suite** to verify compatibility
