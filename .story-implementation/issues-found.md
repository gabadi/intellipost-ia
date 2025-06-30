# Blocking Issues - Story 6.1 (Updated with UX Review)

## REQUIRED-FOR-COMPLETION (Must Fix) - BLOCKERS

### 🚨 CRITICAL UX BLOCKERS (from Playwright testing)

#### 1. CORS Configuration Missing
- Frontend (localhost:4000) cannot communicate with backend (localhost:8080)
- Error: "Disallowed CORS origin"
- **Fix**: Add CORS middleware to FastAPI with proper origins

#### 2. Authentication UI Components Missing
- No login/register forms implemented in frontend
- No authentication-related components found
- **Fix**: Implement login/register forms with mobile-first design

#### 3. Frontend-Backend Integration Gap
- No authentication store or state management
- No persistent authentication sessions
- **Fix**: Create authentication store and session management

### 🔒 SECURITY BLOCKERS

#### 4. Distributed Rate Limiting Not Implemented
- Current rate limiting is per-instance, not distributed
- **Fix**: Implement Redis-based distributed rate limiting

#### 5. CSRF Protection Missing
- Cookie-based authentication vulnerable to CSRF attacks
- **Fix**: Add CSRF token validation middleware

#### 6. JWT Secret Key Validation
- No validation of secret key strength
- **Fix**: Validate key length and randomness on startup

### 🔧 TECHNICAL BLOCKERS

#### 7. Database Migration Not Applied
- Migration file exists but not executed
- **Fix**: Run alembic upgrade head

#### 8. Environment Configuration Issues
- Development environment not properly configured
- Dependencies missing, virtual environment not active
- **Fix**: Proper environment setup with docker compose

#### 9. Token Blacklisting Not Implemented
- Cannot revoke access tokens before expiry
- **Fix**: Add Redis-based token blacklist

#### 10. Auth Middleware Not Integrated
- Endpoints remain unprotected
- **Fix**: Apply require_user dependency to protected routes
