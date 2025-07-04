#!/usr/bin/env python3

import requests
import json

# Test user registration
def test_registration():
    url = "http://localhost:8080/auth/register"
    data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123#",
        "first_name": "John",
        "last_name": "Doe"
    }

    response = requests.post(url, json=data)
    print(f"Registration Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 201:
        print("✅ Registration successful!")
        return response.json()
    else:
        print("❌ Registration failed")
        return None

# Test user login
def test_login():
    url = "http://localhost:8080/auth/login"
    data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123#"
    }

    response = requests.post(url, json=data)
    print(f"Login Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()
    else:
        print("❌ Login failed")
        return None

# Test protected route
def test_protected_route(access_token):
    url = "http://localhost:8080/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    print(f"Protected Route Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        print("✅ Protected route access successful!")
        return response.json()
    else:
        print("❌ Protected route access failed")
        return None

if __name__ == "__main__":
    print("🔐 Testing IntelliPost Authentication System")
    print("=" * 50)

    # Test registration
    print("\n1. Testing User Registration")
    print("-" * 30)
    reg_result = test_registration()

    if reg_result:
        print("\n2. Testing User Login")
        print("-" * 30)
        login_result = test_login()

        if login_result and 'access_token' in login_result:
            print("\n3. Testing Protected Route")
            print("-" * 30)
            test_protected_route(login_result['access_token'])

    print("\n" + "=" * 50)
    print("🏁 Authentication tests completed!")
