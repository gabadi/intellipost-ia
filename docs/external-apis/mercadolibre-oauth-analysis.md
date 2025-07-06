# MercadoLibre OAuth 2.0 Authentication - Technical Analysis Report

## Document Information
- **Analyst:** Mary (Technical Analyst)
- **Date:** July 6, 2025
- **Scope:** OAuth 2.0 Integration Technical Requirements
- **Status:** Research Complete - Ready for Implementation
- **Referenced by:** Epic 6 Story 2 (MercadoLibre OAuth Integration)

---

## Executive Summary

This report provides a comprehensive technical analysis of MercadoLibre's OAuth 2.0 authentication system for integration with IntelliPost AI. The analysis confirms that MercadoLibre uses a robust, industry-standard OAuth 2.0 implementation with specific requirements for mobile applications and multi-country support.

**Key Findings:**
- ✅ **Standard OAuth 2.0 Protocol** - Authorization Code Grant Type (Server Side)
- ✅ **PKCE Support** - Essential for mobile security (recommended for our mobile-first approach)
- ✅ **Multi-Country Support** - Site ID system supports Argentina (MLA), Mexico (MLM), Brazil (MBL), Chile (MLC), Colombia (MCO)
- ⚠️ **Short Token Expiry** - 6-hour access tokens require robust refresh mechanism
- ⚠️ **Manager Account Required** - Only main account users can grant permissions (not collaborators)

---

## OAuth 2.0 Flow Analysis

### 1. Authorization Flow (Server-Side)
```
1. User Redirect → authorization.mercadolibre.com.ar/authorization
2. User Authentication → MercadoLibre Login Interface
3. User Authorization → Permission Grant Screen
4. Authorization Code → Callback to redirect_uri
5. Token Exchange → api.mercadolibre.com/oauth/token
6. Access Token → Ready for API calls
```

### 2. Required OAuth Parameters

#### Authorization Request
```http
GET https://auth.mercadolibre.com.ar/authorization
?response_type=code
&client_id={APP_ID}
&redirect_uri={REGISTERED_URI}
&scope=offline_access read write
&state={CSRF_TOKEN}
&code_challenge={PKCE_CHALLENGE}    # Optional but recommended
&code_challenge_method=S256         # When using PKCE
```

#### Token Exchange Request
```http
POST https://api.mercadolibre.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id={APP_ID}
&client_secret={APP_SECRET}
&code={AUTHORIZATION_CODE}
&redirect_uri={SAME_AS_AUTH_REQUEST}
&code_verifier={PKCE_VERIFIER}      # When using PKCE
```

### 3. Token Response Structure
```json
{
  "access_token": "APP_USR-123456789...",
  "token_type": "bearer",
  "expires_in": 21600,
  "scope": "offline_access read write",
  "user_id": 123456789,
  "refresh_token": "TG-123456789..."
}
```

---

## Country-Specific Implementation

### Site ID Mapping
| Country   | Site ID | Domain               | Auth URL                                    |
|-----------|---------|----------------------|---------------------------------------------|
| Argentina | MLA     | .com.ar              | auth.mercadolibre.com.ar/authorization     |
| Mexico    | MLM     | .com.mx              | auth.mercadolibre.com.mx/authorization     |
| Brazil    | MBL     | .com.br              | auth.mercadolibre.com.br/authorization     |
| Chile     | MLC     | .cl                  | auth.mercadolibre.cl/authorization         |
| Colombia  | MCO     | .com.co              | auth.mercadolibre.com.co/authorization     |

### Implementation Requirements
- **Country Detection**: Must determine user's country to use correct auth URL
- **Site ID Storage**: Store user's site_id for subsequent API calls
- **Domain Mapping**: Authentication domain must match user's marketplace
- **Redirect URI**: Must be registered for each country domain

---

## Security Requirements & PKCE Implementation

### PKCE (Proof Key for Code Exchange) - RECOMMENDED
```python
# PKCE Implementation Example
import base64
import hashlib
import secrets

# Generate code verifier (43-128 characters)
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

# Generate code challenge (SHA256 of verifier)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).decode('utf-8').rstrip('=')

# Authorization URL with PKCE
auth_url = f"https://auth.mercadolibre.com.ar/authorization"
           f"?response_type=code"
           f"&client_id={APP_ID}"
           f"&redirect_uri={REDIRECT_URI}"
           f"&scope=offline_access read write"
           f"&state={STATE}"
           f"&code_challenge={code_challenge}"
           f"&code_challenge_method=S256"
```

### Security Validations Required
1. **State Parameter**: CSRF protection - must validate state in callback
2. **Redirect URI**: Must match exactly with registered URI
3. **HTTPS Only**: Redirect URIs must use HTTPS in production
4. **Code Verifier**: Store securely during OAuth flow (session/cache)

