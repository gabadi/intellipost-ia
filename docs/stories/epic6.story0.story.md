# Story 6.0: Architecture Migration for User Authentication Foundation

## Status: Draft

## Story

- As an IntelliPost AI development team
- I want to migrate the current architecture to support Epic 6 Story 1 (User Authentication & JWT System)
- so that we can implement user authentication on a clean, maintainable architecture foundation that adheres to BMAD hexagonal architecture principles

## Acceptance Criteria (ACs)

1. **AC1: Settings Configuration Compatibility**
   - [ ] Settings configuration uses correct pydantic-settings BaseSettings syntax
   - [ ] Environment variable loading works correctly for all environments (dev, test, prod)
   - [ ] Database connections can be established using settings configuration
   - [ ] Settings validation works properly for production environment checks
   - [ ] All existing services can access configuration without import errors

2. **AC2: Unified User Management Module**
   - [ ] auth and user modules are merged into single user_management module
   - [ ] User entity and authentication logic are in unified bounded context
   - [ ] User domain, application, and infrastructure layers are properly organized
   - [ ] All cross-references between auth and user modules are eliminated
   - [ ] Module follows hexagonal architecture with protocol-based interfaces

3. **AC3: Protocol-Based Module Independence**
   - [ ] All cross-module imports are eliminated (zero violations in tach check)
   - [ ] Modules communicate only via protocol interfaces in domain/ports/
   - [ ] Protocol contracts are clearly defined for all inter-module communication
   - [ ] Each module can be developed and tested independently
   - [ ] Static type checking validates protocol compliance

4. **AC4: Application Layer Foundation**
   - [ ] Application layer directory structure is created as per tach.toml requirements
   - [ ] Use case orchestration pattern is established for cross-module coordination
   - [ ] Application services provide clean interfaces for API layer consumption
   - [ ] Dependency injection pattern is ready for JWT service integration
   - [ ] Application layer enforces business rules without violating module boundaries

5. **AC5: Test Infrastructure Migration**
   - [ ] Module-specific tests are moved inside their respective modules
   - [ ] Global test directory contains only integration and system-level tests
   - [ ] Test fixtures and conftest files are properly organized per module
   - [ ] Module tests can run independently without cross-module dependencies
   - [ ] Test coverage is maintained at 80% or higher for migrated modules

6. **AC6: Architecture Validation**
   - [ ] tach architecture validation passes with zero violations
   - [ ] Pyright type checking passes with strict settings
   - [ ] All existing functionality works after migration
   - [ ] Database migrations run successfully
   - [ ] Docker containers build and run successfully

## Tasks / Subtasks

- [ ] **Task 1: Fix Settings Configuration Critical Issue** (AC: 1)
  - [ ] Update Settings class to use correct pydantic-settings v2 syntax
  - [ ] Fix model_config usage for environment variable loading
  - [ ] Test configuration loading in all environments (dev, test, prod)
  - [ ] Validate database connection using fixed settings
  - [ ] Update any services that import settings to use correct interface

- [ ] **Task 2: Create Application Layer Foundation** (AC: 4)
  - [ ] Create backend/application directory structure
  - [ ] Define application service protocols for cross-module orchestration
  - [ ] Create dependency injection container pattern
  - [ ] Implement use case orchestration pattern
  - [ ] Update tach.toml to reflect actual application layer structure

- [ ] **Task 3: Protocol Extraction and Cross-Module Import Elimination** (AC: 3)
  - [ ] Identify all protocol interfaces needed for module communication
  - [ ] Extract protocols to domain/ports/ directories within each module
  - [ ] Replace direct cross-module imports with protocol-based communication
  - [ ] Implement protocol adapters where necessary
  - [ ] Validate zero cross-module imports with tach check

- [ ] **Task 4: User Management Module Unification** (AC: 2, 5)
  - [ ] Create new modules/user_management directory structure
  - [ ] Merge User entity from user module and auth logic from auth module
  - [ ] Reorganize domain, application, and infrastructure layers
  - [ ] Move module-specific tests to modules/user_management/tests/
  - [ ] Update imports and dependencies to reference unified module

- [ ] **Task 5: Test Infrastructure Reorganization** (AC: 5)
  - [ ] Move module-specific tests from global tests/ to module directories
  - [ ] Update test fixtures and conftest files for module independence
  - [ ] Reorganize global tests to contain only integration/system tests
  - [ ] Validate test isolation and independent execution
  - [ ] Ensure test coverage is maintained during migration

- [ ] **Task 6: Architecture Validation and Integration** (AC: 6)
  - [ ] Run tach check and resolve all architecture violations
  - [ ] Run Pyright type checking and resolve all type errors
  - [ ] Test all existing functionality after migration
  - [ ] Validate database connections and migrations
  - [ ] Test Docker build and container execution

## Dev Technical Guidance

### Critical Issues Identified

**Settings Configuration Problem**:
Current pydantic-settings usage is incompatible with the library version, causing:
- Import failures in services trying to access settings
- Database connection failures
- Environment variable loading failures
- Development environment startup failures

**Module Architecture Violations**:
Current cross-module imports violate hexagonal architecture principles:
```python
# VIOLATION: Direct cross-module import
from modules.user.domain.user import User  # in auth module

# CORRECT: Protocol-based communication
class UserProtocol(Protocol):
    def get_id(self) -> UUID: ...
    def get_email(self) -> str: ...
```

**Missing Application Layer**:
tach.toml references application layer that doesn't exist, causing:
- Architecture validation failures
- No clear orchestration layer for use cases
- API layer directly coupled to domain services

