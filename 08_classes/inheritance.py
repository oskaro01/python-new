"""
=============================================
  22 - INHERITANCE
=============================================
  From: quickref.me/python
  Classes can inherit from other classes.
=============================================
"""

# ===========================================
# Basic Inheritance
# ===========================================
print("=== BASIC INHERITANCE ===")

class Animal:
    """Parent/Base class."""
    def __init__(self, name, legs):
        self.name = name
        self.legs = legs

    def speak(self):
        print(f"{self.name} makes a sound.")

class Dog(Animal):
    """Child class inheriting from Animal."""
    def sound(self):
        print(f"{self.name} says: Woof!")

# Child has all parent attributes + its own methods
yoki = Dog("Yoki", 4)
print(f"Name: {yoki.name}")   # From Parent
print(f"Legs: {yoki.legs}")   # From Parent
yoki.speak()                   # From Parent
yoki.sound()                   # From Child

# ===========================================
# Method Overriding
# ===========================================
print("\n=== METHOD OVERRIDING ===")

class ParentClass:
    def print_self(self):
        print("Parent")

class ChildClass(ParentClass):
    def print_self(self):
        """Override the parent method."""
        print("Child")

parent = ParentClass()
child = ChildClass()
parent.print_self()  # => Parent
child.print_self()   # => Child (overridden)

# ===========================================
# super() — Call the Parent's Method
# ===========================================
print("\n=== super() ===")

class ParentClass2:
    def print_test(self):
        print("Parent Method")

class ChildClass2(ParentClass2):
    def print_test(self):
        print("Child Method")
        super().print_test()  # Call parent's version

child2 = ChildClass2()
child2.print_test()
# Output:
#   Child Method
#   Parent Method

# ===========================================
# super() with __init__
# ===========================================
print("\n=== super() WITH __init__ ===")

class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def info(self):
        return f"{self.brand} {self.model}"

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)  # Call parent's __init__
        self.doors = doors

    def info(self):
        return f"{super().info()} ({self.doors} doors)"

my_car = Car("Toyota", "Camry", 4)
print(my_car.info())  # => Toyota Camry (4 doors)

# ===========================================
# Polymorphism
# ===========================================
print("\n=== POLYMORPHISM ===")

class Cat:
    def sound(self):
        print("Meow!")

class Dog:
    def sound(self):
        print("Woof!")

class Duck:
    def sound(self):
        print("Quack!")

# Same interface, different implementations!
animals = [Cat(), Dog(), Duck()]
for animal in animals:
    animal.sound()  # Each one does its own thing!

# ===========================================
# isinstance() — Check Type
# ===========================================
print("\n=== isinstance() ===")
print(f"Is Dog an Animal? {isinstance(yoki, Animal)}")
print(f"Is yoki a Dog? {isinstance(yoki, Dog)}")
print(f"Is yoki a Cat? {isinstance(yoki, Cat)}")

# ===========================================
# Multiple Inheritance
# ===========================================
print("\n=== MULTIPLE INHERITANCE ===")

class Flyer:
    def fly(self):
        print("Flying...")

class Swimmer:
    def swim(self):
        print("Swimming...")

class Duck2(Flyer, Swimmer):
    def sound(self):
        print("Quack!")

duck = Duck2()
duck.fly()   # From Flyer
duck.swim()  # From Swimmer
duck.sound()  # From Duck2

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a 'Student' class that inherits from a 'Person' class
#   2. Override a method in the child
#   3. Use super() in the child's __init__ to call the parent's __init__
# ===========================================
