"""
=============================================
  24 - MAGIC METHODS (DUNDERS)
=============================================
  From: quickref.me/python - "Classes & Inheritance" (extended)
  Special methods with double underscores __xx__
  that give your objects special powers.
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
# __len__ — make len() work on your objects
# ===========================================
print("\n=== __len__ ===")

class Team:
    def __init__(self, members):
        self.members = members

    def __len__(self):
        return len(self.members)

    def __repr__(self):
        return f"Team({self.members})"

team = Team(["Alice", "Bob", "Charlie"])
print(f"Team: {team}")
print(f"len(team) = {len(team)}")  # 3

# ===========================================
# __getitem__ — make indexing work []
# ===========================================
print("\n=== __getitem__ (indexing) ===")

class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __getitem__(self, index):
        return self.songs[index]

    def __len__(self):
        return len(self.songs)

playlist = Playlist(["Song A", "Song B", "Song C"])
print(f"playlist[0] = '{playlist[0]}'")
print(f"playlist[-1] = '{playlist[-1]}'")
print(f"len(playlist) = {len(playlist)}")

# Can even slice!
print(f"playlist[0:2] = {playlist[0:2]}")

# ===========================================
# __add__ — make + work on your objects
# ===========================================
print("\n=== __add__ (+) ===")

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Add two points together."""
        return Point(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(3, 4)
p3 = p1 + p2  # Uses __add__
print(f"{p1} + {p2} = {p3}")

# ===========================================
# __eq__ and __lt__ — comparison operators
# ===========================================
print("\n=== COMPARISONS ===")

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def __eq__(self, other):
        """Check equality (==)."""
        return self.area() == other.area()

    def __lt__(self, other):
        """Check less than (<)."""
        return self.area() < other.area()

    def __repr__(self):
        return f"Rect({self.width}x{self.height}={self.area()})"

r1 = Rectangle(3, 4)   # Area = 12
r2 = Rectangle(2, 6)   # Area = 12 (equal)
r3 = Rectangle(5, 2)   # Area = 10 (smaller)

print(f"r1 = {r1}")
print(f"r2 = {r2}")
print(f"r3 = {r3}")
print(f"r1 == r2: {r1 == r2}")  # True (same area)
print(f"r1 == r3: {r1 == r3}")  # False
print(f"r3 < r1:  {r3 < r1}")   # True
print(f"r1 > r3:  {r1 > r3}")   # True (uses __lt__ internally)

# ===========================================
# __call__ — make objects callable like functions
# ===========================================
print("\n=== __call__ ===")

class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        """Make the object callable like a function."""
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(f"double(5) = {double(5)}")  # 10
print(f"triple(5) = {triple(5)}")  # 15

# ===========================================
# __contains__ — make 'in' work
# ===========================================
print("\n=== __contains__ ===")

class VowelString:
    def __init__(self, text):
        self.text = text

    def __contains__(self, item):
        """Check if item is in the string (case-insensitive)."""
        return item.lower() in self.text.lower()

message = VowelString("Hello, World!")
print(f"'hello' in message: {'hello' in message}")  # True
print(f"'Python' in message: {'Python' in message}")  # False

# ===========================================
# TRY IT YOURSELF:
#   1. Create a 'BankAccount' class with __str__ showing the balance
#   2. Add __add__ to combine two accounts
#   3. Add __len__ that returns the number of transactions
# ===========================================
