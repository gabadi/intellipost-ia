"""
Advanced test cases for static duck typing with Protocols.

This module explores edge cases and advanced scenarios to thoroughly
validate the capabilities and limitations of Python's static duck typing.
"""

from typing import Any, Protocol, TypeVar, Generic, Union
from uuid import UUID, uuid4
from dataclasses import dataclass

from user_management import User
from product_management import OwnerProtocol


# Additional protocols for testing
class IdentifiableProtocol(Protocol):
    """Protocol for entities with IDs."""
    
    def get_id(self) -> UUID:
        """Get the entity's unique identifier."""
        ...


class NamedProtocol(Protocol):
    """Protocol for entities with names."""
    
    def get_name(self) -> str:
        """Get the entity's name."""
        ...


class ContactableProtocol(Protocol):
    """Protocol for entities that can be contacted."""
    
    def get_email(self) -> str:
        """Get contact email."""
        ...


# Generic protocol
T = TypeVar('T')

class ContainerProtocol(Protocol, Generic[T]):
    """Generic protocol for container-like objects."""
    
    def add_item(self, item: T) -> None:
        """Add an item to the container."""
        ...
    
    def get_items(self) -> list[T]:
        """Get all items in the container."""
        ...


# Test classes that coincidentally satisfy protocols
@dataclass
class Company:
    """Company entity that has no knowledge of user protocols."""
    
    id: UUID
    name: str
    email: str
    headquarters: str
    is_active: bool = True
    
    @classmethod
    def create(cls, name: str, email: str, headquarters: str) -> "Company":
        """Create a new company."""
        return cls(
            id=uuid4(),
            name=name,
            email=email,
            headquarters=headquarters,
            is_active=True
        )
    
    def get_id(self) -> UUID:
        """Get company ID."""
        return self.id
    
    def get_name(self) -> str:
        """Get company name."""
        return self.name
    
    def get_email(self) -> str:
        """Get company email."""
        return self.email
    
    def activate(self) -> None:
        """Activate the company."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the company."""
        self.is_active = False


@dataclass
class Project:
    """Project entity with container-like behavior."""
    
    id: UUID
    name: str
    tasks: list[str]
    
    @classmethod
    def create(cls, name: str) -> "Project":
        """Create a new project."""
        return cls(
            id=uuid4(),
            name=name,
            tasks=[]
        )
    
    def add_item(self, item: str) -> None:
        """Add a task to the project."""
        self.tasks.append(item)
    
    def get_items(self) -> list[str]:
        """Get all tasks."""
        return self.tasks.copy()


# Functions that work with protocols
def process_identifiable(entity: IdentifiableProtocol) -> str:
    """Process any entity that has an ID."""
    return f"Processing entity with ID: {entity.get_id()}"


def process_named(entity: NamedProtocol) -> str:
    """Process any entity that has a name."""
    return f"Processing named entity: {entity.get_name()}"


def process_contactable(entity: ContactableProtocol) -> str:
    """Process any entity that can be contacted."""
    return f"Contact info: {entity.get_email()}"


def process_container(container: ContainerProtocol[str]) -> str:
    """Process a container of strings."""
    items = container.get_items()
    return f"Container has {len(items)} items: {items}"


# Union type with protocols
ProcessableEntity = Union[IdentifiableProtocol, NamedProtocol, ContactableProtocol]


def process_entity(entity: ProcessableEntity) -> str:
    """Process various types of entities using protocol union."""
    # Use proper type narrowing instead of hasattr for protocols
    try:
        # Try to access as IdentifiableProtocol first
        id_val = getattr(entity, 'get_id', None)
        if callable(id_val):
            return f"ID-based: {id_val()}"
        
        # Try to access as NamedProtocol
        name_val = getattr(entity, 'get_name', None)
        if callable(name_val):
            return f"Name-based: {name_val()}"
        
        # Try to access as ContactableProtocol
        email_val = getattr(entity, 'get_email', None)
        if callable(email_val):
            return f"Email-based: {email_val()}"
        
        return "Unknown entity type"
    except Exception as e:
        return f"Error processing entity: {e}"


# Test functions
def test_protocol_intersection() -> None:
    """Test if entities can satisfy multiple protocols simultaneously."""
    print("=== Testing Protocol Intersection ===")
    
    user = User.create(email="test@example.com", name="Test User")
    company = Company.create(
        name="Test Corp",
        email="info@testcorp.com",
        headquarters="Silicon Valley"
    )
    
    # Test if User satisfies multiple protocols
    identifiable: IdentifiableProtocol = user
    named: NamedProtocol = user
    contactable: ContactableProtocol = user
    
    print(f"User as Identifiable: {process_identifiable(identifiable)}")
    print(f"User as Named: {process_named(named)}")
    print(f"User as Contactable: {process_contactable(contactable)}")
    
    # Test if Company satisfies multiple protocols
    company_identifiable: IdentifiableProtocol = company
    company_named: NamedProtocol = company
    company_contactable: ContactableProtocol = company
    
    print(f"Company as Identifiable: {process_identifiable(company_identifiable)}")
    print(f"Company as Named: {process_named(company_named)}")
    print(f"Company as Contactable: {process_contactable(company_contactable)}")


