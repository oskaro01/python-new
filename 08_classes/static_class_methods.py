"""
=============================================
  25 - STATIC METHODS (PYTHON)
=============================================
  Python equivalent of JavaScript static methods.
  
  @staticmethod — belongs to the class, not instances.
  @classmethod  — receives the class (cls), not the instance.
=============================================
"""

# ===========================================
# Static Method (@staticmethod)
# ===========================================
print("=== STATIC METHODS (@staticmethod) ===")

class Dog:
    """A Dog class with a static method."""

    def __init__(self, name):
        self._name = name

    def introduce(self):
        """Instance method — needs an instance."""
        print("This is " + self._name + " !")

    @staticmethod
    def bark():
        """Static method — like JS static bark()."""
        print("Woof!")

# Create an instance
my_dog = Dog("Buster")
my_dog.introduce()  # Instance method

# Calling the static method — on the CLASS itself, not the instance
Dog.bark()  # => Woof!

# Also works on instances (but class-level is preferred)
my_dog.bark()  # => Woof!

# ===========================================
# Static Methods as Utility Functions
# ===========================================
print("\n=== STATIC METHODS AS UTILITIES ===")

class MathUtils:
    """A utility class with static methods."""

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def is_even(n):
        return n % 2 == 0

# Call without creating an instance
print(f"MathUtils.add(5, 3) = {MathUtils.add(5, 3)}")       # => 8
print(f"MathUtils.is_even(7) = {MathUtils.is_even(7)}")     # => False
print(f"MathUtils.is_even(10) = {MathUtils.is_even(10)}")   # => True

# ===========================================
# @classmethod — Alternative Constructor
# ===========================================
print("\n=== CLASS METHOD (@classmethod) ===")

class Song:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

    @classmethod
    def from_string(cls, data_string):
        """Alternative constructor: parse 'title - artist' format."""
        title, artist = data_string.split(" - ")
        return cls(title.strip(), artist.strip())

    def play(self):
        print(f"Playing '{self.title}' by {self.artist}...")

# Regular constructor
song1 = Song("Bohemian Rhapsody", "Queen")
song1.play()

# Alternative constructor (class method)
song2 = Song.from_string("Hotel California - Eagles")
song2.play()

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Add a static method to a class
#   2. Call it on the class (not an instance)
#   3. Try adding a @classmethod as an alternative constructor
# ===========================================
