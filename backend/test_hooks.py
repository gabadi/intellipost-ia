# Test file for backend hooks - TESTING FIXED HOOKS
def test_function(name: str, age: int) -> str:
    if age < 18:
        return f"Hello {name}, you are {age} years old and under 18"
    else:
        return f"Hello {name}, you are {age} years old and an adult"


# Intentional formatting issues
x = 1 + 2 + 3
y = [1, 2, 3, 4, 5]
z = {"name": "test", "value": 123}

print(test_function("John", 25))
