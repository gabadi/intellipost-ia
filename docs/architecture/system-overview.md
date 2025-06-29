# Architecture Implementation Guide

## LLM Implementation Guide

This document provides exact patterns and code templates for implementing modules in the IntelliPost system. All patterns are proven and tested in the auth module reference implementation.

### Module Implementation Checklist

**For any new module, follow these exact steps:**

1. ✅ Create domain/protocols.py with cross-module interfaces
2. ✅ Create domain/value_objects.py with return types
3. ✅ Create domain/{local_types}.py to avoid cross-dependencies
4. ✅ Create application/{module}_service.py with business logic
5. ✅ Create infrastructure services for external concerns
6. ✅ Create di/{module}_container.py for dependency wiring
7. ✅ Create api/{module}_router.py with HTTP endpoints
8. ✅ Update tach.toml with proper dependencies
9. ✅ Validate: `tach check && pyright modules/{module}/`

---

## Protocol Pattern Template

### Step 1: Domain Protocol Definition

**File**: `modules/{module}/domain/protocols.py`

```python
"""
Domain protocols for {module} module.
Defines interfaces for cross-module communication.
"""
from typing import Protocol, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .value_objects import Created{Module}Result

# Cross-module input protocol
class {External}DataProtocol(Protocol):
    """Protocol for data from external modules."""
    id: UUID
    key_field: str
    status: {Module}Status  # Local enum to avoid dependencies

    @property
    def is_active(self) -> bool: ...

# External service protocol
class {External}ServiceProtocol(Protocol):
    """Protocol for external service operations."""
    async def create_{entity}(
        self,
        data: Create{Entity}Protocol
    ) -> {External}DataProtocol: ...

    async def get_{entity}_by_id(
        self,
        entity_id: UUID
    ) -> {External}DataProtocol | None: ...

# Internal service protocol (for DI)
class {Module}ServiceProtocol(Protocol):
    """Protocol for {module} service operations."""
    async def process_{action}(
        self,
        input_data: {Input}Protocol,
        external_service: {External}ServiceProtocol
    ) -> "Created{Module}Result": ...
```

### Step 2: Local Domain Types

**File**: `modules/{module}/domain/{module}_status.py`

```python
"""
Local {module} domain types.
Avoids cross-module dependencies by defining local enums.
"""
from enum import Enum

class {Module}Status(Enum):
    """Local status enum for {module} domain."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROCESSING = "processing"
    COMPLETED = "completed"

    @classmethod
    def from_external_status(cls, external_status: str) -> "{Module}Status":
        """Convert external status to local status."""
        # Map external enum values to local enum values
        mapping = {
            "active": cls.ACTIVE,
            "inactive": cls.INACTIVE,
            # Add mappings as needed
        }
        return mapping.get(external_status, cls.INACTIVE)
```

### Step 3: Value Objects Pattern

**File**: `modules/{module}/domain/value_objects.py`

```python
"""
Value objects for {module} module.
Implements Go principle: return concrete instances.
"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class Created{Module}Result:
    """
    Value object for {module} creation results.
    Returned by service operations - concrete type with embedded logic.
    """
    entity_id: UUID
    key_field: str
    status: str
    created_at: datetime
    processing_metadata: dict[str, str] | None = None

    @property
    def is_ready_for_processing(self) -> bool:
        """Business logic embedded in value object."""
        return self.status == "active" and self.processing_metadata is not None

    @property
    def display_status(self) -> str:
        """Human-readable status with business rules."""
        if self.status == "processing":
            return f"Processing... ({len(self.processing_metadata or {})} steps)"
        return self.status.title()

@dataclass(frozen=True)
class {Module}ProcessingResult:
    """Result of {module} processing operations."""
    entity_id: UUID
    success: bool
    result_data: dict[str, str] | None = None
    error_message: str | None = None
    processing_time_ms: int | None = None

    @property
    def has_errors(self) -> bool:
        return not self.success or self.error_message is not None
```

### Step 4: Application Service Pattern

**File**: `modules/{module}/application/{module}_service.py`

