# Story 6.2: MercadoLibre OAuth Integration

## Status: Draft

## Story

- As a user of the IntelliPost AI platform
- I want to securely connect my MercadoLibre account through OAuth 2.0 flow
- so that I can publish generated product listings directly to MercadoLibre without manually entering credentials

## Technical Analysis Reference

This story is informed by comprehensive technical analysis documented in:
`docs/external-apis/mercadolibre-oauth-analysis.md`

**Key Technical Findings:**
- Manager account requirement (only main accounts can authorize)
- 6-hour access token expiry with mandatory refresh at 5.5 hours
- PKCE mandatory for mobile security (SHA-256 method)
- Country-specific auth URLs and site_id management
- Single-use refresh tokens with 6-month validity
- Rate limiting (429 errors) and specific ML error codes

## Acceptance Criteria (ACs)

1. **AC1: OAuth 2.0 Flow with PKCE**
   - [ ] Users can initiate OAuth connection flow from dashboard or ML setup page
   - [ ] OAuth flow implements PKCE (Proof Key for Code Exchange) using SHA-256 method (mandatory for mobile)
   - [ ] Users are redirected to MercadoLibre OAuth authorization URL with proper parameters
   - [ ] Authorization code exchange successfully retrieves access and refresh tokens
   - [ ] Failed OAuth attempts provide clear error messages and recovery options
   - [ ] **CRITICAL**: Only manager accounts can authorize - collaborator accounts are rejected with clear messaging
   - [ ] **CRITICAL**: PKCE code verifier securely stored during OAuth flow (43-128 characters)
   - [ ] State parameter validation prevents CSRF attacks

2. **AC2: Pre-Auth Education and UX Flow**
   - [ ] Connection modal explains OAuth benefits before redirecting to MercadoLibre
   - [ ] **CRITICAL**: Pre-auth education clearly states "Manager account required - collaborator accounts cannot connect"
   - [ ] "Connect MercadoLibre" button prominently displayed on dashboard when not connected
   - [ ] OAuth handoff provides seamless user experience with loading states
   - [ ] Clear instructions guide users through MercadoLibre permission screens
   - [ ] Success/failure feedback displayed immediately after OAuth completion
   - [ ] Account type validation error provides clear guidance to use manager account

3. **AC3: Token Storage and Management**
   - [ ] Access tokens (6-hour expiry) and refresh tokens (6-month expiry) stored securely
   - [ ] Basic token storage in ml_credentials table with encrypted credentials
   - [ ] **CRITICAL**: Automatic token refresh implemented at 5.5 hours (before 6-hour expiry)
   - [ ] **CRITICAL**: Single-use refresh tokens - new refresh token saved after each refresh
   - [ ] Token validation ensures credentials are functional before usage
   - [ ] Connection status (connected/disconnected) visible across application
   - [ ] **CRITICAL**: Rate limiting protection - handle 429 errors with exponential backoff
   - [ ] Token invalidation handling (password change, secret refresh, user revocation)

4. **AC4: MercadoLibre Integration Data Storage**
   - [ ] ml_credentials table stores OAuth tokens, app credentials, and user data
   - [ ] **ENHANCED**: MercadoLibre user information (nickname, email, site_id, auth_domain) captured during OAuth
   - [ ] **ENHANCED**: Country-specific data stored (site_id: MLA/MLM/MBL/MLC/MCO, auth_domain used)
   - [ ] Token expiration tracking with automatic refresh capability
   - [ ] Connection health monitoring and validation status tracking
   - [ ] Secure credential management prevents token exposure in logs
   - [ ] **ENHANCED**: PKCE parameters (code_challenge, code_verifier) temporarily stored during OAuth flow

5. **AC5: Connection Status and Management UI**
   - [ ] Connection status clearly visible in publishing screens and dashboard
   - [ ] "Disconnect" functionality allows users to revoke MercadoLibre access
   - [ ] "Reconnect" option provides one-tap re-authentication without re-entering credentials
   - [ ] Connection health indicators show token validity and any issues
   - [ ] Publishing workflows properly handle disconnected state with clear messaging