---

## Token Management

### Access Token Characteristics
- **Validity**: 6 hours from generation
- **Format**: Bearer token (APP_USR-xxxxx format)
- **Usage**: Include in Authorization header for API requests
- **Scopes**: "offline_access read write" (all required for publishing)

### Refresh Token Process
- **Validity**: 6 months from generation
- **Single Use**: Each refresh generates new access + refresh tokens
- **Automatic Refresh**: Must implement before 6-hour expiry
- **Storage**: Encrypt and store securely in database

#### Refresh Token Request
```http
POST https://api.mercadolibre.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&client_id={APP_ID}
&client_secret={APP_SECRET}
&refresh_token={CURRENT_REFRESH_TOKEN}
```

### Token Invalidation Triggers
1. **Password Change**: User changes MercadoLibre password
2. **App Secret Refresh**: Developer regenerates app secret
3. **User Revocation**: User manually revokes app permissions
4. **Inactivity**: No API requests for 4 months
5. **Account Type Change**: User changes from manager to collaborator

---

## Scopes and Permissions

### Available Scopes
- **`read`**: View user data, listings, account information
- **`write`**: Create/modify listings, manage account data
- **`offline_access`**: Obtain refresh tokens for extended access

### Permission Requirements
- **Manager Account Only**: Only main account users can grant permissions
- **Collaborator Limitation**: Collaborator accounts cannot authorize apps
- **Validation**: Must check account type during OAuth flow

---

## Rate Limits and Error Handling

### Rate Limiting
- **Error Code**: `429 - local_rate_limited`
- **Response**: Temporary request rejection
- **Recommendation**: Implement exponential backoff (retry after few seconds)
- **Scope**: Applies to both OAuth and API endpoints

### Common OAuth Error Codes
```json
{
  "error": "invalid_client",
  "error_description": "the client_id and/or client_secret provided is invalid"
}

{
  "error": "invalid_scope",
  "error_description": "the requested scope is invalid, unknown, or malformed"
}

{
  "error": "invalid_grant",
  "error_description": "The provided authorization grant is invalid"
}
```

### HTTP Status Codes
- **400**: Bad Request (invalid parameters)
- **401**: Unauthorized (invalid credentials)
- **403**: Forbidden (insufficient permissions/blocked IP)
- **429**: Too Many Requests (rate limited)

---

## Mobile Application Considerations

### PKCE Implementation (MANDATORY for Mobile)
- **Code Challenge Method**: S256 (SHA-256 recommended over plain)
- **Code Verifier Length**: 43-128 characters (base64url encoded)
- **Storage**: Secure temporary storage during OAuth flow
- **Validation**: Server must validate code_verifier in token exchange

### Mobile-Specific Requirements
1. **In-App Browser**: Use system browser or Custom Tabs for OAuth flow
2. **Deep Links**: Handle redirect URI with custom scheme (e.g., `intellipost://oauth/callback`)
3. **Secure Storage**: Store tokens in Keychain (iOS) or Keystore (Android)
4. **Token Refresh**: Background refresh before expiry to maintain session
5. **Network Handling**: Robust error handling for mobile network conditions

---

## Technical Implementation Recommendations

### 1. Database Schema Adjustments
```sql
ALTER TABLE ml_credentials
ADD COLUMN ml_site_id CHAR(3) DEFAULT 'MLA',  -- Country marketplace
ADD COLUMN ml_auth_domain VARCHAR(255),        -- Auth domain used
ADD COLUMN pkce_code_challenge VARCHAR(128),   -- Temporary PKCE storage
ADD COLUMN pkce_code_verifier VARCHAR(128);    -- Temporary PKCE storage
```

### 2. OAuth Service Enhancements
```python
class MercadoLibreOAuthService:
    SITE_DOMAINS = {
        'MLA': 'mercadolibre.com.ar',
        'MLM': 'mercadolibre.com.mx',
        'MBL': 'mercadolibre.com.br',
        'MLC': 'mercadolibre.cl',
        'MCO': 'mercadolibre.com.co'
    }

    def get_auth_url(self, site_id: str, redirect_uri: str) -> dict:
        # Generate PKCE parameters
        # Build country-specific auth URL
        # Return auth_url, state, code_verifier for storage
        pass

    def exchange_code(self, site_id: str, code: str, code_verifier: str) -> dict:
        # Country-specific token endpoint
        # Include PKCE verification
        # Return tokens + user info
        pass
```

