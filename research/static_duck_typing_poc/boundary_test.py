"""
Boundary testing for static duck typing with Protocols.

This module tests edge cases and potential limitations to understand
the exact boundaries of Python's static duck typing capabilities.
"""

from typing import Protocol, runtime_checkable, TYPE_CHECKING
from uuid import UUID, uuid4
from dataclasses import dataclass

from user_management import User
from product_management import OwnerProtocol


# Test protocol with property vs method
class PropertyBasedProtocol(Protocol):
    """Protocol using properties instead of methods."""
    
    @property
    def identifier(self) -> UUID:
        """Get identifier as a property."""
        ...
    
    @property
    def display_name(self) -> str:
        """Get display name as a property."""
        ...


# Test runtime checkable protocol
@runtime_checkable
class RuntimeCheckableOwner(Protocol):
    """Runtime checkable version of owner protocol."""
    
    def get_id(self) -> UUID:
        """Get the owner's unique identifier."""
        ...
    
    def get_name(self) -> str:
        """Get the owner's display name."""
        ...
    
    def get_email(self) -> str:
        """Get the owner's email address."""
        ...


# Test class with properties
@dataclass
class PropertyEntity:
    """Entity that uses properties to satisfy protocol."""
    
    id: UUID
    name: str
    
    @classmethod
    def create(cls, name: str) -> "PropertyEntity":
        """Create a new property entity."""
        return cls(id=uuid4(), name=name)
    
    @property
    def identifier(self) -> UUID:
        """Get identifier as property."""
        return self.id
    
    @property
    def display_name(self) -> str:
        """Get display name as property."""
        return self.name


# Test class with method/property mismatch
@dataclass
class MismatchedEntity:
    """Entity with mixed method/property interface."""
    
    id: UUID
    name: str
    email: str
    
    @classmethod
    def create(cls, name: str, email: str) -> "MismatchedEntity":
        """Create a new mismatched entity."""
        return cls(id=uuid4(), name=name, email=email)
    
    @property
    def get_id(self) -> UUID:
        """ID as property (wrong for OwnerProtocol)."""
        return self.id
    
    def get_name(self) -> str:
        """Name as method (correct for OwnerProtocol)."""
        return self.name
    
    @property
    def get_email(self) -> str:
        """Email as property (wrong for OwnerProtocol)."""
        return self.email


# Test minimal interface
class MinimalOwner:
    """Minimal implementation that just satisfies OwnerProtocol."""
    
    def get_id(self) -> UUID:
        return uuid4()
    
    def get_name(self) -> str:
        return "Minimal Owner"
    
    def get_email(self) -> str:
        return "minimal@example.com"


# Test protocol violation at runtime
class RuntimeViolator:
    """Class that looks compatible but violates at runtime."""
    
    def get_id(self) -> UUID:
        # This will raise an exception at runtime
        raise NotImplementedError("ID not implemented")
    
    def get_name(self) -> str:
        return "Runtime Violator"
    
    def get_email(self) -> str:
        return "violator@example.com"


# Test dynamic attribute addition
class DynamicOwner:
    """Owner that gets methods added dynamically."""
    
    def __init__(self):
        self._id = uuid4()
        self._name = "Dynamic Owner"
        self._email = "dynamic@example.com"


def test_property_vs_method_protocols() -> None:
    """Test property-based vs method-based protocols."""
    print("=== Testing Property vs Method Protocols ===")
    
    prop_entity = PropertyEntity.create("Property Test")
    
    # This should work - properties satisfy property protocol
    prop_protocol: PropertyBasedProtocol = prop_entity
    print(f"Property entity ID: {prop_protocol.identifier}")
    print(f"Property entity name: {prop_protocol.display_name}")


def test_runtime_checkable() -> None:
    """Test runtime checkable protocols."""
    print("\n=== Testing Runtime Checkable Protocols ===")
    
    user = User.create(email="runtime@example.com", name="Runtime User")
    minimal = MinimalOwner()
    
    # Test isinstance with runtime checkable protocol
    print(f"User isinstance RuntimeCheckableOwner: {isinstance(user, RuntimeCheckableOwner)}")
    print(f"MinimalOwner isinstance RuntimeCheckableOwner: {isinstance(minimal, RuntimeCheckableOwner)}")
    
    # Test with non-conforming object
    non_conforming = object()
    print(f"object isinstance RuntimeCheckableOwner: {isinstance(non_conforming, RuntimeCheckableOwner)}")


def test_method_property_mismatch() -> None:
    """Test what happens with method/property mismatches."""
    print("\n=== Testing Method/Property Mismatch ===")
    
    mismatched = MismatchedEntity.create("Mismatched", "mismatch@example.com")
    
    # This should fail static type checking because properties 
    # don't satisfy method protocols
    try:
        # Static type checker should catch this, but let's see runtime behavior
        print(f"Mismatched name (method): {mismatched.get_name()}")
        print(f"Mismatched ID (property): {mismatched.get_id}")
        print(f"Mismatched email (property): {mismatched.get_email}")
    except Exception as e:
        print(f"Error with mismatched entity: {e}")


