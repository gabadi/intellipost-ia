"""
Integration test for static duck typing with Protocols.

This module tests if Pyright can validate Protocol compliance
across independent modules without explicit imports between them.

Test Scenarios:
1. User (from user_management) should satisfy OwnerProtocol (from product_management)
2. User should satisfy ManagerProtocol (from product_management)
3. Creating products with User as owner should work
4. Type checking should validate compatibility
"""

from user_management import User
from product_management import Product, OwnerProtocol, ManagerProtocol


def test_user_as_owner() -> None:
    """Test if User can be used as OwnerProtocol."""
    # Create a user
    user = User.create(email="john@example.com", name="John Doe")
    
    # This should work if User structurally satisfies OwnerProtocol
    owner: OwnerProtocol = user  # Type check validation point
    
    # Use the protocol methods
    owner_id = owner.get_id()
    owner_name = owner.get_name()
    owner_email = owner.get_email()
    
    print(f"Owner ID: {owner_id}")
    print(f"Owner Name: {owner_name}")
    print(f"Owner Email: {owner_email}")
    
    # Create a product with User as owner
    product = Product.create(
        name="Test Product",
        description="A test product",
        owner=user,  # Direct assignment should work
    )
    
    print(f"Created product: {product}")
    print(f"Product owner info: {product.get_owner_info()}")


def test_user_as_manager() -> None:
    """Test if User can be used as ManagerProtocol."""
    # Create a user
    user = User.create(email="jane@example.com", name="Jane Smith")
    
    # This should work if User structurally satisfies ManagerProtocol
    manager: ManagerProtocol = user  # Type check validation point
    
    # Use the protocol methods
    manager_id = manager.get_id()
    manager_name = manager.get_name()
    manager.activate()  # Should work
    is_active = manager.is_active  # Should work
    
    print(f"Manager ID: {manager_id}")
    print(f"Manager Name: {manager_name}")
    print(f"Manager Active: {is_active}")


def test_product_with_user_owner_and_manager() -> None:
    """Test creating a product with User as both owner and manager."""
    # Create users
    owner_user = User.create(email="owner@example.com", name="Product Owner")
    manager_user = User.create(email="manager@example.com", name="Product Manager")
    
    # Create product with User as owner
    product = Product.create(
        name="Complex Product",
        description="A product with both owner and manager",
        owner=owner_user,  # User as OwnerProtocol
        manager=manager_user,  # User as ManagerProtocol
    )
    
    print(f"Created complex product: {product}")
    print(f"Owner info: {product.get_owner_info()}")
    print(f"Manager info: {product.get_manager_info()}")
    
    # Test manager assignment
    new_manager = User.create(email="new.manager@example.com", name="New Manager")
    product.assign_manager(new_manager)
    print(f"Updated manager info: {product.get_manager_info()}")


def test_protocol_type_annotations() -> None:
    """Test explicit protocol type annotations."""
    user = User.create(email="test@example.com", name="Test User")
    
    # Explicit protocol assignments for type checking
    owner_protocol: OwnerProtocol = user
    manager_protocol: ManagerProtocol = user
    
    # Function that accepts protocols
    def process_owner(owner: OwnerProtocol) -> str:
        return f"Processing owner: {owner.get_name()} ({owner.get_email()})"
    
    def process_manager(manager: ManagerProtocol) -> str:
        manager.activate()
        return f"Processing manager: {manager.get_name()}"
    
    # These should work with User instances
    owner_result = process_owner(user)
    manager_result = process_manager(user)
    
    print(f"Owner processing result: {owner_result}")
    print(f"Manager processing result: {manager_result}")
    
    # Test that protocols work with explicitly typed variables
    print(f"Protocol owner name: {owner_protocol.get_name()}")
    print(f"Protocol manager active: {manager_protocol.is_active}")


if __name__ == "__main__":
    print("=== Testing Static Duck Typing with Protocols ===\n")
    
    print("1. Testing User as Owner:")
    test_user_as_owner()
    print()
    
    print("2. Testing User as Manager:")
    test_user_as_manager()
    print()
    
    print("3. Testing Product with User Owner and Manager:")
    test_product_with_user_owner_and_manager()
    print()
    
    print("4. Testing Protocol Type Annotations:")
    test_protocol_type_annotations()
    print()
    
    print("=== All tests completed ===")