def test_protocol_composition() -> None:
    """Test protocol composition and inheritance-like behavior."""
    print("\n=== Testing Protocol Composition ===")
    
    user = User.create(email="comp@example.com", name="Composed User")
    company = Company.create(
        name="Composed Corp",
        email="info@composed.com",
        headquarters="New York"
    )
    
    # Test that entities satisfying multiple protocols can be used
    # in contexts expecting any of those protocols
    entities = [user, company]
    
    for i, entity in enumerate(entities):
        entity_type = "User" if i == 0 else "Company"
        print(f"\n{entity_type} satisfies:")
        print(f"  - OwnerProtocol: {entity.get_name()} ({entity.get_email()})")
        print(f"  - ManagerProtocol: Active={entity.is_active}")
        print(f"  - IdentifiableProtocol: ID={entity.get_id()}")


def test_generic_protocols() -> None:
    """Test generic protocol satisfaction."""
    print("\n=== Testing Generic Protocols ===")
    
    project = Project.create("Test Project")
    
    # Test that Project satisfies ContainerProtocol[str]
    container: ContainerProtocol[str] = project
    container.add_item("Task 1")
    container.add_item("Task 2")
    container.add_item("Task 3")
    
    result = process_container(container)
    print(f"Generic protocol result: {result}")


def test_protocol_unions() -> None:
    """Test union types with protocols."""
    print("\n=== Testing Protocol Unions ===")
    
    user = User.create(email="union@example.com", name="Union User")
    company = Company.create(
        name="Union Corp",
        email="info@union.com",
        headquarters="Boston"
    )
    
    entities: list[ProcessableEntity] = [user, company]
    
    for entity in entities:
        result = process_entity(entity)
        print(f"Union processing: {result}")


def test_cross_module_compatibility() -> None:
    """Test that entities from different modules are compatible."""
    print("\n=== Testing Cross-Module Compatibility ===")
    
    # Import product management module to test cross-module usage
    from product_management import Product
    
    user = User.create(email="cross@example.com", name="Cross User")
    company = Company.create(
        name="Cross Corp",
        email="info@cross.com",
        headquarters="Seattle"
    )
    
    # Test that Company can be used as owner/manager
    product_with_company_owner = Product.create(
        name="Company-Owned Product",
        description="A product owned by a company",
        owner=company,  # Company as OwnerProtocol
        manager=company,  # Company as ManagerProtocol
    )
    
    print(f"Product with company owner: {product_with_company_owner}")
    print(f"Owner info: {product_with_company_owner.get_owner_info()}")
    print(f"Manager info: {product_with_company_owner.get_manager_info()}")
    
    # Test mixed types
    mixed_product = Product.create(
        name="Mixed Product",
        description="A product with user owner and company manager",
        owner=user,  # User as OwnerProtocol
        manager=company,  # Company as ManagerProtocol
    )
    
    print(f"\nMixed product: {mixed_product}")
    print(f"Owner (User) info: {mixed_product.get_owner_info()}")
    print(f"Manager (Company) info: {mixed_product.get_manager_info()}")


def test_protocol_method_compatibility() -> None:
    """Test method signature compatibility between protocols and implementations."""
    print("\n=== Testing Method Signature Compatibility ===")
    
    def strict_owner_processor(owner: OwnerProtocol) -> dict[str, Any]:
        """Process owner with strict typing."""
        return {
            "id": owner.get_id(),
            "name": owner.get_name(),
            "email": owner.get_email(),
            "type": type(owner).__name__
        }
    
    user = User.create(email="strict@example.com", name="Strict User")
    company = Company.create(
        name="Strict Corp",
        email="info@strict.com",
        headquarters="Austin"
    )
    
    user_result = strict_owner_processor(user)
    company_result = strict_owner_processor(company)
    
    print(f"User processed: {user_result}")
    print(f"Company processed: {company_result}")


def test_protocol_limitations() -> None:
    """Test the limitations of static duck typing."""
    print("\n=== Testing Protocol Limitations ===")
    
    # Create an incomplete class that doesn't fully satisfy a protocol
    class IncompleteEntity:
        """Entity that only partially satisfies OwnerProtocol."""
        
        def __init__(self, name: str):
            self.name = name
        
        def get_name(self) -> str:
            return self.name
        
        # Missing get_id() and get_email() methods
    
    incomplete = IncompleteEntity("Incomplete")
    
    # This should work at runtime for the methods that exist
    print(f"Incomplete entity name: {incomplete.get_name()}")
    
    # Note: Static type checker should catch if we try to use this
    # as OwnerProtocol, but runtime might fail
    try:
        named: NamedProtocol = incomplete  # This should work
        result = process_named(named)
        print(f"Incomplete as Named: {result}")
    except Exception as e:
        print(f"Error with incomplete entity: {e}")


if __name__ == "__main__":
    print("=== Advanced Static Duck Typing Tests ===\n")
    
    test_protocol_intersection()
    test_protocol_composition()
    test_generic_protocols()
    test_protocol_unions()
    test_cross_module_compatibility()
    test_protocol_method_compatibility()
    test_protocol_limitations()
    
    print("\n=== All advanced tests completed ===")