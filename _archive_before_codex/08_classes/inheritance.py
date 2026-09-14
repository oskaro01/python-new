"""
=============================================
  22 - INHERITANCE (PYTHON EXTENDS)
=============================================
  Python equivalent of JavaScript extends & super().
  
  Topics covered:
    • Parent class (base)
    • Child class inherits (extends)
    • super() to call parent constructor
=============================================
"""

# ===========================================
# Parent Class & Inheritance (extends)
# ===========================================
print("=== CLASS INHERITANCE (extends) ===")

class Media:
    """Parent / base class."""
    def __init__(self, info):
        self.publish_date = info["publish_date"]
        self.name = info["name"]

    def info(self):
        return f"'{self.name}' (published: {self.publish_date})"

class Song(Media):
    """Child class — inherits from Media (like JS 'extends')."""
    def __init__(self, song_data):
        # Call parent constructor — like JS super()
        super().__init__(song_data)
        self.artist = song_data["artist"]

    def play(self):
        print(f"Playing '{self.name}' by {self.artist}...")

# Create a Song instance
my_song = Song({
    "artist": "Queen",
    "name": "Bohemian Rhapsody",
    "publish_date": 1975
})

# Inherited from Media
print(f"my_song.name         = '{my_song.name}'")           # => Bohemian Rhapsody
print(f"my_song.publish_date = {my_song.publish_date}")     # => 1975

# Own property
print(f"my_song.artist       = '{my_song.artist}'")         # => Queen

# Own method
my_song.play()  # => Playing 'Bohemian Rhapsody' by Queen...

# ===========================================
# Multiple levels of inheritance
# ===========================================
print("\n=== INHERITANCE CHAIN ===")

class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} makes a sound.")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        print(f"{self.name} says Woof!")

my_dog = Dog("Yoki", "Labrador")
my_dog.speak()  # => Yoki says Woof!

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a 'Vehicle' parent class with make/model
#   2. Create a 'Car' child class that inherits from Vehicle
#   3. Use super().__init__() in the child class
# ===========================================
