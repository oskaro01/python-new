"""
=============================================
  18 - FUNCTIONS - BASICS
=============================================
  From: quickref.me/python
  Reusable blocks of code.
=============================================
"""

# ===========================================
# Defining a Function
# ===========================================
print("=== DEFINING FUNCTIONS ===")

def hello_world():
    print('Hello, World!')

# Call the function
hello_world()

# ===========================================
# Functions with Parameters
# ===========================================
print("\n=== PARAMETERS ===")

def add(x, y):
    print(f"x is {x}, y is {y}")
    return x + y

result = add(5, 6)
print(f"add(5, 6) = {result}")

# ===========================================
# Default Parameter Values
# ===========================================
print("\n=== DEFAULT VALUES ===")

def add(x, y=10):
    return x + y

print(f"add(5)      = {add(5)}")   # Uses default y=10
print(f"add(5, 20)  = {add(5, 20)}")  # Overrides default

# ===========================================
# Multiple Return Values
# ===========================================
print("\n=== MULTIPLE RETURNS ===")

def swap(x, y):
    return y, x  # Returns a tuple

x, y = 1, 2
print(f"Before: x={x}, y={y}")
x, y = swap(x, y)
print(f"After:  x={x}, y={y}")

# ===========================================
# Docstrings — documenting your function
# ===========================================
print("\n=== DOCSTRINGS ===")

def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"

print(greet("Alice"))
print(f"Docstring: {greet.__doc__}")

# ===========================================
# Type Hints (Python 3.5+)
# ===========================================
print("\n=== TYPE HINTS ===")

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y

# Type hints are just hints — they don't enforce types!
result = multiply(3, 4)
print(f"multiply(3, 4) = {result}")

# ===========================================
# Functions are Objects
# ===========================================
print("\n=== FUNCTIONS AS OBJECTS ===")

def square(x):
    return x ** 2

# Assign a function to a variable
f = square
print(f"f = square, f(5) = {f(5)}")

# Pass a function as an argument
def apply(func, value):
    return func(value)

print(f"apply(square, 4) = {apply(square, 4)}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Write a function that takes a name and returns a greeting
#   2. Write a function that converts Celsius to Fahrenheit
#   3. Write a function with a default parameter value
# ===========================================