### Migration Strategy

**Phase 1: Critical Fixes (Days 1-2)**
1. Fix settings configuration for immediate development unblocking
2. Create minimal application layer structure
3. Establish basic protocol communication patterns

**Phase 2: Module Unification (Days 3-4)**
1. Merge auth + user into user_management module
2. Extract and implement protocol interfaces
3. Migrate module-specific tests

**Phase 3: Validation (Day 5)**
1. Architecture compliance validation
2. Integration testing
3. Docker environment validation

### Protocol Design Pattern

```python
# Domain layer defines what it needs from external modules
# modules/user_management/domain/ports/owner_provider_protocol.py
class OwnerProviderProtocol(Protocol):
    async def get_owner_by_user_id(self, user_id: UUID) -> OwnerData | None: ...

# Other modules can satisfy this protocol without import coupling
# modules/product_management/infrastructure/adapters/user_owner_adapter.py
class UserOwnerAdapter:  # Automatically satisfies OwnerProviderProtocol
    async def get_owner_by_user_id(self, user_id: UUID) -> OwnerData | None:
        # Implementation here
        pass
```

### Data Models

**Unified User Entity** (post-migration):
```python
@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
```

### File Structure (Target State)

**Application Layer**:
```
backend/application/
├── __init__.py
├── services/
│   ├── __init__.py
│   └── user_orchestration_service.py
├── protocols/
│   ├── __init__.py
│   └── module_coordination_protocols.py
└── container/
    ├── __init__.py
    └── dependency_injection.py
```

**Unified User Management Module**:
```
backend/modules/user_management/
├── __init__.py
├── domain/
│   ├── entities/
│   │   └── user.py
│   ├── services/
│   │   ├── authentication_service.py
│   │   └── user_service.py
│   └── ports/
│       ├── user_repository_protocol.py
│       ├── password_service_protocol.py
│       └── jwt_service_protocol.py
├── application/
│   └── use_cases/
│       ├── register_user.py
│       ├── authenticate_user.py
│       └── verify_email.py
├── infrastructure/
│   ├── repositories/
│   │   └── sqlalchemy_user_repository.py
│   ├── services/
│   │   ├── bcrypt_password_service.py
│   │   └── jose_jwt_service.py
│   └── models/
│       └── user_model.py
├── api/
│   ├── routers/
│   │   └── auth_router.py
│   └── schemas/
│       └── auth_schemas.py
└── tests/
    ├── unit/
    ├── integration/
    └── conftest.py
```

**Test Organization**:
```
tests/  # Global integration tests only
├── integration/
│   ├── api/
│   │   └── test_auth_api_integration.py
│   └── database/
│       └── test_user_data_integration.py
└── system/
    └── test_authentication_flow.py

backend/modules/user_management/tests/  # Module tests
├── unit/
│   ├── test_user_entity.py
│   └── test_authentication_service.py
├── integration/
│   └── test_user_repository.py
└── conftest.py
```

### Technical Constraints

**Migration Requirements**:
- Zero downtime for development environment
- Maintain all existing functionality during migration
- Preserve test coverage (80% minimum)
- No breaking changes to API contracts
- Docker containers must continue to work

**Architecture Compliance**:
- tach check must pass with zero violations
- Pyright type checking must pass in strict mode
- All protocols must be properly typed
- No circular dependencies allowed
- Module boundaries must be enforced

**Quality Standards**:
- Ruff linting must pass
- All tests must pass after migration
- Code coverage must be maintained
- Documentation must be updated

### Risk Mitigation

**High-Risk Items**:
1. **Settings configuration fix** - Test thoroughly in all environments
2. **Database connectivity** - Validate connection strings and pooling
3. **Module merge complexity** - Incremental approach with validation steps
4. **Test migration** - Verify test isolation and coverage maintenance

**Rollback Plan**:
- Keep original modules until validation is complete
- Use feature branches for each migration phase
- Maintain database compatibility throughout migration
- Have Docker image rollback ready

## Testing

Dev Note: Story Requires the following tests:

- [ ] **Architecture Validation**: tach check passes with zero violations
- [ ] **Type Checking**: Pyright passes in strict mode
- [ ] **Unit Tests**: All existing unit tests pass after migration
- [ ] **Integration Tests**: Database and service integration tests pass
- [ ] **System Tests**: Docker containers build and run successfully
- [ ] **Configuration Tests**: Settings work in dev, test, and prod environments

Manual Test Steps:
- Start development environment after settings fix
- Verify database connections work with new configuration
- Confirm all existing API endpoints respond correctly
- Test Docker container build and startup
- Validate tach architecture compliance
- Run full test suite to ensure no regressions

## Dev Agent Record

### Agent Model Used: {{Agent Model Name/Version}}

### Debug Log References

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update]]
[[LLM: (Dev Agent) If the debug is logged to during the current story progress, create a table with the debug log and the specific task section in the debug log - do not repeat all the details in the story]]

### Completion Notes List

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update - remove this line to the SM]]
[[LLM: (Dev Agent) Anything the SM needs to know that deviated from the story that might impact drafting the next story.]]

### Change Log

[[LLM: (SM Agent) When Drafting Story, leave next prompt in place for dev agent to remove and update- remove this line to the SM]]
[[LLM: (Dev Agent) Track document versions and changes during development that deviate from story dev start]]

| Date | Version | Description | Author |
| :--- | :------ | :---------- | :----- |
