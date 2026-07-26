"""
=============================================
  15 - DICTIONARIES (PYTHON OBJECTS)
=============================================
  Python equivalent of JavaScript Objects.
  
  Topics covered:
    • Accessing properties
    • Valid/invalid key names
    • Non-existent properties (KeyError vs .get())
    • Mutable — add, update, delete
    • Destructuring / unpacking
    • Pass by reference
    • Factory functions
    • Methods in dicts (lambdas)
=============================================
"""

# ===========================================
# Accessing Properties (like JS objects)
# ===========================================
print("=== ACCESSING PROPERTIES ===")

apple = {
    "color": "Green",
    "price": {
        "bulk": "$3/kg",
        "smallQty": "$4/kg"
    }
}

print(f"apple['color'] = '{apple['color']}'")            # => Green
print(f"apple['price']['bulk'] = '{apple['price']['bulk']}'")  # => $3/kg

# ===========================================
# Valid / Invalid Key Names
# ===========================================
print("\n=== KEY NAMES ===")

# ✅ Valid: strings, numbers, tuples
train_schedule = {
    "platform num": 10,   # String keys can have spaces
    42: "answer",          # Numbers work as keys
    (1, 2): "tuple key"    # Tuples work as keys
}
print(f"train_schedule: {train_schedule}")

# ❌ Invalid (uncomment to see errors):
# train_schedule = { 40 - 10 + 2: 30 }    # Expressions are evaluated first
# train_schedule = { +compartment: 'C' }  # + alone is invalid

# ===========================================
# Non-existent Properties
# ===========================================
print("\n=== NON-EXISTENT KEYS ===")

class_election = {
    "date": "January 12"
}

# Using .get() returns None (like JS undefined) — no error!
print(f"class_election.get('place') = {class_election.get('place')}")

# Using [] raises KeyError (uncomment to see):
# print(class_election['place'])  # KeyError!

# ===========================================
# Shorthand Object Creation
# ===========================================
print("\n=== SHORTHAND CREATION ===")

# JS: const activity = 'Surfing'; const beach = { activity };
# Python doesn't have this shorthand — you must repeat the key:
activity = 'Surfing'
beach = { 'activity': activity }
print(f"beach = {beach}")  # => {'activity': 'Surfing'}

# ===========================================
# Methods Inside Dicts (like JS object methods)
# ===========================================
print("\n=== METHODS INSIDE DICTS ===")

engine = {
    "start": lambda adverb: print(f"The engine starts up {adverb}..."),
    "sputter": lambda: print("The engine sputters...")
}

engine["start"]("noisily")  # => The engine starts up noisily...
engine["sputter"]()          # => The engine sputters...

# ===========================================
# Mutable — Dictionaries Can Change
# ===========================================
print("\n=== MUTABLE ===")

student = {
    "name": "Sheldon",
    "score": 100,
    "grade": "A"
}
print(f"Before: {student}")

del student["score"]   # Delete a key (like JS delete)
student["grade"] = "F" # Update a value

print(f"After:  {student}")

# ===========================================
# Destructuring / Unpacking
# ===========================================
print("\n=== DESTRUCTURING (UNPACKING) ===")

person = {
    "name": "Tom",
    "age": "22"
}

# Python unpacking — similar to JS destructuring
name, age = person["name"], person["age"]
print(f"name = '{name}'")  # => Tom
print(f"age  = '{age}'")   # => 22

# Or unpack all values at once:
name, age = person.values()
print(f"Unpacked: name='{name}', age='{age}'")

# ===========================================
# Pass by Reference (Objects as Arguments)
# ===========================================
print("\n=== PASS BY REFERENCE ===")

orig_num = 8
orig_obj = {"color": "blue"}

def change_it_up(num, obj):
    num = 7               # Won't affect the original (int is immutable)
    obj["color"] = "red"  # WILL affect the original (dict is mutable)

change_it_up(orig_num, orig_obj)

print(f"orig_num = {orig_num}")            # => 8 (unchanged)
print(f"orig_obj['color'] = '{orig_obj['color']}'")  # => red (changed!)

# ===========================================
# Factory Functions
# ===========================================
print("\n=== FACTORY FUNCTIONS ===")

# JS: const dogFactory = (name, age, breed) => { return { name, age, breed, bark() { ... } } }
def dog_factory(name, age, breed):
    """Factory function — returns a customized dog dict."""
    return {
        "name": name,
        "age": age,
        "breed": breed,
        "bark": lambda: print("Woof!")
    }

my_dog = dog_factory("Buster", 3, "Labrador")
print(f"Dog: {my_dog['name']}, {my_dog['age']} years old, {my_dog['breed']}")
my_dog["bark"]()  # => Woof!

# ===========================================
# Getters and Setters ( __getitem__ / __setitem__ )
# ===========================================
print("\n=== GETTERS & SETTERS (dict style) ===")

# With plain dicts, just access directly:
cat = {"_name": "Dottie"}
print(f"cat['_name'] = '{cat['_name']}'")    # Get

cat["_name"] = "Yankee"                       # Set
print(f"cat['_name'] = '{cat['_name']}'")    # => Yankee

# For true getter/setter behavior, see 08_classes/basics.py

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a dict about yourself (name, age, city, hobby)
#   2. Delete one key using `del`
#   3. Write a factory function that creates "car" dicts
# ===========================================
