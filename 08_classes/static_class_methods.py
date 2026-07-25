"""
=============================================
  25 - STATIC & CLASS METHODS
=============================================
  From: quickref.me/python - "Classes & Inheritance" (extended)
  @staticmethod — doesn't need self or cls
  @classmethod — receives the class, not the instance
=============================================
"""

# ===========================================
# Class Method (@classmethod) — knows 'cls'
# ===========================================
print("=== CLASS METHOD (@classmethod) ===")

class Dog:
    species = "Canis familiaris"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_birth_year(cls, name, birth_year):
        """Alternative constructor: create a Dog from birth year."""
        current_year = 2026
        age = current_year - birth_year
        return cls(name, age)  # Calls the constructor

    @classmethod
    def print_species(cls):
        """Class method that accesses class variables."""
        print(f"Species: {cls.species}")

    def __repr__(self):
        return f"Dog('{self.name}', {self.age})"

# Using the regular constructor
dog1 = Dog("Rex", 3)
print(f"Regular: {dog1}")

# Using the class method (alternative constructor)
dog2 = Dog.from_birth_year("Max", 2020)
print(f"From birth year: {dog2}")

# Calling a class method on the class itself
Dog.print_species()

# ===========================================
# Static Method (@staticmethod) — knows nothing special
# ===========================================
print("\n=== STATIC METHOD (@staticmethod) ===")

class MathUtils:
    """A utility class with static methods."""

    @staticmethod
    def add(a, b):
        """Static method — no self, no cls. Just a function in a class."""
        return a + b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def is_even(n):
        return n % 2 == 0

# Call static methods without creating an instance!
print(f"MathUtils.add(5, 3) = {MathUtils.add(5, 3)}")
print(f"MathUtils.is_even(7) = {MathUtils.is_even(7)}")

# Also works on instances (but class-level is better):
util = MathUtils()
print(f"util.multiply(4, 5) = {util.multiply(4, 5)}")

# ===========================================
# Practical Example: Factory Pattern
# ===========================================
print("\n=== FACTORY PATTERN ===")

class Employee:
    def __init__(self, name, emp_id, department):
        self.name = name
        self.emp_id = emp_id
        self.department = department

    @classmethod
    def from_string(cls, data_string):
        """Alternative constructor: parse 'name,id,dept' format."""
        name, emp_id, department = data_string.split(",")
        return cls(name.strip(), emp_id.strip(), department.strip())

    @classmethod
    def engineer(cls, name, emp_id):
        """Factory: create an engineer."""
        return cls(name, emp_id, "Engineering")

    @classmethod
    def manager(cls, name, emp_id):
        """Factory: create a manager."""
        return cls(name, emp_id, "Management")

    @staticmethod
    def validate_email(email):
        """Utility: check if email looks valid."""
        return "@" in email and "." in email

    def __repr__(self):
        return f"Employee('{self.name}', '{self.emp_id}', '{self.department}')"

# Create via different methods
emp1 = Employee("Alice", "E001", "Sales")
emp2 = Employee.from_string("Bob, E002, Marketing")
emp3 = Employee.engineer("Charlie", "E003")
emp4 = Employee.manager("Diana", "E004")

print(f"emp1: {emp1}")
print(f"emp2: {emp2}")
print(f"emp3: {emp3}")
print(f"emp4: {emp4}")

# Static method for validation
print(f"\nEmployee.validate_email('alice@work.com'): {Employee.validate_email('alice@work.com')}")
print(f"Employee.validate_email('invalid'): {Employee.validate_email('invalid')}")

# ===========================================
# When to use which?
# ===========================================
print("\n=== WHEN TO USE WHICH? ===")
print("""
Instance method  - needs to access/modify the instance (self)
Class method     - needs to access/modify the class (cls)
                   OR provides alternative constructors
Static method    - doesn't need instance or class data
                   just grouped with the class for organization
""")

# ===========================================
# TRY IT YOURSELF:
#   1. Create a class with a @classmethod that creates an object from a file
#   2. Add a @staticmethod that performs a unit conversion
#   3. Use @classmethod as a factory for different object types
# ===========================================