def test_minimal_implementation() -> None:
    """Test minimal protocol implementation."""
    print("\n=== Testing Minimal Implementation ===")
    
    minimal = MinimalOwner()
    
    # This should work both statically and at runtime
    owner: OwnerProtocol = minimal
    print(f"Minimal owner ID: {owner.get_id()}")
    print(f"Minimal owner name: {owner.get_name()}")
    print(f"Minimal owner email: {owner.get_email()}")


def test_runtime_protocol_violation() -> None:
    """Test protocol that passes static checks but fails at runtime."""
    print("\n=== Testing Runtime Protocol Violation ===")
    
    violator = RuntimeViolator()
    
    # Static type checker should accept this
    owner: OwnerProtocol = violator
    
    try:
        # This should fail at runtime
        owner_id = owner.get_id()
        print(f"Violator ID: {owner_id}")
    except Exception as e:
        print(f"Expected runtime error: {e}")
    
    # But other methods should work
    try:
        print(f"Violator name: {owner.get_name()}")
        print(f"Violator email: {owner.get_email()}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def test_dynamic_attribute_addition() -> None:
    """Test adding protocol methods dynamically."""
    print("\n=== Testing Dynamic Attribute Addition ===")
    
    dynamic = DynamicOwner()
    
    # Add methods dynamically
    def get_id(self) -> UUID:
        return self._id
    
    def get_name(self) -> str:
        return self._name
    
    def get_email(self) -> str:
        return self._email
    
    # Bind methods to instance
    import types
    dynamic.get_id = types.MethodType(get_id, dynamic)
    dynamic.get_name = types.MethodType(get_name, dynamic)
    dynamic.get_email = types.MethodType(get_email, dynamic)
    
    # Now it should satisfy the protocol at runtime
    try:
        print(f"Dynamic ID: {dynamic.get_id()}")
        print(f"Dynamic name: {dynamic.get_name()}")
        print(f"Dynamic email: {dynamic.get_email()}")
        
        # But static type checker won't know about this
        # owner: OwnerProtocol = dynamic  # This would fail static checking
        print("Dynamic methods work at runtime")
    except Exception as e:
        print(f"Error with dynamic owner: {e}")


def test_type_checking_behavior() -> None:
    """Test static vs runtime type checking behavior."""
    print("\n=== Testing Type Checking Behavior ===")
    
    if TYPE_CHECKING:
        # This code only runs during static analysis
        print("This code runs during static analysis")
    else:
        print("This code runs at runtime only")
    
    # Test with various implementations
    implementations = [
        User.create(email="test@example.com", name="Test User"),
        MinimalOwner(),
        RuntimeViolator(),
    ]
    
    for impl in implementations:
        impl_type = type(impl).__name__
        print(f"\nTesting {impl_type}:")
        
        # Static type checker should accept all of these
        owner: OwnerProtocol = impl
        
        # Runtime behavior may differ
        try:
            name = owner.get_name()
            email = owner.get_email()
            print(f"  Name: {name}, Email: {email}")
            
            # This might fail for RuntimeViolator
            id_val = owner.get_id()
            print(f"  ID: {id_val}")
        except Exception as e:
            print(f"  Runtime error: {e}")


def test_protocol_inheritance_behavior() -> None:
    """Test how protocol inheritance behaves."""
    print("\n=== Testing Protocol Inheritance Behavior ===")
    
    # Create a protocol that extends OwnerProtocol
    class ExtendedOwnerProtocol(OwnerProtocol, Protocol):
        """Extended owner protocol."""
        
        def get_creation_date(self) -> str:
            """Get creation date."""
            ...
    
    # Test if User can satisfy extended protocol (it can't)
    user = User.create(email="extended@example.com", name="Extended User")
    
    # This should work for base protocol
    base_owner: OwnerProtocol = user
    print(f"User as base owner: {base_owner.get_name()}")
    
    # This should fail for extended protocol since User doesn't have get_creation_date
    # extended_owner: ExtendedOwnerProtocol = user  # Would fail static checking
    print("User cannot satisfy extended protocol (missing get_creation_date)")


if __name__ == "__main__":
    print("=== Boundary Testing for Static Duck Typing ===\n")
    
    test_property_vs_method_protocols()
    test_runtime_checkable()
    test_method_property_mismatch()
    test_minimal_implementation()
    test_runtime_protocol_violation()
    test_dynamic_attribute_addition()
    test_type_checking_behavior()
    test_protocol_inheritance_behavior()
    
    print("\n=== All boundary tests completed ===")