```python
"""
{Module} service implementation.
Implements business logic using protocol-based dependencies.
"""
from uuid import UUID, uuid4
from datetime import datetime, UTC

from modules.{module}.domain.protocols import (
    {External}ServiceProtocol,
    {Module}ServiceProtocol,
    {Input}Protocol
)
from modules.{module}.domain.value_objects import (
    Created{Module}Result,
    {Module}ProcessingResult
)
from modules.{module}.domain.{module}_status import {Module}Status

class {Module}Service:
    """
    {Module} service implementation.
    Accepts protocols, returns value objects (Go principle).
    """

    def __init__(
        self,
        external_service: {External}ServiceProtocol,
        processing_service: ProcessingServiceProtocol,
        settings: SettingsProtocol
    ) -> None:
        self.external_service = external_service
        self.processing_service = processing_service
        self.settings = settings

    async def create_{entity}(
        self,
        input_data: {Input}Protocol
    ) -> Created{Module}Result:
        """
        Create new {entity} with external service coordination.

        Args:
            input_data: Input protocol with required data

        Returns:
            Created{Module}Result: Concrete value object
        """
        # Create entity via external service protocol
        external_entity = await self.external_service.create_{entity}(input_data)

        # Process with internal logic
        processing_result = await self.processing_service.process(
            entity_id=external_entity.id,
            entity_data=external_entity
        )

        # Return concrete value object
        return Created{Module}Result(
            entity_id=external_entity.id,
            key_field=external_entity.key_field,
            status=external_entity.status.value,
            created_at=datetime.now(UTC),
            processing_metadata=processing_result.metadata
        )

    async def process_{action}(
        self,
        entity_id: UUID,
        action_data: {Action}Protocol
    ) -> {Module}ProcessingResult:
        """
        Process {action} for existing entity.

        Args:
            entity_id: Target entity ID
            action_data: Action-specific data protocol

        Returns:
            {Module}ProcessingResult: Concrete processing result
        """
        start_time = datetime.now(UTC)

        try:
            # Get entity via external service protocol
            entity = await self.external_service.get_{entity}_by_id(entity_id)
            if not entity:
                return {Module}ProcessingResult(
                    entity_id=entity_id,
                    success=False,
                    error_message="Entity not found"
                )

            # Process via protocol
            result = await self.processing_service.execute_{action}(
                entity=entity,
                action_data=action_data
            )

            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return {Module}ProcessingResult(
                entity_id=entity_id,
                success=True,
                result_data=result.data,
                processing_time_ms=int(processing_time)
            )

        except Exception as e:
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return {Module}ProcessingResult(
                entity_id=entity_id,
                success=False,
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )
```

### Step 5: DI Container Pattern

**File**: `di/{module}_container.py`

```python
"""
{Module} dependency injection container.
Composition root that wires all dependencies.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from infrastructure.config.settings import Settings, get_settings
from infrastructure.database import get_database_session

# Import concrete implementations
from modules.{module}.application.{module}_service import {Module}Service
from modules.{module}.infrastructure.{external}_adapter import {External}Adapter
from modules.{module}.infrastructure.processing_service import ProcessingService
from modules.{external}.application.{external}_service import {External}Service
from modules.{external}.infrastructure.{external}_repository import {External}Repository

def get_{external}_service(db_session: AsyncSession) -> {External}Service:
    """Create {external} service with dependencies."""
    repository = {External}Repository(db_session)
    return {External}Service(repository)

def get_{module}_service(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)]
) -> {Module}Service:
    """
    Create {module} service with protocol-based dependencies.

    DI container can depend on everything - it's the composition root.
    """
    # Create external service
    external_service = get_{external}_service(db_session)

    # Create processing service
    processing_service = ProcessingService(settings)

    # Return service with protocol dependencies
    return {Module}Service(
        external_service=external_service,  # Implements {External}ServiceProtocol
        processing_service=processing_service,  # Implements ProcessingServiceProtocol
        settings=settings  # Implements SettingsProtocol
    )
```

### Step 6: API Router Pattern

**File**: `modules/{module}/api/{module}_router.py`

