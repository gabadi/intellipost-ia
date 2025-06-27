# Authentication API Documentation

## Overview

The IntelliPost AI Authentication API provides secure user registration, login, and JWT-based session management. All endpoints follow REST conventions and return JSON responses.

**Base URL**: `http://localhost:8000/auth` (development)
**Authentication**: JWT Bearer tokens
**Content-Type**: `application/json`

## Authentication Flow

1. **Register**: Create new user account
2. **Login**: Authenticate and receive JWT tokens
3. **Access Protected Resources**: Use access token in Authorization header
4. **Refresh Token**: Obtain new access token before expiry
5. **Logout**: Invalidate refresh token

## Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "PENDING_VERIFICATION",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login_at": null,
    "email_verified_at": null
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "message": "Registration successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Email already registered",
  "code": "EMAIL_ALREADY_EXISTS"
}
```

**Validation Requirements:**
- Email: Valid email format, unique
- Password: Minimum 8 characters, mixed case, numbers
- First/Last Name: Optional, max 100 characters

---

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login_at": "2024-01-15T10:30:00Z",
    "email_verified_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "message": "Login successful"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

---

### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 900
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid or expired refresh token",
  "code": "INVALID_REFRESH_TOKEN"
}
```

---

### GET /auth/me

Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login_at": "2024-01-15T10:30:00Z",
    "email_verified_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Missing or invalid authentication token",
  "code": "UNAUTHORIZED"
}
```

---

### POST /auth/logout

Logout user and invalidate refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid refresh token",
  "code": "INVALID_REFRESH_TOKEN"
}
```

## JWT Token Configuration

### Access Tokens
- **Expiry**: 15 minutes (optimized for mobile battery life)
- **Algorithm**: HS256
- **Purpose**: Authorize API requests

### Refresh Tokens
- **Expiry**: 7 days (user convenience)
- **Algorithm**: HS256
- **Purpose**: Obtain new access tokens

### Token Payload
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "exp": 1706191800,
  "iat": 1706191000
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `EMAIL_ALREADY_EXISTS` | Email already registered | 400 |
| `INVALID_EMAIL_FORMAT` | Email format validation failed | 400 |
| `WEAK_PASSWORD` | Password doesn't meet requirements | 400 |
| `INVALID_CREDENTIALS` | Wrong email/password combination | 401 |
| `UNAUTHORIZED` | Missing or invalid JWT token | 401 |
| `INVALID_REFRESH_TOKEN` | Refresh token expired or invalid | 401 |
| `USER_INACTIVE` | User account is suspended/inactive | 403 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_SERVER_ERROR` | Server error | 500 |

## Security Headers

All responses include security headers:

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Rate Limiting

Authentication endpoints are rate-limited to prevent abuse:

- **Registration**: 5 requests per IP per hour
- **Login**: 5 failed attempts per email per 15 minutes
- **Token Refresh**: 10 requests per token per minute

## Example Usage

### JavaScript/TypeScript
```javascript
// Registration
const registerUser = async (userData) => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (response.ok) {
    const { user, tokens } = await response.json();
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    return user;
  }

  throw new Error('Registration failed');
};

// Making authenticated requests
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.ok) {
    return await response.json();
  }

  throw new Error('Failed to get profile');
};
```

### cURL Examples
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Get profile (replace TOKEN with actual access token)
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## Performance Requirements

- **Response Time**: All endpoints must respond within 200ms
- **Throughput**: Support 100 concurrent users
- **Availability**: 99.9% uptime SLA

## Testing

Integration tests are available in `tests/integration/api/test_auth_flow.py`
E2E tests are available in `frontend/tests/e2e/auth-flow.spec.ts`

Run tests:
```bash
# Backend integration tests
cd backend && uv run pytest tests/integration/api/test_auth_flow.py

# Frontend E2E tests
cd frontend && npm run test:e2e
```
