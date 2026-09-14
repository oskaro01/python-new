"""
=============================================
  26 - ERROR HANDLING (EXCEPTIONS)
=============================================
  From: quickref.me/python
  Handling errors gracefully with try/except.
=============================================
"""

# ===========================================
# Basic try/except
# ===========================================
print("=== BASIC TRY/EXCEPT ===")

try:
    # Code that might cause an error
    result = 10 / 0
    print("This won't print")
except ZeroDivisionError:
    print("Caught: Can't divide by zero!")

print("Program continues...")

# ===========================================
# Catching Specific Exceptions
# ===========================================
print("\n=== CATCHING SPECIFIC TYPES ===")

try:
    num = int("not_a_number")
except ValueError as e:
    print(f"ValueError: {e}")
except (TypeError, NameError):
    print("Caught TypeError or NameError")

# ===========================================
# Using raise to trigger errors
# ===========================================
print("\n=== RAISING EXCEPTIONS ===")

def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative!")
    if age < 18:
        raise ValueError("Must be 18 or older!")
    return "Access granted!"

# Using the function with try/except
try:
    result = check_age(-5)
    print(result)
except ValueError as e:
    print(f"Error: {e}")

# ===========================================
# else and finally
# ===========================================
print("\n=== ELSE AND FINALLY ===")

def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        result = None
    else:
        # Runs only if NO exception occurred
        print(f"Division successful! Result = {result}")
    finally:
        # ALWAYS runs — even if there's an error
        print("Finally: Cleanup happens here.")

    return result

print("\nTest 1: normal division")
divide(10, 2)

print("\nTest 2: division by zero")
divide(10, 0)

# ===========================================
# Capturing Exception Info
# ===========================================
print("\n=== EXCEPTION INFO ===")

try:
    x = [1, 2, 3]
    print(x[10])  # IndexError
except IndexError as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception args: {e.args}")
    print(f"Exception str: {e}")

# ===========================================
# Custom Exception Classes
# ===========================================
print("\n=== CUSTOM EXCEPTIONS ===")

class CustomError(Exception):
    """A custom exception for our application."""
    pass

class NegativeNumberError(Exception):
    """Raised when a negative number is not allowed."""
    def __init__(self, value):
        self.value = value
        self.message = f"Negative numbers not allowed: {value}"
        super().__init__(self.message)

def calculate_square_root(n):
    if n < 0:
        raise NegativeNumberError(n)
    return n ** 0.5

try:
    calculate_square_root(-5)
except NegativeNumberError as e:
    print(f"Custom error: {e.message}")

# ===========================================
# Common Built-in Exceptions
# ===========================================
print("\n=== COMMON EXCEPTIONS ===")

# ZeroDivisionError: 10 / 0
# ValueError: int("abc")
# TypeError: "hello" + 5
# IndexError: [1,2,3][10]
# KeyError: {"a": 1}["b"]
# FileNotFoundError: open("nonexistent.txt")
# ImportError: import nonexistent_module
# AttributeError: None.something

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Write a try/except that catches a KeyError from a dict
#   2. Create a custom exception for when a password is too short
#   3. Use try/except/else/finally in a function
# ===========================================