```python
"""
{Module} API router.
Handles HTTP endpoints with dependency injection.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from uuid import UUID

from di.{module}_container import get_{module}_service
from modules.{module}.application.{module}_service import {Module}Service
from modules.{module}.api.schemas import (
    {Module}CreateRequest,
    {Module}Response,
    {Module}ProcessRequest,
    ProcessingResponse,
    ErrorResponse
)

router = APIRouter(prefix="/{module}s", tags=["{Module}"])

@router.post("/", response_model={Module}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity}(
    request: {Module}CreateRequest,
    service: Annotated[{Module}Service, Depends(get_{module}_service)]
) -> {Module}Response:
    """Create new {entity} with {module} processing."""
    try:
        result = await service.create_{entity}(request)

        return {Module}Response(
            entity_id=result.entity_id,
            status=result.status,
            created_at=result.created_at,
            processing_metadata=result.processing_metadata,
            message="Created successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error"
        )

@router.post("/{entity_id}/process", response_model=ProcessingResponse)
async def process_{action}(
    entity_id: UUID,
    request: {Module}ProcessRequest,
    service: Annotated[{Module}Service, Depends(get_{module}_service)]
) -> ProcessingResponse:
    """Process {action} for existing {entity}."""
    result = await service.process_{action}(entity_id, request)

    if result.has_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message
        )

    return ProcessingResponse(
        entity_id=result.entity_id,
        success=result.success,
        result_data=result.result_data,
        processing_time_ms=result.processing_time_ms,
        message="Processing completed"
    )

@router.get("/{entity_id}", response_model={Module}Response)
async def get_{entity}(
    entity_id: UUID,
    service: Annotated[{Module}Service, Depends(get_{module}_service)]
) -> {Module}Response:
    """Get {entity} by ID."""
    # Implementation using service protocols
    pass
```

### Step 7: API Schemas Pattern

**File**: `modules/{module}/api/schemas.py`

```python
"""
{Module} API schemas.
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class {Module}CreateRequest(BaseModel):
    """Request schema for creating {entity}."""
    key_field: str = Field(..., min_length=1, max_length=255)
    processing_options: dict[str, str] | None = None
    external_references: list[UUID] | None = None

class {Module}ProcessRequest(BaseModel):
    """Request schema for processing operations."""
    action_type: str = Field(..., regex="^(process|validate|transform)$")
    action_data: dict[str, str] = Field(default_factory=dict)
    options: dict[str, bool] | None = None

class {Module}Response(BaseModel):
    """Response schema for {module} operations."""
    entity_id: UUID
    status: str
    created_at: datetime
    processing_metadata: dict[str, str] | None = None
    message: str

class ProcessingResponse(BaseModel):
    """Response schema for processing operations."""
    entity_id: UUID
    success: bool
    result_data: dict[str, str] | None = None
    processing_time_ms: int | None = None
    message: str

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

### Step 8: tach.toml Configuration

**Add to tach.toml:**

```toml
# DI module (composition root - can depend on everything)
[[modules]]
path = "di"
depends_on = [
    "infrastructure",
    "modules.{module}.application",
    "modules.{module}.infrastructure",
    "modules.{external}.application",
    "modules.{external}.infrastructure",
]

# {Module} domain (zero dependencies)
[[modules]]
path = "modules.{module}.domain"
depends_on = []

# {Module} application (only domain + external domain)
[[modules]]
path = "modules.{module}.application"
depends_on = [
    "modules.{module}.domain",
    "modules.{external}.domain",  # Only for types/protocols
]

# {Module} infrastructure (domain + shared infrastructure)
[[modules]]
path = "modules.{module}.infrastructure"
depends_on = [
    "infrastructure",
    "modules.{module}.domain",
]

# {Module} API (domain + application + infrastructure via DI)
[[modules]]
path = "modules.{module}.api"
depends_on = [
    "di",  # For dependency injection
    "infrastructure",
    "modules.{module}.domain",
    "modules.{module}.application",
]
```

## Validation Commands for LLMs

### Step 9: Quality Gates (Copy-Paste Ready)

**Run after every module implementation:**

```bash
# 1. Module boundary validation (MUST PASS)
cd backend && tach check

