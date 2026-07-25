"""
=============================================
  30 - COMMENTS & DOCSTRINGS
=============================================
  From: quickref.me/python - "Miscellaneous" section
  How to write comments and documentation in Python.
=============================================

This is a module-level docstring. It describes what
this file does. You can access it with:
  print(__doc__)
"""

# ===========================================
# 1. Single-Line Comments
# ===========================================
print("=== SINGLE-LINE COMMENTS ===")

# This is a single-line comment
# Everything after '#' is ignored by Python
print("Hello!")  # Comments can be at the end of a line too

# Use comments to explain WHY, not what:
# Bad: x = x + 1  # Add 1 to x   (obvious!)
# Good: x = x + 1  # Shift index by 1 to skip the header row

# ===========================================
# 2. Multi-Line Strings (used as comments)
# ===========================================
print("\n=== MULTI-LINE STRINGS AS COMMENTS ===")

"""
Multi-line strings can be written
using three double-quotes, and are often used
as documentation (docstrings) or as block comments.
"""

'''
You can also use three single-quotes,
which works the same way.
'''

# These strings are not assigned to anything,
# so they are effectively ignored — like comments!
print("Multi-line strings work as block comments.")

# ===========================================
# 3. Docstrings — Documenting Functions
# ===========================================
print("\n=== FUNCTION DOCSTRINGS ===")

def greet(name):
    """Greet a person by name.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"

print(greet("Alice"))
print(f"Docstring: {greet.__doc__}")

# ===========================================
# 4. Docstrings — Documenting Classes
# ===========================================
print("\n=== CLASS DOCSTRINGS ===")

class Calculator:
    """A simple calculator class.

    This class provides basic arithmetic operations.
    """

    def add(self, a, b):
        """Add two numbers together.

        Args:
            a (int/float): First number.
            b (int/float): Second number.

        Returns:
            int/float: The sum of a and b.
        """
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

calc = Calculator()
print(f"calc.add(5, 3) = {calc.add(5, 3)}")
print(f"calc.__doc__: {calc.__doc__}")
print(f"calc.add.__doc__: {calc.add.__doc__}")

# ===========================================
# 5. Accessing Docstrings
# ===========================================
print("\n=== ACCESSING DOCSTRINGS ===")

# Using the .__doc__ attribute
print(f"greet.__doc__: {greet.__doc__}")

# Using the help() function
# Uncomment to try:
# help(greet)

# ===========================================
# 6. The `pass` Statement (placeholder)
# ===========================================
print("\n=== THE pass STATEMENT ===")

class MyFutureClass:
    """I'll implement this later."""
    pass  # pass = "do nothing" — placeholder

def not_implemented_yet():
    """TODO: implement this function."""
    pass  # Without pass, this would cause an error

print("pass allows empty code blocks (no error).")

# ===========================================
# TRY IT YOURSELF:
#   1. Write a function with a docstring explaining what it does
#   2. Access the docstring using .__doc__
#   3. Use a multi-line string as a comment block
# ===========================================
