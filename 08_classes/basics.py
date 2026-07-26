"""
=============================================
  21 - CLASSES (PYTHON)
=============================================
  Python equivalent of JavaScript Classes.
  
  Topics covered:
    • Class definition
    • Constructor (__init__)
    • Methods
    • Factory functions
    • Getters and setters (@property)
=============================================
"""

# ===========================================
# 1. Class Definition & Constructor
# ===========================================
print("=== CLASS & CONSTRUCTOR ===")

class Song:
    """A class representing a song."""

    def __init__(self, title="", artist=""):
        """Constructor — like JS constructor()."""
        self.title = title
        self.artist = artist

    def play(self):
        """Instance method — like JS play()."""
        print("Song playing!")

    def stop(self):
        """Instance method — like JS stop()."""
        print("Stopping!")

# Create an instance (like JS `new Song()`)
my_song = Song("Bohemian Rhapsody", "Queen")
print(f"my_song.title  = '{my_song.title}'")    # => Bohemian Rhapsody
print(f"my_song.artist = '{my_song.artist}'")    # => Queen
my_song.play()   # => Song playing!
my_song.stop()   # => Stopping!

# ===========================================
# 2. Methods & 'self' (like JS 'this')
# ===========================================
print("\n=== METHODS & self (like JS this) ===")

class Dog:
    def __init__(self, name):
        self._name = name  # _name by convention (like JS _name)

    def introduce(self):
        """Instance method — 'self' refers to the instance (like JS 'this')."""
        print("This is " + self._name + " !")

my_dog = Dog("Buster")
my_dog.introduce()  # => This is Buster !

# ===========================================
# 3. Factory Functions (like JS factory functions)
# ===========================================
print("\n=== FACTORY FUNCTIONS ===")

def dog_factory(name, age, breed):
    """A factory function that returns a dog object."""

    class Dog:
        def __init__(self, name, age, breed):
            self.name = name
            self.age = age
            self.breed = breed

        def bark(self):
            print("Woof!")

        def __repr__(self):
            return f"Dog({self.name}, {self.age}, {self.breed})"

    return Dog(name, age, breed)

my_dog = dog_factory("Buster", 3, "Labrador")
print(f"Dog: {my_dog}")
my_dog.bark()  # => Woof!

# Simpler factory — returns a namedtuple-like dict
def simple_dog_factory(name, age, breed):
    return {
        "name": name,
        "age": age,
        "breed": breed,
        "bark": lambda: print("Woof!")
    }

dog2 = simple_dog_factory("Max", 5, "Beagle")
print(f"Simple factory: {dog2['name']}, {dog2['breed']}")
dog2["bark"]()

# ===========================================
# 4. Getters and Setters (@property)
# ===========================================
print("\n=== GETTERS & SETTERS ===")

class MyCat:
    def __init__(self):
        self._name = "Dottie"  # Private by convention (_ prefix)

    @property
    def name(self):
        """Getter — like JS get name()."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Setter — like JS set name(newName)."""
        self._name = new_name

my_cat = MyCat()

# Reference invokes the getter (no parentheses needed!)
print(f"my_cat.name = '{my_cat.name}'")  # => Dottie

# Assignment invokes the setter
my_cat.name = "Yankee"
print(f"my_cat.name = '{my_cat.name}'")  # => Yankee

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a 'Book' class with title, author, and a method
#   2. Add a getter and setter for a 'rating' property
#   3. Write a factory function that creates 'Car' objects
# ===========================================
