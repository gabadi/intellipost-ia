"""
Type Safety Validator for Content Generation Module.

This module provides comprehensive runtime validation to ensure type safety
across all service layer interactions and prevent dict[str, Any] violations.
"""

import inspect
from typing import Any, TypeVar, get_type_hints

from modules.content_generation.domain.exceptions import (
    TypeSafetyViolationError,
)
from modules.content_generation.domain.ports.logging.protocols import (
    ContentLoggerProtocol,
)

T = TypeVar("T")


class TypeSafetyValidator:
    """
    Runtime type safety validator for content generation services.

    This validator ensures that all service layer methods return proper
    value objects instead of raw dictionaries, maintaining type safety.
    """

    def __init__(self, logger: ContentLoggerProtocol):
        """
        Initialize the type safety validator.

        Args:
            logger: Logger protocol for logging validation events
        """
        self.logger = logger
        self._validation_cache: dict[str, bool] = {}

    def validate_service_response(
        self,
        response: Any,
        expected_type: type[T],
        service_name: str,
        method_name: str,
    ) -> T:
        """
        Validate service response matches expected type.

        Args:
            response: The actual response from the service
            expected_type: The expected type for the response
            service_name: Name of the service for error reporting
            method_name: Name of the method for error reporting

        Returns:
            The validated response cast to expected type

        Raises:
            TypeSafetyViolationError: If response doesn't match expected type
        """
        try:
            # Check for None response
            if response is None and expected_type is not type(None):
                self.logger.warning(
                    f"{service_name}.{method_name} returned None, expected {expected_type.__name__}"
                )
                raise TypeSafetyViolationError(
                    f"Service {service_name}.{method_name} returned None but expected {expected_type.__name__}",
                    service_name=service_name,
                    method_name=method_name,
                    expected_type=expected_type.__name__,
                    actual_type="NoneType",
                )

            # Check type match
            if not isinstance(response, expected_type):
                actual_type = type(response).__name__
                expected_type_name = expected_type.__name__

                # Special check for dict[str, Any] violations
                if isinstance(response, dict) and expected_type_name != "dict":
                    self.logger.error(
                        f"CRITICAL TYPE SAFETY VIOLATION: {service_name}.{method_name} "
                        f"returned dict[str, Any] but expected {expected_type_name}. "
                        f"This violates the architecture's type safety requirements."
                    )

                raise TypeSafetyViolationError(
                    f"Service {service_name}.{method_name} type mismatch: "
                    f"expected {expected_type_name}, got {actual_type}",
                    service_name=service_name,
                    method_name=method_name,
                    expected_type=expected_type_name,
                    actual_type=actual_type,
                )

            # Log successful validation
            self.logger.debug(
                f"✅ Type safety validated: {service_name}.{method_name} "
                f"returned correct type {expected_type.__name__}"
            )

            return response

        except TypeSafetyViolationError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during type validation: {e}")
            raise TypeSafetyViolationError(
                f"Validation error for {service_name}.{method_name}: {str(e)}",
                service_name=service_name,
                method_name=method_name,
                expected_type=expected_type.__name__,
                actual_type="unknown",
            ) from e

    def validate_method_signature(
        self,
        service_instance: Any,
        method_name: str,
        expected_return_type: type[T],
    ) -> bool:
        """
        Validate that a service method has the expected return type annotation.

        Args:
            service_instance: The service instance
            method_name: Name of the method to validate
            expected_return_type: Expected return type

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            method = getattr(service_instance, method_name, None)
            if not method:
                self.logger.warning(
                    f"Method {method_name} not found on {type(service_instance).__name__}"
                )
                return False

            # Get type hints
            type_hints = get_type_hints(method)
            return_annotation = type_hints.get("return")

            if return_annotation is None:
                self.logger.warning(
                    f"Method {type(service_instance).__name__}.{method_name} "
                    f"has no return type annotation"
                )
                return False

            # Check if return annotation matches expected type
            is_valid = return_annotation == expected_return_type

            if not is_valid:
                self.logger.warning(
                    f"Method {type(service_instance).__name__}.{method_name} "
                    f"return annotation {return_annotation} doesn't match "
                    f"expected {expected_return_type}"
                )

            return is_valid

        except Exception as e:
            self.logger.error(f"Error validating method signature: {e}")
            return False

    def validate_no_dict_any_returns(
        self,
        service_instance: Any,
        exclude_methods: set[str] | None = None,
    ) -> list[str]:
        """
        Validate that no service methods return dict[str, Any].

        Args:
            service_instance: The service instance to validate
            exclude_methods: Set of method names to exclude from validation

        Returns:
            List of method names that violate type safety (return dict[str, Any])
        """
        violations = []
        exclude_methods = exclude_methods or set()

        try:
            # Get all public methods
            for name, method in inspect.getmembers(service_instance, inspect.ismethod):
                if name.startswith("_") or name in exclude_methods:
                    continue

                try:
                    # Get type hints
                    type_hints = get_type_hints(method)
                    return_annotation = type_hints.get("return")

                    if return_annotation is None:
                        continue

                    # Check if return type is dict[str, Any] or similar
                    return_str = str(return_annotation)
                    if (
                        "dict[str, Any]" in return_str
                        or "Dict[str, Any]" in return_str
                        or "typing.Dict[str, typing.Any]" in return_str
                    ):
                        violations.append(name)
                        self.logger.error(
                            f"TYPE SAFETY VIOLATION: {type(service_instance).__name__}.{name} "
                            f"returns {return_annotation}, should return a proper value object"
                        )

                except Exception as e:
                    self.logger.debug(f"Could not analyze method {name}: {e}")
                    continue

        except Exception as e:
            self.logger.error(
                f"Error scanning service for dict[str, Any] violations: {e}"
            )

        return violations

    def create_validation_decorator(
        self,
        expected_type: type[T],
        service_name: str | None = None,
    ):
        """
        Create a decorator for automatic response validation.

        Args:
            expected_type: Expected return type
            service_name: Optional service name override

        Returns:
            Decorator function
        """

        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)

                # Determine service name
                actual_service_name = service_name
                if not actual_service_name and args:
                    actual_service_name = type(args[0]).__name__

                return self.validate_service_response(
                    result,
                    expected_type,
                    actual_service_name or "Unknown",
                    func.__name__,
                )

            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                # Determine service name
                actual_service_name = service_name
                if not actual_service_name and args:
                    actual_service_name = type(args[0]).__name__

                return self.validate_service_response(
                    result,
                    expected_type,
                    actual_service_name or "Unknown",
                    func.__name__,
                )

            # Return appropriate wrapper based on whether function is async
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def validate_protocol_compliance(
        self,
        service_instance: Any,
        protocol_class: type,
    ) -> dict[str, bool]:
        """
        Validate that a service instance complies with its protocol.

        Args:
            service_instance: The service instance to validate
            protocol_class: The protocol class it should implement

        Returns:
            Dict mapping method names to compliance status
        """
        compliance_results = {}

        try:
            # Get protocol methods
            protocol_methods = [
                name
                for name, _ in inspect.getmembers(protocol_class)
                if not name.startswith("_")
                and callable(getattr(protocol_class, name, None))
            ]

            for method_name in protocol_methods:
                try:
                    # Check if service has the method
                    service_method = getattr(service_instance, method_name, None)
                    if not service_method:
                        compliance_results[method_name] = False
                        self.logger.error(
                            f"Protocol compliance violation: {type(service_instance).__name__} "
                            f"missing method {method_name} from {protocol_class.__name__}"
                        )
                        continue

                    # Get type hints from both protocol and service
                    protocol_hints = get_type_hints(
                        getattr(protocol_class, method_name)
                    )
                    service_hints = get_type_hints(service_method)

                    # Compare return types
                    protocol_return = protocol_hints.get("return")
                    service_return = service_hints.get("return")

                    if protocol_return != service_return:
                        compliance_results[method_name] = False
                        self.logger.error(
                            f"Protocol compliance violation: {type(service_instance).__name__}.{method_name} "
                            f"return type {service_return} doesn't match protocol {protocol_return}"
                        )
                    else:
                        compliance_results[method_name] = True
                        self.logger.debug(
                            f"✅ Protocol compliance: {type(service_instance).__name__}.{method_name}"
                        )

                except Exception as e:
                    compliance_results[method_name] = False
                    self.logger.error(
                        f"Error checking compliance for {method_name}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error validating protocol compliance: {e}")

        return compliance_results

    def get_validation_summary(self) -> dict[str, Any]:
        """
        Get a summary of all validation activities.

        Returns:
            Dict containing validation statistics and results
        """
        return {
            "cache_size": len(self._validation_cache),
            "validations_performed": sum(
                1 for v in self._validation_cache.values() if v
            ),
            "validation_failures": sum(
                1 for v in self._validation_cache.values() if not v
            ),
        }