6. **AC6: Error Handling and Security**
   - [ ] **ENHANCED**: ML-specific error handling (invalid_client, invalid_grant, invalid_scope, rate_limited)
   - [ ] **ENHANCED**: HTTP status code handling (400, 401, 403, 429) with appropriate user messaging
   - [ ] Security headers and CSRF protection for OAuth endpoints
   - [ ] Rate limiting protection on OAuth-related endpoints
   - [ ] No sensitive credentials logged or exposed in error messages
   - [ ] Proper error recovery flows guide users to successful connection
   - [ ] **CRITICAL**: Manager account validation with clear error messaging for collaborator accounts
   - [ ] **CRITICAL**: Redirect URI exact matching (including trailing slash) validation

## Tasks / Subtasks

- [ ] **Task 1: Backend OAuth Infrastructure** (AC: 1, 3, 4, 6)
  - [ ] Create ML credentials entity and repository in user_management module
  - [ ] **ENHANCED**: Implement OAuth service with PKCE flow support (SHA-256 method, mandatory for mobile)
  - [ ] **ENHANCED**: Add ml_credentials table migration with encryption support and country-specific fields
  - [ ] **ENHANCED**: Create MercadoLibre API client for OAuth and token refresh with rate limiting
  - [ ] Implement secure token storage with basic encryption
  - [ ] **ENHANCED**: Add manager account validation service
  - [ ] **ENHANCED**: Implement country-specific auth URL selection
  - [ ] **ENHANCED**: Add token refresh scheduling at 5.5 hours

- [ ] **Task 2: OAuth API Endpoints** (AC: 1, 3, 6)
  - [ ] Create POST /auth/ml/initiate endpoint for OAuth flow start
  - [ ] **ENHANCED**: Create GET /auth/ml/callback endpoint with PKCE verification and manager account validation
  - [ ] Create POST /auth/ml/disconnect endpoint for credential revocation
  - [ ] Create GET /auth/ml/status endpoint for connection status checking
  - [ ] **ENHANCED**: Add input validation and rate limiting to all OAuth endpoints with ML-specific error handling
  - [ ] **ENHANCED**: Add country-specific parameter handling for site_id selection
  - [ ] **ENHANCED**: Implement ML error code mapping (invalid_client, invalid_grant, invalid_scope, rate_limited)

- [ ] **Task 3: Frontend OAuth Integration** (AC: 2, 5)
  - [ ] **ENHANCED**: Create MercadoLibre connection modal with pre-auth education and manager account warning
  - [ ] Implement OAuth flow initiation from dashboard and setup pages
  - [ ] Create connection status components for dashboard and publishing screens
  - [ ] Add disconnect/reconnect functionality with confirmation flows
  - [ ] **ENHANCED**: Implement OAuth callback handling with ML-specific error states and manager account validation
  - [ ] **ENHANCED**: Add country selection UI for multi-marketplace support
  - [ ] **ENHANCED**: Implement rate limiting feedback with retry guidance

- [ ] **Task 4: Token Management and Refresh** (AC: 3, 4)
  - [ ] **ENHANCED**: Implement automatic token refresh logic at 5.5 hours (before 6-hour expiry)
  - [ ] **ENHANCED**: Handle single-use refresh tokens with proper new token storage
  - [ ] Create token validation service for connection health checking
  - [ ] Add background token refresh scheduling
  - [ ] Implement credential encryption/decryption services
  - [ ] Create connection monitoring and health status tracking
  - [ ] **ENHANCED**: Add token invalidation detection (password change, secret refresh, user revocation)
  - [ ] **ENHANCED**: Implement rate limiting backoff for token refresh requests

