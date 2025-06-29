# Authentication Setup - LLM Reference

## Quick Start

### Environment Variables
```bash
# Required variables in .env
INTELLIPOST_SECRET_KEY=your-secret-key
INTELLIPOST_JWT_SECRET_KEY=your-jwt-secret-key
INTELLIPOST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5443/db
```

### Backend Setup
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Backend Structure
```
backend/modules/auth/
├── api/auth_router.py          # Endpoints: /auth/register, /auth/login
├── application/authentication_service_impl.py  # Business logic
├── domain/authentication_service.py           # Protocol interface
└── infrastructure/
    ├── jwt_service.py          # JWT token handling
    ├── password_service.py     # bcrypt hashing
    └── secure_storage.py       # Cookie management
```

### Key Components
- **AuthenticationService**: Protocol defining auth operations
- **AuthenticationServiceImpl**: Concrete implementation
- **JWTService**: Token creation/validation
- **PasswordService**: bcrypt hashing with 12 rounds
- **SecureTokenStorage**: HTTP-only cookie management

## API Endpoints

### POST /auth/register
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### POST /auth/login
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### POST /auth/refresh
Uses refresh token from HTTP-only cookie

### POST /auth/logout
Clears authentication cookies

## Database Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'PENDING_VERIFICATION',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

## Security Features
- **Password**: bcrypt hashing, 8+ chars required
- **JWT**: HS256, 15min access token, 7day refresh token
- **Storage**: HTTP-only cookies with CSRF protection
- **Headers**: CSP, XSS protection, CORS configured

## Testing
```bash
# Backend tests
cd backend && uv run pytest tests/modules/user/

# Frontend tests
cd frontend && npm run test:e2e

# Quick API test
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","first_name":"Test","last_name":"User"}'
```

## Common Issues
- **DB connection**: Check PostgreSQL is running
- **JWT errors**: Verify SECRET_KEY is set
- **CORS**: Ensure frontend origin in CORS_ORIGINS
- **Auth state**: Clear localStorage if frontend auth broken
