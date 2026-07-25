"""
=============================================
  21 - CLASSES - BASICS
=============================================
  From: quickref.me/python
  Object-oriented programming in Python.
=============================================
"""

# ===========================================
# Simple Class Definition
# ===========================================
print("=== SIMPLE CLASS ===")

class MyNewClass:
    """A simple example class."""
    pass  # 'pass' means "do nothing" — placeholder

# Create an instance (object) of the class
my = MyNewClass()
print(f"Instance: {my}")
print(f"Type: {type(my)}")

# ===========================================
# Constructor (__init__)
# ===========================================
print("\n=== CONSTRUCTOR ===")

class Animal:
    def __init__(self, voice):
        """Constructor — called when creating a new Animal."""
        self.voice = voice  # Instance variable

# Creating instances
cat = Animal('Meow')
dog = Animal('Woof')

print(f"cat.voice = '{cat.voice}'")
print(f"dog.voice = '{dog.voice}'")

# ===========================================
# Instance Methods
# ===========================================
print("\n=== INSTANCE METHODS ===")

class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        """Instance method — 'self' refers to the instance."""
        print(f"{self.name} says: Ham-Ham!")

# Creating and using the object
charlie = Dog("Charlie")
charlie.bark()

# ===========================================
# Class Variables (shared across all instances)
# ===========================================
print("\n=== CLASS VARIABLES ===")

class MyClass:
    class_variable = "A class variable!"  # Shared by ALL instances

    def __init__(self, name):
        self.instance_variable = name  # Unique to each instance

# Access directly from the class
print(f"MyClass.class_variable = '{MyClass.class_variable}'")

# Also accessible from instances
x = MyClass("instance X")
y = MyClass("instance Y")
print(f"x.class_variable = '{x.class_variable}'")
print(f"x.instance_variable = '{x.instance_variable}'")
print(f"y.instance_variable = '{y.instance_variable}'")

# ===========================================
# __repr__ — How the object is displayed
# ===========================================
print("\n=== __repr__ METHOD ===")

class Employee:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        """Controls how the object is printed."""
        return f"Employee('{self.name}')"

john = Employee('John')
print(f"repr: {john}")  # Now says something useful!

# ===========================================
# Properties (getters/setters)
# ===========================================
print("\n=== PROPERTIES ===")

class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero!")
        self._celsius = value

temp = Temperature(25)
print(f"Temp: {temp.celsius}°C = {temp.fahrenheit:.1f}°F")

temp.celsius = 30
print(f"After change: {temp.celsius}°C = {temp.fahrenheit:.1f}°F")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a 'Book' class with title and author
#   2. Add a method that prints book info
#   3. Add a __repr__ method for nice printing
# ===========================================