### 3. Error Handling Strategy
```python
class MLOAuthError(Exception):
    def __init__(self, error_code: str, description: str, http_status: int = None):
        self.error_code = error_code
        self.description = description
        self.http_status = http_status
        super().__init__(f"{error_code}: {description}")

# Specific error classes
class MLInvalidClientError(MLOAuthError): pass
class MLInvalidGrantError(MLOAuthError): pass
class MLRateLimitedError(MLOAuthError): pass
class MLInsufficientPermissionsError(MLOAuthError): pass
```

---

## API Testing Strategy

### Test Environment
- **Test Users**: MercadoLibre provides test user accounts for development
- **Test App**: Register test application in MercadoLibre Developer Portal
- **Sandbox**: Full OAuth flow testing without affecting production data

### Test Scenarios
1. **Happy Path**: Complete OAuth flow with valid manager account
2. **PKCE Flow**: Verify PKCE parameters are properly validated
3. **Error Handling**: Test with invalid credentials, expired codes, wrong redirect URI
4. **Token Refresh**: Verify automatic refresh before expiry
5. **Multi-Country**: Test with different site_id values
6. **Rate Limiting**: Test behavior under rate limit conditions
7. **Account Types**: Verify collaborator account rejection

### Mock Testing for CI/CD
```python
# For integration tests - mock MercadoLibre responses
@pytest.fixture
def mock_ml_oauth_responses():
    with responses.RequestsMock() as rsps:
        # Mock authorization endpoint
        rsps.add(responses.POST,
                "https://api.mercadolibre.com/oauth/token",
                json={"access_token": "test_token", "expires_in": 21600})
        yield rsps
```

---

## Security Best Practices

### 1. Credential Management
- **App Secret**: Store in secure environment variables (never in code)
- **Token Encryption**: Encrypt access/refresh tokens in database using AES-256
- **Key Rotation**: Plan for regular app secret rotation
- **Access Logs**: Log OAuth attempts without sensitive data

### 2. HTTPS Requirements
- **Production**: All redirect URIs must use HTTPS
- **Development**: localhost with HTTP allowed for testing
- **Certificate Validation**: Verify SSL certificates in API calls

### 3. State Management
- **CSRF Protection**: Generate cryptographically secure state parameter
- **Time Limits**: Expire state parameters after reasonable time (5-10 minutes)
- **Storage**: Store state securely (signed cookies, secure session)

---

## Critical Implementation Warnings

### ⚠️ High Priority Issues
1. **Manager Account Requirement**: UI must clearly indicate only manager accounts can connect
2. **Token Refresh Timing**: Must refresh before 6-hour expiry (implement at 5.5 hours)
3. **Single-Use Refresh**: Never reuse refresh tokens - always save new ones
4. **Country Detection**: Must correctly identify user's marketplace for proper auth URL
5. **PKCE for Mobile**: Mandatory for mobile security - implement properly

### ⚠️ Common Pitfalls to Avoid
1. **Redirect URI Mismatch**: Must exactly match registered URI (including trailing slash)
2. **Scope Requirements**: Must request "offline_access" for refresh tokens
3. **Rate Limit Handling**: Don't retry immediately on 429 errors
4. **Token Storage**: Never log access/refresh tokens in plain text
5. **Error Exposure**: Don't expose detailed OAuth errors to end users

---

## Integration Timeline Recommendations

### Phase 1: Basic OAuth (Epic 6 Story 2)
- ✅ Authorization Code flow with PKCE
- ✅ Argentina (MLA) marketplace only
- ✅ Basic token storage and refresh
- ✅ Manager account validation

### Phase 2: Multi-Country Support (Future Epic)
- 🔄 Dynamic country detection
- 🔄 Multiple site_id support
- 🔄 Country-specific UI flows
- 🔄 Cross-border listing capabilities

### Phase 3: Advanced Features (Future Epic)
- 🔄 Token monitoring and health checks
- 🔄 Advanced error recovery
- 🔄 Usage analytics and monitoring
- 🔄 Advanced security features

---

## Conclusion and Recommendations

### ✅ Implementation Ready
MercadoLibre's OAuth 2.0 system is well-documented and follows industry standards. The API is mature and suitable for production integration with the following recommendations:

1. **Start with Argentina (MLA)** for MVP to reduce complexity
2. **Implement PKCE** from the beginning for mobile security
3. **Robust token refresh** is critical due to 6-hour expiry
4. **Clear user communication** about manager account requirements
5. **Comprehensive error handling** for rate limits and auth failures

### 🚀 Ready for Epic 6 Story 2 Implementation
This analysis provides all necessary technical details for the SM to create a comprehensive Story 6.2. The OAuth integration can proceed with confidence based on this research.

---

**Report Status**: ✅ **COMPLETE** - Ready for Story Development
**Next Action**: SM can reference this document in Epic 6 Story 2 technical guidance
**File Location**: `docs/external-apis/mercadolibre-oauth-analysis.md`
