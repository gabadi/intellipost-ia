"""
Test cases for wrong method signature detection in protocols.

This module tests whether type checkers correctly identify when classes
have methods with incorrect signatures compared to protocol requirements.
"""

from typing import Protocol, Any, Optional, Union, Callable
from uuid import UUID
from datetime import datetime


class ServiceProtocol(Protocol):
    """Protocol for service-like objects."""

    def process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data and return result."""
        ...

    def validate_input(self, input_data: str, strict: bool = False) -> bool:
        """Validate input data."""
        ...

    def get_status(self) -> str:
        """Get service status."""
        ...

    def configure(self, config: dict[str, Any], reload: bool = True) -> None:
        """Configure the service."""
        ...


class AsyncServiceProtocol(Protocol):
    """Protocol for async service operations."""

    async def fetch_data(self, url: str, timeout: int = 30) -> dict[str, Any]:
        """Fetch data from URL."""
        ...

    async def save_data(self, data: dict[str, Any], path: str) -> bool:
        """Save data to path."""
        ...

    async def process_batch(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process batch of items."""
        ...


class CompliantService:
    """Service implementation with correct signatures."""

    def process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"processed": True, "data": data}

    def validate_input(self, input_data: str, strict: bool = False) -> bool:
        return len(input_data) > 0

    def get_status(self) -> str:
        return "active"

    def configure(self, config: dict[str, Any], reload: bool = True) -> None:
        pass


class WrongReturnTypeService:
    """Service with wrong return types."""

    def process_data(self, data: dict[str, Any]) -> str:  # Wrong: should return dict[str, Any]
        return "processed"

    def validate_input(self, input_data: str, strict: bool = False) -> str:  # Wrong: should return bool
        return "valid"

    def get_status(self) -> dict[str, str]:  # Wrong: should return str
        return {"status": "active"}

    def configure(self, config: dict[str, Any], reload: bool = True) -> bool:  # Wrong: should return None
        return True


class WrongParameterTypeService:
    """Service with wrong parameter types."""

    def process_data(self, data: str) -> dict[str, Any]:  # Wrong: data should be dict[str, Any]
        return {"processed": True, "data": data}

    def validate_input(self, input_data: dict[str, Any], strict: bool = False) -> bool:  # Wrong: input_data should be str
        return True

    def get_status(self) -> str:
        return "active"

    def configure(self, config: str, reload: bool = True) -> None:  # Wrong: config should be dict[str, Any]
        pass


class MissingParameterService:
    """Service missing required parameters."""

    def process_data(self) -> dict[str, Any]:  # Wrong: missing data parameter
        return {"processed": True}

    def validate_input(self, input_data: str) -> bool:  # Wrong: missing strict parameter (with default)
        return True

    def get_status(self) -> str:
        return "active"

    def configure(self, config: dict[str, Any]) -> None:  # Wrong: missing reload parameter (with default)
        pass


class ExtraParameterService:
    """Service with extra parameters."""

    def process_data(self, data: dict[str, Any], extra_param: str) -> dict[str, Any]:  # Wrong: extra parameter
        return {"processed": True, "data": data}

    def validate_input(self, input_data: str, strict: bool = False, verbose: bool = False) -> bool:  # Wrong: extra parameter
        return True

    def get_status(self, detailed: bool = False) -> str:  # Wrong: extra parameter
        return "active"

    def configure(self, config: dict[str, Any], reload: bool = True, validate: bool = True) -> None:  # Wrong: extra parameter
        pass


class WrongDefaultValueService:
    """Service with wrong default values."""

    def process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"processed": True, "data": data}

    def validate_input(self, input_data: str, strict: bool = True) -> bool:  # Wrong: default should be False
        return True

    def get_status(self) -> str:
        return "active"

    def configure(self, config: dict[str, Any], reload: bool = False) -> None:  # Wrong: default should be True
        pass


