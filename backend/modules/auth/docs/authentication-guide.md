# Authentication Guide

## Overview
This guide explains how to implement authentication in IntelliPost API endpoints.

## Authentication Dependencies

The auth module provides two main dependencies for protecting endpoints:

### 1. CurrentUser (Required Authentication)
Use this dependency when an endpoint requires authentication:

```python
from modules.auth.api.dependencies import CurrentUser

@router.get("/protected")
async def protected_endpoint(current_user: CurrentUser):
    # current_user is guaranteed to be an AuthenticatedUser instance
    return {"user_id": current_user.user_id, "email": current_user.email}
```

### 2. OptionalUser (Optional Authentication)
Use this dependency when an endpoint supports both authenticated and anonymous access:

```python
from modules.auth.api.dependencies import OptionalUser

@router.get("/public")
async def public_endpoint(current_user: OptionalUser):
    if current_user:
        # User is authenticated
        return {"message": f"Hello {current_user.email}"}
    else:
        # Anonymous user
        return {"message": "Hello anonymous"}
```

## Example: Protected Router

Here's a complete example of a protected module router:

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_database_session
from modules.auth.api.dependencies import CurrentUser
from modules.auth.domain.models import AuthenticatedUser

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreateRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_database_session)]
):
    """Create a new product. Requires authentication."""
    # current_user.user_id is available here
    product = await product_service.create(
        user_id=current_user.user_id,
        data=request
    )
    return product

@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_database_session)]
):
    """Get a product by ID. Only owner can access."""
    product = await product_service.get_by_id(product_id)

    # Authorization check
    if product.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return product
```

## Authentication Flow

1. **Client sends request** with Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

2. **Middleware validates token**:
   - Checks if token is blacklisted (Redis)
   - Validates JWT signature and expiration
   - Extracts user information

3. **Dependency injection**:
   - `CurrentUser` dependency receives the authenticated user
   - Endpoint handler can access user information

## Error Responses

### 401 Unauthorized
- Missing Authorization header
- Invalid or expired token
- Token has been revoked

### 403 Forbidden
- User is authenticated but lacks permission
- Resource ownership check failed

## Testing Protected Endpoints

### Using curl:
```bash
# Get access token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r .access_token)

# Use token in protected endpoint
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using HTTPie:
```bash
# Login
http POST localhost:8000/api/auth/login \
  email=user@example.com password=password

# Use token
http GET localhost:8000/api/users/me \
  "Authorization: Bearer <access_token>"
```

### In Frontend (JavaScript):
```javascript
// Store token after login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await loginResponse.json();

// Use token in requests
const response = await fetch('/api/users/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

## Security Middleware

The application includes several security middleware:

### 1. Rate Limiting
- Distributed rate limiting using Redis
- Default: 60 requests per minute per IP
- Headers included: X-RateLimit-Limit, X-RateLimit-Remaining

### 2. CSRF Protection
- Enabled in production for cookie-based auth
- Double-submit cookie pattern
- Header: X-CSRF-Token

### 3. Token Blacklisting
- Tokens can be revoked before expiration
- Logout invalidates all user sessions
- Password change invalidates all sessions

## Best Practices

1. **Always validate ownership** when accessing user-specific resources
2. **Use generic error messages** to prevent user enumeration
3. **Implement proper token rotation** for refresh tokens
4. **Store tokens securely** on client side (see mobile-token-storage.md)
5. **Monitor failed authentication attempts** for security

## Integration Checklist

When adding authentication to a new module:

- [ ] Import CurrentUser or OptionalUser dependency
- [ ] Add dependency to endpoint parameters
- [ ] Implement authorization checks for resource access
- [ ] Handle authentication errors appropriately
- [ ] Update API documentation with auth requirements
- [ ] Add tests for authenticated endpoints
- [ ] Test with expired/invalid tokens