# 2. Type safety validation (MUST PASS)
pyright modules/{module}/

# 3. Code quality validation (MUST PASS)
ruff check modules/{module}/

# 4. Test validation (MUST PASS)
pytest modules/{module}/ -v

# 5. Full system validation
pytest backend/ --cov=modules/ --cov-report=term-missing

# 6. Import validation
python -c "from modules.{module}.api.{module}_router import router; print('✅ Imports work')"

# 7. DI container validation
python -c "from di.{module}_container import get_{module}_service; print('✅ DI works')"
```

### Directory Structure Template

**Copy this exact structure for every new module:**

```
modules/{module}/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── {module}_router.py          # FastAPI endpoints
│   └── schemas.py                  # Pydantic models
├── application/
│   ├── __init__.py
│   └── {module}_service.py         # Business logic
├── domain/
│   ├── __init__.py
│   ├── protocols.py                # Cross-module interfaces
│   ├── value_objects.py            # Return types
│   ├── models.py                   # Domain entities (if needed)
│   └── {module}_status.py          # Local enums
└── infrastructure/
    ├── __init__.py
    ├── {external}_adapter.py       # External service adapters
    └── {storage}_repository.py     # Storage implementations

di/
└── {module}_container.py           # Dependency injection
```

### Real Example from Auth Module

**Reference implementation (copy these exact patterns):**

```python
# modules/auth/domain/protocols.py
class AuthUserProtocol(Protocol):
    id: UUID
    email: str
    password_hash: str
    status: AuthUserStatus  # Local enum - no cross-dependencies

    @property
    def is_active(self) -> bool: ...

# modules/auth/domain/value_objects.py
@dataclass(frozen=True)
class CreatedAuthUser:
    user_id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime

# modules/auth/application/authentication_service.py
async def register_user(
    self,
    email: str,
    password: str,
    user_service: UserServiceProtocol  # Accept interface
) -> CreatedAuthUser:  # Return concrete instance
    user = await user_service.create_user(...)
    return CreatedAuthUser(...)  # Concrete value object

# di/auth_container.py
def get_auth_service(
    db_session: Annotated[AsyncSession, Depends(get_database_session)]
) -> AuthenticationService:
    user_service = get_user_service(db_session)
    password_service = PasswordService()
    jwt_service = JWTService(settings)
    return AuthenticationService(user_service, password_service, jwt_service)
```

### Success Criteria Checklist

**Every module implementation must achieve:**

- ✅ `tach check` passes without violations
- ✅ `pyright modules/{module}/` passes without errors
- ✅ No cross-module imports in domain layer
- ✅ All services accept protocols, return value objects
- ✅ DI container wires dependencies correctly
- ✅ API endpoints use dependency injection
- ✅ Local types avoid external dependencies
- ✅ Tests cover all public interfaces

### Common Patterns Reference

**Protocol Definition:**
```python
class {External}ServiceProtocol(Protocol):
    async def operation(self, data: InputProtocol) -> OutputProtocol: ...
```

**Value Object:**
```python
@dataclass(frozen=True)
class {Module}Result:
    field: type
    @property
    def computed_field(self) -> type: ...
```

**Service Implementation:**
```python
async def service_method(
    self,
    input_protocol: InputProtocol
) -> ConcreteValueObject:
    return ConcreteValueObject(...)
```

**DI Container:**
```python
def get_{module}_service(dependencies) -> ConcreteService:
    return ConcreteService(protocol_implementations...)
```

**API Router:**
```python
@router.post("/endpoint")
async def endpoint(
    request: RequestSchema,
    service: Annotated[ServiceType, Depends(get_service)]
) -> ResponseSchema:
    result = await service.method(request)
    return ResponseSchema.from_value_object(result)
```

---

## Auth Module: Proven Reference Implementation

**Current status**: ✅ Production-ready with full test coverage

The auth module demonstrates every pattern in this guide:
- Zero cross-module dependencies in domain
- Protocol-based communication with user module
- Value objects for all return types
- DI composition root pattern
- Clean API integration
- Full validation passing

**Use auth module as the exact template for all future module implementations.**
