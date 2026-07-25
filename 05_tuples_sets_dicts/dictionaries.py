"""
=============================================
  15 - DICTIONARIES
=============================================
  From: quickref.me/python
  Key-Value pairs — like a real dictionary!
  (Or JSON objects, if you know those.)
=============================================
"""

# ===========================================
# Creating Dictionaries
# ===========================================
print("=== CREATING DICTIONARIES ===")

# With curly braces
a = {"one": 1, "two": 2, "three": 3}
print(f"a = {a}")

# Using dict() constructor
b = dict(one=1, two=2, three=3)
print(f"b = {b}")

# Empty dictionary
empty = {}
print(f"empty = {empty}")

# ===========================================
# Accessing Values
# ===========================================
print("\n=== ACCESSING VALUES ===")
print(f"a['one'] = {a['one']}")

# .get() is safer (returns None if key doesn't exist)
print(f"a.get('one') = {a.get('one')}")
print(f"a.get('four') = {a.get('four')}")  # No error!
print(f"a.get('four', 'NOT FOUND') = {a.get('four', 'NOT FOUND')}")

# Accessing with [] on missing key raises KeyError
# print(a['four'])  # KeyError: 'four'

# ===========================================
# Getting All Keys and Values
# ===========================================
print("\n=== KEYS & VALUES ===")
print(f"a.keys():   {a.keys()}")
print(f"a.values(): {a.values()}")
print(f"a.items():  {a.items()}")  # Key-value pairs as tuples

# Iterate over keys
for key in a:
    print(f"  Key: {key} -> Value: {a[key]}")

# Iterate over key-value pairs
for key, value in a.items():
    print(f"  {key}: {value}")

# ===========================================
# Adding and Updating
# ===========================================
print("\n=== ADDING & UPDATING ===")
person = {"name": "John", "age": 30}
print(f"Original: {person}")

# Add a new key-value pair
person["city"] = "New York"
print(f"After adding 'city': {person}")

# Update an existing value
person["age"] = 31
print(f"After updating 'age': {person}")

# Update multiple pairs at once
person.update({"job": "Engineer", "hobby": "Guitar"})
print(f"After update(): {person}")

# ===========================================
# Removing Items
# ===========================================
print("\n=== REMOVING ===")

# pop() — remove and return a value
age = person.pop("age")
print(f"pop('age') returned: {age}")
print(f"After pop: {person}")

# del — delete by key
del person["hobby"]
print(f"After del person['hobby']: {person}")

# popitem() — remove and return the last inserted item
last = person.popitem()
print(f"popitem() returned: {last}")
print(f"After popitem: {person}")

# ===========================================
# Checking if a Key Exists
# ===========================================
print("\n=== CHECKING KEYS ===")
print(f"'name' in person: {'name' in person}")
print(f"'age' in person: {'age' in person}")

# ===========================================
# Practical Example
# ===========================================
print("\n=== PRACTICAL EXAMPLE ===")
student = {
    "name": "Alice",
    "grades": [85, 92, 78],
    "active": True,
    "address": {
        "city": "Boston",
        "state": "MA"
    }
}

print(f"Student: {student}")
print(f"Name: {student['name']}")
print(f"Average grade: {sum(student['grades']) / len(student['grades']):.1f}")
print(f"City: {student['address']['city']}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a dictionary about yourself (name, age, city, hobby)
#   2. Add a new key 'languages' with a list of languages you know
#   3. Loop through and print all keys and values
# ===========================================