- [ ] **Task 5: Security and Error Handling** (AC: 6)
  - [ ] Configure CSRF protection for OAuth endpoints
  - [ ] **ENHANCED**: Implement rate limiting for OAuth-related requests with 429 error handling
  - [ ] **ENHANCED**: Add comprehensive error handling for ML-specific OAuth failures
  - [ ] Create secure logging that excludes sensitive credential data
  - [ ] Implement proper error recovery and user guidance flows
  - [ ] **ENHANCED**: Add manager account validation with clear error messaging
  - [ ] **ENHANCED**: Implement PKCE security validation (SHA-256 method)
  - [ ] **ENHANCED**: Add redirect URI exact matching validation
  - [ ] **ENHANCED**: Implement exponential backoff for rate limiting recovery

- [ ] **Task 6: Testing and Integration** (AC: 1, 2, 3, 4, 5, 6)
  - [ ] **ENHANCED**: Unit tests for OAuth service and token management with ML-specific scenarios
  - [ ] **ENHANCED**: Integration tests for OAuth endpoints with mocked MercadoLibre API including error codes
  - [ ] Frontend component tests for OAuth flow and connection status
  - [ ] **ENHANCED**: End-to-end OAuth flow testing with test MercadoLibre application and manager account validation
  - [ ] Security testing for token handling and credential protection
  - [ ] **ENHANCED**: Rate limiting testing with 429 error simulation
  - [ ] **ENHANCED**: PKCE flow testing with SHA-256 method validation
  - [ ] **ENHANCED**: Country-specific auth URL testing for multiple site_id values
  - [ ] **ENHANCED**: Token refresh timing testing (5.5 hour trigger)
  - [ ] **ENHANCED**: Single-use refresh token testing with new token generation

## Dev Technical Guidance

### Critical Implementation Warnings

**⚠️ MANDATORY REQUIREMENTS - FAILURE TO IMPLEMENT WILL BREAK ML INTEGRATION:**

1. **Manager Account Enforcement**
   - Only main MercadoLibre accounts can authorize applications
   - Collaborator accounts MUST be rejected with clear error messaging
   - Account type validation MUST occur during OAuth flow
   - UI MUST clearly communicate this requirement before OAuth initiation

2. **Token Refresh Timing**
   - Access tokens expire in exactly 6 hours
   - Refresh MUST be implemented at 5.5 hours (NOT at expiry)
   - Single-use refresh tokens - each refresh generates new access + refresh tokens
   - NEVER reuse refresh tokens - always save and use the new ones

3. **PKCE Security (Mobile Mandatory)**
   - PKCE is MANDATORY for mobile applications (not optional)
   - Use SHA-256 method (S256) for code challenge
   - Code verifier: 43-128 characters, base64url encoded
   - Code challenge: SHA-256 hash of code verifier
   - Store code verifier securely during OAuth flow

4. **Country-Specific Implementation**
   - Each country has different auth URLs (MLA, MLM, MBL, MLC, MCO)
   - Site ID must be stored and used for all subsequent API calls
   - Auth domain used must be stored for reference
   - Redirect URI registration required for each country domain

5. **Rate Limiting & Error Handling**
   - Handle 429 (rate_limited) errors with exponential backoff
   - Don't retry immediately on rate limit - wait and retry
   - Implement proper ML error code handling (invalid_client, invalid_grant, invalid_scope)
   - Never expose detailed OAuth errors to end users

6. **Security Best Practices**
   - Redirect URI must match EXACTLY (including trailing slash)
   - Never log access/refresh tokens in plain text
   - Encrypt tokens in database storage
   - Validate state parameter to prevent CSRF attacks
   - Use HTTPS only for redirect URIs in production

**📖 Technical Analysis Reference:**
Complete technical specifications available in: `/docs/external-apis/mercadolibre-oauth-analysis.md`

### Previous Story Insights
From Epic 6 Story 1 completion:
- Authentication system fully functional with JWT tokens and user management
- User authentication infrastructure in place with bcrypt password hashing
- FastAPI authentication middleware validates JWT tokens on protected endpoints
- Mobile-optimized JWT strategy: 15-minute access tokens, 7-day refresh tokens
- Users table with proper indexes and authentication ready for ML credentials integration
- Security middleware with rate limiting (5 attempts/min) and proper error handling
- Protocol-based hexagonal architecture maintained with zero cross-module imports