class AsyncCompliantService:
    """Async service implementation with correct signatures."""

    async def fetch_data(self, url: str, timeout: int = 30) -> dict[str, Any]:
        return {"url": url, "timeout": timeout}

    async def save_data(self, data: dict[str, Any], path: str) -> bool:
        return True

    async def process_batch(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return items


class SyncAsyncService:
    """Service with sync methods instead of async."""

    def fetch_data(self, url: str, timeout: int = 30) -> dict[str, Any]:  # Wrong: should be async
        return {"url": url, "timeout": timeout}

    def save_data(self, data: dict[str, Any], path: str) -> bool:  # Wrong: should be async
        return True

    def process_batch(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:  # Wrong: should be async
        return items


class WrongAsyncReturnService:
    """Async service with wrong return types."""

    async def fetch_data(self, url: str, timeout: int = 30) -> str:  # Wrong: should return dict[str, Any]
        return "data"

    async def save_data(self, data: dict[str, Any], path: str) -> str:  # Wrong: should return bool
        return "saved"

    async def process_batch(self, items: list[dict[str, Any]]) -> dict[str, Any]:  # Wrong: should return list[dict[str, Any]]
        return {"processed": len(items)}


# Test functions
def use_service(service: ServiceProtocol) -> str:
    """Use service following protocol."""
    data = {"input": "test"}
    result = service.process_data(data)
    valid = service.validate_input("test", strict=True)
    status = service.get_status()
    service.configure({"key": "value"}, reload=False)
    return f"Result: {result}, Valid: {valid}, Status: {status}"


async def use_async_service(service: AsyncServiceProtocol) -> str:
    """Use async service following protocol."""
    data = await service.fetch_data("http://example.com", timeout=60)
    saved = await service.save_data(data, "/tmp/data.json")
    batch_result = await service.process_batch([{"id": 1}, {"id": 2}])
    return f"Data: {data}, Saved: {saved}, Batch: {len(batch_result)}"


def test_wrong_signatures():
    """Test wrong signature detection."""

    # This should work
    compliant = CompliantService()
    result1 = use_service(compliant)  # Should be OK

    # These should fail due to wrong signatures
    wrong_return = WrongReturnTypeService()
    wrong_param = WrongParameterTypeService()
    missing_param = MissingParameterService()
    extra_param = ExtraParameterService()
    wrong_default = WrongDefaultValueService()

    result2 = use_service(wrong_return)    # Should cause error: wrong return types
    result3 = use_service(wrong_param)     # Should cause error: wrong parameter types
    result4 = use_service(missing_param)   # Should cause error: missing parameters
    result5 = use_service(extra_param)     # Should cause error: extra parameters
    result6 = use_service(wrong_default)   # Should cause error: wrong default values

    return result1, result2, result3, result4, result5, result6


async def test_async_wrong_signatures():
    """Test async wrong signature detection."""

    # This should work
    async_compliant = AsyncCompliantService()
    result1 = await use_async_service(async_compliant)  # Should be OK

    # These should fail due to wrong signatures
    sync_async = SyncAsyncService()
    wrong_async_return = WrongAsyncReturnService()

    result2 = await use_async_service(sync_async)           # Should cause error: not async
    result3 = await use_async_service(wrong_async_return)   # Should cause error: wrong return types

    return result1, result2, result3


# Test callable protocols
class CallableProtocol(Protocol):
    """Protocol for callable objects."""

    def __call__(self, x: int, y: int) -> int:
        """Callable with specific signature."""
        ...


class HandlerProtocol(Protocol):
    """Protocol for event handlers."""

    def handle(self, event: str, data: dict[str, Any]) -> None:
        """Handle event with data."""
        ...

    def __call__(self, event: str) -> bool:
        """Callable shortcut for event handling."""
        ...


class CompliantCallable:
    """Callable with correct signature."""

    def __call__(self, x: int, y: int) -> int:
        return x + y


class WrongCallableSignature:
    """Callable with wrong signature."""

    def __call__(self, x: str, y: str) -> str:  # Wrong: parameters should be int, return should be int
        return x + y


class CompliantHandler:
    """Handler with correct signatures."""

    def handle(self, event: str, data: dict[str, Any]) -> None:
        pass

    def __call__(self, event: str) -> bool:
        return True


class WrongHandlerSignature:
    """Handler with wrong signatures."""

    def handle(self, event: str) -> None:  # Wrong: missing data parameter
        pass

    def __call__(self, event: str, extra: str) -> bool:  # Wrong: extra parameter
        return True


def use_callable(func: CallableProtocol) -> int:
    """Use callable following protocol."""
    return func(10, 20)


def use_handler(handler: HandlerProtocol) -> str:
    """Use handler following protocol."""
    handler.handle("test_event", {"key": "value"})
    result = handler("test_event")
    return f"Handler result: {result}"


def test_callable_signatures():
    """Test callable signature detection."""

    # These should work
    compliant_callable = CompliantCallable()
    compliant_handler = CompliantHandler()

    result1 = use_callable(compliant_callable)  # Should be OK
    result2 = use_handler(compliant_handler)    # Should be OK

    # These should fail
    wrong_callable = WrongCallableSignature()
    wrong_handler = WrongHandlerSignature()

    result3 = use_callable(wrong_callable)  # Should cause error: wrong callable signature
    result4 = use_handler(wrong_handler)    # Should cause error: wrong handler signatures

    return result1, result2, result3, result4


if __name__ == "__main__":
    test_wrong_signatures()
    import asyncio
    asyncio.run(test_async_wrong_signatures())
    test_callable_signatures()
