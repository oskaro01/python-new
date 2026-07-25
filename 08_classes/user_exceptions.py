"""
=============================================
  23 - USER-DEFINED EXCEPTIONS
=============================================
  From: quickref.me/python - "Classes & Inheritance" section
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

# Raise it
def test_custom_error():
    try:
        raise CustomError("Something went wrong!")
    except CustomError as e:
        print(f"Caught CustomError: {e}")

test_custom_error()

# ===========================================
# Custom Exception with Extra Fields
# ===========================================
print("\n=== CUSTOM EXCEPTION WITH FIELDS ===")

class NegativeNumberError(Exception):
    """Raised when a negative number is used where positive is required."""

    def __init__(self, value, message=None):
        self.value = value
        self.message = message or f"Negative number not allowed: {value}"
        super().__init__(self.message)

def calculate_square_root(n):
    if n < 0:
        raise NegativeNumberError(n, "Cannot calculate sqrt of negative")
    return n ** 0.5

# Test it
try:
    calculate_square_root(-5)
except NegativeNumberError as e:
    print(f"Error: {e.message}")
    print(f"Offending value: {e.value}")

# ===========================================
# Practical Example: Validation
# ===========================================
print("\n=== PRACTICAL: VALIDATION ===")

class InvalidAgeError(Exception):
    """Raised when an age value is invalid."""
    pass

class AgeTooLowError(InvalidAgeError):
    """Raised when age is below minimum."""
    pass

class AgeTooHighError(InvalidAgeError):
    """Raised when age is above maximum."""
    pass

def set_age(age):
    if age < 0:
        raise AgeTooLowError(f"Age {age} is negative!")
    if age < 18:
        raise AgeTooLowError(f"Age {age} is too young (min 18)")
    if age > 120:
        raise AgeTooHighError(f"Age {age} is too old (max 120)")
    print(f"Age set to {age}")

# Test different cases
test_ages = [25, -5, 15, 150]
for age in test_ages:
    try:
        set_age(age)
    except AgeTooLowError as e:
        print(f"  Too low: {e}")
    except AgeTooHighError as e:
        print(f"  Too high: {e}")

# ===========================================
# Exception Hierarchy
# ===========================================
print("\n=== EXCEPTION HIERARCHY ===")

# You can catch parent exceptions to handle multiple types:
try:
    set_age(-1)
except InvalidAgeError as e:
    # Catches BOTH AgeTooLowError and AgeTooHighError!
    print(f"Caught via parent class: {type(e).__name__}: {e}")

# ===========================================
# Exception with Custom Methods
# ===========================================
print("\n=== EXCEPTION WITH METHODS ===")

class ValidationError(Exception):
    """Collects multiple validation errors."""

    def __init__(self):
        self.errors = []
        super().__init__("Validation failed")

    def add_error(self, field, message):
        self.errors.append({"field": field, "message": message})

    @property
    def has_errors(self):
        return len(self.errors) > 0

    def __str__(self):
        return f"ValidationError: {len(self.errors)} error(s)"

try:
    err = ValidationError()
    err.add_error("email", "Email is invalid")
    err.add_error("password", "Too short")
    raise err
except ValidationError as e:
    print(f"Caught: {e}")
    for error in e.errors:
        print(f"  - {error['field']}: {error['message']}")

# ===========================================
# TRY IT YOURSELF:
#   1. Create a custom exception called 'OutOfStockError'
#   2. Add a field for the product name that caused the error
#   3. Raise it and catch it in a try/except block
# ===========================================
