"""
=============================================
  24 - MAGIC METHODS (DUNDERS) — BONUS
=============================================
  🌟 Bonus content — not from the cheat sheet.
  
  Magic methods (__xx__) give your objects
  special powers: len(), indexing, +, ==, etc.
=============================================
"""

# ===========================================
# __str__ vs __repr__
# ===========================================
print("=== __str__ vs __repr__ ===")

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        """For developers: unambiguous representation."""
        return f"Person('{self.name}', {self.age})"

    def __str__(self):
        """For users: readable representation."""
        return f"{self.name} ({self.age} years old)"

p = Person("Alice", 30)
print(f"__str__:   {p}")      # Uses __str__
print(f"__repr__:  {repr(p)}")  # Uses __repr__

# ===========================================
# __len__ — make len() work
# ===========================================
print("\n=== __len__ ===")

class Team:
    def __init__(self, members):
        self.members = members

    def __len__(self):
        return len(self.members)

team = Team(["Alice", "Bob", "Charlie"])
print(f"len(team) = {len(team)}")  # 3

# ===========================================
# __add__ — make + work
# ===========================================
print("\n=== __add__ (+) ===")

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(3, 4)
p3 = p1 + p2
print(f"{p1} + {p2} = {p3}")

# ===========================================
# __eq__ and __lt__ — comparisons
# ===========================================
print("\n=== COMPARISONS ===")

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def __eq__(self, other):
        return self.area() == other.area()

    def __lt__(self, other):
        return self.area() < other.area()

    def __repr__(self):
        return f"Rect({self.width}x{self.height}={self.area()})"

r1 = Rectangle(3, 4)   # Area = 12
r2 = Rectangle(2, 6)   # Area = 12
print(f"{r1} == {r2}: {r1 == r2}")  # True

# ===========================================
# 🌟 These are bonus topics!
# The cheat sheet only covers __repr__.
# ===========================================