### Data Models
**ML Credentials Entity** [Source: architecture/database-schema.md#ml-credentials-table]:
```python
@dataclass
class MLCredentials:
    id: UUID
    user_id: UUID
    ml_app_id: str
    ml_secret_key_encrypted: str
    ml_access_token_encrypted: str
    ml_refresh_token_encrypted: str
    ml_token_type: str = "bearer"
    ml_expires_at: datetime
    ml_refresh_expires_at: datetime
    ml_scopes: str = "offline_access read write"
    ml_user_id: int
    ml_nickname: Optional[str] = None
    ml_email: Optional[str] = None
    ml_site_id: str = "MLA"  # ENHANCED: MLA/MLM/MBL/MLC/MCO support
    ml_auth_domain: Optional[str] = None  # ENHANCED: Country-specific auth domain used
    ml_is_valid: bool = False
    ml_last_validated_at: Optional[datetime] = None
    ml_validation_error: Optional[str] = None
    # ENHANCED: PKCE temporary storage during OAuth flow
    pkce_code_challenge: Optional[str] = None  # Temporary storage
    pkce_code_verifier: Optional[str] = None   # Temporary storage
    created_at: datetime
    updated_at: datetime
```

**OAuth DTOs** [Source: architecture/source-tree.md#backend-dto]:
```python
class MLOAuthInitiateRequest(BaseModel):
    redirect_uri: str = Field(..., regex=r'^https?://.+')

class MLOAuthInitiateResponse(BaseModel):
    authorization_url: str
    state: str
    code_verifier: str  # For PKCE flow

class MLOAuthCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str

class MLConnectionStatusResponse(BaseModel):
    is_connected: bool
    ml_nickname: Optional[str] = None
    ml_email: Optional[str] = None
    connection_health: str  # "healthy", "expired", "invalid", "disconnected"
    expires_at: Optional[datetime] = None
    last_validated_at: Optional[datetime] = None
```

### API Specifications
**MercadoLibre OAuth Endpoints** [Source: architecture/api-specification.md#mercadolibre-oauth]:
```http
POST /auth/ml/initiate
Authorization: Bearer <access_token>
Content-Type: application/json
{
  "redirect_uri": "http://localhost:3001/ml-setup/callback"
}

GET /auth/ml/callback?code=ABC123&state=xyz789
Authorization: Bearer <access_token>

POST /auth/ml/disconnect
Authorization: Bearer <access_token>

GET /auth/ml/status
Authorization: Bearer <access_token>
```

**MercadoLibre OAuth 2.0 Configuration** [Source: epics/epic6-security-authentication.md#mercadolibre-integration]:
```python
# ENHANCED: Country-specific OAuth configuration
ML_OAUTH_CONFIG = {
    "scope": "offline_access read write",
    "response_type": "code",
    "grant_type": "authorization_code",
    "token_url": "https://api.mercadolibre.com/oauth/token",
    # ENHANCED: Country-specific authorization URLs
    "auth_urls": {
        "MLA": "https://auth.mercadolibre.com.ar/authorization",
        "MLM": "https://auth.mercadolibre.com.mx/authorization",
        "MBL": "https://auth.mercadolibre.com.br/authorization",
        "MLC": "https://auth.mercadolibre.cl/authorization",
        "MCO": "https://auth.mercadolibre.com.co/authorization"
    }
}

# ENHANCED: PKCE Configuration (MANDATORY for mobile security)
PKCE_CONFIG = {
    "code_challenge_method": "S256",  # SHA-256 required
    "code_verifier_length": 128,     # 43-128 characters allowed
    "mandatory_for_mobile": True     # Critical security requirement
}

# ENHANCED: Token refresh timing (critical for 6-hour expiry)
TOKEN_REFRESH_CONFIG = {
    "refresh_before_expiry_hours": 5.5,  # Refresh at 5.5 hours (before 6-hour expiry)
    "access_token_expiry_hours": 6,      # MercadoLibre access token validity
    "refresh_token_expiry_months": 6,    # MercadoLibre refresh token validity
    "single_use_refresh_tokens": True    # Each refresh generates new tokens
}
```

### Component Specifications
**OAuth Service Protocol** [Source: architecture/coding-standards.md#protocol-based-communication]:
```python
class MLOAuthServiceProtocol(Protocol):
    async def initiate_oauth_flow(
        self, 
        user_id: UUID, 
        redirect_uri: str
    ) -> OAuthFlowData: ...
    
    async def handle_oauth_callback(
        self, 
        user_id: UUID, 
        code: str, 
        state: str, 
        code_verifier: str
    ) -> MLCredentials: ...
    
    async def refresh_token(
        self, 
        credentials: MLCredentials
    ) -> MLCredentials: ...
    
    async def validate_connection(
        self, 
        credentials: MLCredentials
    ) -> ConnectionStatus: ...

class MLCredentialsRepositoryProtocol(Protocol):
    async def save(self, credentials: MLCredentials) -> None: ...
    async def find_by_user_id(self, user_id: UUID) -> MLCredentials | None: ...
    async def delete_by_user_id(self, user_id: UUID) -> None: ...
    async def find_expiring_tokens(self, before: datetime) -> List[MLCredentials]: ...
```

**Frontend OAuth Store** [Source: architecture/source-tree.md#frontend-stores]:
```typescript
interface MLConnectionState {
  isConnected: boolean;
  connectionHealth: 'healthy' | 'expired' | 'invalid' | 'disconnected';
  mlNickname: string | null;
  mlEmail: string | null;
  expiresAt: Date | null;
  isLoading: boolean;
  error: string | null;
}

function createMLConnectionStore() {
  const { subscribe, update } = writable<MLConnectionState>({
    isConnected: false,
    connectionHealth: 'disconnected',
    mlNickname: null,
    mlEmail: null,
    expiresAt: null,
    isLoading: false,
    error: null
  });

  return {
    subscribe,
    initiateConnection: async (redirectUri: string) => Promise<void>,
    handleCallback: async (code: string, state: string) => Promise<void>,
    disconnect: async () => Promise<void>,
    checkStatus: async () => Promise<void>
  };
}
```

### File Locations
**Backend MercadoLibre Integration** [Source: architecture/source-tree.md#backend-structure]:
**NOTE**: Integration with existing user_management module following protocol-based architecture

- ML credentials entity: `backend/modules/user_management/domain/entities/ml_credentials.py`
- OAuth service: `backend/modules/user_management/domain/services/ml_oauth.py`
- ML credentials repository protocol: `backend/modules/user_management/domain/ports/ml_credentials_repository_protocol.py`
- OAuth service protocol: `backend/modules/user_management/domain/ports/ml_oauth_service_protocol.py`
- OAuth use cases: `backend/modules/user_management/application/use_cases/`
  - `initiate_ml_oauth.py`
  - `handle_ml_callback.py`
  - `refresh_ml_token.py`
  - `validate_ml_connection.py`
- Repository implementation: `backend/modules/user_management/infrastructure/repositories/sqlalchemy_ml_credentials_repository.py`
- OAuth service implementation: `backend/modules/user_management/infrastructure/services/mercadolibre_oauth_service.py`
- Encryption service: `backend/modules/user_management/infrastructure/services/credential_encryption_service.py`
- SQLAlchemy model: `backend/modules/user_management/infrastructure/models/ml_credentials_model.py`
- OAuth endpoints: `backend/modules/user_management/api/routers/ml_oauth_router.py`
- OAuth schemas: `backend/modules/user_management/api/schemas/ml_oauth_schemas.py`

**Frontend MercadoLibre Integration** [Source: architecture/source-tree.md#frontend-structure]:
- ML connection modal: `frontend/src/lib/components/ml/MLConnectionModal.svelte`
- Connection status indicator: `frontend/src/lib/components/ml/MLConnectionStatus.svelte`
- ML setup page: `frontend/src/routes/(protected)/ml-setup/+page.svelte`
- OAuth callback handler: `frontend/src/routes/(protected)/ml-setup/callback/+page.svelte`
- ML connection store: `frontend/src/lib/stores/ml-connection.ts`
- ML API client: `frontend/src/lib/api/ml-oauth.ts`
- ML types: `frontend/src/lib/types/ml-connection.ts`

**Database Migration**:
- Migration file: `backend/migrations/versions/create_ml_credentials_table.py`

### Testing Requirements
**Backend Testing** [Source: architecture/coding-standards.md#testing-strategy]:
```python
# Unit tests - OAuth service logic
def test_pkce_flow_generation():
    oauth_service = MLOAuthService()
    flow_data = oauth_service.generate_pkce_flow()
    assert len(flow_data.code_verifier) == 128
    assert flow_data.code_challenge_method == "S256"

def test_token_refresh_logic():
    mock_ml_api = AsyncMock(spec=MLAPIClientProtocol)
    oauth_service = MLOAuthService(mock_ml_api)
    # Test token refresh with mocked ML API
    pass

# ENHANCED: ML-specific test scenarios
def test_manager_account_validation():
    # Test that collaborator accounts are rejected
    # Test that only manager accounts can complete OAuth
    pass

def test_country_specific_auth_urls():
    # Test correct auth URL selection for each site_id
    # Test auth_domain storage and validation
    pass

def test_rate_limiting_handling():
    # Test 429 error handling with exponential backoff
    # Test rate limit recovery mechanisms
    pass

def test_token_refresh_timing():
    # Test refresh triggers at 5.5 hours
    # Test single-use refresh token behavior
    pass

def test_ml_error_code_handling():
    # Test invalid_client, invalid_grant, invalid_scope errors
    # Test HTTP status codes: 400, 401, 403, 429
    pass

# Integration tests - Real OAuth flow with mocked ML API
def test_oauth_endpoints_integration():
    # Test complete OAuth flow with httpx-mock for MercadoLibre API
    # Validate token storage and retrieval from database
    pass
```

**Frontend Testing** [Source: architecture/source-tree.md#frontend-tests]:
```typescript
// Component tests
test('ML connection modal explains benefits before OAuth redirect')
test('Connection status indicator shows correct health states')
test('OAuth callback handler processes success and error states')

// Integration tests  
test('ML connection store manages OAuth flow state correctly')
test('API client handles OAuth initiation and callback')
test('Connection status updates across components')
```

### Technical Constraints
**MercadoLibre OAuth Requirements** [Source: architecture/tech-stack.md#external-integrations]:
- OAuth 2.0 with PKCE for mobile security (RFC 7636) - **MANDATORY for mobile applications**
- Access tokens: 6-hour expiry - **CRITICAL: Must refresh at 5.5 hours**
- Refresh tokens: 6-month expiry - **CRITICAL: Single-use tokens (generate new on each refresh)**
- Required scopes: "offline_access read write" - **All three required for publishing**
- HTTPS only for redirect URIs in production
- Rate limiting: 10 OAuth requests per minute per user - **Handle 429 errors with exponential backoff**
- **CRITICAL**: Manager account requirement - **Only main accounts can authorize (not collaborators)**
- **CRITICAL**: Country-specific auth URLs - **Must use correct domain for user's marketplace**
- **CRITICAL**: Redirect URI exact matching - **Including trailing slash must match exactly**

**Security Requirements** [Source: architecture/tech-stack.md#security-stack]:
- Token encryption: AES-256-GCM for credential storage
- CSRF protection: State parameter validation in OAuth flow
- Token storage: Encrypted credentials never logged or exposed
- Rate limiting: OAuth endpoints protected against abuse
- Input validation: OAuth parameters validated for security

**Mobile Performance** [Source: architecture/tech-stack.md#mobile-optimization]:
- OAuth flow optimized for mobile browsers with proper redirects
- Connection status cached to avoid repeated API calls
- Optimistic UI updates during OAuth flow
- Minimal bundle impact: OAuth components should add <5KB to frontend bundle

**Architecture Integration** [Source: architecture/coding-standards.md#module-independence]:
- **Module Integration**: ML OAuth functionality added to existing user_management module
- **Protocol-Based Implementation**: OAuth service follows protocol patterns from authentication
- **Zero Cross-Module Dependencies**: ML credentials isolated within user_management boundary
- **Database Integration**: ml_credentials table extends existing user management schema
- **Error Handling**: OAuth errors follow domain exception hierarchy from Story 6.1

**Critical Implementation Warnings** [Source: docs/external-apis/mercadolibre-oauth-analysis.md]:
- ⚠️ **Manager Account Validation**: UI must clearly indicate only manager accounts can connect
- ⚠️ **Token Refresh Timing**: Must refresh before 6-hour expiry (implement at 5.5 hours)
- ⚠️ **Single-Use Refresh**: Never reuse refresh tokens - always save new ones
- ⚠️ **Country Detection**: Must correctly identify user's marketplace for proper auth URL
- ⚠️ **PKCE for Mobile**: Mandatory for mobile security - implement SHA-256 method properly
- ⚠️ **Rate Limit Handling**: Don't retry immediately on 429 errors - use exponential backoff
- ⚠️ **Token Storage**: Never log access/refresh tokens in plain text
- ⚠️ **Error Exposure**: Don't expose detailed OAuth errors to end users
- ⚠️ **Redirect URI Matching**: Must exactly match registered URI (including trailing slash)

## Testing

Dev Note: Story Requires the following tests:

- [ ] **pytest Unit Tests**: location: `modules/user_management/tests/test_ml_oauth.py` (inside module), coverage requirement: 80%
- [ ] **pytest Integration Tests**: location: `modules/user_management/tests/test_ml_integration.py` (inside module)
- [ ] **Vitest Component Tests**: location: `frontend/tests/unit/ml/`
- [ ] **Playwright E2E**: location: `frontend/tests/e2e/ml-oauth-flow.spec.ts`

Manual Test Steps:
- Navigate to dashboard and verify "Connect MercadoLibre" button is displayed when not connected
- Click connect button and verify pre-auth education modal explains OAuth benefits
- **ENHANCED**: Verify pre-auth modal clearly states "Manager account required"
- Complete OAuth flow through MercadoLibre test application and verify successful connection
- **ENHANCED**: Test with collaborator account and verify rejection with clear error message
- Verify connection status indicator shows "connected" state across dashboard and publishing screens
- Test disconnect functionality and verify connection status updates correctly
- **ENHANCED**: Test token refresh by manually expiring tokens at 5.5 hours and verifying automatic refresh
- **ENHANCED**: Verify single-use refresh tokens generate new tokens on each refresh
- Verify OAuth error handling with invalid codes and network failures
- **ENHANCED**: Test rate limiting by making rapid OAuth requests and verify 429 error handling
- **ENHANCED**: Test country-specific auth URLs for different site_id values
- **ENHANCED**: Test PKCE flow with SHA-256 method and verify security parameters
- **ENHANCED**: Test redirect URI exact matching (including trailing slash variations)

## Dev Agent Record

### Agent Model Used: {{Agent Model Name/Version}}

### Debug Log References

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update]]
[[LLM: (Dev Agent) If the debug is logged to during the current story progress, create a table with the debug log and the specific task section in the debug log - do not repeat all the details in the story]]

### Completion Notes List

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update - remove this line to the SM]]
[[LLM: (Dev Agent) Anything the SM needs to know that deviated from the story that might impact drafting the next story.]]

### File List

[[LLM: (Dev Agent) List every new file created, or existing file modified in a bullet list.]]

### Change Log

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update- remove this line to the SM]]
[[LLM: (Dev Agent) Track document versions and changes during development that deviate from story dev start]]

| Date | Version | Description | Author |
| :--- | :------ | :---------- | :----- |

## QA Results

[[LLM: QA Agent Results]]