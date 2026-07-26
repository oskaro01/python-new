"""
=============================================
  23 - USER-DEFINED EXCEPTIONS
=============================================
  From: quickref.me/python - "Classes & Inheritance"
  
  Creating your own exception classes by
  inheriting from the built-in Exception class.
=============================================
"""

# ===========================================
# Basic Custom Exception
# ===========================================
print("=== BASIC CUSTOM EXCEPTION ===")

class CustomError(Exception):
    """A custom exception for our application."""
    pass

# Raise and catch it
def test_custom_error():
    try:
        raise CustomError("Something went wrong!")
    except CustomError as e:
        print(f"Caught CustomError: {e}")

test_custom_error()

# ===========================================
# Practical Example: Validation
# ===========================================
print("\n=== PRACTICAL: VALIDATION ===")

class NegativeNumberError(Exception):
    """Raised when a negative number is used where positive is required."""
    def __init__(self, value):
        self.value = value
        super().__init__(f"Negative number not allowed: {value}")

def calculate_square_root(n):
    if n < 0:
        raise NegativeNumberError(n)
    return n ** 0.5

try:
    calculate_square_root(-5)
except NegativeNumberError as e:
    print(f"Error: {e}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a custom exception called 'OutOfStockError'
#   2. Raise it when stock is 0
#   3. Catch it in a try/except block
# ===========================================
